import request from '@/utils/request'

/**
 * 获取房源列表
 */
export function getHouseList(params) {
  return request({
    url: '/houses/',
    method: 'get',
    params
  })
}

/**
 * 获取房源详情
 */
export function getHouseDetail(id) {
  return request({
    url: `/houses/${id}/`,
    method: 'get'
  })
}

/**
 * 创建房源
 */
export function createHouse(data) {
  return request({
    url: '/houses/',
    method: 'post',
    data
  })
}

/**
 * 更新房源（完整更新）
 */
export function updateHouse(id, data) {
  return request({
    url: `/houses/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 部分更新房源
 */
export function patchHouse(id, data) {
  return request({
    url: `/houses/${id}/`,
    method: 'patch',
    data
  })
}

/**
 * 删除房源
 */
export function deleteHouse(id) {
  return request({
    url: `/houses/${id}/`,
    method: 'delete'
  })
}

/**
 * 获取地图数据
 */
export function getMapData(params) {
  return request({
    url: '/houses/map_data/',
    method: 'get',
    params
  })
}

/**
 * 获取热门房源
 */
export function getHotHouses(params) {
  return request({
    url: '/houses/hot_houses/',
    method: 'get',
    params
  })
}

/**
 * 获取区域列表
 */
export function getDistrictList(params) {
  return request({
    url: '/districts/',
    method: 'get',
    params
  })
}

/**
 * 获取区域详情
 */
export function getDistrictDetail(id) {
  return request({
    url: `/districts/${id}/`,
    method: 'get'
  })
}

/**
 * 创建区域
 */
export function createDistrict(data) {
  return request({
    url: '/districts/',
    method: 'post',
    data
  })
}

/**
 * 更新区域
 */
export function updateDistrict(id, data) {
  return request({
    url: `/districts/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除区域
 */
export function deleteDistrict(id) {
  return request({
    url: `/districts/${id}/`,
    method: 'delete'
  })
}

/**
 * 上传房源图片
 */
export function uploadHouseImage(data) {
  return request({
    url: '/house-images/',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

