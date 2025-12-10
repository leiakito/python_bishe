"""
Utilities for crawling Fang.com top listings and exporting them to Excel.
"""
from __future__ import annotations

import html
import json
import logging
import random
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

FANG_TOP_URL = "https://esf.fang.com/top/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://esf.fang.com/",
}

BEIJING_LON_RANGE = (115.40, 117.60)
BEIJING_LAT_RANGE = (39.40, 41.10)

DECORATION_CHOICES = ["精装", "简装", "毛坯"]

AREA_PATTERN = re.compile(r"([\d.]+)\s*㎡")
TOTAL_FLOOR_PATTERN = re.compile(r"共(\d+)层")
UNIT_PRICE_PATTERN = re.compile(r"([\d,]+)")


@dataclass
class FangListing:
    """
    Dataclass mirroring the fields we want to persist for each listing.
    """

    source_id: str
    title: str
    house_url: str
    layout: str
    house_type: str
    area_sqm: Optional[float]
    floor: str
    total_floors: Optional[int]
    orientation: str
    price_total_wan: Optional[float]
    unit_price: Optional[float]
    agent_name: str
    agent_store_url: str
    agent_id: Optional[str]
    community: str
    region: str
    district_name: str
    sub_district: str
    address: str
    tags: List[str]
    cover_image: str
    status: str
    decoration: str
    build_year: int
    description: str
    longitude: float
    latitude: float
    city: str = "北京"
    data_source: str = "fang.com/top"
    scraped_at: str = field(default_factory=lambda: timezone.now().isoformat())

    def as_dict(self) -> Dict[str, Any]:
        record = asdict(self)
        record["tags"] = ", ".join(self.tags)
        return record


