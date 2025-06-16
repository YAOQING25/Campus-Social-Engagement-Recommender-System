<template>
  <div class="recommended-page">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-left">
        <i class="bi bi-boxes"></i>
        <span>CSE</span>
      </div>
      <div class="nav-right">
        <router-link to="/home" class="nav-link">
          <i class="bi bi-house"></i>
          <span>Home</span>
        </router-link>
        <router-link to="/recommended" class="nav-link">
          <i class="bi bi-lightning"></i>
          <span>Recommended</span>
        </router-link>
        <router-link to="/favorites" class="nav-link">
          <i class="bi bi-bookmark"></i>
          <span>Favorites</span>
        </router-link>
        <router-link to="/profile" class="nav-link">
          <i class="bi bi-person"></i>
          <span>My Profile</span>
        </router-link>
        <a @click="handleLogout" class="nav-link">
          <i class="bi bi-box-arrow-right"></i>
          <span>Logout</span>
        </a>
      </div>
    </nav>
    
    <!-- 内容区域 -->
    <div class="content">
      <!-- Loading indicator -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>Loading recommendations...</p>
      </div>
      
      <!-- Error message -->
      <div v-else-if="error" class="error-container">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="retryFetchRecommendations" class="retry-btn">
          <i class="bi bi-arrow-clockwise"></i> Retry
        </button>
      </div>
      
      <div v-else>
        <!-- 推荐社团列表 -->
        <div class="section">
          <div class="section-header">
            <h2><i class="bi bi-lightning"></i> Recommended For You</h2>
            <p class="recommendation-explanation">Clubs that match your interests and activities</p>
          </div>
          <div v-if="recommendedClubs.length === 0" class="empty-state">
            <i class="bi bi-exclamation-circle"></i>
            <p>No recommendations available yet. </p>
          </div>
          <div v-else class="clubs-grid">
            <div v-for="club in recommendedClubs" 
                 :key="club.id" 
                 class="club-card"
                 @click="goToDetail(club.id)"
            >
              <div class="card-header">
                <!--<img :src="club.image || '/images/default-club.jpg'" :alt="club.name">-->
                <div class="card-bg" :style="{ backgroundColor: getColorFromString(club.name) }">
                  <span class="club-name-bg">{{ club.name.charAt(0) }}</span>
                </div>
                <div class="card-overlay">
                  <span class="recommend-badge">
                    <i class="bi bi-lightning"></i> Recommended
                  </span>
                </div>
              </div>
              <div class="card-body">
                <h3>{{ club.name }}</h3>
                <p class="club-category">{{ club.category }}</p>

                <div class="card-stats">
                  <div class="stat">
                    <i class="bi bi-people"></i>
                    <span>{{ club.memberCount || 0 }} members</span>
                  </div>
                  <!--<div class="stat">
                    <i class="bi bi-star-fill"></i>
                    <span>{{ club.rating || '0.0' }}/5.0</span>
                  </div>-->
                </div>
                <button class="join-btn" @click.stop="handleJoin(club)" :disabled="joinInProgress">
                  <span v-if="joinInProgress && joiningClubId === club.id">
                    <i class="bi bi-hourglass"></i> Processing...
                  </span>
                  <span v-else>
                    {{ club.isJoined ? 'Joined' : 'Join Now' }}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const recommendedClubs = ref([])
const error = ref(null)
const joinInProgress = ref(false)
const joiningClubId = ref(null)

