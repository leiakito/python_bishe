"""
房源模块URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet, HouseViewSet, HouseImageViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'houses', HouseViewSet, basename='house')
router.register(r'house-images', HouseImageViewSet, basename='house-image')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]

