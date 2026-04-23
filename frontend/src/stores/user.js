import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useDataStore } from './data'
import api from '@/api'

export const useUserStore = defineStore('user', () => {
  // userInfo 存储在 localStorage 以便页面刷新后恢复
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  function setUserInfo(info) {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  async function logout() {
    try {
      // 调用后端清除 cookie
      await api.post('/auth/logout')
    } catch (error) {
      // 忽略错误
    }
    userInfo.value = null
    localStorage.removeItem('userInfo')
    // 清空数据缓存
    const dataStore = useDataStore()
    dataStore.clearData()
  }

  return {
    userInfo,
    setUserInfo,
    logout
  }
})
