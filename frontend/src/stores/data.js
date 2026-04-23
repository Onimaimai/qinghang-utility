import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useDataStore = defineStore('data', () => {
  // 当前数据类型
  const dataType = ref('electricity') // 'electricity' | 'water'

  // 余额数据
  const balance = ref(null)
  const balanceTime = ref('')
  const balanceHasData = ref(false)

  // 明细数据
  const details = ref([])
  const detailsTime = ref('')
  const detailsHasData = ref(false)

  // 能耗数据
  const energy = ref([])
  const energyTime = ref('')
  const energyHasData = ref(false)
  const energyUnit = ref('kW·h')
  const energyPrice = ref(null)

  // 加载状态
  const loadingBalance = ref(false)
  const loadingDetails = ref(false)
  const loadingEnergy = ref(false)

  // 设置数据类型
  function setDataType(type) {
    dataType.value = type
  }

  // 获取余额
  async function fetchBalance() {
    if (loadingBalance.value) return

    loadingBalance.value = true
    try {
      const { data } = await api.get(`/data/balance?type=${dataType.value}`)
      balance.value = data.balance
      balanceHasData.value = data.has_data
      if (data.crawled_at) {
        balanceTime.value = new Date(data.crawled_at).toLocaleString()
      }
      return data
    } catch (error) {
      throw error
    } finally {
      loadingBalance.value = false
    }
  }

  // 获取明细
  async function fetchDetails() {
    if (loadingDetails.value) return

    loadingDetails.value = true
    try {
      const { data } = await api.get(`/data/details?type=${dataType.value}`)
      details.value = data.details || []
      detailsHasData.value = data.has_data
      if (data.crawled_at) {
        detailsTime.value = new Date(data.crawled_at).toLocaleString()
      }
      return data
    } catch (error) {
      throw error
    } finally {
      loadingDetails.value = false
    }
  }

  // 获取能耗
  async function fetchEnergy() {
    if (loadingEnergy.value) return

    loadingEnergy.value = true
    try {
      const { data } = await api.get(`/data/energy?type=${dataType.value}`)
      energy.value = data.energy || []
      energyHasData.value = data.has_data
      energyUnit.value = data.unit || 'kW·h'
      energyPrice.value = data.price || null
      if (data.crawled_at) {
        energyTime.value = new Date(data.crawled_at).toLocaleString()
      }
      return data
    } catch (error) {
      throw error
    } finally {
      loadingEnergy.value = false
    }
  }

  // 获取所有数据
  async function fetchAllData() {
    await Promise.all([
      fetchBalance(),
      fetchDetails(),
      fetchEnergy()
    ])
  }

  // 清空数据（退出登录时调用）
  function clearData() {
    dataType.value = 'electricity'
    balance.value = null
    balanceTime.value = ''
    balanceHasData.value = false
    details.value = []
    detailsTime.value = ''
    detailsHasData.value = false
    energy.value = []
    energyTime.value = ''
    energyHasData.value = false
    energyUnit.value = 'kW·h'
    energyPrice.value = null
  }

  return {
    // 状态
    dataType,
    balance, balanceTime, balanceHasData,
    details, detailsTime, detailsHasData,
    energy, energyTime, energyHasData, energyUnit, energyPrice,
    loadingBalance, loadingDetails, loadingEnergy,
    // 方法
    setDataType,
    fetchBalance, fetchDetails, fetchEnergy, fetchAllData, clearData
  }
})
