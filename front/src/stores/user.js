import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getUserProfile } from '@/api/user'
import { setToken, setRefreshToken, setUserInfo, clearAuth, getToken } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)
  const isLoggedIn = ref(false)

  /**
   * 初始化用户信息
   */
  function initUser() {
    const savedToken = getToken()
    if (savedToken) {
      token.value = savedToken
      isLoggedIn.value = true
      // 获取用户信息
      fetchUserInfo()
    }
  }

  /**
   * 登录
   */
  async function login(loginForm) {
    try {
      const res = await loginApi(loginForm)
      if (res.code === 200) {
        const { access, refresh, user } = res.data
        
        // 保存token
        token.value = access
        setToken(access)
        setRefreshToken(refresh)
        
        // 保存用户信息
        userInfo.value = user
        setUserInfo(user)
        isLoggedIn.value = true
        
        return { success: true }
      }
    } catch (error) {
      return { success: false, message: error.message }
    }
  }

  /**
   * 获取用户信息
   */
  async function fetchUserInfo() {
    try {
      const res = await getUserProfile()
      if (res.code === 200) {
        userInfo.value = res.data
        setUserInfo(res.data)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  /**
   * 更新用户信息
   */
  function updateUserInfo(data) {
    userInfo.value = { ...userInfo.value, ...data }
    setUserInfo(userInfo.value)
  }

  /**
   * 登出
   */
  function logout() {
    token.value = ''
    userInfo.value = null
    isLoggedIn.value = false
    clearAuth()
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    initUser,
    login,
    fetchUserInfo,
    updateUserInfo,
    logout
  }
})

