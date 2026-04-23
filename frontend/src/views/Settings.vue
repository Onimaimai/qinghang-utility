<template>
  <div class="settings-page">
    <!-- Settings Grid -->
    <div class="settings-grid">
      <!-- Credentials Card -->
      <div class="settings-card">
        <div class="card-header">
          <div class="header-icon credential-icon">
            <el-icon :size="24"><Key /></el-icon>
          </div>
          <div class="header-text">
            <h2 class="card-title">公寓系统凭证</h2>
            <p class="card-subtitle">配置您的公寓系统登录信息</p>
          </div>
          <div class="status-badge" :class="hasCredential ? 'success' : 'warning'">
            {{ hasCredential ? '已配置' : '未配置' }}
          </div>
        </div>

        <div class="card-body">
          <el-form
            :model="credentialForm"
            :rules="credentialRules"
            ref="credentialFormRef"
            class="settings-form"
          >
            <div class="form-row">
              <el-form-item prop="pms_account" label="账号">
                <div class="input-wrapper">
                  <el-icon class="input-icon"><User /></el-icon>
                  <el-input
                    v-model="credentialForm.pms_account"
                    placeholder="请输入公寓系统账号"
                    size="large"
                  />
                </div>
              </el-form-item>
            </div>

            <div class="form-row">
              <el-form-item prop="pms_password" label="密码">
                <div class="input-wrapper">
                  <el-icon class="input-icon"><Lock /></el-icon>
                  <el-input
                    v-model="credentialForm.pms_password"
                    type="password"
                    placeholder="请输入公寓系统密码"
                    size="large"
                    show-password
                  />
                </div>
              </el-form-item>
            </div>

            <div class="form-actions">
              <button
                type="button"
                class="btn btn-primary"
                :class="{ loading: savingCredential }"
                :disabled="savingCredential"
                @click="saveCredential"
              >
                <el-icon v-if="!savingCredential"><Check /></el-icon>
                <el-icon v-else class="spin"><Loading /></el-icon>
                <span>{{ savingCredential ? '保存中...' : '保存凭证' }}</span>
              </button>

              <button
                v-if="hasCredential"
                type="button"
                class="btn btn-secondary"
                :class="{ loading: crawling }"
                :disabled="crawling"
                @click="triggerCrawl"
              >
                <el-icon v-if="!crawling"><Refresh /></el-icon>
                <el-icon v-else class="spin"><Loading /></el-icon>
                <span>{{ crawling ? '爬取中...' : '立即爬取' }}</span>
              </button>

              <button
                v-if="hasCredential"
                type="button"
                class="btn btn-danger"
                :class="{ loading: deletingCredential }"
                :disabled="deletingCredential"
                @click="deleteCredential"
              >
                <el-icon v-if="!deletingCredential"><Delete /></el-icon>
                <el-icon v-else class="spin"><Loading /></el-icon>
                <span>{{ deletingCredential ? '删除中...' : '删除凭证' }}</span>
              </button>
            </div>

            <!-- 爬取日志显示区域 -->
            <div class="crawl-logs" v-if="crawlLogs.length > 0 || crawling">
              <div class="logs-header">
                <span class="logs-title">
                  <el-icon><Document /></el-icon>
                  爬取日志
                </span>
                <button
                  type="button"
                  class="btn-clear"
                  @click="clearCrawlLogs"
                  :disabled="crawling"
                >
                  <el-icon><Delete /></el-icon>
                  清除
                </button>
              </div>
              <div class="logs-content" ref="logsContent">
                <div
                  v-for="(log, index) in crawlLogs"
                  :key="index"
                  class="log-line"
                  :class="{
                    'log-success': log.includes('✓'),
                    'log-error': log.includes('✗'),
                    'log-warning': log.includes('⚠')
                  }"
                >
                  {{ log }}
                </div>
                <div v-if="crawling" class="log-loading">
                  <el-icon class="spin"><Loading /></el-icon>
                  正在爬取中...
                </div>
              </div>
            </div>
          </el-form>
        </div>
      </div>

      <!-- Notification Card -->
      <div class="settings-card">
        <div class="card-header">
          <div class="header-icon notification-icon">
            <el-icon :size="24"><Bell /></el-icon>
          </div>
          <div class="header-text">
            <h2 class="card-title">提醒设置</h2>
            <p class="card-subtitle">配置余额提醒和通知方式</p>
          </div>
        </div>

        <div class="card-body">
          <el-form
            :model="settingsForm"
            ref="settingsFormRef"
            class="settings-form"
          >
            <div class="form-row">
              <el-form-item label="PushPlus Token">
                <div class="input-wrapper">
                  <el-icon class="input-icon"><Message /></el-icon>
                  <el-input
                    v-model="settingsForm.pushplus_token"
                    placeholder="请输入PushPlus Token"
                    type="password"
                    size="large"
                    show-password
                  />
                </div>
                <div class="form-tip">
                  <el-icon><InfoFilled /></el-icon>
                  <span>获取Token: <a href="http://www.pushplus.plus/" target="_blank" class="link">pushplus.plus</a></span>
                </div>
              </el-form-item>
            </div>

            <div class="form-row">
              <el-form-item label="电费提醒阈值">
                <div class="threshold-input">
                  <el-input-number
                    v-model="settingsForm.balance_threshold"
                    :min="0"
                    :precision="2"
                    :step="10"
                    size="large"
                  />
                  <span class="unit">元</span>
                </div>
                <div class="form-tip">
                  <el-icon><InfoFilled /></el-icon>
                  <span>当电费余额低于此值时发送提醒通知</span>
                </div>
              </el-form-item>
            </div>

            <div class="form-row">
              <el-form-item label="水费提醒阈值">
                <div class="threshold-input">
                  <el-input-number
                    v-model="settingsForm.water_balance_threshold"
                    :min="0"
                    :precision="2"
                    :step="10"
                    size="large"
                  />
                  <span class="unit">元</span>
                </div>
                <div class="form-tip">
                  <el-icon><InfoFilled /></el-icon>
                  <span>当水费余额低于此值时发送提醒通知（水费单价：2.4元/吨）</span>
                </div>
              </el-form-item>
            </div>

            <div class="form-actions">
              <button
                type="button"
                class="btn btn-primary"
                :class="{ loading: savingSettings }"
                :disabled="savingSettings"
                @click="saveSettings"
              >
                <el-icon v-if="!savingSettings"><Check /></el-icon>
                <el-icon v-else class="spin"><Loading /></el-icon>
                <span>{{ savingSettings ? '保存中...' : '保存设置' }}</span>
              </button>

              <button
                type="button"
                class="btn btn-secondary"
                :class="{ loading: testingPush }"
                :disabled="testingPush || !settingsForm.pushplus_token"
                @click="testPushPlus"
              >
                <el-icon v-if="!testingPush"><Promotion /></el-icon>
                <el-icon v-else class="spin"><Loading /></el-icon>
                <span>{{ testingPush ? '发送中...' : '测试通知' }}</span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <!-- Account Info Card -->
    <div class="info-card">
      <div class="card-header">
        <div class="header-icon account-icon">
          <el-icon :size="24"><UserFilled /></el-icon>
        </div>
        <div class="header-text">
          <h2 class="card-title">账号信息</h2>
          <p class="card-subtitle">您的账户基本信息</p>
        </div>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <div class="info-label">
            <el-icon><User /></el-icon>
            <span>用户名</span>
          </div>
          <div class="info-value">{{ userStore.userInfo?.username }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">
            <el-icon><Calendar /></el-icon>
            <span>注册时间</span>
          </div>
          <div class="info-value">{{ formatDate(userStore.userInfo?.created_at) }}</div>
        </div>

        <div class="info-item">
          <div class="info-label">
            <el-icon><Key /></el-icon>
            <span>凭证状态</span>
          </div>
          <div class="info-value">
            <span class="tag" :class="hasCredential ? 'success' : 'warning'">
              {{ hasCredential ? '已配置' : '未配置' }}
            </span>
          </div>
        </div>

        <div class="info-item">
          <div class="info-label">
            <el-icon><Bell /></el-icon>
            <span>通知状态</span>
          </div>
          <div class="info-value">
            <span class="tag" :class="userStore.userInfo?.pushplus_token ? 'success' : 'default'">
              {{ userStore.userInfo?.pushplus_token ? '已配置' : '未配置' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const credentialFormRef = ref()
const settingsFormRef = ref()
const logsContent = ref(null)

const savingCredential = ref(false)
const deletingCredential = ref(false)
const crawling = ref(false)
const savingSettings = ref(false)
const testingPush = ref(false)

const crawlLogs = ref([])
const logsInterval = ref(null)

const isMobile = ref(false)

const hasCredential = computed(() => userStore.userInfo?.has_credential)

const credentialForm = reactive({
  pms_account: '',
  pms_password: ''
})

const settingsForm = reactive({
  pushplus_token: userStore.userInfo?.pushplus_token || '',
  balance_threshold: userStore.userInfo?.balance_threshold || 50,
  water_balance_threshold: userStore.userInfo?.water_balance_threshold || 30
})

const credentialRules = {
  pms_account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  pms_password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

function formatDate(dateString) {
  if (!dateString) return '--'
  return new Date(dateString).toLocaleString()
}

async function saveCredential() {
  const valid = await credentialFormRef.value.validate().catch(() => false)
  if (!valid) return

  savingCredential.value = true
  try {
    await api.put('/user/credentials', credentialForm)
    ElMessage.success({
      message: '凭证保存成功',
      duration: 2000
    })

    const { data } = await api.get('/auth/me')
    userStore.setUserInfo(data)

    credentialForm.pms_password = ''
  } catch (error) {
    // 错误已处理
  } finally {
    savingCredential.value = false
  }
}

async function deleteCredential() {
  try {
    await ElMessageBox.confirm(
      '确定要删除凭证吗？删除后将无法自动获取水电费数据',
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    deletingCredential.value = true
    await api.delete('/user/credentials')
    ElMessage.success({
      message: '凭证已删除',
      duration: 2000
    })

    const { data } = await api.get('/auth/me')
    userStore.setUserInfo(data)
  } catch (error) {
    if (error !== 'cancel') {
      // 错误已处理
    }
  } finally {
    deletingCredential.value = false
  }
}

async function triggerCrawl() {
  if (!hasCredential.value && !credentialForm.pms_account) {
    ElMessage.warning('请先配置公寓系统凭证')
    return
  }

  // 如果凭证表单中有密码，先保存凭证
  if (credentialForm.pms_password) {
    try {
      await api.put('/user/credentials', credentialForm)
      // 更新用户信息
      const { data } = await api.get('/auth/me')
      userStore.setUserInfo(data)
      credentialForm.pms_password = ''
    } catch (error) {
      ElMessage.error('保存凭证失败')
      return
    }
  }

  crawling.value = true
  crawlLogs.value = []

  // 清除服务器端旧日志
  try {
    await api.delete('/user/crawl/logs')
  } catch (error) {
    // 忽略
  }

  // 启动日志轮询
  startLogsPolling()

  try {
    await api.post('/user/crawl')
    ElMessage.success({
      message: '数据爬取已启动',
      duration: 2000
    })
  } catch (error) {
    crawling.value = false
    stopLogsPolling()
  }
}

// 开始轮询日志
function startLogsPolling() {
  // 立即获取一次
  fetchCrawlLogs()

  // 每1.5秒轮询一次
  logsInterval.value = setInterval(() => {
    fetchCrawlLogs()
  }, 1500)
}

// 停止轮询
function stopLogsPolling() {
  if (logsInterval.value) {
    clearInterval(logsInterval.value)
    logsInterval.value = null
  }
}

// 获取日志
async function fetchCrawlLogs() {
  try {
    const { data } = await api.get('/user/crawl/logs')
    if (data.logs && data.logs.length > 0) {
      crawlLogs.value = data.logs
      // 滚动到底部
      nextTick(() => {
        if (logsContent.value) {
          logsContent.value.scrollTop = logsContent.value.scrollHeight
        }
      })

      // 检查最后几条日志是否包含完成标记
      const lastFewLogs = data.logs.slice(-3).join(' ')
      if (lastFewLogs.includes('数据爬取完成') || lastFewLogs.includes('数据爬取失败') || lastFewLogs.includes('爬取异常')) {
        stopLogsPolling()
        crawling.value = false
      }
    }
  } catch (error) {
    // 忽略错误
  }
}

// 清除日志
async function clearCrawlLogs() {
  try {
    await api.delete('/user/crawl/logs')
    crawlLogs.value = []
    ElMessage.success('日志已清除')
  } catch (error) {
    // 错误已处理
  }
}

async function saveSettings() {
  savingSettings.value = true
  try {
    await api.put('/user/settings', settingsForm)
    ElMessage.success({
      message: '设置已保存',
      duration: 2000
    })

    const { data } = await api.get('/auth/me')
    userStore.setUserInfo(data)
  } catch (error) {
    // 错误已处理
  } finally {
    savingSettings.value = false
  }
}

async function testPushPlus() {
  if (!settingsForm.pushplus_token) {
    ElMessage.warning('请先配置PushPlus Token')
    return
  }

  testingPush.value = true
  try {
    await api.put('/user/settings', { pushplus_token: settingsForm.pushplus_token })
    await api.post('/user/test-push')
    ElMessage.success({
      message: '测试消息已发送，请检查微信',
      duration: 3000
    })
  } catch (error) {
    // 错误已处理
  } finally {
    testingPush.value = false
  }
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)

  // 从后端获取最新的用户信息
  try {
    const { data } = await api.get('/auth/me')
    userStore.setUserInfo(data)
    settingsForm.pushplus_token = data.pushplus_token || ''
    settingsForm.balance_threshold = data.balance_threshold || 50
    settingsForm.water_balance_threshold = data.water_balance_threshold || 30
  } catch (error) {
    // 如果获取失败，使用 localStorage 中的数据
    settingsForm.pushplus_token = userStore.userInfo?.pushplus_token || ''
    settingsForm.balance_threshold = userStore.userInfo?.balance_threshold || 50
    settingsForm.water_balance_threshold = userStore.userInfo?.water_balance_threshold || 30
  }

  if (hasCredential.value) {
    api.get('/user/credentials').then(res => {
      credentialForm.pms_account = res.data.pms_account
    }).catch(() => {})
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  stopLogsPolling()
})
</script>

<style scoped>
.settings-page {
  max-width: 1200px;
}

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-5);
  margin-bottom: var(--space-5);
}

@media (min-width: 768px) {
  .settings-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Settings Card */
.settings-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  border-bottom: 1px solid var(--border-light);
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.credential-icon {
  background: var(--primary-alpha);
  color: var(--primary);
}

.notification-icon {
  background: var(--warning-alpha);
  color: var(--warning);
}

.account-icon {
  background: var(--success-alpha);
  color: var(--success);
}

.header-text {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.status-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.status-badge.success {
  background: var(--success-alpha);
  color: var(--success);
}

.status-badge.warning {
  background: var(--warning-alpha);
  color: var(--warning);
}

.card-body {
  padding: var(--space-6);
}

/* Settings Form */
.settings-form :deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--space-4);
  color: var(--text-muted);
  font-size: 18px;
  z-index: 1;
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 44px;
}

.input-wrapper :deep(.el-input__inner) {
  font-size: 15px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
  font-size: 13px;
  color: var(--text-secondary);
}

.form-tip .el-icon {
  color: var(--primary);
  font-size: 14px;
}

.form-tip .link {
  color: var(--primary);
  font-weight: 500;
  text-decoration: none;
}

.form-tip .link:hover {
  text-decoration: underline;
}

.threshold-input {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.threshold-input :deep(.el-input-number) {
  width: 150px;
}

.threshold-input .unit {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-white);
  border-color: var(--primary-light);
  color: var(--primary);
}

.btn-danger {
  background: var(--bg-secondary);
  color: var(--danger);
  border: 1px solid var(--danger-light);
}

.btn-danger:hover:not(:disabled) {
  background: var(--danger-alpha);
  border-color: var(--danger);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Info Card */
.info-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-5);
  padding: var(--space-6);
}

@media (min-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  color: var(--text-secondary);
}

.info-label .el-icon {
  color: var(--primary);
}

.info-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.tag.success {
  background: var(--success-alpha);
  color: var(--success);
}

.tag.warning {
  background: var(--warning-alpha);
  color: var(--warning);
}

.tag.default {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

/* Crawl Logs */
.crawl-logs {
  margin-top: var(--space-5);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  overflow: hidden;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-white);
  border-bottom: 1px solid var(--border);
}

.logs-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.logs-title .el-icon {
  color: var(--primary);
}

.btn-clear {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  background: transparent;
  border: none;
  border-radius: var(--radius);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-clear:hover:not(:disabled) {
  background: var(--danger-alpha);
  color: var(--danger);
}

.btn-clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.logs-content {
  padding: var(--space-3) var(--space-4);
  max-height: 300px;
  overflow-y: auto;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  padding: var(--space-1) 0;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.log-success {
  color: var(--success);
}

.log-error {
  color: var(--danger);
}

.log-warning {
  color: var(--warning);
}

.log-loading {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) 0;
  color: var(--primary);
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .card-header {
    flex-wrap: wrap;
    gap: var(--space-3);
  }

  .header-icon {
    width: 48px;
    height: 48px;
  }

  .status-badge {
    margin-left: auto;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .logs-content {
    max-height: 200px;
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .form-actions {
    flex-wrap: wrap;
  }

  .form-actions .btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>
