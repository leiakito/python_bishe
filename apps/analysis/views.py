"""
数据分析视图
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Max, Min, Q
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .models import MarketReport
from .serializers import MarketReportSerializer
from apps.houses.models import House, Transaction, District
from apps.common.response import success_response, error_response
from apps.common.permissions import IsAgentOrAdmin


class AnalysisViewSet(viewsets.ViewSet):
    """
    数据分析视图集
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def price_trend(self, request):
        """
        价格趋势分析
        GET /api/analysis/price_trend/
        参数: district_id, days (默认180天)
        """
        district_id = request.query_params.get('district_id')
        days = int(request.query_params.get('days', 180))
        
        # 计算起始日期
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # 查询成交记录
        transactions = Transaction.objects.filter(
            deal_date__gte=start_date,
            deal_date__lte=end_date
        ).select_related('house', 'house__district')
        
        if district_id:
            transactions = transactions.filter(house__district_id=district_id)
        
        # 转换为DataFrame进行分析
        if not transactions.exists():
            return success_response(data={'trend': [], 'summary': {}})
        
        data = []
        for t in transactions:
            data.append({
                'date': t.deal_date,
                'price': float(t.deal_price),
                'area': float(t.house.area),
                'unit_price': float(t.deal_price * 10000 / t.house.area)
            })
        
        df = pd.DataFrame(data)
        
        # 按月分组统计
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_stats = df.groupby('month').agg({
            'price': 'mean',
            'unit_price': 'mean',
            'date': 'count'
        }).reset_index()
        
        trend_data = []
        for _, row in monthly_stats.iterrows():
            trend_data.append({
                'month': str(row['month']),
                'avg_price': round(row['price'], 2),
                'avg_unit_price': round(row['unit_price'], 2),
                'transaction_count': int(row['date'])
            })
        
        # 计算总体统计
        summary = {
            'avg_price': round(df['price'].mean(), 2),
            'max_price': round(df['price'].max(), 2),
            'min_price': round(df['price'].min(), 2),
            'avg_unit_price': round(df['unit_price'].mean(), 2),
            'total_transactions': len(df)
        }
        
        return success_response(data={
            'trend': trend_data,
            'summary': summary
        })
    
    @action(detail=False, methods=['get'])
    def district_comparison(self, request):
        """
        区域对比分析
        GET /api/analysis/district_comparison/
        """
        # 获取所有区域的统计数据
        districts = District.objects.all()
        
        comparison_data = []
        for district in districts:
            # 在售房源统计
            available_houses = House.objects.filter(
                district=district,
                status='available'
            )
            
            if available_houses.exists():
                stats = available_houses.aggregate(
                    avg_price=Avg('price'),
                    avg_unit_price=Avg('unit_price'),
                    min_price=Min('price'),
                    max_price=Max('price'),
                    count=Count('id')
                )
                
                comparison_data.append({
                    'district_id': district.id,
                    'district_name': district.name,
                    'avg_price': round(float(stats['avg_price'] or 0), 2),
                    'avg_unit_price': round(float(stats['avg_unit_price'] or 0), 2),
                    'min_price': round(float(stats['min_price'] or 0), 2),
                    'max_price': round(float(stats['max_price'] or 0), 2),
                    'house_count': stats['count']
                })
        
        # 按平均价格排序
        comparison_data.sort(key=lambda x: x['avg_price'], reverse=True)
        
        return success_response(data=comparison_data)
    
    @action(detail=False, methods=['get'])
    def house_type_distribution(self, request):
        """
        户型分布统计
        GET /api/analysis/house_type_distribution/
        参数: district_id (可选)
        """
        district_id = request.query_params.get('district_id')
        
        queryset = House.objects.filter(status='available')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        # 统计各户型数量
        type_stats = queryset.values('house_type').annotate(
            count=Count('id'),
            avg_price=Avg('price')
        ).order_by('-count')
        
        distribution_data = []
        total_count = queryset.count()
        
        for stat in type_stats:
            distribution_data.append({
                'house_type': stat['house_type'],
                'count': stat['count'],
                'percentage': round((stat['count'] / total_count * 100), 2) if total_count > 0 else 0,
                'avg_price': round(float(stat['avg_price'] or 0), 2)
            })
        
        return success_response(data={
            'distribution': distribution_data,
            'total_count': total_count
        })
    
    @action(detail=False, methods=['get'])
    def price_range_distribution(self, request):
        """
        价格区间分布
        GET /api/analysis/price_range_distribution/
        参数: district_id (可选)
        """
        district_id = request.query_params.get('district_id')
        
        queryset = House.objects.filter(status='available')
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        
        # 定义价格区间
        price_ranges = [
            (0, 100, '100万以下'),
            (100, 200, '100-200万'),
            (200, 300, '200-300万'),
            (300, 500, '300-500万'),
            (500, 1000, '500-1000万'),
            (1000, float('inf'), '1000万以上')
        ]
        
        distribution_data = []
        total_count = queryset.count()
        
        for min_price, max_price, label in price_ranges:
            if max_price == float('inf'):
                count = queryset.filter(price__gte=min_price).count()
            else:
                count = queryset.filter(price__gte=min_price, price__lt=max_price).count()
            
            distribution_data.append({
                'range': label,
                'count': count,
                'percentage': round((count / total_count * 100), 2) if total_count > 0 else 0
            })
        
        return success_response(data={
            'distribution': distribution_data,
            'total_count': total_count
        })
    
    @action(detail=False, methods=['post'])
    def predict_price(self, request):
        """
        房价预测
        POST /api/analysis/predict_price/
        Body: {"district_id": 1, "house_type": "2室", "area": 80}
        
        预测公式: P = A × M(r,t)
        P: 预测总价
        A: 目标房源面积
        M(r,t): 近6个月同区域r、同户型t的成交单价中位数
        """
        district_id = request.data.get('district_id')
        house_type = request.data.get('house_type')
        area = request.data.get('area')
        
        if not all([district_id, house_type, area]):
            return error_response(msg='缺少必要参数')
        
        try:
            area = float(area)
        except ValueError:
            return error_response(msg='面积必须是数字')
        
        # 获取近6个月的成交记录
        six_months_ago = datetime.now().date() - timedelta(days=180)
        transactions = Transaction.objects.filter(
            house__district_id=district_id,
            house__house_type=house_type,
            deal_date__gte=six_months_ago
        ).select_related('house')
        
        if not transactions.exists():
            return error_response(msg='暂无足够的历史数据进行预测')
        
        # 计算单价中位数
        unit_prices = []
        for t in transactions:
            unit_price = float(t.deal_price * 10000 / t.house.area)
            unit_prices.append(unit_price)
        
        median_unit_price = np.median(unit_prices)
        
        # 预测总价
        predicted_price = (area * median_unit_price) / 10000
        
        # 计算价格区间 (±10%)
        price_range_min = predicted_price * 0.9
        price_range_max = predicted_price * 1.1
        
        return success_response(data={
            'predicted_price': round(predicted_price, 2),
            'price_range': {
                'min': round(price_range_min, 2),
                'max': round(price_range_max, 2)
            },
            'median_unit_price': round(median_unit_price, 2),
            'sample_count': len(unit_prices),
            'area': area
        })


    @action(detail=False, methods=['get'])
    def district_heat_map(self, request):
        """
        区域热度图数据
        GET /api/analysis/district_heat_map/
        
        返回各区域的热度指数（基于房源数量、平均价格、成交活跃度）
        """
        from datetime import datetime, timedelta
        
        # 获取所有区域
        districts = District.objects.all()
        
        heat_map_data = []
        max_heat = 0
        
        for district in districts:
            # 在售房源数
            available_count = House.objects.filter(
                district=district,
                status='available'
            ).count()
            
            # 近30天成交数
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            transaction_count = Transaction.objects.filter(
                house__district=district,
                deal_date__gte=thirty_days_ago
            ).count()
            
            # 平均价格
            avg_price = House.objects.filter(
                district=district,
                status='available'
            ).aggregate(avg_price=Avg('price'))['avg_price'] or 0
            
            # 计算热度指数
            # 热度 = (在售房源数 × 0.3) + (成交数 × 5) + (平均价格/50 × 0.2)
            heat_index = (available_count * 0.3) + (transaction_count * 5) + (float(avg_price) / 50 * 0.2)
            
            if heat_index > max_heat:
                max_heat = heat_index
            
            heat_map_data.append({
                'district_id': district.id,
                'district_name': district.name,
                'heat_index': round(heat_index, 2),
                'available_count': available_count,
                'transaction_count': transaction_count,
                'avg_price': round(float(avg_price), 2)
            })
        
        # 归一化热度指数到0-100
        if max_heat > 0:
            for item in heat_map_data:
                item['heat_percentage'] = round((item['heat_index'] / max_heat) * 100, 1)
        else:
            for item in heat_map_data:
                item['heat_percentage'] = 0
        
        # 按热度排序
        heat_map_data.sort(key=lambda x: x['heat_index'], reverse=True)
        
        return success_response(data=heat_map_data)
    
    @action(detail=False, methods=['post'])
    def roi_analysis(self, request):
        """
        投资回报率分析 (经纪人专用)
        POST /api/analysis/roi_analysis/
        Body: {
            "house_id": 1,  # 可选，指定房源
            "purchase_price": 300,  # 购入价格（万元）
            "monthly_rent": 5000,  # 预期月租金（元）
            "property_fee": 300,  # 月物业费（元）
            "other_costs": 200  # 其他月成本（元）
        }
        
        返回:
        - gross_roi: 毛投资回报率 (不考虑成本)
        - net_roi: 净投资回报率 (考虑成本)
        - payback_period: 回本周期（年）
        - annual_income: 年租金收入
        - annual_cost: 年成本
        - price_reasonability: 价格合理性评估
        """
        # 检查是否为经纪人
        if request.user.role not in ['agent', 'admin']:
            return error_response(msg='此功能仅限经纪人使用', code=403)
        
        house_id = request.data.get('house_id')
        purchase_price = request.data.get('purchase_price')  # 万元
        monthly_rent = request.data.get('monthly_rent')  # 元
        property_fee = request.data.get('property_fee', 0)  # 元
        other_costs = request.data.get('other_costs', 0)  # 元
        
        if not all([purchase_price, monthly_rent]):
            return error_response(msg='缺少必要参数：购入价格和月租金')
        
        try:
            purchase_price = float(purchase_price)
            monthly_rent = float(monthly_rent)
            property_fee = float(property_fee)
            other_costs = float(other_costs)
        except ValueError:
            return error_response(msg='参数必须是数字')
        
        # 计算年收入和成本
        annual_income = monthly_rent * 12
        annual_cost = (property_fee + other_costs) * 12
        net_annual_income = annual_income - annual_cost
        
        # 购入价格（元）
        purchase_price_yuan = purchase_price * 10000
        
        # 毛投资回报率 = 年租金收入 / 购入价格 × 100%
        gross_roi = (annual_income / purchase_price_yuan) * 100
        
        # 净投资回报率 = 净年收入 / 购入价格 × 100%
        net_roi = (net_annual_income / purchase_price_yuan) * 100
        
        # 回本周期 = 购入价格 / 净年收入
        payback_period = purchase_price_yuan / net_annual_income if net_annual_income > 0 else float('inf')
        
        # 价格合理性评估
        if house_id:
            try:
                house = House.objects.get(id=house_id)
                district_avg = House.objects.filter(
                    district=house.district,
                    status='available'
                ).aggregate(avg_price=Avg('price'))['avg_price']
                
                price_diff_percent = ((purchase_price - float(district_avg)) / float(district_avg)) * 100 if district_avg else 0
                
                if price_diff_percent < -10:
                    reasonability = '价格偏低，投资价值较高'
                    reasonability_level = 'excellent'
                elif price_diff_percent < 0:
                    reasonability = '价格略低于市场均价，具有投资价值'
                    reasonability_level = 'good'
                elif price_diff_percent < 10:
                    reasonability = '价格接近市场均价，投资需谨慎评估'
                    reasonability_level = 'fair'
                else:
                    reasonability = '价格偏高，投资风险较大'
                    reasonability_level = 'poor'
                
                district_name = house.district.name
            except House.DoesNotExist:
                reasonability = '无法评估（房源不存在）'
                reasonability_level = 'unknown'
                price_diff_percent = 0
                district_name = ''
                district_avg = 0
        else:
            # 根据ROI评估
            if net_roi > 5:
                reasonability = '投资回报率优秀（>5%）'
                reasonability_level = 'excellent'
            elif net_roi > 3:
                reasonability = '投资回报率良好（3-5%）'
                reasonability_level = 'good'
            elif net_roi > 2:
                reasonability = '投资回报率一般（2-3%）'
                reasonability_level = 'fair'
            else:
                reasonability = '投资回报率偏低（<2%）'
                reasonability_level = 'poor'
            
            price_diff_percent = 0
            district_name = ''
            district_avg = 0
        
        result = {
            'gross_roi': round(gross_roi, 2),
            'net_roi': round(net_roi, 2),
            'payback_period': round(payback_period, 1) if payback_period != float('inf') else None,
            'annual_income': round(annual_income, 2),
            'annual_cost': round(annual_cost, 2),
            'net_annual_income': round(net_annual_income, 2),
            'purchase_price': purchase_price,
            'monthly_rent': monthly_rent,
            'price_reasonability': reasonability,
            'reasonability_level': reasonability_level,
        }
        
        if house_id:
            result.update({
                'district_name': district_name,
                'district_avg_price': round(float(district_avg or 0), 2),
                'price_diff_percent': round(price_diff_percent, 2)
            })
        
        return success_response(data=result)
    
    @action(detail=False, methods=['get'])
    def market_trend_forecast(self, request):
        """
        市场趋势预测分析 (经纪人专用)
        GET /api/analysis/market_trend_forecast/
        参数: district_id (可选)
        
        返回:
        - supply_demand_ratio: 供需比
        - market_heat: 市场热度指数
        - price_trend: 价格趋势（上涨/平稳/下跌）
        - forecast_next_month: 下月价格预测
        - transaction_activity: 成交活跃度
        """
        # 检查是否为经纪人
        if request.user.role not in ['agent', 'admin']:
            return error_response(msg='此功能仅限经纪人使用', code=403)
        
        district_id = request.query_params.get('district_id')
        
        # 基础查询
        available_houses = House.objects.filter(status='available')
        if district_id:
            available_houses = available_houses.filter(district_id=district_id)
        
        # 获取近30天的数据
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = Transaction.objects.filter(deal_date__gte=thirty_days_ago)
        if district_id:
            recent_transactions = recent_transactions.filter(house__district_id=district_id)
        
        # 获取近90天的数据用于对比
        ninety_days_ago = datetime.now().date() - timedelta(days=90)
        older_transactions = Transaction.objects.filter(
            deal_date__gte=ninety_days_ago,
            deal_date__lt=thirty_days_ago
        )
        if district_id:
            older_transactions = older_transactions.filter(house__district_id=district_id)
        
        # 供需比 = 在售房源数 / 近30天成交量
        supply_count = available_houses.count()
        demand_count = recent_transactions.count()
        supply_demand_ratio = supply_count / demand_count if demand_count > 0 else supply_count
        
        # 成交活跃度
        if demand_count > 20:
            transaction_activity = '高'
            activity_level = 'high'
        elif demand_count > 10:
            transaction_activity = '中'
            activity_level = 'medium'
        else:
            transaction_activity = '低'
            activity_level = 'low'
        
        # 市场热度指数 (0-100)
        # 基于供需比和成交活跃度
        if supply_demand_ratio < 1:
            heat_base = 80
        elif supply_demand_ratio < 2:
            heat_base = 60
        elif supply_demand_ratio < 5:
            heat_base = 40
        else:
            heat_base = 20
        
        activity_bonus = min(demand_count * 2, 20)
        market_heat = min(heat_base + activity_bonus, 100)
        
        # 价格趋势分析
        if recent_transactions.exists() and older_transactions.exists():
            recent_avg = recent_transactions.aggregate(
                avg_price=Avg('deal_price')
            )['avg_price']
            older_avg = older_transactions.aggregate(
                avg_price=Avg('deal_price')
            )['avg_price']
            
            if recent_avg and older_avg:
                price_change_percent = ((float(recent_avg) - float(older_avg)) / float(older_avg)) * 100
                
                if price_change_percent > 3:
                    price_trend = '上涨'
                    trend_direction = 'up'
                    forecast_change = price_change_percent * 0.8  # 预测下月涨幅
                elif price_change_percent < -3:
                    price_trend = '下跌'
                    trend_direction = 'down'
                    forecast_change = price_change_percent * 0.8
                else:
                    price_trend = '平稳'
                    trend_direction = 'stable'
                    forecast_change = 0
                
                # 预测下月价格
                current_avg_price = float(recent_avg)
                forecast_next_month = current_avg_price * (1 + forecast_change / 100)
            else:
                price_trend = '数据不足'
                trend_direction = 'unknown'
                price_change_percent = 0
                current_avg_price = 0
                forecast_next_month = 0
                forecast_change = 0
        else:
            price_trend = '数据不足'
            trend_direction = 'unknown'
            price_change_percent = 0
            current_avg_price = 0
            forecast_next_month = 0
            forecast_change = 0
        
        # 市场建议
        if market_heat > 70 and trend_direction == 'up':
            market_suggestion = '市场火热，价格上涨，建议及时把握投资机会'
        elif market_heat > 70 and trend_direction == 'stable':
            market_suggestion = '市场活跃但价格平稳，适合投资'
        elif market_heat < 40 and trend_direction == 'down':
            market_suggestion = '市场低迷，价格下跌，建议观望或寻找低价机会'
        elif trend_direction == 'up':
            market_suggestion = '价格上涨趋势，但市场活跃度一般'
        elif trend_direction == 'down':
            market_suggestion = '价格下跌，可关注潜在投资机会'
        else:
            market_suggestion = '市场平稳，可根据个人需求决策'
        
        result = {
            'supply_demand_ratio': round(supply_demand_ratio, 2),
            'supply_count': supply_count,
            'demand_count': demand_count,
            'market_heat': round(market_heat, 1),
            'transaction_activity': transaction_activity,
            'activity_level': activity_level,
            'price_trend': price_trend,
            'trend_direction': trend_direction,
            'price_change_percent': round(price_change_percent, 2),
            'current_avg_price': round(current_avg_price, 2),
            'forecast_next_month': round(forecast_next_month, 2),
            'forecast_change_percent': round(forecast_change, 2),
            'market_suggestion': market_suggestion,
            'analysis_date': datetime.now().date().isoformat()
        }
        
        return success_response(data=result)


class MarketReportViewSet(viewsets.ModelViewSet):
    """
    市场报告视图集
    """
    queryset = MarketReport.objects.select_related('district')
    serializer_class = MarketReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAgentOrAdmin()]
        return [IsAuthenticated()]

