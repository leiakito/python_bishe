"""
收藏与提醒模型
"""
from django.db import models
from apps.common.models import BaseModel
from apps.users.models import User
from apps.houses.models import House


class Favorite(BaseModel):
    """
    收藏模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='favorites', verbose_name='用户')
    house = models.ForeignKey(House, on_delete=models.CASCADE, 
                             related_name='favorited_by', verbose_name='房源')
    note = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        db_table = 'favorites'
        verbose_name = '收藏'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'house']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.house.title}"


class PriceAlert(BaseModel):
    """
    价格提醒模型
    """
    STATUS_CHOICES = [
        ('active', '激活'),
        ('triggered', '已触发'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                            related_name='price_alerts', verbose_name='用户')
    house = models.ForeignKey(House, on_delete=models.CASCADE, 
                             related_name='price_alerts', verbose_name='房源')
    target_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                      verbose_name='目标价格(万元)')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                       verbose_name='当前价格(万元)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                             default='active', verbose_name='状态')
    triggered_at = models.DateTimeField(null=True, blank=True, verbose_name='触发时间')
    
    class Meta:
        db_table = 'price_alerts'
        verbose_name = '价格提醒'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.house.title} - {self.target_price}"
    
    def check_and_trigger(self):
        """
        检查价格是否达到目标,如果达到则触发提醒
        """
        if self.status == 'active' and self.house.price <= self.target_price:
            from django.utils import timezone
            self.status = 'triggered'
            self.triggered_at = timezone.now()
            self.save()
            return True
        return False

