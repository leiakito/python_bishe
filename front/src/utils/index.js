import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.locale('zh-cn')
dayjs.extend(relativeTime)

/**
 * 格式化日期
 * @param {string|Date} date 日期
 * @param {string} format 格式
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 相对时间
 * @param {string|Date} date 日期
 */
export function fromNow(date) {
  if (!date) return ''
  return dayjs(date).fromNow()
}

/**
 * 格式化价格
 * @param {number} price 价格
 */
export function formatPrice(price) {
  if (!price) return '0'
  return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 格式化面积
 * @param {number} area 面积
 */
export function formatArea(area) {
  if (!area) return '0'
  return area.toFixed(2)
}

/**
 * 防抖函数
 * @param {Function} fn 函数
 * @param {number} delay 延迟时间
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn 函数
 * @param {number} delay 延迟时间
 */
export function throttle(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (!timer) {
      timer = setTimeout(() => {
        fn.apply(this, args)
        timer = null
      }, delay)
    }
  }
}

/**
 * 获取房源状态文本
 * @param {string} status 状态
 */
export function getHouseStatusText(status) {
  const statusMap = {
    available: '在售',
    sold: '已售',
    rented: '已租',
    reserved: '预定'
  }
  return statusMap[status] || status
}

/**
 * 获取房源状态类型
 * @param {string} status 状态
 */
export function getHouseStatusType(status) {
  const typeMap = {
    available: 'success',
    sold: 'info',
    rented: 'warning',
    reserved: 'primary'
  }
  return typeMap[status] || 'info'
}

/**
 * 获取用户角色文本
 * @param {string} role 角色
 */
export function getUserRoleText(role) {
  const roleMap = {
    user: '普通用户',
    agent: '经纪人',
    admin: '管理员'
  }
  return roleMap[role] || role
}

/**
 * 获取提醒状态文本
 * @param {string} status 状态
 */
export function getAlertStatusText(status) {
  const statusMap = {
    active: '激活',
    triggered: '已触发',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

/**
 * 获取提醒状态类型
 * @param {string} status 状态
 */
export function getAlertStatusType(status) {
  const typeMap = {
    active: 'success',
    triggered: 'warning',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

/**
 * 下载文件
 * @param {string} url 文件URL
 * @param {string} filename 文件名
 */
export function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
}

