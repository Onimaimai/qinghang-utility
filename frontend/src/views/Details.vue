<template>
  <div class="details-page">
    <!-- Summary Stats -->
    <div class="stats-row" v-if="dataStore.details.length > 0">
      <div class="stat-item">
        <div class="stat-icon income-icon">
          <el-icon><CirclePlus /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">总充值</span>
          <span class="stat-value positive">+{{ totalIncome }}元</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon expense-icon">
          <el-icon><Minus /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">总支出</span>
          <span class="stat-value negative">{{ totalExpense }}元</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon month-income-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">月充值</span>
          <span class="stat-value positive">+{{ monthlyIncome }}元</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon month-expense-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">月支出</span>
          <span class="stat-value negative">{{ monthlyExpense }}元</span>
        </div>
      </div>
    </div>

    <!-- Content Card -->
    <div class="content-card" v-loading="dataStore.loadingDetails">
      <!-- Empty State -->
      <div class="empty-state" v-if="!dataStore.loadingDetails && !dataStore.detailsHasData">
        <div class="empty-icon">
          <el-icon :size="64"><Document /></el-icon>
        </div>
        <h3 class="empty-title">暂无数据</h3>
        <p class="empty-desc">系统每天 9:00 自动更新余额明细</p>
      </div>

      <!-- Mobile List View -->
      <div class="mobile-list" v-else-if="isMobile && sortedDetails.length > 0">
        <div
          class="detail-card"
          v-for="(item, index) in sortedDetails"
          :key="index"
          :class="{ 'income': parseFloat(item.amount) > 0, 'expense': parseFloat(item.amount) < 0 }"
        >
          <div class="detail-header">
            <div class="detail-type">
              <span class="type-text">{{ dataStore.dataType === 'water' ? '水费' : item.type }}</span>
            </div>
            <div class="detail-amount" :class="{ 'positive': parseFloat(item.amount) > 0, 'negative': parseFloat(item.amount) < 0 }">
              {{ formatAmount(item.amount) }}元
            </div>
          </div>
          <div class="detail-body">
            <div class="detail-row">
              <span class="row-label">日期</span>
              <span class="row-value">{{ item.date }}</span>
            </div>
            <div class="detail-row">
              <span class="row-label">房间</span>
              <span class="row-value">{{ item.room }}</span>
            </div>
            <div class="detail-row">
              <span class="row-label">余额</span>
              <span class="row-value highlight">{{ item.balance }}元</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop Table View -->
      <div class="table-container" v-else-if="sortedDetails.length > 0">
        <el-table
          :data="sortedDetails"
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

          <el-table-column prop="room" label="房间" width="120">
            <template #default="{ row }">
              <span class="cell-room">{{ row.room }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">
              <span class="cell-type">{{ dataStore.dataType === 'water' ? '水费' : row.type }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              <span class="cell-amount" :class="{ 'positive': parseFloat(row.amount) > 0, 'negative': parseFloat(row.amount) < 0 }">
                {{ formatAmount(row.amount) }}元
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="balance" label="余额" width="120">
            <template #default="{ row }">
              <span class="cell-balance">{{ row.balance }}元</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useDataStore } from '@/stores/data'

const dataStore = useDataStore()
const isMobile = ref(false)

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

const totalIncome = computed(() => {
  return dataStore.details
    .filter(item => parseFloat(item.amount) > 0)
    .reduce((sum, item) => sum + parseFloat(item.amount), 0)
    .toFixed(2)
})

const totalExpense = computed(() => {
  return dataStore.details
    .filter(item => parseFloat(item.amount) < 0)
    .reduce((sum, item) => sum + parseFloat(item.amount), 0)
    .toFixed(2)
})

const monthlyIncome = computed(() => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonthNum = now.getMonth() + 1
  // 匹配中文日期格式: 2026年04月...
  const monthPrefix = `${currentYear}年${String(currentMonthNum).padStart(2, '0')}月`
  return dataStore.details
    .filter(item => parseFloat(item.amount) > 0 && item.date && item.date.startsWith(monthPrefix))
    .reduce((sum, item) => sum + parseFloat(item.amount), 0)
    .toFixed(2)
})

