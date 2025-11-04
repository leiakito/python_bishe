"""
收藏与提醒后台管理
"""
from django.contrib import admin
from .models import Favorite, PriceAlert


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'house', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'house__title']
    raw_id_fields = ['user', 'house']


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'house', 'target_price', 'current_price', 'status', 'created_at', 'triggered_at']
    list_filter = ['status', 'created_at', 'triggered_at']
    search_fields = ['user__username', 'house__title']
    raw_id_fields = ['user', 'house']
    readonly_fields = ['triggered_at']

