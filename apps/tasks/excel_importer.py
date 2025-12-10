"""
Excel 导入工具: 负责扫描 data 目录中的爬虫 Excel, 将其写入数据库.
"""
from __future__ import annotations

import logging
import random
import re
import shutil
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.houses.models import District, House, HouseImage
from apps.users.models import User

logger = logging.getLogger(__name__)

DEFAULT_CITY = "北京"
PHONE_PREFIXES = ["131", "132", "133", "134", "135", "136", "137", "138", "139", "150", "151", "152"]

@dataclass
class ImportStats:
    file: str
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    error_messages: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": self.errors,
            "error_messages": self.error_messages or [],
        }


class FangExcelImporter:
    """
    读取 data 目录下的 Excel 文件, 将其内容同步到 House / District / User.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        base_dir = Path(settings.BASE_DIR)
        self.data_dir = data_dir or (base_dir / "data")
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.placeholder_images = self._load_placeholder_images()

    def run(self) -> Dict[str, Any]:
        if not self.data_dir.exists():
            logger.info("Data directory %s does not exist, skipping import.", self.data_dir)
            return {"files": [], "total_created": 0, "total_updated": 0, "total_errors": 0}

        excel_files = sorted(self.data_dir.glob("*.xlsx"))
        results: List[ImportStats] = []

        for file_path in excel_files:
            stats = self._process_file(file_path)
            results.append(stats)

        summary = {
            "files": [stat.to_dict() for stat in results],
            "total_created": sum(stat.created for stat in results),
            "total_updated": sum(stat.updated for stat in results),
            "total_errors": sum(stat.errors for stat in results),
        }
        logger.info(
            "Excel import completed: %s created, %s updated, %s errors",
            summary["total_created"],
            summary["total_updated"],
            summary["total_errors"],
        )
        return summary

    def _process_file(self, file_path: Path) -> ImportStats:
        stats = ImportStats(file=str(file_path), error_messages=[])
        logger.info("Processing Excel file: %s", file_path)
        try:
            df = pd.read_excel(file_path)
        except Exception as exc:
            stats.errors += 1
            stats.error_messages.append(f"读取失败: {exc}")
            logger.exception("Failed to read Excel file %s", file_path)
            return stats

        df = df.where(pd.notnull(df), None)
        records = df.to_dict("records")

        for row in records:
            if not row.get("title"):
                stats.skipped += 1
                continue
            try:
                created = self._import_row(row)
                if created:
                    stats.created += 1
                else:
                    stats.updated += 1
            except Exception as exc:
                stats.errors += 1
                logger.exception("Failed to import row from %s: %s", file_path, exc)
                stats.error_messages.append(str(exc))

        self._archive_file(file_path)
        return stats

    @transaction.atomic
    def _import_row(self, row: Dict[str, Any]) -> bool:
        district = self._get_or_create_district(row)
        agent = self._get_or_create_agent(row)

        house_data = self._build_house_defaults(row, district, agent)
        lookup = {
            "title": house_data["title"],
            "district": district,
            "address": house_data["address"],
        }

        defaults = house_data.copy()
        for key in ("title", "district", "address"):
            defaults.pop(key, None)

        house, created = House.objects.update_or_create(defaults=defaults, **lookup)

        if created:
            logger.debug("Created house %s (%s)", house.title, house.id)
        else:
            logger.debug("Updated house %s (%s)", house.title, house.id)

        self._ensure_house_image(house, house_data["cover_image"])

        return created

    def _build_house_defaults(self, row: Dict[str, Any], district: District, agent: Optional[User]) -> Dict[str, Any]:
        price = self._to_decimal(row.get("price_total_wan"))
        unit_price = self._to_decimal(row.get("unit_price"))
        area = self._to_decimal(row.get("area_sqm"), digits=8)
        total_floors = self._to_int(row.get("total_floors"), default=1)
        build_year = self._to_int(row.get("build_year"), default=None)

        house_type = self._normalize_house_type(row.get("house_type") or row.get("layout"))
        orientation = self._normalize_orientation(row.get("orientation"))
        status = row.get("status") if row.get("status") in dict(House.STATUS_CHOICES) else "available"
        decoration = row.get("decoration") or "精装"
        if decoration not in ["精装", "简装", "毛坯"]:
            decoration = "精装"

        cover_image = self._choose_cover_image()
        description_extra = f"来源: {row.get('data_source', 'fang.com/top')} | 链接: {row.get('house_url', '')} | ID: {row.get('source_id', '')}"
        description = "\n".join(
            filter(None, [row.get("description"), description_extra, row.get("tags")])
        )

        longitude = self._to_decimal(row.get("longitude"), digits=10, decimal_places=7)
        latitude = self._to_decimal(row.get("latitude"), digits=10, decimal_places=7)

        return {
            "title": row.get("title").strip(),
            "district": district,
            "address": (row.get("address") or "").strip()[:200],
            "price": price,
            "unit_price": unit_price,
            "area": area,
            "house_type": house_type,
            "floor": (row.get("floor") or "未知楼层").strip()[:20],
            "total_floors": total_floors,
            "orientation": orientation or "南北",
            "decoration": decoration,
            "build_year": build_year,
            "longitude": longitude,
            "latitude": latitude,
            "description": description[:1000],
            "cover_image": cover_image,
            "status": status,
            "agent": agent,
            "views": 0,
        }

    def _get_or_create_district(self, row: Dict[str, Any]) -> District:
        district_name = (row.get("district_name") or row.get("region") or "未知区域").split("-")[0].strip()
        defaults = {
            "city": DEFAULT_CITY,
            "description": row.get("region") or "",
        }
        district, created = District.objects.get_or_create(name=district_name, defaults=defaults)
        if created:
            logger.debug("Created district %s (%s)", district.name, district.id)
        else:
            updates = {}
            if district.city != DEFAULT_CITY:
                updates["city"] = DEFAULT_CITY
            if not district.description and defaults["description"]:
                updates["description"] = defaults["description"]
            if updates:
                for field, value in updates.items():
                    setattr(district, field, value)
                district.save(update_fields=list(updates.keys()))
        return district

    def _get_or_create_agent(self, row: Dict[str, Any]) -> Optional[User]:
        agent_name = (row.get("agent_name") or "").strip()
        if not agent_name:
            return self._default_agent()

        agent = User.objects.filter(role="agent", real_name=agent_name).first()
        if agent:
            return agent

        agent = User.objects.filter(role="agent", username=agent_name).first()
        if agent:
            # 补充真实姓名
            if not agent.real_name:
                agent.real_name = agent_name
                agent.save(update_fields=["real_name"])
            return agent

        username = self._sanitize_username(agent_name)
        if User.objects.filter(username=username).exists():
            username = f"{username}_{timezone.now().strftime('%H%M%S%f')}"

        phone = self._generate_unique_phone()
        password = User.objects.make_random_password()
        agent = User.objects.create_user(
            username=username,
            password=password,
            phone=phone,
            role="agent",
            real_name=agent_name,
            company="北京经纪联盟",
            is_verified=True,
        )
        logger.debug("Created agent %s (%s)", agent.real_name, agent.id)
        return agent

    def _default_agent(self) -> Optional[User]:
        agent = User.objects.filter(role="agent").order_by("id").first()
        if agent:
            return agent

        phone = self._generate_unique_phone()
        agent = User.objects.create_user(
            username="beijing_agent",
            password=User.objects.make_random_password(),
            phone=phone,
            role="agent",
            real_name="北京经纪人",
            company="北京经纪联盟",
            is_verified=True,
        )
        return agent

    def _generate_unique_phone(self) -> str:
        while True:
            prefix = random.choice(PHONE_PREFIXES)
            suffix = "".join(random.choices("0123456789", k=8))
            phone = prefix + suffix
            if not User.objects.filter(phone=phone).exists():
                return phone

    def _load_placeholder_images(self) -> List[str]:
        media_root = Path(settings.MEDIA_ROOT)
        images_dir = media_root / "houses" / "images"
        if not images_dir.exists():
            return ["houses/images/shutterstock_1722002524.jpg"]

        images = [
            str(path.relative_to(media_root)).replace("\\", "/")
            for path in images_dir.iterdir()
            if path.is_file()
        ]
        return images or ["houses/images/shutterstock_1722002524.jpg"]

    def _choose_cover_image(self) -> str:
        return random.choice(self.placeholder_images)

    def _ensure_house_image(self, house: House, image_path: str) -> None:
        """
        确保HouseImage至少有一张图片，使用同一张占位图。
        """
        normalized = image_path
        if normalized.startswith(settings.MEDIA_URL):
            normalized = normalized.replace(settings.MEDIA_URL, "", 1).lstrip("/")

        has_image = house.images.filter(image=normalized).exists()
        if not has_image:
            HouseImage.objects.create(house=house, image=normalized, order=0)

    @staticmethod
    def _sanitize_username(name: str) -> str:
        ascii_name = re.sub(r"[^A-Za-z0-9]", "", name)
        if not ascii_name:
            ascii_name = "agent"
        return f"bj_{ascii_name.lower()[:12]}"

    @staticmethod
    def _normalize_house_type(value: Optional[str]) -> str:
        if not value:
            return "1室"
        value = value.strip()
        if value in dict(House.HOUSE_TYPE_CHOICES):
            return value
        match = re.search(r"(\d+)", value)
        if match:
            rooms = int(match.group(1))
            if rooms >= 5:
                return "5室及以上"
            return f"{rooms}室"
        return "1室"

    @staticmethod
    def _normalize_orientation(value: Optional[str]) -> str:
        if not value:
            return ""
        return value.replace("向", "").strip()

    @staticmethod
    def _to_decimal(value: Any, digits: int = 10, decimal_places: int = 2) -> Decimal:
        if value in (None, "", "null"):
            return Decimal("0")
        try:
            quantize_str = "1." + "0" * decimal_places
            decimal_value = Decimal(str(value))
            return decimal_value.quantize(Decimal(quantize_str))
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def _to_int(value: Any, default: Optional[int] = 0) -> Optional[int]:
        if value in (None, "", "null"):
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _archive_file(self, file_path: Path) -> None:
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        destination = self.processed_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        try:
            shutil.move(str(file_path), destination)
            logger.info("Archived Excel %s -> %s", file_path, destination)
        except Exception as exc:
            logger.warning("Failed to archive Excel %s: %s", file_path, exc)
