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
    phone = serializers.CharField(required=True, label='手机号')
    email = serializers.EmailField(required=True, label='邮箱')
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='user', label='角色')
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'phone', 'email', 'role']
        extra_kwargs = {
            'username': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs
    
    def validate_phone(self, value):
        if not value:
            raise serializers.ValidationError("手机号不能为空")
        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入正确的手机号格式")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被注册")
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("邮箱不能为空")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value
    
    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("用户名不能为空")
        if len(value) < 3:
            raise serializers.ValidationError("用户名长度至少3个字符")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
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

