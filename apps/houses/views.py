"""
房源视图
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import District, House, HouseImage, Transaction
from .serializers import (
    DistrictSerializer, HouseListSerializer, HouseDetailSerializer,
    HouseCreateUpdateSerializer, TransactionSerializer, HouseMapSerializer,
    HouseImageSerializer
)
from apps.common.response import success_response, error_response
from apps.common.permissions import IsAgentOrAdmin
from apps.common.pagination import CustomPagination


class DistrictViewSet(viewsets.ModelViewSet):
    """
    区域视图集
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # 区域数据不分页
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'city']
    filterset_fields = ['city']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAgentOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def list(self, request, *args, **kwargs):
        """获取区域列表"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """获取区域详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建区域"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, msg='创建成功', code=201)
    
    def update(self, request, *args, **kwargs):
        """更新区域"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, msg='更新成功')
    
    def destroy(self, request, *args, **kwargs):
        """删除区域"""
        instance = self.get_object()
        # 检查该区域下是否有房源
        if instance.houses.exists():
            return error_response(msg=f'该区域下还有 {instance.houses.count()} 套房源，无法删除', code=400)
        self.perform_destroy(instance)
        return success_response(msg='删除成功', code=204)


class HouseViewSet(viewsets.ModelViewSet):
    """
    房源视图集
    """
    queryset = House.objects.select_related('district', 'agent').prefetch_related('images').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district', 'status', 'house_type', 'orientation']
    search_fields = ['title', 'address', 'description']
    ordering_fields = ['price', 'unit_price', 'area', 'created_at', 'views']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return HouseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HouseCreateUpdateSerializer
        return HouseDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAgentOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 价格区间筛选
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # 面积区间筛选
        min_area = self.request.query_params.get('min_area')
        max_area = self.request.query_params.get('max_area')
        if min_area:
            queryset = queryset.filter(area__gte=min_area)
        if max_area:
            queryset = queryset.filter(area__lte=max_area)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """获取房源列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建房源"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(data=serializer.data, msg='创建成功', code=201)
    
    def perform_create(self, serializer):
        """创建房源时自动设置发布者"""
        serializer.save(agent=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """获取房源详情,增加浏览次数"""
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新房源"""
        instance = self.get_object()
        # 验证用户是否有权限编辑该房源
        # 管理员(admin)或超级用户可以编辑任何房源，否则只能编辑自己的房源
        if instance.agent != request.user and not (request.user.role == 'admin' or request.user.is_superuser):
            return error_response(msg='您没有权限编辑该房源', code=403)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data, msg='更新成功')
    
    def destroy(self, request, *args, **kwargs):
        """删除房源"""
        instance = self.get_object()
        # 验证用户是否有权限删除该房源
        # 管理员(admin)或超级用户可以删除任何房源，否则只能删除自己的房源
        if instance.agent != request.user and not (request.user.role == 'admin' or request.user.is_superuser):
            return error_response(msg='您没有权限删除该房源', code=403)
        
        self.perform_destroy(instance)
        return success_response(msg='删除成功', code=204)
    
    @action(detail=False, methods=['post'])
    def batch_update_status(self, request):
        """
        批量更新房源状态（管理员专用）
        POST /api/houses/batch_update_status/
        Body: {"ids": [1, 2, 3], "status": "sold"}
        """
        # 检查是否为管理员
        if request.user.role != 'admin' and not request.user.is_superuser:
            return error_response(msg='此功能仅限管理员使用', code=403)
        
        ids = request.data.get('ids', [])
        new_status = request.data.get('status', '')
        
        if not ids or not new_status:
            return error_response(msg='缺少必要参数: ids 和 status')
        
        # 验证status有效性
        valid_statuses = ['available', 'sold', 'rented', 'pending']
        if new_status not in valid_statuses:
            return error_response(msg=f'状态值无效，必须是: {", ".join(valid_statuses)}')
        
        # 批量更新
        updated_count = House.objects.filter(id__in=ids).update(status=new_status)
        
        return success_response(
            data={'updated_count': updated_count},
            msg=f'成功更新 {updated_count} 个房源的状态'
        )
    
    @action(detail=False, methods=['post'])
    def batch_delete(self, request):
        """
        批量删除房源（管理员专用）
        POST /api/houses/batch_delete/
        Body: {"ids": [1, 2, 3]}
        """
        # 检查是否为管理员
        if request.user.role != 'admin' and not request.user.is_superuser:
            return error_response(msg='此功能仅限管理员使用', code=403)
        
        ids = request.data.get('ids', [])
        
        if not ids:
            return error_response(msg='缺少必要参数: ids')
        
        # 批量删除
        deleted_count, _ = House.objects.filter(id__in=ids).delete()
        
        return success_response(
            data={'deleted_count': deleted_count},
            msg=f'成功删除 {deleted_count} 个房源'
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        房源统计（管理员专用）
        GET /api/houses/stats/
        """
        # 检查是否为管理员
        if request.user.role != 'admin' and not request.user.is_superuser:
            return error_response(msg='此功能仅限管理员使用', code=403)
        
        from django.db.models import Count, Avg
        
        # 总房源数
        total_houses = House.objects.count()
        
        # 各状态房源数
        status_stats = House.objects.values('status').annotate(count=Count('id'))
        
        # 各区域房源数
        district_stats = House.objects.values('district__name').annotate(count=Count('id')).order_by('-count')[:10]
        
        # 平均价格
        avg_price = House.objects.filter(status='available').aggregate(avg=Avg('price'))['avg'] or 0
        
        # 各经纪人房源数
        agent_stats = House.objects.values('agent__username', 'agent__real_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return success_response(data={
            'total_houses': total_houses,
            'status_stats': list(status_stats),
            'district_stats': list(district_stats),
            'avg_price': round(float(avg_price), 2),
            'top_agents': list(agent_stats)
        })
    
    @action(detail=False, methods=['get'])
    def map_data(self, request):
        """
        获取地图数据(GeoJSON格式)
        GET /api/houses/map_data/
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(
            longitude__isnull=False, 
            latitude__isnull=False,
            status='available'
        )
        
        # 构建GeoJSON格式
        features = []
        for house in queryset:
            # 获取封面图URL
            cover_image_url = house.get_cover_image_url()
            if cover_image_url and not cover_image_url.startswith('http'):
                try:
                    cover_image_url = request.build_absolute_uri(cover_image_url)
                except Exception:
                    pass
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(house.longitude), float(house.latitude)]
                },
                "properties": {
                    "id": house.id,
                    "title": house.title,
                    "price": float(house.price),
                    "unit_price": float(house.unit_price),
                    "area": float(house.area),
                    "house_type": house.house_type,
                    "address": house.address,
                    "cover_image": cover_image_url,
                    "district": house.district.id if house.district else None,
                    "district_name": house.district.name if house.district else "未知区域",
                }
            }
            features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return success_response(data=geojson)
    
    @action(detail=False, methods=['get'])
    def my_houses(self, request):
        """
        获取当前用户发布的房源
        GET /api/houses/my_houses/
        """
        queryset = self.get_queryset().filter(agent=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HouseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = HouseListSerializer(queryset, many=True, context={'request': request})
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def hot_houses(self, request):
        """
        获取热门房源(按浏览量排序)
        GET /api/houses/hot_houses/
        """
        queryset = self.get_queryset().filter(status='available').order_by('-views')[:10]
        serializer = HouseListSerializer(queryset, many=True, context={'request': request})
        return success_response(data=serializer.data)


class HouseImageViewSet(viewsets.ModelViewSet):
    """
    房源图片视图集
    """
    queryset = HouseImage.objects.select_related('house')
    serializer_class = HouseImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAgentOrAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        house_id = self.request.query_params.get('house_id')
        if house_id:
            queryset = queryset.filter(house_id=house_id)
        return queryset
    
    def get_serializer_context(self):
        """传递request上下文给序列化器"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        """
        上传房源图片
        POST /api/house-images/
        """
        # 记录请求信息用于调试
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"图片上传请求 - FILES: {request.FILES.keys()}, DATA: {request.data.keys()}")
        
        # 检查是否有上传的文件
        if 'image' not in request.FILES:
            logger.error(f"缺少image字段 - FILES keys: {list(request.FILES.keys())}")
            return error_response(msg='请选择要上传的图片文件', code=400)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证用户是否有权限为该房源上传图片
        house_id = request.data.get('house')
        try:
            house = House.objects.get(id=house_id)
            if house.agent != request.user and not request.user.is_staff:
                return error_response(msg='您没有权限为该房源上传图片', code=403)
        except House.DoesNotExist:
            return error_response(msg='房源不存在', code=404)
        
        self.perform_create(serializer)
        logger.info(f"图片上传成功 - 房源ID: {house_id}, 图片ID: {serializer.data.get('id')}")
        return success_response(data=serializer.data, msg='图片上传成功', code=201)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除房源图片
        DELETE /api/house-images/{id}/
        """
        instance = self.get_object()
        
        # 验证用户是否有权限删除该图片
        if instance.house.agent != request.user and not request.user.is_staff:
            return error_response(msg='您没有权限删除该图片', code=403)
        
        self.perform_destroy(instance)
        return success_response(msg='图片删除成功', code=204)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    成交记录视图集
    """
    queryset = Transaction.objects.select_related('house', 'house__district')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['house__district']
    ordering_fields = ['deal_date', 'deal_price']
    ordering = ['-deal_date']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAgentOrAdmin()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def recent_deals(self, request):
        """
        获取最近成交记录
        GET /api/transactions/recent_deals/
        """
        days = int(request.query_params.get('days', 30))
        from datetime import datetime, timedelta
        start_date = datetime.now().date() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(deal_date__gte=start_date)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
