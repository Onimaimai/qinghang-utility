<template>
  <div class="register-page">
    <!-- Background Elements -->
    <div class="bg-gradient"></div>
    <div class="bg-pattern">
      <div class="pattern-dot"></div>
      <div class="pattern-dot"></div>
      <div class="pattern-dot"></div>
      <div class="pattern-ring"></div>
      <div class="pattern-ring"></div>
    </div>

    <!-- Register Card -->
    <div class="register-container">
      <div class="brand">
        <div class="brand-icon">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <h1 class="brand-title">青航人才公寓</h1>
        <p class="brand-subtitle">水电费查询面板</p>
      </div>

      <div class="register-card">
        <h2 class="card-title">创建账号</h2>
        <p class="card-subtitle">开始管理您的水电费用</p>

        <el-form :model="form" :rules="rules" ref="formRef" class="register-form">
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="form.username"
                placeholder="用户名"
                size="large"
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                size="large"
                show-password
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="input-wrapper">
              <el-icon class="input-icon"><CircleCheck /></el-icon>
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                show-password
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>

          <el-form-item>
            <button
              type="button"
              class="register-btn"
              :class="{ loading: loading }"
              :disabled="loading"
              @click="handleRegister"
            >
              <span class="btn-text">{{ loading ? '注册中...' : '注册' }}</span>
              <el-icon class="btn-icon" v-if="!loading"><ArrowRight /></el-icon>
              <el-icon class="btn-loading" v-else><Loading /></el-icon>
            </button>
          </el-form-item>
        </el-form>

        <div class="login-link">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await api.post('/auth/register', {
      username: form.username,
      password: form.password
    })

    ElMessage.success({
      message: '注册成功，请登录',
      duration: 2000
    })
    router.push('/login')
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-primary);
}

/* Background */
.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  opacity: 0.1;
}

.bg-pattern {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.pattern-dot {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: var(--gradient-primary);
  opacity: 0.05;
  filter: blur(60px);
}

.pattern-dot:nth-child(1) {
  top: -100px;
  right: -100px;
  width: 400px;
  height: 400px;
}

.pattern-dot:nth-child(2) {
  bottom: -150px;
  left: -150px;
  width: 500px;
  height: 500px;
  background: var(--gradient-success);
}

.pattern-dot:nth-child(3) {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600px;
  height: 600px;
  background: var(--gradient-warning);
}

.pattern-ring {
  position: absolute;
  border: 2px solid var(--primary);
  border-radius: 50%;
  opacity: 0.1;
}

.pattern-ring:nth-child(4) {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -200px;
}

.pattern-ring:nth-child(5) {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
}

/* Container */
.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: var(--space-6);
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Brand */
.brand {
  text-align: center;
  margin-bottom: var(--space-8);
}

.brand-icon {
  width: 64px;
  height: 64px;
  background: var(--gradient-primary);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin: 0 auto var(--space-4);
  box-shadow: var(--shadow-glow);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: var(--space-2);
}

.brand-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
}

/* Card */
.register-card {
  background: var(--bg-white);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-xl);
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: var(--space-2);
}

.card-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  text-align: center;
  margin-bottom: var(--space-6);
}

/* Form */
.register-form {
  margin-top: var(--space-6);
}

.register-form :deep(.el-form-item) {
  margin-bottom: var(--space-5);
}

.register-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: var(--text-muted);
  z-index: 1;
  font-size: 18px;
}

:deep(.custom-input) {
  width: 100%;
}

:deep(.custom-input .el-input__wrapper) {
  padding-left: 48px;
  height: 52px;
  border-radius: var(--radius-lg);
  background: var(--bg-secondary);
  box-shadow: none !important;
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

:deep(.custom-input .el-input__wrapper:hover) {
  background: var(--bg-white);
  border-color: var(--border);
}

:deep(.custom-input .el-input__wrapper.is-focus) {
  background: var(--bg-white);
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-alpha) !important;
}

:deep(.custom-input .el-input__inner) {
  font-size: 15px;
  color: var(--text-primary);
}

:deep(.custom-input .el-input__inner::placeholder) {
  color: var(--text-muted);
}

/* Register Button */
.register-btn {
  width: 100%;
  height: 52px;
  background: var(--gradient-success);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
  transition: all var(--transition-fast);
}

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-icon {
  transition: transform var(--transition-fast);
}

.register-btn:hover:not(:disabled) .btn-icon {
  transform: translateX(4px);
}

.btn-loading {
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

/* Login Link */
.login-link {
  text-align: center;
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--border);
  font-size: 14px;
  color: var(--text-secondary);
}

.link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  margin-left: var(--space-1);
  transition: all var(--transition-fast);
}

.link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

/* Copyright */
.copyright {
  text-align: center;
  margin-top: var(--space-8);
  font-size: 13px;
  color: var(--text-muted);
}

/* Responsive */
@media (max-width: 480px) {
  .register-container {
    padding: var(--space-4);
  }

  .register-card {
    padding: var(--space-6);
  }

  .brand-title {
    font-size: 24px;
  }

  .card-title {
    font-size: 20px;
  }
}
</style>