class FangTopScraper:
    """
    Scraper that fetches Fang.com top listings, enriches them, and writes Excel files.
    """

    def __init__(self, url: str = FANG_TOP_URL, timeout: Tuple[int, int] = (8, 20)) -> None:
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()

    def _build_headers(self) -> Dict[str, str]:
        headers = HEADERS_BASE.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        return headers

    def fetch_html(self) -> str:
        response = self.session.get(
            self.url,
            headers=self._build_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        if not response.encoding:
            response.encoding = response.apparent_encoding or "utf-8"
        return response.text

    def parse_listings(self, html_text: str) -> List[FangListing]:
        soup = BeautifulSoup(html_text, "html.parser")
        nodes = soup.select('dl[dataflag="bg"]')
        listings: List[FangListing] = []

        for node in nodes:
            try:
                record = self._parse_node(node)
                if record:
                    listings.append(record)
            except Exception as exc:
                logger.warning("Failed to parse listing node: %s", exc, exc_info=True)

        return listings

    def _parse_node(self, node) -> Optional[FangListing]:
        metadata = self._extract_metadata(node)
        title_link = node.select_one("dd h4 a")
        if not title_link:
            return None

        title = title_link.get_text(strip=True)
        house_url = self._normalize_url(title_link.get("href"))
        layout, area_sqm, floor_text, total_floors, orientation = self._extract_house_info(node)

        price_total, unit_price = self._extract_price_info(node)

        agent_anchor = node.select_one("p.tel_shop span.people_name a")
        agent_name = agent_anchor.get_text(strip=True) if agent_anchor else ""
        agent_store_url = self._normalize_url(agent_anchor.get("href")) if agent_anchor else ""
        community, region = self._extract_location(node)
        tags = [span.get_text(strip=True) for span in node.select("p.label span") if span.get_text(strip=True)]
        cover_image = self._extract_cover(node)

        district_name, sub_district = self._split_region(region)
        address = " / ".join(filter(None, [community, region]))
        longitude, latitude = self._random_beijing_coordinates()

        return FangListing(
            source_id=str(metadata.get("houseid") or title),
            title=title,
            house_url=house_url,
            layout=layout,
            house_type=self._to_house_type(layout),
            area_sqm=area_sqm,
            floor=floor_text,
            total_floors=total_floors,
            orientation=self._normalize_orientation(orientation),
            price_total_wan=price_total,
            unit_price=unit_price,
            agent_name=agent_name,
            agent_store_url=agent_store_url,
            agent_id=str(metadata.get("agentid") or "") or None,
            community=community,
            region=region,
            district_name=district_name,
            sub_district=sub_district,
            address=address,
            tags=tags,
            cover_image=cover_image,
            status="available",
            decoration=random.choice(DECORATION_CHOICES),
            build_year=random.randint(1995, timezone.now().year),
            description=" | ".join(tags) if tags else "",
            longitude=longitude,
            latitude=latitude,
        )

    def export_to_excel(self, listings: List[FangListing]) -> Tuple[Optional[Path], int]:
        if not listings:
            return None, 0

        df = pd.DataFrame([listing.as_dict() for listing in listings])

        numeric_columns = ["area_sqm", "total_floors", "price_total_wan", "unit_price", "longitude", "latitude"]
        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df = df.drop_duplicates(subset=["source_id"]).reset_index(drop=True)

        output_dir = Path(settings.BASE_DIR) / "data"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"fang_top_{timestamp}.xlsx"

        df.to_excel(output_path, index=False)
        return output_path, len(df)

    def run(self) -> Dict[str, Any]:
        html_text = self.fetch_html()
        listings = self.parse_listings(html_text)
        output_path, count = self.export_to_excel(listings)

        return {
            "count": count,
            "output_path": str(output_path) if output_path else "",
            "timestamp": timezone.now().isoformat(),
        }

    @staticmethod
    def _extract_metadata(node) -> Dict[str, Any]:
        raw = node.get("data-bg")
        if not raw:
            return {}
        try:
            return json.loads(html.unescape(raw))
        except json.JSONDecodeError:
            logger.debug("Failed to decode metadata: %s", raw)
            return {}

    @staticmethod
    def _extract_house_info(node) -> Tuple[str, Optional[float], str, Optional[int], str]:
        tel_shop = node.select_one("p.tel_shop")
        if not tel_shop:
            return "", None, "", None, ""

        parts = [part.strip() for part in tel_shop.get_text(separator="|", strip=True).split("|") if part.strip()]
        layout = parts[0] if parts else ""

        area_match = next((AREA_PATTERN.search(part) for part in parts if "㎡" in part), None)
        area_sqm = float(area_match.group(1)) if area_match else None

        floor_part = next((part for part in parts if "层" in part), "")
        total_floors_match = TOTAL_FLOOR_PATTERN.search(floor_part)
        total_floors = int(total_floors_match.group(1)) if total_floors_match else None

        floor_text = floor_part.split("（")[0] if floor_part else ""

        orientation_part = next((part for part in parts if part.endswith("向")), "")

        return layout, area_sqm, floor_text, total_floors, orientation_part

    @staticmethod
    def _extract_price_info(node) -> Tuple[Optional[float], Optional[float]]:
        total_price_node = node.select_one("dd.price_right span.red b")
        unit_price_node = node.select_one("dd.price_right span:nth-of-type(2)")

        total_price = float(total_price_node.get_text(strip=True)) if total_price_node else None

        unit_price_value = None
        if unit_price_node:
            match = UNIT_PRICE_PATTERN.search(unit_price_node.get_text())
            if match:
                unit_price_value = float(match.group(1).replace(",", ""))

        return total_price, unit_price_value

    @staticmethod
    def _extract_location(node) -> Tuple[str, str]:
        add_shop = node.select_one("p.add_shop")
        if not add_shop:
            return "", ""

        community_anchor = add_shop.select_one("a")
        community = community_anchor.get_text(strip=True) if community_anchor else ""
        region_span = add_shop.select_one("span")
        region = region_span.get_text(strip=True) if region_span else ""

        return community, region

    @staticmethod
    def _extract_cover(node) -> str:
        image = node.select_one("dt img")
        if not image:
            return ""
        cover = image.get("data-src") or image.get("src") or ""
        return FangTopScraper._normalize_url(cover)

    @staticmethod
    def _split_region(region: str) -> Tuple[str, str]:
        if "-" in region:
            district, sub = region.split("-", 1)
            return district.strip(), sub.strip()
        return region, ""

    @staticmethod
    def _normalize_url(url: Optional[str]) -> str:
        if not url:
            return ""
        if url.startswith("//"):
            return f"https:{url}"
        if url.startswith("http"):
            return url
        return urljoin(FANG_TOP_URL, url)

    @staticmethod
    def _normalize_orientation(value: str) -> str:
        return value.replace("向", "").strip() if value else ""

    @staticmethod
    def _to_house_type(layout: str) -> str:
        match = re.search(r"(\d+)室", layout)
        if match:
            rooms = int(match.group(1))
            if rooms >= 5:
                return "5室及以上"
            return f"{rooms}室"
        return ""

    @staticmethod
    def _random_beijing_coordinates() -> Tuple[float, float]:
        # Spread the coordinates across Beijing administrative bounds
        lon = round(random.uniform(*BEIJING_LON_RANGE), 6)
        lat = round(random.uniform(*BEIJING_LAT_RANGE), 6)
        return lon, lat

