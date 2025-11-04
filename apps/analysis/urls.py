"""
数据分析模块URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisViewSet, MarketReportViewSet

router = DefaultRouter()
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'market-reports', MarketReportViewSet, basename='market-report')

urlpatterns = [
    path('', include(router.urls)),
]

