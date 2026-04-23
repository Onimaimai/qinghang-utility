<template>
  <div class="energy-page">
    <!-- Summary Stats -->
    <div class="stats-row" v-if="dataStore.energy.length > 0">
      <div class="stat-item">
        <div class="stat-icon total-icon">
          <el-icon>
            <Lightning v-if="dataStore.dataType === 'electricity'" />
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
            </svg>
          </el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">{{ dataStore.dataType === 'water' ? '总用水量' : '总用电量' }}</span>
          <span class="stat-value">{{ totalUsage }} {{ dataStore.energyUnit }}</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon cost-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">总费用</span>
          <span class="stat-value">{{ totalAmount }}元</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon avg-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">{{ dataStore.dataType === 'water' ? '日均用水' : '日均用电' }}</span>
          <span class="stat-value">{{ avgUsage }} {{ dataStore.energyUnit }}</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-card" v-if="dataStore.energy.length > 0">
      <div class="chart-header">
        <h2 class="chart-title">
          <el-icon><TrendCharts /></el-icon>
          {{ dataStore.dataType === 'water' ? '用水量趋势' : '用电量趋势' }}
        </h2>
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-dot electricity"></div>
            <span>{{ dataStore.dataType === 'water' ? '用水量' : '用电量' }} ({{ dataStore.energyUnit }})</span>
          </div>
          <div class="legend-item">
            <div class="legend-dot amount"></div>
            <span>金额 (元)</span>
          </div>
        </div>
      </div>
      <div class="chart-container">
        <div ref="chartRef" class="chart"></div>
      </div>
    </div>

    <!-- Content Card -->
    <div class="content-card" v-loading="dataStore.loadingEnergy">
      <!-- Empty State -->
      <div class="empty-state" v-if="!dataStore.loadingEnergy && !dataStore.energyHasData">
        <div class="empty-icon">
          <el-icon :size="64"><TrendCharts /></el-icon>
        </div>
        <h3 class="empty-title">暂无数据</h3>
        <p class="empty-desc">系统每天 9:00 自动更新能耗记录</p>
      </div>

      <!-- Mobile List View -->
      <div class="mobile-list" v-else-if="isMobile && dataStore.energy.length > 0">
        <div
          class="energy-card"
          v-for="(item, index) in dataStore.energy"
          :key="index"
        >
          <div class="energy-header">
            <div class="energy-date">
              <el-icon><Calendar /></el-icon>
              <span>{{ item.date }}</span>
            </div>
            <div class="energy-amount">-{{ item.amount }}元</div>
          </div>
          <div class="energy-body">
            <div class="energy-info">
              <div class="info-item">
                <span class="info-label">{{ dataStore.dataType === 'water' ? '水表' : '电表' }}</span>
                <span class="info-value">{{ item.meter }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">{{ dataStore.dataType === 'water' ? '用水量' : '用电量' }}</span>
                <span class="info-value highlight">{{ item.usage }} {{ dataStore.energyUnit }}</span>
              </div>
            </div>
            <div class="energy-bar">
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: getBarWidth(item.electricity) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop Table View -->
      <div class="table-container" v-else-if="dataStore.energy.length > 0">
        <el-table
          :data="dataStore.energy"
          style="width: 100%"
          :header-cell-style="headerStyle"
          :cell-style="cellStyle"
        >
          <el-table-column prop="date" label="日期" min-width="180">
            <template #default="{ row }">
              <div class="cell-date">
                <el-icon><Calendar /></el-icon>
                <span>{{ row.date }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="meter" :label="dataStore.dataType === 'water' ? '水表' : '电表'" min-width="180">
            <template #default="{ row }">
              <div class="cell-meter">
                <div class="meter-icon">
                  <el-icon>
                    <Lightning v-if="dataStore.dataType === 'electricity'" />
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
                    </svg>
                  </el-icon>
                </div>
                <span class="meter-text">{{ row.meter }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="usage" :label="dataStore.dataType === 'water' ? '用水量' : '用电量'" width="140">
            <template #default="{ row }">
              <div class="cell-electricity">
                <span class="electricity-value">{{ row.usage }}</span>
                <span class="electricity-unit">{{ dataStore.energyUnit }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              <div class="cell-amount">
                <span>-{{ row.amount }}元</span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import { useDataStore } from '@/stores/data'

const dataStore = useDataStore()
const chartRef = ref(null)
const isMobile = ref(false)
let chart = null

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

const totalUsage = computed(() => {
  return dataStore.energy
    .reduce((sum, item) => sum + (parseFloat(item.usage) || 0), 0)
    .toFixed(2)
})

const totalAmount = computed(() => {
  return dataStore.energy
    .reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0)
    .toFixed(2)
})

const avgUsage = computed(() => {
  if (dataStore.energy.length === 0) return '0.00'
  return (parseFloat(totalUsage.value) / dataStore.energy.length).toFixed(2)
})

const maxUsage = computed(() => {
  return Math.max(...dataStore.energy.map(item => parseFloat(item.usage) || 0))
})

function getBarWidth(usage) {
  if (maxUsage.value === 0) return 0
  return (parseFloat(usage) / maxUsage.value) * 100
}

function renderChart() {
  if (!chartRef.value || dataStore.energy.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
    window.addEventListener('resize', () => chart?.resize())
  }

  // 按日期升序排序（从早到晚）
  const sortedEnergy = [...dataStore.energy].sort((a, b) => {
    const parseDate = (dateStr) => {
      if (!dateStr) return 0
      const match = dateStr.match(/(\d{4})年(\d{2})月(\d{2})日\s+(\d{2}):(\d{2})/)
      if (match) {
        return new Date(match[1], match[2] - 1, match[3], match[4], match[5]).getTime()
      }
      return 0
    }
    return parseDate(a.date) - parseDate(b.date)
  })

  const dates = sortedEnergy.map(e => e.date.slice(5))
  const usageData = sortedEnergy.map(e => parseFloat(e.usage) || 0)
  const amountData = sortedEnergy.map(e => parseFloat(e.amount) || 0)

  const unitLabel = dataStore.dataType === 'water' ? '用水量' : '用电量'
  const unit = dataStore.energyUnit

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
        return `
          <div style="font-weight: 600; margin-bottom: 8px;">${params[0].axisValue}</div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <div style="width: 8px; height: 8px; background: #f59e0b; border-radius: 50%;"></div>
            <span style="color: #64748b;">${unitLabel}:</span>
            <span style="font-weight: 600; color: #f59e0b;">${params[0].value} ${unit}</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 8px; height: 8px; background: #000000; border-radius: 50%;"></div>
            <span style="color: #64748b;">金额:</span>
            <span style="font-weight: 600; color: #000000;">${params[1].value}元</span>
          </div>
        `
      }
    },
    legend: {
      show: false
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
      data: dates,
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
    yAxis: [
      {
        type: 'value',
        name: unit,
        position: 'left',
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: '#f1f5f9',
            type: 'dashed'
          }
        }
      },
      {
        type: 'value',
        name: '元',
        position: 'right',
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#64748b',
          fontSize: 12
        },
        splitLine: {
          show: false
        }
      }
    ],
    series: [
      {
        name: unitLabel,
        data: usageData,
        type: 'bar',
        barWidth: '40%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fbbf24' },
            { offset: 1, color: '#f59e0b' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#fcd34d' },
              { offset: 1, color: '#fbbf24' }
            ])
          }
        }
      },
      {
        name: '金额',
        data: amountData,
        type: 'line',
        yAxisIndex: 1,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          color: '#000000',
          width: 3
        },
        itemStyle: {
          color: '#000000',
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          itemStyle: {
            color: '#fff',
            borderColor: '#000000',
            borderWidth: 3,
            shadowColor: 'rgba(59, 130, 246, 0.5)',
            shadowBlur: 10
          }
        }
      }
    ]
  }

  chart.setOption(option)
}

