"""
数据分析模型
"""
from django.db import models
from apps.common.models import BaseModel
from apps.houses.models import District


class MarketReport(BaseModel):
    """
    市场报告模型
    """
    REPORT_TYPE_CHOICES = [
        ('monthly', '月度报告'),
        ('quarterly', '季度报告'),
        ('yearly', '年度报告'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='报告标题')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, 
                                   default='monthly', verbose_name='报告类型')
    district = models.ForeignKey(District, on_delete=models.CASCADE, 
                                 null=True, blank=True, 
                                 related_name='market_reports', verbose_name='区域')
    report_date = models.DateField(verbose_name='报告日期')
    
    # 统计数据
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                    verbose_name='平均价格(万元)')
    avg_unit_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                         verbose_name='平均单价(元/平米)')
    total_listings = models.IntegerField(verbose_name='总房源数')
    total_transactions = models.IntegerField(verbose_name='总成交数')
    
    # 价格趋势
    price_change_rate = models.DecimalField(max_digits=5, decimal_places=2, 
                                           verbose_name='价格变化率(%)')
    
    # 报告内容
    summary = models.TextField(verbose_name='摘要')
    content = models.TextField(blank=True, verbose_name='详细内容')
    
    class Meta:
        db_table = 'market_reports'
        verbose_name = '市场报告'
        verbose_name_plural = verbose_name
        ordering = ['-report_date']
    
    def __str__(self):
        return f"{self.title} - {self.report_date}"

