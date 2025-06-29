<template>
  <div class="login-container">
    <div class="login-content">
      <h2 class="title">CSE</h2>
      <form @submit.prevent="handleLogin" class="login-form" autocomplete="off">
        <div class="form-group">
          <label>Student ID</label>
          <input
            v-model="studentId"
            type="text"
            placeholder="Enter your student ID"
            autocomplete="off"
            required
          >
        </div>
        <div class="form-group">
          <label>Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter your password"
            autocomplete="off"
            required
          >
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <div class="register-link">
          No account? <router-link to="/register">Register Now</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { prepareForLogin } from '@/utils/sessionCleaner'

const router = useRouter()
const authStore = useAuthStore()
const studentId = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// Clear any existing session data when login page loads
onMounted(() => {
  prepareForLogin()
  console.log('Login form initialized with clean session')
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    // Perform student login via auth store
    const success = await authStore.login(studentId.value, password.value, false)
    if (success) {
      // Redirect to home
      router.push({ name: 'home' })
    }
  } catch (err) {
    // Show error to user
    error.value = err.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 90%;
  max-width: 360px;
}

.title {
  text-align: center;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.login-btn:hover {
  background: #764ba2;
}

.register-link {
  text-align: center;
  margin-top: 1rem;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

.error-message {
  color: #ef4444;
  margin-bottom: 1rem;
  text-align: center;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style> 