watch(() => dataStore.energy, () => {
  nextTick(() => renderChart())
}, { deep: true })

watch(() => dataStore.dataType, () => {
  dataStore.fetchEnergy().then(() => {
    nextTick(() => renderChart())
  })
})

const headerStyle = () => ({
  background: '#f8fafc',
  color: '#64748b',
  fontWeight: 600,
  fontSize: '12px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  padding: '16px'
})

const cellStyle = () => ({
  padding: '16px'
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  // 加载数据
  if (dataStore.energy.length === 0) {
    dataStore.fetchEnergy().then(() => {
      nextTick(() => renderChart())
    })
  } else {
    nextTick(() => renderChart())
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.energy-page {
  max-width: 1200px;
}

/* Update Info */
.update-info {
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

.update-info .el-icon {
  color: var(--primary);
}

/* Chart Card */
.chart-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-title .el-icon {
  color: var(--primary);
}

.chart-legend {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  color: var(--text-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.electricity {
  background: var(--warning);
}

.legend-dot.amount {
  background: var(--primary);
}

.chart-container {
  width: 100%;
  overflow: visible;
}

.chart {
  height: 300px;
  width: 100%;
}

/* Content Card */
.content-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 300px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-10);
  text-align: center;
}

.empty-icon {
  width: 100px;
  height: 100px;
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  margin-bottom: var(--space-5);
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.empty-desc {
  font-size: 15px;
  color: var(--text-secondary);
}

/* Table Container */
.table-container {
  padding: var(--space-2);
}

:deep(.el-table) {
  border-radius: var(--radius-lg);
}

:deep(.el-table__row) {
  transition: background-color var(--transition-fast);
}

:deep(.el-table__row:hover) {
  background-color: var(--primary-alpha) !important;
}

.cell-date {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
}

.cell-date .el-icon {
  color: var(--primary);
}

.cell-meter {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.meter-icon {
  width: 32px;
  height: 32px;
  background: var(--warning-alpha);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--warning);
}

.meter-text {
  font-size: 14px;
  color: var(--text-primary);
}

.cell-electricity {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.electricity-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--warning);
}

.electricity-unit {
  font-size: 12px;
  color: var(--text-secondary);
}

.cell-amount {
  font-weight: 600;
  color: var(--danger);
}

/* Mobile List */
.mobile-list {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.energy-card {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: all var(--transition-fast);
}

.energy-card:active {
  transform: scale(0.98);
}

.energy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.energy-date {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--text-primary);
  font-weight: 500;
}

.energy-date .el-icon {
  color: var(--primary);
}

.energy-amount {
  font-size: 18px;
  font-weight: 700;
  color: var(--danger);
}

.energy-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.energy-info {
  display: flex;
  justify-content: space-between;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.info-value.highlight {
  font-weight: 700;
  color: var(--warning);
}

.energy-bar {
  width: 100%;
}

.bar-bg {
  height: 6px;
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--gradient-warning);
  border-radius: var(--radius-full);
  transition: width 0.5s ease;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
}

.total-icon {
  background: var(--warning-alpha);
  color: var(--warning);
}

.cost-icon {
  background: var(--danger-alpha);
  color: var(--danger);
}

.avg-icon {
  background: var(--primary-alpha);
  color: var(--primary);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .chart-card {
    padding: var(--space-4);
  }

  .chart {
    height: 280px;
  }

  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    margin-bottom: var(--space-5);
  }

  .stat-item {
    padding: var(--space-4);
  }
}
</style>
