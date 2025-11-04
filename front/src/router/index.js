import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUserInfo } from '@/utils/auth'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/houses',
        name: 'HouseList',
        component: () => import('@/views/house/List.vue'),
        meta: { title: '房源列表' }
      },
      {
        path: '/houses/:id',
        name: 'HouseDetail',
        component: () => import('@/views/house/Detail.vue'),
        meta: { title: '房源详情' }
      },
      {
        path: '/map',
        name: 'Map',
        component: () => import('@/views/Map.vue'),
        meta: { title: '地图找房' }
      },
      {
        path: '/analysis',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '数据分析' }
      },
      {
        path: '/favorites',
        name: 'Favorites',
        component: () => import('@/views/user/Favorites.vue'),
        meta: { title: '我的收藏', requireAuth: true }
      },
      {
        path: '/alerts',
        name: 'PriceAlerts',
        component: () => import('@/views/user/PriceAlerts.vue'),
        meta: { title: '价格提醒', requireAuth: true }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人中心', requireAuth: true }
      },
      {
        path: '/my-houses',
        name: 'MyHouses',
        component: () => import('@/views/user/MyHouses.vue'),
        meta: { title: '我的房源', requireAuth: true }
      },
      {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '管理中心', requireAuth: true, requireAdmin: true }
      },
      {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { title: '用户管理', requireAuth: true, requireAdmin: true }
      },
      {
        path: '/admin/houses',
        name: 'AdminHouses',
        component: () => import('@/views/admin/HouseManagement.vue'),
        meta: { title: '房源管理', requireAuth: true, requireAdmin: true }
      },
      {
        path: '/admin/districts',
        name: 'AdminDistricts',
        component: () => import('@/views/admin/DistrictManagement.vue'),
        meta: { title: '区域管理', requireAuth: true, requireAdmin: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 二手房可视化系统` : '二手房可视化系统'

  // 检查是否需要登录
  if (to.meta.requireAuth) {
    const token = getToken()
    if (!token) {
      ElMessage.warning('请先登录')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requireAdmin) {
      const userInfo = getUserInfo()
      if (!userInfo || userInfo.role !== 'admin') {
        ElMessage.error('需要管理员权限')
        next('/')
        return
      }
    }
    
    next()
  } else {
    next()
  }
})

export default router

