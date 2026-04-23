<template>
  <div class="layout">
    <!-- Mobile Overlay -->
    <transition name="fade">
      <div class="mobile-overlay" v-show="isMobile && !isCollapse" @click="isCollapse = true"></div>
    </transition>

    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': isCollapse, 'sidebar-mobile': isMobile }">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <el-icon :size="24"><Money /></el-icon>
          </div>
          <span class="logo-text" v-show="!isCollapse">青航人才公寓</span>
        </div>
        <button class="sidebar-close" v-if="isMobile" @click="isCollapse = true">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: currentRoute === item.path }"
          @click="handleMenuSelect"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span class="nav-text" v-show="!isCollapse">{{ item.title }}</span>
          <div class="nav-indicator" v-show="!isCollapse && currentRoute === item.path"></div>
        </router-link>
      </nav>

      <div class="sidebar-footer" v-show="!isCollapse">
        <div class="version">v1.0.0</div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <button class="menu-toggle" @click="toggleMenu">
            <el-icon :size="20">
              <Fold v-if="!isCollapse && !isMobile" />
              <Expand v-else />
            </el-icon>
          </button>
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>

        <div class="header-right">
          <!-- 水电费切换按钮 -->
          <div class="type-switch" v-if="showTypeSwitch">
            <button
              class="switch-btn"
              :class="{ active: dataStore.dataType === 'electricity' }"
              @click="setData('electricity')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
              <span v-if="!isMobile">电费</span>
            </button>
            <button
              class="switch-btn"
              :class="{ active: dataStore.dataType === 'water' }"
              @click="setData('water')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
              </svg>
              <span v-if="!isMobile">水费</span>
            </button>
          </div>

          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-menu">
              <div class="user-avatar">
                <el-icon :size="18"><User /></el-icon>
              </div>
              <span class="user-name" v-if="!isMobile">{{ userStore.userInfo?.username }}</span>
              <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown">
                <el-dropdown-item command="logout" class="logout-item">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Page Content -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useDataStore } from '@/stores/data'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const dataStore = useDataStore()

const isMobile = ref(false)
const isCollapse = ref(false)

const menuItems = [
  { path: '/', title: '仪表盘', icon: 'HomeFilled' },
  { path: '/details', title: '余额明细', icon: 'Document' },
  { path: '/energy', title: '能耗记录', icon: 'TrendCharts' },
  { path: '/settings', title: '系统设置', icon: 'Setting' }
]

const currentRoute = computed(() => route.path)
const currentPageTitle = computed(() => {
  const item = menuItems.find(item => item.path === route.path)
  return item?.title || '仪表盘'
})

// 只在仪表盘、明细、能耗页面显示切换按钮
const showTypeSwitch = computed(() => {
  return ['/', '/details', '/energy'].includes(route.path)
})

function setData(type) {
  dataStore.setDataType(type)
  // 触发数据重新加载
  dataStore.fetchAllData()
}

function checkMobile() {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    isCollapse.value = false
  } else {
    isCollapse.value = true
  }
}

function toggleMenu() {
  isCollapse.value = !isCollapse.value
}

function handleMenuSelect() {
  if (isMobile.value) {
    isCollapse.value = true
  }
}

function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: var(--bg-white);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: transform var(--transition), width var(--transition);
}

.sidebar-collapsed {
  width: 72px;
}

.sidebar-mobile {
  box-shadow: var(--shadow-xl);
}

.sidebar-mobile.sidebar-collapsed {
  transform: translateX(-100%);
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 99;
}

/* Sidebar Header */
.sidebar-header {
  padding: var(--space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-light);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--gradient-primary);
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.sidebar-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.sidebar-close:hover {
  background: var(--danger-alpha);
  color: var(--danger);
}

/* Sidebar Navigation */
.sidebar-nav {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--primary-alpha);
  color: var(--primary);
}

.nav-item.active {
  background: var(--primary-alpha);
  color: var(--primary);
  font-weight: 600;
}

.nav-text {
  font-size: 14px;
  white-space: nowrap;
}

.nav-indicator {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.version {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
}

/* Main Content */
.main {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left var(--transition);
}

.sidebar-collapsed + .main,
.main:has(+ .sidebar-collapsed) {
  margin-left: 72px;
}

/* Header */
.header {
  height: 70px;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.menu-toggle {
  width: 40px;
  height: 40px;
  border: none;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.menu-toggle:hover {
  background: var(--primary-alpha);
  color: var(--primary);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

/* Type Switch */
.type-switch {
  display: flex;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  padding: 3px;
  gap: 2px;
}

.switch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.switch-btn:hover {
  color: var(--text-primary);
}

.switch-btn.active {
  background: var(--bg-white);
  color: var(--primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-menu:hover {
  background: var(--bg-secondary);
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  color: var(--text-muted);
  font-size: 12px;
}

/* Content */
.content {
  flex: 1;
  padding: var(--space-6);
  background: var(--bg-primary);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* User Dropdown */
:deep(.user-dropdown) {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2);
}

:deep(.logout-item) {
  border-radius: var(--radius);
  padding: var(--space-3) var(--space-4);
  color: var(--danger);
}

:deep(.logout-item:hover) {
  background: var(--danger-alpha);
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    width: 280px;
  }

  .main {
    margin-left: 0 !important;
  }

  .header {
    padding: 0 var(--space-4);
  }

  .page-title {
    font-size: 18px;
  }

  .content {
    padding: var(--space-4);
  }
}
</style>
