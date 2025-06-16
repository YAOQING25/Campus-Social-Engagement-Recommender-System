<template>
  <div class="profile-dropdown" v-click-outside="closeDropdown">
    <button class="profile-btn" @click="toggleDropdown">
      <div class="avatar">
        <i class="bi bi-person-circle"></i>
      </div>
      <span class="name">{{ adminName }}</span>
      <i class="bi bi-chevron-down"></i>
    </button>

    <div class="dropdown-menu" v-show="isOpen">
      <div class="dropdown-header">
        <div class="avatar">
          <i class="bi bi-person-circle"></i>
        </div>
        <div class="info">
          <div class="name">{{ adminName }}</div>
          <div class="email">{{ adminEmail }}</div>
        </div>
      </div>
      <div class="dropdown-divider"></div>
      <router-link class="dropdown-item" to="/admin/profile">
        <i class="bi bi-person"></i>
        Profile
      </router-link>
      <router-link class="dropdown-item" to="/admin/home">
        <i class="bi bi-speedometer2"></i>
        Dashboard
      </router-link>
      <div class="dropdown-divider"></div>
      <a class="dropdown-item logout" href="#" @click.prevent="handleLogout">
        <i class="bi bi-box-arrow-right"></i>
        Logout
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUser, clearAuth } from '@/utils/auth'
import axios from 'axios'

const router = useRouter()
const isOpen = ref(false)
const adminData = ref(null)

const adminName = computed(() => {
  if (adminData.value && adminData.value.name) {
    return adminData.value.name
  }
  return 'Admin'
})

const adminEmail = computed(() => {
  if (adminData.value && adminData.value.email) {
    return adminData.value.email
  }
  return 'admin@example.com'
})

// Toggle dropdown
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

// Close dropdown
const closeDropdown = () => {
  isOpen.value = false
}

// Handle logout
const handleLogout = async () => {
  try {
    clearAuth()
    router.push('/admin/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

// Load admin data
const loadAdminData = () => {
  const user = getUser()
  if (user) {
    adminData.value = user
  }
}

// Initialize on component mount
onMounted(() => {
  loadAdminData()
})

// Click outside directive
const vClickOutside = {
  mounted(el, { value }) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.profile-dropdown {
  position: relative;
}

.profile-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: none;
  border: none;
  color: #030303;
  cursor: pointer;
  transition: all 0.2s;
}

.profile-btn:hover {
  color: #fff;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #4338ca;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar i {
  font-size: 1.25rem;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  width: 240px;
  background: #2d3748;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 50;
}

.dropdown-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info .name {
  font-weight: 500;
  color: #e2e8f0;
}

.info .email {
  font-size: 0.875rem;
  color: #94a3b8;
}

.dropdown-divider {
  height: 1px;
  background: #4a5568;
  margin: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #e2e8f0;
  text-decoration: none;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background: #374151;
}

.dropdown-item.logout {
  color: #ef4444;
}

.dropdown-item.logout:hover {
  background: #991b1b;
  color: #fca5a5;
}

@media (max-width: 768px) {
  .name {
    display: none;
  }
}
</style> 