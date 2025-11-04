"""
自定义权限类
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    对象级权限,只允许对象的所有者编辑它
    """
    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写权限只允许对象的所有者
        return obj.user == request.user


class IsAgentOrAdmin(permissions.BasePermission):
    """
    只允许经纪人或管理员访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role in ['agent', 'admin'] or request.user.is_staff)


class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.role == 'admin' or request.user.is_superuser)