// 随机颜色生成器 - 基于俱乐部名称生成一致的颜色
function getColorFromString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 80%)`;
}

// Fetch recommendations from API
const fetchRecommendations = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Get user token
    const token = localStorage.getItem('token')
    
    if (!token) {
      router.push('/login')
      return
    }
    
    const config = {
      headers: {
        'Authorization': `Token ${token}`
      }
    }
    
    // Fetch hybrid recommendations
    const response = await axios.get('/api/recommender/recommend/', config)
    
    if (!response.data || response.data.length === 0) {
      console.info('No recommendations received from API')
    } else {
      console.info(`Received ${response.data.length} recommendations`)
    }
    
    // Process recommendations
    recommendedClubs.value = processClubs(response.data || [])
    
  } catch (err) {
    console.error('Error fetching recommendations:', err)
    
    if (err.response) {
      // 处理不同的HTTP错误代码
      if (err.response.status === 401) {
        error.value = 'Your session has expired. Please login again.'
        setTimeout(() => router.push('/login'), 2000)
      } else if (err.response.status === 404) {
        error.value = 'Recommendation service not available.'
      } else {
        error.value = `Server error: ${err.response.status} ${err.response.statusText}`
      }
    } else if (err.request) {
      error.value = 'Unable to reach the recommendation server. Please check your connection.'
    } else {
      error.value = err.message || 'Failed to load recommendations'
    }
  } finally {
    loading.value = false
  }
}

const retryFetchRecommendations = () => {
  error.value = null
  fetchRecommendations()
}

// Process club data
const processClubs = (clubs) => {
  return clubs.map(club => {
    // 提取键以确保我们有所有需要的数据
    const { 
      id, 
      name, 
      category = 'General',
      description = '',
      score = 0,
      recommendation_type = 'hybrid',
      member_count = 0,
      is_member = false,
      // 其他可能的字段
      club_name,  // 后端可能返回club_name而不是name
      club_category, // 后端可能返回club_category而不是category
    } = club
    
    return {
      id: id,
      name: name || club_name || 'Unknown Club',
      category: category || club_category || 'General',
      description: description || '',
      memberCount: member_count || 0,
      score: score,
      recommendationType: recommendation_type,
      image: club.banner_image || null,
      isJoined: is_member || false
    }
  })
}

const goToDetail = (clubId) => {
  router.push(`/club/${clubId}`)
}

const handleJoin = async (club) => {
  // 如果正在处理其他加入请求，不允许新的请求
  if (joinInProgress.value) {
    return
  }
  
  joinInProgress.value = true
  joiningClubId.value = club.id
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    
    // 暂时更新UI以提供即时反馈
    club.isJoined = !club.isJoined
    
    // 准备请求配置
    const config = {
      headers: {
        'Authorization': `Token ${token}`
      }
    }
    
    // 记录交互
    await axios.post('/api/interactions/', {
      club: club.id,
      interaction_type: club.isJoined ? 'join' : 'leave'
    }, config)
    
    // 刷新推荐（使用await等待完成）
    setTimeout(async () => {
      try {
        await fetchRecommendations()
      } finally {
        joinInProgress.value = false
        joiningClubId.value = null
      }
    }, 500)
    
  } catch (err) {
    console.error('Error handling join:', err)
    // 发生错误时恢复UI
    club.isJoined = !club.isJoined
    joinInProgress.value = false
    joiningClubId.value = null
    
    // 向用户显示错误
    if (err.response && err.response.data) {
      error.value = err.response.data.error || 'Failed to join club. Please try again.'
    } else {
      error.value = 'Failed to join club. Please check your connection.'
    }
    
    // 3秒后清除错误消息
    setTimeout(() => {
      if (error.value && error.value.includes('Failed to join club')) {
        error.value = null
      }
    }, 3000)
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  router.push('/login')
}

// Fetch data on component mount
onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped>
.recommended-page {
  min-height: 100vh;
  width: 100vw;
  background: #f3f4f6;
  overflow-x: hidden;
}

/* 导航栏样式与主页保持一致 */
.navbar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: #4338ca;
}

.nav-left i {
  font-size: 1.5rem;
  color: #4338ca;
}

.nav-right {
  display: flex;
  gap: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #4338ca;
}

.nav-link.router-link-active {
  color: #4338ca;
  background: #eef2ff;
}

/* 内容区域样式 */
.content {
  width: 100%;
  padding: 2rem;
}

.recommendation-explanation {
  color: #6b7280;
  margin-top: 0.25rem;
  font-size: 0.875rem;
}

.section {
  margin-bottom: 3rem;
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-header {
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 1.5rem;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.section-header i {
  font-size: 1.25rem;
}

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.club-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e5e7eb;
}

.club-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  position: relative;
  height: 160px;
}

.card-bg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.club-name-bg {
  font-size: 4rem;
  font-weight: bold;
  opacity: 0.7;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-header img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
}

.recommend-badge {
  background: #4338ca;
  color: white;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-body {
  padding: 1rem;
  position: relative;
}

.card-body h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.125rem;
  color: #111827;
}

.score-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.score-badge i {
  color: #f59e0b;
}

.club-category {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0 0 0.75rem 0;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.stat i {
  color: #4338ca;
}

.join-btn {
  width: 100%;
  padding: 0.5rem;
  background: #4338ca;
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.join-btn:hover:not(:disabled) {
  background: #3730a3;
}

.join-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

/* Loading styles */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(67, 56, 202, 0.1);
  border-left-color: #4338ca;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error container */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background: #fee2e2;
  border-radius: 8px;
  color: #b91c1c;
  text-align: center;
}

.error-container i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #b91c1c;
  border: 1px solid #b91c1c;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: #fee2e2;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  color: #6b7280;
  text-align: center;
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: #9ca3af;
}
</style> 