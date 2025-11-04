#!/usr/bin/env python
"""
上海地区房源和成交数据初始化脚本
是一个更加完善和专业的数据初始化脚本，专门为上海房地产项目设计，包含了
python scripts/init_shanghai_data.py
"""
import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
import random

# 设置 Django 环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

from apps.houses.models import House, Transaction, District
from apps.users.models import User

# 上海真实地标和小区名称
SHANGHAI_LANDMARKS = {
    '浦东新区': ['陆家嘴', '世纪公园', '金桥', '张江', '碧云'],
    '黄浦区': ['外滩', '南京路', '人民广场', '豫园', '新天地'],
    '徐汇区': ['徐家汇', '衡山路', '田林', '漕河泾', '上海南站'],
    '长宁区': ['中山公园', '虹桥', '古北', '天山', '北新泾'],
    '静安区': ['静安寺', '南京西路', '曹家渡', '江宁路', '北站'],
    '普陀区': ['长寿路', '长风', '真如', '桃浦', '武宁'],
    '虹口区': ['四川北路', '虹口足球场', '鲁迅公园', '曲阳', '凉城'],
    '杨浦区': ['五角场', '大学路', '控江路', '新江湾城', '黄兴公园']
}

COMMUNITY_SUFFIXES = ['花园', '公馆', '华庭', '豪庭', '苑', '城', '湾', '府', '里', '坊']
HOUSE_TYPES = ['1室', '2室', '3室', '4室']
ORIENTATIONS = ['南', '东', '东南', '南北']
DECORATIONS = ['精装', '简装', '毛坯', '豪华装修']

def clear_existing_data():
    """清除现有数据"""
    print("正在清除现有数据...")
    Transaction.objects.all().delete()
    House.objects.all().delete()
    print(f"已清除所有房源和成交记录")

def create_houses():
    """创建房源数据"""
    print("\n开始创建房源数据...")
    
    districts = District.objects.all()
    agents = list(User.objects.filter(role='agent'))
    
    if not agents:
        print("错误：没有找到经纪人用户，请先创建经纪人账户")
        return []
    
    houses = []
    
    for district in districts:
        landmarks = SHANGHAI_LANDMARKS.get(district.name, [district.name])
        
        # 每个区域生成10-15套房源
        num_houses = random.randint(10, 15)
        
        for i in range(num_houses):
            # 随机选择地标和小区
            landmark = random.choice(landmarks)
            suffix = random.choice(COMMUNITY_SUFFIXES)
            community_name = f'{landmark}{suffix}'
            
            # 随机生成房源属性
            house_type = random.choice(HOUSE_TYPES)
            area = round(random.uniform(50, 180), 2)
            
            # 根据区域设置不同的价格区间（万元）
            if district.name in ['黄浦区', '徐汇区', '长宁区', '静安区']:
                unit_price = random.uniform(70000, 120000)
            elif district.name == '浦东新区':
                unit_price = random.uniform(55000, 95000)
            else:
                unit_price = random.uniform(45000, 75000)
            
            total_price = round((area * unit_price) / 10000, 2)
            unit_price = round(unit_price, 2)
            
            floor_num = random.randint(1, 30)
            total_floors = random.randint(floor_num, 35)
            floor = f'{floor_num}/{total_floors}'
            
            build_year = random.randint(2005, 2023)
            
            # 随机选择经纪人
            agent = random.choice(agents)
            
            # 随机生成经纬度（上海市区范围）
            # 上海大致范围：纬度 30.9-31.5，经度 121.1-121.9
            latitude = round(random.uniform(30.9, 31.5), 6)
            longitude = round(random.uniform(121.1, 121.9), 6)
            
            house = House(
                title=f'{district.name}{house_type}{random.choice(["精品", "优质", "豪华", "舒适"])}房源',
                district=district,
                address=f'{district.name}{landmark}街道{random.randint(1, 999)}号{community_name}',
                price=total_price,
                unit_price=unit_price,
                area=area,
                house_type=house_type,
                floor=floor,
                total_floors=total_floors,
                orientation=random.choice(ORIENTATIONS),
                decoration=random.choice(DECORATIONS),
                build_year=build_year,
                latitude=latitude,
                longitude=longitude,
                description=f'位于{district.name}{landmark}核心区域，{community_name}，{house_type}户型，建筑面积{area}平方米，{random.choice(ORIENTATIONS)}朝向，{random.choice(DECORATIONS)}，楼层{floor}，房龄{2025-build_year}年。周边配套设施齐全，交通便利，紧邻地铁站，周边有大型商场、学校、医院等生活配套。',
                agent=agent,
                status='available',
                views=random.randint(50, 1500)  # 随机生成初始浏览量
            )
            
            houses.append(house)
    
    # 批量创建
    House.objects.bulk_create(houses)
    print(f"成功创建 {len(houses)} 套房源")
    
    # 重新从数据库获取所有房源（带ID）
    houses = list(House.objects.all())
    
    return houses

