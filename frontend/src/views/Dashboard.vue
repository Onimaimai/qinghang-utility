<template>
  <div class="dashboard">
    <!-- Stats Grid -->
    <div class="stats-grid">
      <!-- Balance Card -->
      <div class="stat-card balance-card" :class="{ 'loading': dataStore.loadingBalance }">
        <div class="card-glow"></div>
        <div class="stat-header">
          <div class="stat-icon balance-icon">
            <svg v-if="dataStore.dataType === 'electricity'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
            </svg>
          </div>
          <span class="stat-label">{{ dataStore.dataType === 'water' ? '水费余额' : '电费余额' }}</span>
        </div>

        <div class="stat-body" v-if="dataStore.balanceHasData">
          <div class="balance-display">
            <span class="currency">¥</span>
            <span class="amount">{{ formattedBalance }}</span>
          </div>
          <div class="balance-status" v-if="dataStore.balance !== null && dataStore.balance < threshold">
            <div class="status-badge warning">
              <el-icon><Warning /></el-icon>
              <span>余额不足（低于 {{ threshold }}元）</span>
            </div>
          </div>
          <div class="balance-status" v-else>
            <div class="status-badge success">
              <el-icon><CircleCheck /></el-icon>
              <span>余额充足</span>
            </div>
          </div>
        </div>

        <div class="stat-empty" v-else>
          <div class="empty-icon">
            <svg v-if="dataStore.dataType === 'electricity'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
            </svg>
          </div>
          <p class="empty-text">暂无数据</p>
          <p class="empty-desc">系统每天 9:00 自动更新</p>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="quick-stats">
        <div class="quick-card" @click="$router.push('/details')">
          <div class="quick-icon details-icon">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="quick-info">
            <span class="quick-label">余额明细</span>
            <span class="quick-desc">查看消费记录</span>
          </div>
          <el-icon class="quick-arrow"><ArrowRight /></el-icon>
        </div>

        <div class="quick-card" @click="$router.push('/energy')">
          <div class="quick-icon energy-icon">
            <el-icon :size="24"><TrendCharts /></el-icon>
          </div>
          <div class="quick-info">
            <span class="quick-label">能耗记录</span>
            <span class="quick-desc">{{ dataStore.dataType === 'water' ? '用水趋势分析' : '用电趋势分析' }}</span>
          </div>
          <el-icon class="quick-arrow"><ArrowRight /></el-icon>
        </div>

        <div class="quick-card" @click="$router.push('/settings')">
          <div class="quick-icon settings-icon">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <div class="quick-info">
            <span class="quick-label">系统设置</span>
            <span class="quick-desc">配置提醒参数</span>
          </div>
          <el-icon class="quick-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <!-- Setup Alert -->
    <transition name="slide-down">
      <div class="setup-alert" v-if="!hasCredential">
        <div class="alert-content">
          <div class="alert-icon">
            <el-icon :size="24"><InfoFilled /></el-icon>
          </div>
          <div class="alert-text">
            <h3>欢迎使用青航公寓水电费查询系统</h3>
            <p>请先配置您的公寓系统凭证，以便自动获取水电费数据</p>
          </div>
          <button class="alert-btn" @click="$router.push('/settings')">
            前往设置
            <el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </div>
    </transition>

    <!-- Chart Section -->
    <transition name="fade-slide">
      <div class="chart-section" v-if="chartData.length >= 2">
        <div class="section-header">
          <h2 class="section-title">
            <el-icon><TrendCharts /></el-icon>
            {{ dataStore.dataType === 'water' ? '水费' : '电费' }}余额变化趋势
          </h2>
          <div class="section-actions">
            <span class="chart-period">最近30天</span>
          </div>
        </div>
        <div class="chart-container">
          <div ref="chartRef" class="chart"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { useUserStore } from '@/stores/user'
import { useDataStore } from '@/stores/data'
import api from '@/api'

const userStore = useUserStore()
const dataStore = useDataStore()

const historyRecords = ref([])
const chartData = ref([])
const chartRef = ref(null)
let chart = null

const hasCredential = computed(() => userStore.userInfo?.has_credential)
const threshold = computed(() => {
  return dataStore.dataType === 'water'
    ? userStore.userInfo?.water_balance_threshold || 30
    : userStore.userInfo?.balance_threshold || 50
})

const formattedBalance = computed(() => {
  const balance = dataStore.balance
  if (balance === null || balance === undefined) return '--'
  return balance.toFixed(2)
})

async function loadAllData() {
  if (!hasCredential.value) return
  try {
    await dataStore.fetchAllData()
    await fetchHistory()
  } catch (error) {
    // 错误已处理
  }
}

async function fetchHistory() {
  try {
    const { data } = await api.get(`/data/history?type=${dataStore.dataType}&limit=30`)
    historyRecords.value = data.records.reverse()
    await nextTick()
    renderChart()
  } catch (error) {
    // 忽略
  }
}

