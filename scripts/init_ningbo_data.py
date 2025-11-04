#!/usr/bin/env python
"""
宁波地区房源和成交数据初始化脚本
基于宁波真实地理位置和商圈信息生成房源数据
python scripts/init_ningbo_data.py
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

# 宁波真实地标和商圈
NINGBO_LANDMARKS = {
    '海曙区': ['天一广场', '鼓楼', '月湖', '天封塔', '南门', '西门'],
    '鄞州区': ['东部新城', '南部商务区', '印象城', '万达广场', '钱湖北路', '四明中路'],
    '江北区': ['老外滩', '来福士广场', '北岸琴森', '慈城古县城', '洪塘', '庄桥'],
    '镇海区': ['招宝山', '九龙湖', '骆驼', '庄市', '蛟川', '澥浦'],
    '北仑区': ['新碶', '大碶', '小港', '春晓', '梅山', '白峰'],
    '奉化区': ['溪口', '江口', '西坞', '锦屏', '岳林', '萧王庙']
}

COMMUNITY_SUFFIXES = ['花园', '公馆', '华庭', '豪庭', '苑', '城', '湾', '府', '里', '坊', '新村', '小区']
HOUSE_TYPES = ['1室', '2室', '3室', '4室', '5室']
ORIENTATIONS = ['南', '东', '东南', '南北', '西南']
DECORATIONS = ['精装', '简装', '毛坯', '豪华装修']



def create_ningbo_districts():
    """创建宁波区域数据"""
    print("正在创建宁波区域数据...")
    
    districts_data = [
        {'name': '海曙区', 'city': '宁波', 'description': '宁波市中心城区，商业繁华'},
        {'name': '鄞州区', 'city': '宁波', 'description': '宁波市政府所在地，东部新城核心区'},
        {'name': '江北区', 'city': '宁波', 'description': '宁波市北部城区，老外滩所在地'},
        {'name': '镇海区', 'city': '宁波', 'description': '宁波市东北部，港口重镇'},
        {'name': '北仑区', 'city': '宁波', 'description': '宁波市东部，深水港所在地'},
        {'name': '奉化区', 'city': '宁波', 'description': '宁波市南部，溪口风景区所在地'},
    ]
    
    districts = []
    for data in districts_data:
        district, created = District.objects.get_or_create(
            name=data['name'],
            defaults={'city': data['city'], 'description': data['description']}
        )
        districts.append(district)
        if created:
            print(f"创建区域: {district.name}")
    
    return districts

def create_houses():
    """创建房源数据"""
    print("\n开始创建房源数据...")
    
    districts = District.objects.filter(city='宁波')  # 只获取宁波的区域
    agents = list(User.objects.filter(role='agent'))
    
    if not agents:
        print("错误：没有找到经纪人用户，请先创建经纪人账户")
        return []
    
    houses = []
    
    for district in districts:
        landmarks = NINGBO_LANDMARKS.get(district.name, [district.name])
        
        # 每个区域生成12-18套房源
        num_houses = random.randint(12, 18)
        
        for i in range(num_houses):
            # 随机选择地标和小区
            landmark = random.choice(landmarks)
            suffix = random.choice(COMMUNITY_SUFFIXES)
            community_name = f'{landmark}{suffix}'
            
            # 随机生成房源属性
            house_type = random.choice(HOUSE_TYPES)
            area = round(random.uniform(45, 200), 2)
            
            # 根据区域设置不同的价格区间（宁波房价相对较低）
            if district.name in ['海曙区', '鄞州区']:
                unit_price = random.uniform(25000, 45000)  # 核心区域
            elif district.name in ['江北区', '镇海区']:
                unit_price = random.uniform(20000, 35000)  # 次核心区域
            else:
                unit_price = random.uniform(15000, 28000)  # 外围区域
            
            total_price = round((area * unit_price) / 10000, 2)
            unit_price = round(unit_price, 2)
            
            floor_num = random.randint(1, 28)
            total_floors = random.randint(floor_num, 33)
            floor = f'{floor_num}/{total_floors}'
            
            build_year = random.randint(2008, 2024)
            
            # 随机选择经纪人
            agent = random.choice(agents)
            
            # 随机生成经纬度（宁波市区范围）
            # 宁波大致范围：纬度 29.7-30.2，经度 121.3-121.8
            latitude = round(random.uniform(29.7, 30.2), 6)
            longitude = round(random.uniform(121.3, 121.8), 6)
            
            house = House(
                title=f'{district.name}{house_type}{random.choice(["精品", "优质", "豪华", "舒适", "温馨"])}房源',
                district=district,
                address=f'{district.name}{landmark}街道{random.randint(1, 888)}号{community_name}',
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
                description=f'位于{district.name}{landmark}核心区域，{community_name}，{house_type}户型，建筑面积{area}平方米，{random.choice(ORIENTATIONS)}朝向，{random.choice(DECORATIONS)}，楼层{floor}，房龄{2025-build_year}年。周边配套设施完善，交通便利，临近地铁站，周边有商场、学校、医院等生活配套设施齐全。宁波优质居住区域，投资自住两相宜。',
                agent=agent,
                status='available',
                views=random.randint(30, 1200)  # 随机生成初始浏览量
            )
            
            houses.append(house)
    
    # 批量创建
    House.objects.bulk_create(houses)
    print(f"成功创建 {len(houses)} 套房源")
    
    # 重新从数据库获取新创建的房源（带ID）
    new_houses = list(House.objects.filter(district__city='宁波').order_by('-id')[:len(houses)])
    
    return new_houses

def create_transactions(houses):
    """创建成交记录"""
    print("\n开始创建成交记录...")
    
    transactions = []
    
    for house in houses:
        # 为每套房源生成1-5条历史成交记录
        num_transactions = random.randint(1, 5)
        
        for i in range(num_transactions):
            # 随机生成成交日期（近18个月内）
            days_ago = random.randint(1, 540)
            deal_date = datetime.now().date() - timedelta(days=days_ago)
            
            # 成交价格为挂牌价的82%-96%
            deal_price = round(float(house.price) * random.uniform(0.82, 0.96), 2)
            
            # 生成买家姓氏（宁波常见姓氏）
            surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '吴', 
                       '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高',
                       '应', '毛', '俞', '金', '叶', '沈', '童', '袁', '方', '邵']
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
    print("宁波地区数据统计")
    print("="*60)
    
    # 只统计宁波地区的数据
    ningbo_districts = District.objects.filter(city='宁波')
    ningbo_houses = House.objects.filter(district__city='宁波')
    ningbo_transactions = Transaction.objects.filter(house__district__city='宁波')
    
    # 房源统计
    total_houses = ningbo_houses.count()
    print(f"\n总房源数: {total_houses}")
    
    print("\n各区域房源统计:")
    for district in ningbo_districts:
        count = ningbo_houses.filter(district=district).count()
        avg_price = ningbo_houses.filter(district=district).aggregate(
            avg_price=django.db.models.Avg('price')
        )['avg_price']
        if avg_price:
            print(f"  {district.name}: {count}套, 均价 {avg_price:.2f}万")
    
    # 成交记录统计
    total_transactions = ningbo_transactions.count()
    print(f"\n总成交记录数: {total_transactions}")
    
    print("\n各区域成交统计:")
    for district in ningbo_districts:
        count = ningbo_transactions.filter(house__district=district).count()
        if count > 0:
            print(f"  {district.name}: {count}条")
    
    # 近6个月成交统计
    six_months_ago = datetime.now().date() - timedelta(days=180)
    recent_transactions = ningbo_transactions.filter(deal_date__gte=six_months_ago)
    print(f"\n近6个月成交记录数: {recent_transactions.count()}")
    
    # 价格区间统计
    print("\n价格区间统计:")
    price_ranges = [
        (0, 100, "100万以下"),
        (100, 200, "100-200万"),
        (200, 300, "200-300万"),
        (300, 500, "300-500万"),
        (500, 1000, "500万以上")
    ]
    
    for min_price, max_price, label in price_ranges:
        if max_price == 1000:  # 500万以上
            count = ningbo_houses.filter(price__gte=min_price).count()
        else:
            count = ningbo_houses.filter(price__gte=min_price, price__lt=max_price).count()
        print(f"  {label}: {count}套")

def main():
    """主函数"""
    print("="*60)
    print("宁波地区房源和成交数据初始化")
    print("="*60)
    
    # 确认添加数据
    confirm = input("\n是否添加宁波地区房源和成交数据? (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    # 创建宁波区域
    create_ningbo_districts()
    
    # 创建房源
    houses = create_houses()
    
    if not houses:
        return
    
    # 创建成交记录
    create_transactions(houses)
    
    # 打印统计信息
    print_statistics()
    
    print("\n" + "="*60)
    print("宁波地区数据初始化完成！")
    print("="*60)
    print("\n提示:")
    print("1. 请重启Django服务器以刷新缓存")
    print("2. 前端访问 http://localhost:3000/analysis 查看数据分析")
    print("3. 选择'鄞州区'和'近6个月'应该能看到完整的趋势图表")
    print("4. 宁波地区房价相对合理，适合投资和居住")
    print("5. 数据已添加到现有数据库中，不会影响其他城市的数据")

if __name__ == '__main__':
    # 导入Django的Avg函数
    import django.db.models
    main()