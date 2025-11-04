"""
Celery异步任务
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_price_alerts():
    """
    定期检查价格提醒
    每小时执行一次,检查是否有房源价格达到用户设置的目标价格
    """
    from apps.favorites.models import PriceAlert
    from apps.houses.models import House
    
    # 获取所有激活状态的价格提醒
    active_alerts = PriceAlert.objects.filter(status='active').select_related('house', 'user')
    
    triggered_count = 0
    for alert in active_alerts:
        # 更新当前价格
        alert.current_price = alert.house.price
        alert.save(update_fields=['current_price'])
        
        # 检查是否触发
        if alert.check_and_trigger():
            triggered_count += 1
            # 这里可以发送通知(邮件、短信等)
            logger.info(f"价格提醒触发: 用户{alert.user.username}, 房源{alert.house.title}")
    
    logger.info(f"价格提醒检查完成, 触发{triggered_count}个提醒")
    return f"检查完成, 触发{triggered_count}个提醒"


@shared_task
def generate_market_report(district_id=None, report_type='monthly'):
    """
    生成市场报告
    参数:
        district_id: 区域ID,为None时生成全市报告
        report_type: 报告类型 (monthly/quarterly/yearly)
    """
    from apps.analysis.models import MarketReport
    from apps.houses.models import House, Transaction, District
    from django.db.models import Avg, Count
    
    # 确定时间范围
    end_date = datetime.now().date()
    if report_type == 'monthly':
        start_date = end_date - timedelta(days=30)
        title_prefix = "月度"
    elif report_type == 'quarterly':
        start_date = end_date - timedelta(days=90)
        title_prefix = "季度"
    else:  # yearly
        start_date = end_date - timedelta(days=365)
        title_prefix = "年度"
    
    # 查询数据
    houses = House.objects.filter(status='available')
    transactions = Transaction.objects.filter(
        deal_date__gte=start_date,
        deal_date__lte=end_date
    )
    
    district = None
    if district_id:
        district = District.objects.get(id=district_id)
        houses = houses.filter(district=district)
        transactions = transactions.filter(house__district=district)
        title = f"{district.name}{title_prefix}市场报告"
    else:
        title = f"全市{title_prefix}市场报告"
    
    # 统计数据
    house_stats = houses.aggregate(
        avg_price=Avg('price'),
        avg_unit_price=Avg('unit_price'),
        count=Count('id')
    )
    
    transaction_count = transactions.count()
    
    # 计算价格变化率(与上期对比)
    previous_start = start_date - (end_date - start_date)
    previous_transactions = Transaction.objects.filter(
        deal_date__gte=previous_start,
        deal_date__lt=start_date
    )
    if district_id:
        previous_transactions = previous_transactions.filter(house__district=district)
    
    current_avg = transactions.aggregate(avg=Avg('deal_price'))['avg'] or 0
    previous_avg = previous_transactions.aggregate(avg=Avg('deal_price'))['avg'] or 0
    
    if previous_avg > 0:
        price_change_rate = ((current_avg - previous_avg) / previous_avg) * 100
    else:
        price_change_rate = 0
    
    # 生成摘要
    summary = f"本期平均价格{house_stats['avg_price']:.2f}万元，" \
              f"平均单价{house_stats['avg_unit_price']:.2f}元/平米，" \
              f"在售房源{house_stats['count']}套，" \
              f"成交{transaction_count}套，" \
              f"价格{'上涨' if price_change_rate > 0 else '下降'}{abs(price_change_rate):.2f}%"
    
    # 创建报告
    report = MarketReport.objects.create(
        title=title,
        report_type=report_type,
        district=district,
        report_date=end_date,
        avg_price=house_stats['avg_price'] or 0,
        avg_unit_price=house_stats['avg_unit_price'] or 0,
        total_listings=house_stats['count'],
        total_transactions=transaction_count,
        price_change_rate=price_change_rate,
        summary=summary,
        content=f"报告时间范围: {start_date} 至 {end_date}"
    )
    
    logger.info(f"市场报告生成完成: {title}")
    return f"报告生成完成: {report.id}"


@shared_task
def cleanup_old_data():
    """
    清理旧数据
    删除超过2年的已售房源和成交记录
    """
    from apps.houses.models import House, Transaction
    
    two_years_ago = datetime.now().date() - timedelta(days=730)
    
    # 删除旧的已售房源
    old_houses = House.objects.filter(
        status='sold',
        updated_at__lt=two_years_ago
    )
    house_count = old_houses.count()
    old_houses.delete()
    
    # 删除旧的成交记录
    old_transactions = Transaction.objects.filter(
        deal_date__lt=two_years_ago
    )
    transaction_count = old_transactions.count()
    old_transactions.delete()
    
    logger.info(f"数据清理完成: 删除{house_count}个房源, {transaction_count}条成交记录")
    return f"清理完成: {house_count}个房源, {transaction_count}条记录"


@shared_task
def send_notification_email(user_email, subject, message):
    """
    发送通知邮件
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f"邮件发送成功: {user_email}")
        return f"邮件发送成功: {user_email}"
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return f"邮件发送失败: {str(e)}"


@shared_task
def update_house_statistics():
    """
    更新房源统计数据
    计算每个区域的房源数量、平均价格等统计信息
    """
    from apps.houses.models import District, House
    from django.db.models import Avg, Count, Max, Min
    
    districts = District.objects.all()
    
    for district in districts:
        stats = House.objects.filter(
            district=district,
            status='available'
        ).aggregate(
            count=Count('id'),
            avg_price=Avg('price'),
            max_price=Max('price'),
            min_price=Min('price')
        )
        
        logger.info(f"区域 {district.name}: {stats}")
    
    logger.info("房源统计更新完成")
    return "统计更新完成"