const monthlyExpense = computed(() => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonthNum = now.getMonth() + 1
  // 匹配中文日期格式: 2026年04月...
  const monthPrefix = `${currentYear}年${String(currentMonthNum).padStart(2, '0')}月`
  return dataStore.details
    .filter(item => parseFloat(item.amount) < 0 && item.date && item.date.startsWith(monthPrefix))
    .reduce((sum, item) => sum + parseFloat(item.amount), 0)
    .toFixed(2)
})

// 格式化金额显示，避免重复显示正负号
function formatAmount(amount) {
  const num = parseFloat(amount)
  if (isNaN(num)) return amount
  // 如果 amount 已经带有正负号，直接返回
  if (typeof amount === 'string' && (amount.startsWith('+') || amount.startsWith('-'))) {
    return amount
  }
  // 否则根据正负值添加符号
  return num > 0 ? `+${amount}` : amount
}

// 对明细数据按日期时间排序（最新的排在最前面）
const sortedDetails = computed(() => {
  return [...dataStore.details].sort((a, b) => {
    // 将中文日期格式转换为可比较的格式
    const parseDate = (dateStr) => {
      if (!dateStr) return 0
      // 格式: 2026年04月11日 18:22
      const match = dateStr.match(/(\d{4})年(\d{2})月(\d{2})日\s+(\d{2}):(\d{2})/)
      if (match) {
        return new Date(match[1], match[2] - 1, match[3], match[4], match[5]).getTime()
      }
      return 0
    }
    return parseDate(b.date) - parseDate(a.date)
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

watch(() => dataStore.dataType, () => {
  dataStore.fetchDetails()
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  // 加载数据
  if (dataStore.details.length === 0) {
    dataStore.fetchDetails()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.details-page {
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

/* Content Card */
.content-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 400px;
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

.cell-room {
  padding: var(--space-1) var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.cell-type {
  font-size: 13px;
  color: var(--text-secondary);
}

.cell-amount {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-weight: 600;
}

.cell-amount.positive {
  color: var(--success);
}

.cell-amount.negative {
  color: var(--danger);
}

.cell-balance {
  font-weight: 600;
  color: var(--text-primary);
}

/* Mobile List */
.mobile-list {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-card {
  background: var(--bg-white);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: all var(--transition-fast);
}

.detail-card:active {
  transform: scale(0.98);
}

.detail-card.income {
  border-left: 4px solid var(--success);
}

.detail-card.expense {
  border-left: 4px solid var(--danger);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.detail-type {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.type-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-card.income .type-icon {
  background: var(--success-alpha);
  color: var(--success);
}

.detail-card.expense .type-icon {
  background: var(--danger-alpha);
  color: var(--danger);
}

.type-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-amount {
  font-size: 18px;
  font-weight: 700;
}

.detail-amount.positive {
  color: var(--success);
}

.detail-amount.negative {
  color: var(--danger);
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.row-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.row-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.row-value.highlight {
  font-weight: 700;
  color: var(--primary);
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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

.income-icon {
  background: var(--success-alpha);
  color: var(--success);
}

.expense-icon {
  background: var(--danger-alpha);
  color: var(--danger);
}

.count-icon {
  background: var(--primary-alpha);
  color: var(--primary);
}

.month-income-icon {
  background: var(--success-alpha);
  color: var(--success);
}

.month-expense-icon {
  background: var(--danger-alpha);
  color: var(--danger);
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

.stat-value.positive {
  color: var(--success);
}

.stat-value.negative {
  color: var(--danger);
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

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-item {
    padding: var(--space-4);
  }
}
</style>
