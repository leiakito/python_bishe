"""
用户序列化器
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'email', 'role', 
                  'real_name', 'company', 'is_verified', 'is_active', 
                  'is_superuser', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_superuser']


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='确认密码')
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'phone', 'email', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被注册")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """
    username = serializers.CharField(required=True, label='用户名')
    password = serializers.CharField(required=True, write_only=True, label='密码')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户信息更新序列化器（普通用户使用）
    """
    class Meta:
        model = User
        fields = ['email', 'real_name', 'company']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    管理员用户更新序列化器（管理员专用，可以修改更多字段）
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'real_name', 'company', 
                  'role', 'is_active', 'is_verified']
        read_only_fields = ['username']  # 用户名不允许修改


class PasswordChangeSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """
    old_password = serializers.CharField(required=True, write_only=True, label='旧密码')
    new_password = serializers.CharField(required=True, write_only=True, 
                                        validators=[validate_password], label='新密码')
    new_password2 = serializers.CharField(required=True, write_only=True, label='确认新密码')
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次密码不一致"})
        return attrs

