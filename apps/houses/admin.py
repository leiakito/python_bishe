"""
房源后台管理
"""
from django.contrib import admin
from .models import District, House, HouseImage, Transaction


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'created_at']
    search_fields = ['name', 'city']


class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['title', 'district', 'price', 'area', 'house_type', 'status', 'agent', 'views', 'created_at']
    list_filter = ['status', 'house_type', 'district', 'created_at']
    search_fields = ['title', 'address']
    inlines = [HouseImageInline]
    readonly_fields = ['views', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['house', 'deal_price', 'deal_date', 'buyer_name', 'created_at']
    list_filter = ['deal_date']
    search_fields = ['house__title', 'buyer_name']
    date_hierarchy = 'deal_date'

