"""
房源序列化器
"""
from rest_framework import serializers
from .models import District, House, HouseImage, Transaction
from apps.users.serializers import UserSerializer


class DistrictSerializer(serializers.ModelSerializer):
    """
    区域序列化器
    """
    house_count = serializers.SerializerMethodField()
    
    class Meta:
        model = District
        fields = ['id', 'name', 'city', 'description', 'house_count', 'created_at']
    
    def get_house_count(self, obj):
        return obj.houses.filter(status='available').count()


class HouseImageSerializer(serializers.ModelSerializer):
    """
    房源图片序列化器
    """
    class Meta:
        model = HouseImage
        fields = ['id', 'house', 'image', 'order']
    
    def to_representation(self, instance):
        """自定义序列化输出，返回完整URL"""
        representation = super().to_representation(instance)
        if instance.image:
            request = self.context.get('request')
            if request:
                try:
                    representation['image'] = request.build_absolute_uri(instance.image.url)
                except Exception:
                    # 如果构建绝对URL失败，返回相对URL
                    representation['image'] = instance.image.url
            else:
                representation['image'] = instance.image.url
        return representation


class HouseListSerializer(serializers.ModelSerializer):
    """
    房源列表序列化器
    """
    district_name = serializers.CharField(source='district.name', read_only=True)
    agent_name = serializers.CharField(source='agent.real_name', read_only=True)
    
    class Meta:
        model = House
        fields = ['id', 'title', 'district_name', 'address', 'price', 'unit_price', 
                  'area', 'house_type', 'floor', 'orientation', 'cover_image', 
                  'status', 'agent_name', 'views', 'created_at']
    
    def to_representation(self, instance):
        """自定义序列化输出，返回完整URL"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        cover_url = instance.get_cover_image_url()
        if cover_url and request and not cover_url.startswith('http'):
            try:
                cover_url = request.build_absolute_uri(cover_url)
            except Exception:
                pass
        representation['cover_image'] = cover_url
            
        return representation


class HouseDetailSerializer(serializers.ModelSerializer):
    """
    房源详情序列化器
    """
    district_info = DistrictSerializer(source='district', read_only=True)
    agent_info = UserSerializer(source='agent', read_only=True)
    images = HouseImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = House
        fields = ['id', 'title', 'district_info', 'address', 'price', 'unit_price', 
                  'area', 'house_type', 'floor', 'total_floors', 'orientation', 
                  'decoration', 'build_year', 'longitude', 'latitude', 'description', 
                  'cover_image', 'images', 'status', 'agent_info', 'views', 
                  'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """自定义序列化输出，返回完整URL"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        cover_url = instance.get_cover_image_url()
        if cover_url and request and not cover_url.startswith('http'):
            try:
                cover_url = request.build_absolute_uri(cover_url)
            except Exception:
                pass
        representation['cover_image'] = cover_url
            
        return representation


class HouseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    房源创建/更新序列化器
    """
    class Meta:
        model = House
        fields = ['title', 'district', 'address', 'price', 'unit_price', 'area', 
                  'house_type', 'floor', 'total_floors', 'orientation', 'decoration', 
                  'build_year', 'longitude', 'latitude', 'description', 'cover_image', 
                  'status']
    
    def validate(self, attrs):
        # 验证单价和总价的合理性
        if 'price' in attrs and 'area' in attrs and 'unit_price' in attrs:
            calculated_price = (attrs['unit_price'] * attrs['area']) / 10000
            if abs(float(calculated_price) - float(attrs['price'])) > 1:
                raise serializers.ValidationError("总价与单价面积不匹配")
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    """
    成交记录序列化器
    """
    house_title = serializers.CharField(source='house.title', read_only=True)
    house_address = serializers.CharField(source='house.address', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'house', 'house_title', 'house_address', 'deal_price', 
                  'deal_date', 'buyer_name', 'created_at']


class HouseMapSerializer(serializers.ModelSerializer):
    """
    地图展示序列化器(GeoJSON格式)
    """
    class Meta:
        model = House
        fields = ['id', 'title', 'price', 'house_type', 'longitude', 'latitude']