function renderChart() {
  if (!chartRef.value || historyRecords.value.length === 0) return

  // 过滤：只保留余额发生变化的记录
  const filteredRecords = []
  let lastBalance = null
  for (const record of historyRecords.value) {
    if (lastBalance === null || record.balance !== lastBalance) {
      filteredRecords.push(record)
      lastBalance = record.balance
    }
  }

  chartData.value = filteredRecords

  if (filteredRecords.length < 2) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
    window.addEventListener('resize', () => chart?.resize())
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: {
        color: '#1e293b'
      },
      formatter: function(params) {
        const data = filteredRecords[params[0].dataIndex]
        const date = new Date(data.crawled_at)
        return `
          <div style="font-weight: 600; margin-bottom: 4px;">${date.toLocaleDateString()}</div>
          <div style="color: #3b82f6; font-size: 16px; font-weight: 600;">
            ¥${data.balance.toFixed(2)}
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: filteredRecords.map(r => {
        const date = new Date(r.crawled_at)
        return `${date.getMonth() + 1}/${date.getDate()}`
      }),
      axisLine: {
        lineStyle: {
          color: '#e2e8f0'
        }
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 12
      },
      axisTick: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#64748b',
        fontSize: 12,
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: {
          color: '#f1f5f9',
          type: 'dashed'
        }
      }
    },
    series: [{
      data: filteredRecords.map(r => r.balance),
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: '#3b82f6',
        width: 3
      },
      itemStyle: {
        color: '#3b82f6',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
          { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
        ])
      },
      emphasis: {
        itemStyle: {
          color: '#fff',
          borderColor: '#3b82f6',
          borderWidth: 3,
          shadowColor: 'rgba(59, 130, 246, 0.5)',
          shadowBlur: 10
        }
      }
    }]
  }

  chart.setOption(option)
}

watch(hasCredential, (val) => {
  if (val) loadAllData()
}, { immediate: true })

watch(() => dataStore.dataType, () => {
  if (hasCredential.value) loadAllData()
})

onMounted(() => {
  if (hasCredential.value) loadAllData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

/* Update Badge */
.update-badge {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--bg-white);
  border-radius: var(--radius-full);
  font-size: 13px;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
}

.update-badge .el-icon {
  color: var(--primary);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Balance Card */
.balance-card {
  position: relative;
  background: var(--gradient-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  color: white;
  overflow: hidden;
  min-height: 240px;
  display: flex;
  flex-direction: column;
}

.card-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
  pointer-events: none;
}

.balance-card.loading::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.1);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.stat-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  position: relative;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.2);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.stat-label {
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
}

.stat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.balance-display {
  display: flex;
  align-items: flex-start;
  gap: var(--space-1);
}

.currency {
  font-size: 24px;
  font-weight: 600;
  opacity: 0.8;
  margin-top: 4px;
}

.amount {
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
}

.balance-status {
  margin-top: var(--space-5);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: rgba(255,255,255,0.2);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.3);
}

.status-badge.warning {
  background: rgba(245, 158, 11, 0.3);
}

/* Stat Empty */
.stat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  background: rgba(255,255,255,0.1);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-4);
  backdrop-filter: blur(10px);
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--space-1);
}

.empty-desc {
  font-size: 14px;
  opacity: 0.7;
}

/* Quick Stats */
.quick-stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.quick-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.quick-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border);
}

.quick-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.details-icon {
  background: var(--success-alpha);
  color: var(--success);
}

.energy-icon {
  background: var(--warning-alpha);
  color: var(--warning);
}

.settings-icon {
  background: var(--primary-alpha);
  color: var(--primary);
}

.quick-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.quick-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.quick-arrow {
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.quick-card:hover .quick-arrow {
  transform: translateX(4px);
  color: var(--primary);
}

/* Setup Alert */
.setup-alert {
  margin-bottom: var(--space-6);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding: var(--space-5) var(--space-6);
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.alert-icon {
  width: 48px;
  height: 48px;
  background: var(--warning);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.alert-text {
  flex: 1;
}

.alert-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: var(--space-1);
}

.alert-text p {
  font-size: 14px;
  color: #a16207;
}

.alert-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--warning);
  border: none;
  border-radius: var(--radius);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.alert-btn:hover {
  background: #d97706;
  transform: translateY(-1px);
}

/* Chart Section */
.chart-section {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-title .el-icon {
  color: var(--primary);
}

.chart-period {
  font-size: 13px;
  color: var(--text-secondary);
  padding: var(--space-1) var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

.chart-container {
  width: 100%;
}

.chart {
  height: 300px;
  width: 100%;
}

/* Transitions */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all var(--transition);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-4);
  }

  .page-title {
    font-size: 24px;
  }

  .amount {
    font-size: 40px;
  }

  .alert-content {
    flex-direction: column;
    text-align: center;
  }

  .alert-btn {
    width: 100%;
    justify-content: center;
  }

  .chart {
    height: 240px;
  }
}
</style>
