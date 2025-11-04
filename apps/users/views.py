"""
用户视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, AdminUserUpdateSerializer
)
from apps.common.response import success_response, error_response
from apps.common.permissions import IsAdminUser


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        根据不同的action设置不同的权限
        """
        if self.action in ['register', 'login']:
            return [AllowAny()]
        elif self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            # 管理员可以进行所有CRUD操作
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def list(self, request, *args, **kwargs):
        """
        获取用户列表（管理员专用）
        GET /api/users/
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # 支持搜索
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                phone__icontains=search
            ) | queryset.filter(
                real_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        # 支持角色筛选
        role = request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(role=role)
        
        # 支持状态筛选
        is_active = request.query_params.get('is_active', '')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 排序
        queryset = queryset.order_by('-date_joined')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            # 包装成统一的响应格式
            return success_response(data=paginated_response.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        创建用户（管理员专用）
        POST /api/users/
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data=UserSerializer(user).data,
                msg='用户创建成功',
                code=201
            )
        return error_response(msg='创建失败', data=serializer.errors)
    
    def update(self, request, *args, **kwargs):
        """
        更新用户信息（管理员专用）
        PUT /api/users/{id}/
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # 管理员使用AdminUserUpdateSerializer，可以修改更多字段
        serializer = AdminUserUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=UserSerializer(instance).data, msg='用户更新成功')
        return error_response(msg='更新失败', data=serializer.errors)
    
    def destroy(self, request, *args, **kwargs):
        """
        删除用户（管理员专用）
        DELETE /api/users/{id}/
        """
        instance = self.get_object()
        
        # 不能删除自己
        if instance.id == request.user.id:
            return error_response(msg='不能删除自己的账户', code=400)
        
        # 不能删除超级管理员
        if instance.is_superuser:
            return error_response(msg='不能删除超级管理员', code=400)
        
        instance.delete()
        return success_response(msg='用户删除成功', code=204)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        用户注册
        POST /api/users/register/
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data={
                    'user': UserSerializer(user).data,
                    'message': '注册成功'
                },
                msg='注册成功'
            )
        return error_response(msg='注册失败', data=serializer.errors)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        用户登录
        POST /api/users/login/
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                # 生成JWT token
                refresh = RefreshToken.for_user(user)
                return success_response(
                    data={
                        'user': UserSerializer(user).data,
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    },
                    msg='登录成功'
                )
            return error_response(msg='用户名或密码错误', code=401)
        return error_response(msg='参数错误', data=serializer.errors)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        获取当前用户信息
        GET /api/users/profile/
        """
        serializer = UserSerializer(request.user)
        return success_response(data=serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        更新当前用户信息
        PUT/PATCH /api/users/update_profile/
        """
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(data=serializer.data, msg='更新成功')
        return error_response(msg='更新失败', data=serializer.errors)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改密码
        POST /api/users/change_password/
        """
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            # 验证旧密码
            if not user.check_password(serializer.validated_data['old_password']):
                return error_response(msg='旧密码错误', code=400)
            
            # 设置新密码
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return success_response(msg='密码修改成功')
        return error_response(msg='参数错误', data=serializer.errors)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出
        POST /api/users/logout/
        """
        return success_response(msg='登出成功')

