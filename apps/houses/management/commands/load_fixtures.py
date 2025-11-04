"""
自动加载 data_fixtures 文件夹中的 JSON 数据
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.houses.models import House, Transaction, District
from apps.users.models import User
import json
import os
from pathlib import Path
from datetime import datetime


class Command(BaseCommand):
    help = '从 data_fixtures 文件夹加载房源和成交记录数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='在导入前清除现有数据',
        )
        parser.add_argument(
            '--folder',
            type=str,
            default='data_fixtures',
            help='指定数据文件夹路径（默认：data_fixtures）',
        )

    def handle(self, *args, **options):
        clear_data = options['clear']
        folder_name = options['folder']
        
        # 获取数据文件夹路径
        base_dir = settings.BASE_DIR
        data_folder = base_dir / folder_name
        
        if not data_folder.exists():
            self.stdout.write(self.style.ERROR(f'数据文件夹不存在: {data_folder}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'开始从 {data_folder} 加载数据...'))
        
        # 如果需要清除数据
        if clear_data:
            self.stdout.write(self.style.WARNING('正在清除现有数据...'))
            Transaction.objects.all().delete()
            House.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('现有数据已清除'))
        
        # 查找所有 JSON 文件
        json_files = list(data_folder.glob('*.json'))
        
        if not json_files:
            self.stdout.write(self.style.WARNING(f'在 {data_folder} 中没有找到 JSON 文件'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'找到 {len(json_files)} 个 JSON 文件'))
        
        total_houses = 0
        total_transactions = 0
        
        # 逐个处理 JSON 文件
        for json_file in json_files:
            self.stdout.write(f'\n处理文件: {json_file.name}')
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 处理房源数据
                houses_data = data.get('houses', data.get('房源数据', []))
                transactions_data = data.get('transactions', data.get('成交记录', []))
                
                houses_count = self.load_houses(houses_data)
                transactions_count = self.load_transactions(transactions_data)
                
                total_houses += houses_count
                total_transactions += transactions_count
                
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ 加载了 {houses_count} 套房源，{transactions_count} 条成交记录'
                ))
                
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'  ✗ JSON 解析错误: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ 处理失败: {e}'))
        
        # 输出总计
        self.stdout.write(self.style.SUCCESS(
            f'\n\n总计: 导入了 {total_houses} 套房源，{total_transactions} 条成交记录'
        ))

    def load_houses(self, houses_data):
        """加载房源数据"""
        count = 0
        
        for house_info in houses_data:
            try:
                # 获取或创建区域
                district_name = house_info.get('district', house_info.get('district_name'))
                district_id = house_info.get('district_id')
                
                if district_id:
                    district = District.objects.get(id=district_id)
                elif district_name:
                    district, _ = District.objects.get_or_create(name=district_name)
                else:
                    self.stdout.write(self.style.WARNING(f'    跳过房源（缺少区域信息）: {house_info.get("title")}'))
                    continue
                
                # 获取经纪人
                agent_username = house_info.get('agent', house_info.get('agent_username', 'agent1'))
                try:
                    agent = User.objects.get(username=agent_username)
                except User.DoesNotExist:
                    # 如果找不到指定经纪人，使用第一个经纪人
                    agent = User.objects.filter(role='agent').first()
                    if not agent:
                        self.stdout.write(self.style.WARNING(f'    跳过房源（找不到经纪人）: {house_info.get("title")}'))
                        continue
                
                # 检查房源是否已存在（通过地址判断）
                address = house_info.get('address')
                if House.objects.filter(address=address).exists():
                    continue  # 跳过已存在的房源
                
                # 创建房源
                house = House.objects.create(
                    title=house_info.get('title', '房源'),
                    district=district,
                    address=address,
                    price=float(house_info.get('price', 0)),
                    unit_price=float(house_info.get('unit_price', 0)),
                    area=float(house_info.get('area', 0)),
                    house_type=house_info.get('house_type', '2室'),
                    floor=house_info.get('floor', '1/1'),
                    total_floors=house_info.get('total_floors', 1),
                    orientation=house_info.get('orientation', '南'),
                    decoration=house_info.get('decoration', '精装'),
                    build_year=house_info.get('build_year', 2020),
                    latitude=float(house_info.get('latitude', 31.2304)),
                    longitude=float(house_info.get('longitude', 121.4737)),
                    description=house_info.get('description', ''),
                    agent=agent,
                    status=house_info.get('status', 'available')
                )
                
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    跳过房源（错误: {e}）: {house_info.get("title")}'))
                continue
        
        return count

    def load_transactions(self, transactions_data):
        """加载成交记录数据"""
        count = 0
        
        for trans_info in transactions_data:
            try:
                # 获取房源
                house_id = trans_info.get('house_id')
                house_address = trans_info.get('house_address')
                
                house = None
                if house_id:
                    try:
                        house = House.objects.get(id=house_id)
                    except House.DoesNotExist:
                        pass
                
                if not house and house_address:
                    try:
                        house = House.objects.get(address=house_address)
                    except House.DoesNotExist:
                        pass
                
                if not house:
                    continue  # 找不到对应房源，跳过
                
                # 解析日期
                deal_date_str = trans_info.get('deal_date')
                if isinstance(deal_date_str, str):
                    deal_date = datetime.fromisoformat(deal_date_str.replace('Z', '+00:00')).date()
                else:
                    deal_date = deal_date_str
                
                # 检查成交记录是否已存在
                if Transaction.objects.filter(house=house, deal_date=deal_date).exists():
                    continue  # 跳过已存在的记录
                
                # 创建成交记录
                Transaction.objects.create(
                    house=house,
                    deal_price=float(trans_info.get('deal_price', 0)),
                    deal_date=deal_date,
                    buyer_name=trans_info.get('buyer_name', '买家')
                )
                
                count += 1
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    跳过成交记录（错误: {e}）'))
                continue
        
        return count

