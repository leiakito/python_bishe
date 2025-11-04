"""
数据分析序列化器
"""
from rest_framework import serializers
from .models import MarketReport


class MarketReportSerializer(serializers.ModelSerializer):
    """
    市场报告序列化器
    """
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = MarketReport
        fields = ['id', 'title', 'report_type', 'district', 'district_name', 
                  'report_date', 'avg_price', 'avg_unit_price', 'total_listings', 
                  'total_transactions', 'price_change_rate', 'summary', 'content', 
                  'created_at']

