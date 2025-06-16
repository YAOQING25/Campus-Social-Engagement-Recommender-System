<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo">
        <i class="bi bi-boxes"></i>
        <span>CSE Admin</span>
      </div>
      <nav class="nav-menu">
        <router-link to="/admin/home" class="nav-item">
          <i class="bi bi-house"></i>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/admin/students" class="nav-item">
          <i class="bi bi-people"></i>
          <span>Students</span>
        </router-link>
        <router-link to="/admin/clubs" class="nav-item">
          <i class="bi bi-collection"></i>
          <span>Clubs</span>
        </router-link>
        <router-link to="/admin/categories" class="nav-item">
          <i class="bi bi-tags"></i>
          <span>Categories</span>
        </router-link>
        <router-link to="/admin/applications" class="nav-item">
          <i class="bi bi-file-text"></i>
          <span>Applications</span>
        </router-link>
        <router-link to="/admin/admins" class="nav-item">
          <i class="bi bi-shield"></i>
          <span>Admins</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">
          <i class="bi bi-box-arrow-right"></i>
          <span>Logout</span>
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/admin/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  overflow-x: hidden;
  background: #f3f4f6;
}

.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 50;
}

.logo {
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #4338ca;
  border-bottom: 1px solid #e5e7eb;
}

.logo i {
  font-size: 1.5rem;
}

.nav-menu {
  padding: 1.5rem 1rem;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.nav-item:hover {
  background: #f3f4f6;
  color: #4338ca;
}

.nav-item.router-link-active {
  background: #eef2ff;
  color: #4338ca;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fee2e2;
  color: #ef4444;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: #fecaca;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 2rem;
  min-height: 100vh;
  width: calc(100vw - 260px);
}

@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }

  .logo span,
  .nav-item span,
  .logout-btn span {
    display: none;
  }

  .main-content {
    margin-left: 80px;
  }
}
</style> 