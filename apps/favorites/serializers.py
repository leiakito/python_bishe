"""
收藏与提醒序列化器
"""
from rest_framework import serializers
from .models import Favorite, PriceAlert
from apps.houses.serializers import HouseListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """
    收藏序列化器
    """
    house = HouseListSerializer(read_only=True)
    house_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.houses.models', fromlist=['House']).House.objects.all(),
        source='house',
        write_only=True
    )
    
    class Meta:
        model = Favorite
        fields = ['id', 'house', 'house_id', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        # 检查是否已经收藏
        user = self.context['request'].user
        house = attrs.get('house')
        if Favorite.objects.filter(user=user, house=house).exists():
            raise serializers.ValidationError("您已经收藏过该房源")
        return attrs
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PriceAlertSerializer(serializers.ModelSerializer):
    """
    价格提醒序列化器
    """
    house = HouseListSerializer(read_only=True)
    house_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.houses.models', fromlist=['House']).House.objects.all(),
        source='house',
        write_only=True
    )
    
    class Meta:
        model = PriceAlert
        fields = ['id', 'house', 'house_id', 'target_price', 'current_price', 
                  'status', 'triggered_at', 'created_at']
        read_only_fields = ['id', 'current_price', 'status', 'triggered_at', 'created_at']
    
    def validate_target_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("目标价格必须大于0")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['current_price'] = validated_data['house'].price
        return super().create(validated_data)

