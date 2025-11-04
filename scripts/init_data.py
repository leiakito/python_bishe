"""
初始化测试数据脚本
使用方法: python manage.py shell < scripts/init_data.py
是一个基础的测试数据脚本，适合项目初期的简单测试。
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate_project.settings')
django.setup()

from apps.users.models import User
from apps.houses.models import District, House
from datetime import datetime, timedelta
import random

print("开始初始化数据...")

# 创建区域
districts_data = [
    {'name': '浦东新区', 'city': '上海', 'description': '上海市中心城区之一'},
    {'name': '黄浦区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '徐汇区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '长宁区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '静安区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '普陀区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '虹口区', 'city': '上海', 'description': '上海市中心城区'},
    {'name': '杨浦区', 'city': '上海', 'description': '上海市中心城区'},
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

# 创建测试用户
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        phone='13800000000',
        role='admin'
    )
    print(f"创建管理员: {admin.username}")

if not User.objects.filter(username='agent1').exists():
    agent = User.objects.create_user(
        username='agent1',
        email='agent1@example.com',
        password='agent123',
        phone='13800000001',
        role='agent',
        real_name='张经纪',
        company='安居房产'
    )
    print(f"创建经纪人: {agent.username}")

# 创建示例房源
house_types = ['1室', '2室', '3室', '4室']
orientations = ['南', '东南', '南北', '东', '西南']
decorations = ['精装', '简装', '毛坯', '豪装']

agent = User.objects.filter(role='agent').first()

for i in range(50):
    district = random.choice(districts)
    house_type = random.choice(house_types)
    area = random.uniform(50, 150)
    unit_price = random.uniform(40000, 100000)
    price = (area * unit_price) / 10000
    
    house, created = House.objects.get_or_create(
        title=f"{district.name}{house_type}精品房源{i+1}",
        defaults={
            'district': district,
            'address': f'{district.name}某某路{random.randint(1, 999)}号',
            'price': round(price, 2),
            'unit_price': round(unit_price, 2),
            'area': round(area, 2),
            'house_type': house_type,
            'floor': f'{random.randint(1, 20)}/{random.randint(20, 33)}',
            'total_floors': random.randint(20, 33),
            'orientation': random.choice(orientations),
            'decoration': random.choice(decorations),
            'build_year': random.randint(2000, 2023),
            'longitude': 121.4 + random.uniform(-0.2, 0.2),
            'latitude': 31.2 + random.uniform(-0.1, 0.1),
            'description': f'这是一套位于{district.name}的优质{house_type}房源，交通便利，配套完善。',
            'status': 'available',
            'agent': agent,
            'views': random.randint(0, 1000)
        }
    )
    if created:
        print(f"创建房源: {house.title}")

print("数据初始化完成！")
print(f"区域数量: {District.objects.count()}")
print(f"用户数量: {User.objects.count()}")
print(f"房源数量: {House.objects.count()}")

