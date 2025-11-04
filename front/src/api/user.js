import request from '@/utils/request'

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/users/register/',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 */
export function login(data) {
  return request({
    url: '/users/login/',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 */
export function getUserProfile() {
  return request({
    url: '/users/profile/',
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateUserProfile(data) {
  return request({
    url: '/users/update_profile/',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(data) {
  return request({
    url: '/users/change_password/',
    method: 'post',
    data
  })
}

