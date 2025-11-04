import request from '@/utils/request'

/**
 * 获取价格趋势
 */
export function getPriceTrend(params) {
  return request({
    url: '/analysis/price_trend/',
    method: 'get',
    params
  })
}

/**
 * 获取区域对比
 */
export function getDistrictComparison(params) {
  return request({
    url: '/analysis/district_comparison/',
    method: 'get',
    params
  })
}

/**
 * 获取户型分布
 */
export function getHouseTypeDistribution(params) {
  return request({
    url: '/analysis/house_type_distribution/',
    method: 'get',
    params
  })
}

/**
 * 获取价格区间分布
 */
export function getPriceRangeDistribution(params) {
  return request({
    url: '/analysis/price_range_distribution/',
    method: 'get',
    params
  })
}

/**
 * 预测房价
 */
export function predictPrice(data) {
  return request({
    url: '/analysis/predict_price/',
    method: 'post',
    data
  })
}

/**
 * 获取市场报告列表
 */
export function getMarketReportList(params) {
  return request({
    url: '/market-reports/',
    method: 'get',
    params
  })
}

/**
 * 获取市场报告详情
 */
export function getMarketReportDetail(id) {
  return request({
    url: `/market-reports/${id}/`,
    method: 'get'
  })
}

/**
 * 投资回报率分析 (经纪人专用)
 */
export function roiAnalysis(data) {
  return request({
    url: '/analysis/roi_analysis/',
    method: 'post',
    data
  })
}

/**
 * 市场趋势预测分析 (经纪人专用)
 */
export function marketTrendForecast(params) {
  return request({
    url: '/analysis/market_trend_forecast/',
    method: 'get',
    params
  })
}

/**
 * 获取区域热度图数据
 */
export function getDistrictHeatMap(params) {
  return request({
    url: '/analysis/district_heat_map/',
    method: 'get',
    params
  })
}

