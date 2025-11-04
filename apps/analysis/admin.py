"""
数据分析后台管理
"""
from django.contrib import admin
from .models import MarketReport


@admin.register(MarketReport)
class MarketReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'district', 'report_date', 
                    'avg_price', 'total_transactions', 'created_at']
    list_filter = ['report_type', 'district', 'report_date']
    search_fields = ['title', 'summary']
    date_hierarchy = 'report_date'

