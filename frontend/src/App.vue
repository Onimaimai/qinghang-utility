<template>
  <el-config-provider :locale="zhCn">
    <router-view v-slot="{ Component }">
      <transition name="fade-slide" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </el-config-provider>
</template>

<script setup>
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
/* CSS Variables - Modern Color System */
:root {
  /* Primary - Black */
  --primary: #000000;
  --primary-light: #333333;
  --primary-dark: #000000;
  --primary-alpha: rgba(0, 0, 0, 0.08);

  /* Success - Emerald */
  --success: #10b981;
  --success-light: #34d399;
  --success-alpha: rgba(16, 185, 129, 0.1);

  /* Warning - Amber */
  --warning: #f59e0b;
  --warning-light: #fbbf24;
  --warning-alpha: rgba(245, 158, 11, 0.1);

  /* Danger - Rose */
  --danger: #ef4444;
  --danger-light: #f87171;
  --danger-alpha: rgba(239, 68, 68, 0.1);

  /* Neutral Colors */
  --bg-primary: #f1f5f9;
  --bg-secondary: #f8fafc;
  --bg-white: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border: #e2e8f0;
  --border-light: #f1f5f9;

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
  --gradient-success: linear-gradient(135deg, #10b981 0%, #059669 100%);
  --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  --gradient-card: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  --gradient-glass: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  --shadow-glow: 0 0 20px rgba(0, 0, 0, 0.15);

  /* Border Radius */
  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition: 300ms ease;
  --transition-slow: 500ms ease;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
}

/* Reset & Base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
               'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* Element Plus Overrides */
.el-card {
  border-radius: var(--radius-lg) !important;
  border: none !important;
  box-shadow: var(--shadow) !important;
  background: var(--bg-white) !important;
  transition: transform var(--transition), box-shadow var(--transition) !important;
}

.el-card:hover {
  box-shadow: var(--shadow-md) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--border-light) !important;
  padding: var(--space-5) var(--space-6) !important;
  font-weight: 600;
  color: var(--text-primary);
}

.el-card__body {
  padding: var(--space-6) !important;
}

/* Button Modernization */
.el-button {
  border-radius: var(--radius) !important;
  font-weight: 500 !important;
  transition: all var(--transition-fast) !important;
}

.el-button--primary {
  background: var(--gradient-primary) !important;
  border: none !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15) !important;
}

.el-button--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.2) !important;
}

.el-button--success {
  background: var(--gradient-success) !important;
  border: none !important;
}

.el-button--danger {
  background: var(--gradient-warning) !important;
  border: none !important;
}

/* Input Modernization */
.el-input__wrapper {
  border-radius: var(--radius) !important;
  box-shadow: 0 0 0 1px var(--border) inset !important;
  transition: all var(--transition-fast) !important;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--primary-light) inset !important;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px var(--primary-alpha) !important;
}

/* Table Modernization */
.el-table {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.el-table th {
  background-color: var(--bg-secondary) !important;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
}

.el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: var(--bg-secondary) !important;
}

.el-table__row:hover td {
  background-color: var(--primary-alpha) !important;
}

/* Menu Modernization */
.el-menu {
  border-right: none !important;
  background: transparent !important;
}

.el-menu-item {
  border-radius: var(--radius);
  margin: 4px 12px;
  height: 44px;
  line-height: 44px;
  transition: all var(--transition-fast) !important;
}

.el-menu-item:hover {
  background-color: var(--primary-alpha) !important;
  color: var(--primary) !important;
}

.el-menu-item.is-active {
  background-color: var(--primary-alpha) !important;
  color: var(--primary) !important;
  font-weight: 600;
}

/* Form Modernization */
.el-form-item__label {
  font-weight: 500;
  color: var(--text-secondary);
}

/* Empty State */
.el-empty {
  padding: var(--space-10) 0;
}

.el-empty__description {
  color: var(--text-muted);
  margin-top: var(--space-4);
}

/* Tag Modernization */
.el-tag {
  border-radius: var(--radius-full) !important;
  font-weight: 500;
  padding: 0 12px;
  height: 26px;
  line-height: 24px;
}

.el-tag--success {
  background-color: var(--success-alpha) !important;
  border-color: var(--success-light) !important;
  color: var(--success) !important;
}

.el-tag--warning {
  background-color: var(--warning-alpha) !important;
  border-color: var(--warning-light) !important;
  color: var(--warning) !important;
}

.el-tag--danger {
  background-color: var(--danger-alpha) !important;
  border-color: var(--danger-light) !important;
  color: var(--danger) !important;
}

/* Page Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all var(--transition);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* Utility Classes */
.glass {
  background: var(--gradient-glass);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.text-gradient {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-hover {
  transition: transform var(--transition), box-shadow var(--transition);
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
</style>
