"""
收藏与提醒视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Favorite, PriceAlert
from .serializers import FavoriteSerializer, PriceAlertSerializer
from apps.common.response import success_response, error_response
from apps.common.pagination import CustomPagination
from apps.houses.models import House


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    收藏视图集
    """
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('house', 'house__district').prefetch_related('house__images')
    
    def create(self, request, *args, **kwargs):
        """
        添加收藏
        POST /api/favorites/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, msg='收藏成功')
        return error_response(msg='收藏失败', data=serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        """
        取消收藏
        DELETE /api/favorites/{id}/
        """
        instance = self.get_object()
        instance.delete()
        return success_response(msg='取消收藏成功')
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        切换收藏状态
        POST /api/favorites/toggle/
        Body: {"house": 1}
        """
        house_id = request.data.get('house')
        if not house_id:
            return error_response(msg='缺少房源ID')
        
        house = get_object_or_404(House, id=house_id)
        favorite = Favorite.objects.filter(user=request.user, house=house).first()
        
        if favorite:
            favorite.delete()
            return success_response(data={'is_favorited': False}, msg='取消收藏成功')
        else:
            favorite = Favorite.objects.create(user=request.user, house=house)
            return success_response(
                data={'is_favorited': True, 'favorite_id': favorite.id}, 
                msg='收藏成功'
            )
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        检查房源是否已收藏
        GET /api/favorites/check/?house=1
        """
        house_id = request.query_params.get('house')
        if not house_id:
            return error_response(msg='缺少房源ID')
        
        is_favorited = Favorite.objects.filter(
            user=request.user, 
            house_id=house_id
        ).exists()
        
        return success_response(data={'is_favorited': is_favorited})


class PriceAlertViewSet(viewsets.ModelViewSet):
    """
    价格提醒视图集
    """
    serializer_class = PriceAlertSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return PriceAlert.objects.filter(user=self.request.user).select_related('house', 'house__district').prefetch_related('house__images')
    
    def create(self, request, *args, **kwargs):
        """
        创建价格提醒
        POST /api/price-alerts/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, msg='价格提醒创建成功')
        return error_response(msg='创建失败', data=serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除价格提醒
        DELETE /api/price-alerts/{id}/
        """
        instance = self.get_object()
        instance.delete()
        return success_response(msg='价格提醒删除成功')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        取消价格提醒
        POST /api/price-alerts/{id}/cancel/
        """
        alert = self.get_object()
        alert.status = 'cancelled'
        alert.save()
        return success_response(msg='价格提醒已取消')
    
    @action(detail=False, methods=['get'])
    def active_alerts(self, request):
        """
        获取激活状态的价格提醒
        GET /api/price-alerts/active_alerts/
        """
        queryset = self.get_queryset().filter(status='active')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def triggered_alerts(self, request):
        """
        获取已触发的价格提醒
        GET /api/price-alerts/triggered_alerts/
        """
        queryset = self.get_queryset().filter(status='triggered')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def check_house_alert(self, request):
        """
        检查特定房源的价格提醒状态
        GET /api/price-alerts/check_house_alert/?house_id=1
        """
        house_id = request.query_params.get('house_id')
        if not house_id:
            return error_response(msg='缺少房源ID')
        
        # 获取该房源的激活状态提醒
        alert = PriceAlert.objects.filter(
            user=request.user,
            house_id=house_id,
            status='active'
        ).first()
        
        if not alert:
            return success_response(data={'has_alert': False})
        
        # 更新当前价格
        alert.current_price = alert.house.price
        alert.save(update_fields=['current_price'])
        
        # 检查是否触发
        triggered = alert.check_and_trigger()
        
        return success_response(data={
            'has_alert': True,
            'alert_id': alert.id,
            'target_price': float(alert.target_price),
            'current_price': float(alert.current_price),
            'triggered': triggered,
            'status': alert.status
        })

