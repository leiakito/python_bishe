"""
收藏与提醒模块URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet, PriceAlertViewSet

router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'price-alerts', PriceAlertViewSet, basename='price-alert')

urlpatterns = [
    path('', include(router.urls)),
]

