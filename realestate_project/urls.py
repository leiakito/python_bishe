"""
URL Configuration for realestate_project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/', include('apps.houses.urls')),
    path('api/', include('apps.favorites.urls')),
    path('api/', include('apps.analysis.urls')),
    
    # JWT token refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 自定义Admin站点信息
admin.site.site_header = '二手房可视化系统管理后台'
admin.site.site_title = '二手房系统'
admin.site.index_title = '欢迎使用二手房可视化系统'

