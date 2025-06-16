<template>
  <div class="profile-page">
    <!-- 顶部导航 -->
    <nav class="navbar">
      <router-link to="/home" class="nav-back">
        <i class="bi bi-arrow-left"></i>
        <span>Back</span>
      </router-link>
      <div class="nav-title">My Profile</div>
      <button class="logout-btn" @click="handleLogout">
        <i class="bi bi-box-arrow-right"></i>
        <span>Logout</span>
      </button>
    </nav>

    <div class="profile-content">
      <!-- 个人信息卡片 -->
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <img :src="user.avatar || '/default-avatar.png'" :alt="authStore.currentUser?.username">
            <button class="change-avatar-btn">
              <i class="bi bi-camera"></i>
            </button>
          </div>
          <h1>{{ authStore.currentUser?.username }}</h1>
          <p class="student-id">Student ID: {{ authStore.currentUser?.student_id }}</p>
        </div>
      </div>

      <!-- 我的社团 -->
      <div class="section-card">
        <div class="section-header">
          <h2>My Clubs</h2>
          <span class="club-count">{{ user.clubs.length }} clubs joined</span>
        </div>
        <div class="clubs-grid">
          <div v-for="club in user.clubs" :key="club.id" class="club-item">
            <!--<img :src="club.image" :alt="club.name">-->
            <div class="club-info">
              <h3>{{ club.name }}</h3>
              <p class="join-date">Member since {{ club.joinDate }}</p>
              <router-link :to="`/club/${club.id}`" class="view-btn">
                View Details
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 账户设置 -->
      <div class="section-card">
        <div class="section-header">
          <h2>Account Settings</h2>
        </div>
        <form @submit.prevent="updateProfile" class="settings-form">
          <div class="form-group">
            <label>Username</label>
            <input 
              v-model="form.username" 
              type="text" 
              placeholder="Your username"
            >
          </div>
          <div class="form-group">
            <label>Email</label>
            <input 
              v-model="form.email" 
              type="email" 
              placeholder="Your email"
            >
          </div>
          <div class="form-group">
            <label>New Password</label>
            <input 
              v-model="form.newPassword" 
              type="password" 
              placeholder="Enter new password"
            >
          </div>
          <button type="submit" class="save-btn">
            <i class="bi bi-check2"></i>
            Save Changes
          </button>
        </form>
      </div>

      <!-- 活动历史 -->
      <div class="section-card">
        <div class="section-header">
          <h2>Activity History</h2>
        </div>
        <div class="activity-timeline">
          <div v-for="activity in user.activities" 
               :key="activity.id" 
               class="activity-item"
          >
            <div class="activity-icon">
              <i :class="activity.icon"></i>
            </div>
            <div class="activity-content">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
              <span class="activity-date">{{ activity.date }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()

// 示例用户数据
const user = ref({
  avatar: '/images/avatar.jpg',
  clubs: [
    {
      id: 1,
      name: 'Basketball Club',
      //image: '/images/basketball.jpg',
      joinDate: '2024-01-15'
    },
    // 更多社团...
  ],
  activities: [
    {
      id: 1,
      icon: 'fas fa-user-plus',
      title: 'Joined Basketball Club',
      description: 'Became a member of the Basketball Club',
      date: '2024-01-15'
    },
    // 更多活动...
  ]
})

// Initialize form with empty values
const form = reactive({
  username: authStore.currentUser?.username || '',
  email: authStore.currentUser?.email || '',
  newPassword: ''
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  router.push('/login')
}

const updateProfile = async () => {
  try {
    console.log('Starting profile update with form data:', form);
    
    const updateData = {
      user: {
        username: form.username,
        email: form.email
      }
    }
    
    // Only include password in update if it's provided
    if (form.newPassword) {
      updateData.user.password = form.newPassword
    }
    
    console.log('Prepared update data:', updateData);

    // Check if token exists
    if (!authStore.token) {
      console.error('No auth token found');
      alert('You are not logged in. Please log in again.')
      router.push('/login')
      return
    }

    const headers = {
      'Authorization': `Token ${authStore.token}`,
      'Content-Type': 'application/json'
    }

    // Use the database ID directly from the auth store
    const studentId = authStore.currentUser?.id
    if (!studentId) {
      console.error('Student ID not found in auth store:', authStore.currentUser);
      throw new Error('Student ID not found')
    }
    
    console.log(`Updating profile for student ID: ${studentId}`);

    // Update directly with the database ID
    console.log(`Sending PATCH request to /api/students/${studentId}/`);
    const updateResponse = await axios.patch(`/api/students/${studentId}/`, updateData, {
      headers
    })

    console.log('Profile update response:', updateResponse.data);
    
    if (updateResponse.data) {
      // Update the auth store with new user data
      authStore.updateUser({
        username: form.username,
        email: form.email
      })

      // Clear password field after update
      form.newPassword = ''

      // Show success message
      alert('Profile updated successfully!')
    }
  } catch (error) {
    console.error('Failed to update profile:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
      console.error('Error status:', error.response.status)
    }
    
    if (error.response?.status === 401) {
      alert('Session expired. Please login again.')
      await authStore.logout()
      router.push('/login')
    } else {
      alert(error.response?.data?.error || error.message || 'Failed to update profile')
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f3f4f6;
  width: 100vw;
  overflow-x: hidden;
}

.navbar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-back, .logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-back:hover, .logout-btn:hover {
  background: #f3f4f6;
}

.nav-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.profile-content {
  width: 100%;
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  gap: 2rem;
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 1.5rem;
}

.avatar-wrapper img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #4338ca;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.change-avatar-btn:hover {
  transform: scale(1.1);
}

.section-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #111827;
  margin: 0;
}

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.club-item {
  background: #f8f9fa;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.club-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.club-item img {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.club-info {
  padding: 1.5rem;
}

.club-info h3 {
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.join-date {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.view-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #4338ca;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.3s;
}

.view-btn:hover {
  background: #4f46e5;
}

.settings-form {
  display: grid;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4b5563;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.3s;
}

.form-group input:focus {
  border-color: #4338ca;
  outline: none;
  box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.1);
}

.save-btn {
  justify-self: end;
  padding: 0.75rem 1.5rem;
  background: #4338ca;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.save-btn:hover {
  background: #4f46e5;
}

.activity-timeline {
  display: grid;
  gap: 1.5rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: #eef2ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4338ca;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 0.25rem 0;
  color: #111827;
}

.activity-content p {
  margin: 0;
  color: #6b7280;
}

.activity-date {
  display: block;
  margin-top: 0.5rem;
  color: #9ca3af;
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .profile-content {
    padding: 1rem;
    width: 100%;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .clubs-grid {
    grid-template-columns: 1fr;
  }
}
</style> 