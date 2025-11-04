"""
房源相关模型
"""
from django.db import models
from apps.common.models import BaseModel
from apps.users.models import User


class District(BaseModel):
    """
    区域模型
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='区域名称')
    city = models.CharField(max_length=50, default='上海', verbose_name='城市')
    description = models.TextField(blank=True, verbose_name='区域描述')
    
    class Meta:
        db_table = 'districts'
        verbose_name = '区域'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.city}-{self.name}"


class House(BaseModel):
    """
    房源模型
    """
    STATUS_CHOICES = [
        ('available', '在售'),
        ('sold', '已售'),
        ('reserved', '预定'),
    ]
    
    HOUSE_TYPE_CHOICES = [
        ('1室', '1室'),
        ('2室', '2室'),
        ('3室', '3室'),
        ('4室', '4室'),
        ('5室及以上', '5室及以上'),
    ]
    
    ORIENTATION_CHOICES = [
        ('东', '东'),
        ('南', '南'),
        ('西', '西'),
        ('北', '北'),
        ('东南', '东南'),
        ('东北', '东北'),
        ('西南', '西南'),
        ('西北', '西北'),
        ('南北', '南北'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='房源标题')
    district = models.ForeignKey(District, on_delete=models.CASCADE, 
                                 related_name='houses', verbose_name='所属区域')
    address = models.CharField(max_length=200, verbose_name='详细地址')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总价(万元)')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价(元/平米)')
    area = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='建筑面积(平米)')
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPE_CHOICES, verbose_name='户型')
    floor = models.CharField(max_length=20, verbose_name='楼层')
    total_floors = models.IntegerField(verbose_name='总楼层')
    orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES, verbose_name='朝向')
    decoration = models.CharField(max_length=50, default='精装', verbose_name='装修情况')
    build_year = models.IntegerField(null=True, blank=True, verbose_name='建造年份')
    
    # 地理位置
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, 
                                    blank=True, verbose_name='经度')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, 
                                   blank=True, verbose_name='纬度')
    
    # 房源详情
    description = models.TextField(blank=True, verbose_name='房源描述')
    cover_image = models.ImageField(upload_to='houses/', null=True, 
                                    blank=True, verbose_name='封面图')
    
    # 状态与发布者
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='available', verbose_name='状态')
    agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                             related_name='published_houses', verbose_name='发布经纪人')
    views = models.IntegerField(default=0, verbose_name='浏览次数')
    
    class Meta:
        db_table = 'houses'
        verbose_name = '房源'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['district', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['house_type']),
        ]
    
    def __str__(self):
        return self.title


class HouseImage(BaseModel):
    """
    房源图片模型
    """
    house = models.ForeignKey(House, on_delete=models.CASCADE, 
                             related_name='images', verbose_name='所属房源')
    image = models.ImageField(upload_to='houses/images/', verbose_name='图片')
    order = models.IntegerField(default=0, verbose_name='排序')
    
    class Meta:
        db_table = 'house_images'
        verbose_name = '房源图片'
        verbose_name_plural = verbose_name
        ordering = ['order']
    
    def __str__(self):
        return f"{self.house.title} - 图片{self.order}"


class Transaction(BaseModel):
    """
    成交记录模型
    """
    house = models.ForeignKey(House, on_delete=models.CASCADE, 
                             related_name='transactions', verbose_name='房源')
    deal_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='成交价(万元)')
    deal_date = models.DateField(verbose_name='成交日期')
    buyer_name = models.CharField(max_length=50, blank=True, verbose_name='买家姓名')
    
    class Meta:
        db_table = 'transactions'
        verbose_name = '成交记录'
        verbose_name_plural = verbose_name
        ordering = ['-deal_date']
    
    def __str__(self):
        return f"{self.house.title} - {self.deal_date}"

