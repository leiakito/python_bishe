"""
用户模型
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.models import BaseModel


class User(AbstractUser):
    """
    自定义用户模型
    """
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('agent', '经纪人'),
        ('admin', '管理员'),
    ]
    
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    real_name = models.CharField(max_length=50, blank=True, verbose_name='真实姓名')
    company = models.CharField(max_length=100, blank=True, verbose_name='所属公司')
    is_verified = models.BooleanField(default=False, verbose_name='是否认证')
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.username

