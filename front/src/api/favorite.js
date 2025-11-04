import request from '@/utils/request'

/**
 * 获取收藏列表
 */
export function getFavoriteList(params) {
  return request({
    url: '/favorites/',
    method: 'get',
    params
  })
}

/**
 * 添加收藏
 */
export function addFavorite(data) {
  return request({
    url: '/favorites/',
    method: 'post',
    data
  })
}

/**
 * 取消收藏
 */
export function removeFavorite(id) {
  return request({
    url: `/favorites/${id}/`,
    method: 'delete'
  })
}

/**
 * 切换收藏状态
 */
export function toggleFavorite(data) {
  return request({
    url: '/favorites/toggle/',
    method: 'post',
    data
  })
}

/**
 * 检查收藏状态
 */
export function checkFavorite(params) {
  return request({
    url: '/favorites/check/',
    method: 'get',
    params
  })
}

/**
 * 获取价格提醒列表
 */
export function getPriceAlertList(params) {
  return request({
    url: '/price-alerts/',
    method: 'get',
    params
  })
}

/**
 * 创建价格提醒
 */
export function createPriceAlert(data) {
  return request({
    url: '/price-alerts/',
    method: 'post',
    data
  })
}

/**
 * 删除价格提醒
 */
export function deletePriceAlert(id) {
  return request({
    url: `/price-alerts/${id}/`,
    method: 'delete'
  })
}

/**
 * 取消价格提醒
 */
export function cancelPriceAlert(id) {
  return request({
    url: `/price-alerts/${id}/cancel/`,
    method: 'post'
  })
}

/**
 * 检查房源的价格提醒状态
 */
export function checkHouseAlert(params) {
  return request({
    url: '/price-alerts/check_house_alert/',
    method: 'get',
    params
  })
}