def create_transactions(houses):
    """创建成交记录"""
    print("\n开始创建成交记录...")
    
    transactions = []
    
    for house in houses:
        # 为每套房源生成2-6条历史成交记录
        num_transactions = random.randint(2, 6)
        
        for i in range(num_transactions):
            # 随机生成成交日期（近12个月内）
            days_ago = random.randint(1, 365)
            deal_date = datetime.now().date() - timedelta(days=days_ago)
            
            # 成交价格为挂牌价的85%-98%
            deal_price = round(float(house.price) * random.uniform(0.85, 0.98), 2)
            
            # 生成买家姓氏
            surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', 
                       '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
            buyer_name = f'{random.choice(surnames)}先生/女士'
            
            transaction = Transaction(
                house=house,
                deal_price=deal_price,
                deal_date=deal_date,
                buyer_name=buyer_name
            )
            
            transactions.append(transaction)
    
    # 批量创建
    Transaction.objects.bulk_create(transactions)
    print(f"成功创建 {len(transactions)} 条成交记录")
    
    return transactions

def print_statistics():
    """打印统计信息"""
    print("\n" + "="*60)
    print("数据统计")
    print("="*60)
    
    # 房源统计
    total_houses = House.objects.count()
    print(f"\n总房源数: {total_houses}")
    
    districts = District.objects.all()
    print("\n各区域房源统计:")
    for district in districts:
        count = House.objects.filter(district=district).count()
        avg_price = House.objects.filter(district=district).aggregate(
            avg_price=django.db.models.Avg('price')
        )['avg_price']
        if avg_price:
            print(f"  {district.name}: {count}套, 均价 {avg_price:.2f}万")
    
    # 成交记录统计
    total_transactions = Transaction.objects.count()
    print(f"\n总成交记录数: {total_transactions}")
    
    print("\n各区域成交统计:")
    for district in districts:
        count = Transaction.objects.filter(house__district=district).count()
        if count > 0:
            print(f"  {district.name}: {count}条")
    
    # 近6个月成交统计
    six_months_ago = datetime.now().date() - timedelta(days=180)
    recent_transactions = Transaction.objects.filter(deal_date__gte=six_months_ago)
    print(f"\n近6个月成交记录数: {recent_transactions.count()}")

def main():
    """主函数"""
    print("="*60)
    print("上海地区房源和成交数据初始化")
    print("="*60)
    
    # 确认清除数据
    confirm = input("\n是否清除现有数据并重新生成? (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    # 清除现有数据
    clear_existing_data()
    
    # 创建房源
    houses = create_houses()
    
    if not houses:
        return
    
    # 创建成交记录
    create_transactions(houses)
    
    # 打印统计信息
    print_statistics()
    
    print("\n" + "="*60)
    print("数据初始化完成！")
    print("="*60)
    print("\n提示:")
    print("1. 请重启Django服务器以刷新缓存")
    print("2. 前端访问 http://localhost:3000/analysis 查看数据分析")
    print("3. 选择'浦东新区'和'近6个月'应该能看到完整的趋势图表")

if __name__ == '__main__':
    # 导入Django的Avg函数
    import django.db.models
    main()

