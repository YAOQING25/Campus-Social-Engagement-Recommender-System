<template>
  <div class="favorite-page">
    <!-- 导航栏与主页保持一致 -->
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

    <!-- 收藏内容 -->
    <div class="content">
      <div class="section">
        <div class="section-header">
          <h2><i class="bi bi-bookmark-heart"></i> My Favorite Clubs</h2>
          <span class="count-badge">{{ favoriteClubs.length }} clubs</span>
        </div>
        
        <!-- 收藏为空时显示 -->
        <div v-if="favoriteClubs.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-bookmark-heart"></i>
          </div>
          <h3>No Favorite Clubs Yet</h3>
          <p>Start exploring and bookmark the clubs you're interested in!</p>
          <div class="action-buttons">
            <router-link to="/recommended" class="primary-btn">
              <i class="bi bi-lightning"></i>
              Discover Clubs
            </router-link>
            <router-link to="/home" class="secondary-btn">
              <i class="bi bi-house"></i>
              Back to Home
            </router-link>
          </div>
        </div>

        <!-- 收藏列表 -->
        <div v-else class="clubs-grid">
          <div v-for="club in favoriteClubs" 
               :key="club.id" 
               class="club-card"
          >
            <div class="card-header" @click="goToDetail(club.id)">
              <!--<img :src="club.image" :alt="club.name">-->
              <div class="card-bg" :style="{ backgroundColor: getColorFromString(club.name) }">
                  <span class="club-name-bg">{{ club.name.charAt(0) }}</span>
                </div>
              <div class="card-overlay">
                <span class="category-tag" :class="club.category">
                  {{ club.category }}
                </span>
              </div>
            </div>
            <div class="card-body">
              <h3 @click="goToDetail(club.id)">{{ club.name }}</h3>
              <div class="card-stats">
                <div class="stat">
                  <i class="bi bi-people"></i>
                  <span>{{ club.memberCount }} members</span>
                </div>
                <div class="stat">
                  <i class="bi bi-star-fill"></i>
                  <span>{{ club.rating }}/5.0</span>
                </div>
              </div>
              <div class="card-actions">
                <button 
                  class="join-btn"
                  :class="{ 'joined': club.isJoined }"
                  @click="handleJoin(club)"
                >
                  <i :class="club.isJoined ? 'bi bi-check2' : 'bi bi-plus'"></i>
                  {{ club.isJoined ? 'Joined' : 'Join Now' }}
                </button>
                <button 
                  class="remove-btn" 
                  @click="removeFavorite(club)"
                  title="Remove from favorites"
                >
                  <i class="bi bi-bookmark-x"></i>
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
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const favoriteClubs = ref([])

// 获取API基础URL
const baseUrl = window.location.hostname === 'localhost' 
  ? `http://${window.location.hostname}:8000` 
  : `${window.location.protocol}//${window.location.host}`

// 获取收藏的俱乐部
const fetchFavoriteClubs = async () => {
  loading.value = true
  error.value = null
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    
    const config = {
      headers: { 'Authorization': `Token ${token}` }
    }
    
    // 从API获取收藏的俱乐部
    const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
    const savedClubs = savedClubsResponse.data
    
    if (savedClubs && savedClubs.length > 0) {
      // 获取每个收藏俱乐部的详细信息
      const clubPromises = savedClubs.map(async (savedClub) => {
        try {
          const clubResponse = await axios.get(`${baseUrl}/api/clubs/${savedClub.club}/`, config)
          return {
            ...clubResponse.data,
            isFavorited: true,
            isJoined: false // 假设未加入，实际应根据用户状态确定
          }
        } catch (err) {
          console.error(`Error fetching club ${savedClub.club}:`, err)
          return null
        }
      })
      
      const clubResults = await Promise.all(clubPromises)
      favoriteClubs.value = clubResults.filter(Boolean) // 过滤掉null结果
    } else {
      favoriteClubs.value = []
    }
    
    // 备份到localStorage以提高性能
    const favoritedClubIds = favoriteClubs.value.map(club => club.id)
    localStorage.setItem('favoritedClubs', JSON.stringify(favoritedClubIds))
    
  } catch (err) {
    console.error('Error fetching favorite clubs:', err)
    error.value = 'Failed to fetch favorite clubs'
    
    // 如果API调用失败，回退到localStorage
    try {
      const favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
      if (favoritedClubIds.length > 0) {
        // 尝试使用localStorage中的ID获取俱乐部详情
        const clubPromises = favoritedClubIds.map(async (clubId) => {
          try {
            const token = localStorage.getItem('token')
            const config = token ? { headers: { 'Authorization': `Token ${token}` } } : {}
            const clubResponse = await axios.get(`${baseUrl}/api/clubs/${clubId}/`, config)
            return {
              ...clubResponse.data,
              isFavorited: true
            }
          } catch (err) {
            console.error(`Error fetching club ${clubId}:`, err)
            return null
          }
        })
        
        const clubResults = await Promise.all(clubPromises)
        favoriteClubs.value = clubResults.filter(Boolean)
      }
    } catch (localErr) {
      console.error('Error using localStorage fallback:', localErr)
    }
  } finally {
    loading.value = false
  }
}

// 处理移除收藏
const removeFavorite = async (club) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    
    const config = {
      headers: { 'Authorization': `Token ${token}` }
    }
    
    // 从UI中先移除，提供即时反馈
    const index = favoriteClubs.value.findIndex(c => c.id === club.id)
    if (index > -1) {
      favoriteClubs.value.splice(index, 1)
    }
    
    // 从API中删除收藏
    try {
      // 先获取保存的记录ID
      const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
      const savedClub = savedClubsResponse.data.find(item => item.club === club.id)
      
      if (savedClub) {
        await axios.delete(`${baseUrl}/api/saved-clubs/${savedClub.id}/`, config)
        console.log(`Club ${club.id} removed from favorites successfully`)
      }
    } catch (apiError) {
      console.error('Error removing club from API:', apiError)
      // 如果API调用失败，尝试推回到UI
      fetchFavoriteClubs() // 重新刷新以保持一致
    }
    
    // 更新localStorage
    const favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
    const updatedIds = favoritedClubIds.filter(id => id !== club.id)
    localStorage.setItem('favoritedClubs', JSON.stringify(updatedIds))
  } catch (err) {
    console.error('Error in removeFavorite:', err)
  }
}

const handleJoin = (club) => {
  // 处理加入俱乐部的逻辑（可与推荐页面相同）
  club.isJoined = !club.isJoined
}

const goToDetail = (clubId) => {
  router.push(`/club/${clubId}`)
}

const getColorFromString = (str) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  const c = (hash & 0x00FFFFFF).toString(16).toUpperCase()
  return `#${'00000'.substring(0, 6 - c.length)}${c}`
}

const handleLogout = () => {
  // 清除认证数据
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  
  // 重定向到登录页
  router.push('/login')
}

// 组件加载时获取数据
onMounted(() => {
  fetchFavoriteClubs()
})
</script>

<style scoped>
/* 导航栏样式与主页完全一致 */
.navbar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 100;
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

/* 复用主页的基础样式 */
.favorite-page {
  min-height: 100vh;
  width: 100vw;
  background: #f3f4f6;
  overflow-x: hidden;
}

.content {
  padding: 2rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  color: #111827;
}

.section-header i {
  color: #4338ca;
}

.count-badge {
  padding: 0.5rem 1rem;
  background: #eef2ff;
  color: #4338ca;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: #eef2ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon i {
  font-size: 2.5rem;
  color: #4338ca;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #111827;
  margin-bottom: 0.75rem;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 2rem;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s;
  text-decoration: none;
}

.primary-btn {
  background: linear-gradient(45deg, #4338ca, #6366f1);
  color: white;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.secondary-btn {
  background: #f3f4f6;
  color: #4b5563;
}

.secondary-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.clubs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.club-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.club-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  position: relative;
  height: 180px;
  cursor: pointer;
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
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.4));
  padding: 1rem;
}

.category-tag {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

/* 保持类别标签的渐变色样式 */
.category-tag.sports { background: linear-gradient(45deg, #ef4444, #f87171); }
/* ... 其他类别样式 ... */

.card-body {
  padding: 1.5rem;
}

.card-body h3 {
  font-size: 1.25rem;
  color: #111827;
  margin-bottom: 1rem;
  cursor: pointer;
}

.card-body h3:hover {
  color: #4338ca;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.stat i {
  color: #4338ca;
}

.card-actions {
  display: flex;
  gap: 1rem;
}

.join-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(45deg, #4338ca, #6366f1);
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.join-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.join-btn.joined {
  background: linear-gradient(45deg, #059669, #10b981);
}

.remove-btn {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: #fee2e2;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: #fecaca;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .content {
    padding: 1rem;
  }
  
  .clubs-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .nav-right a span {
    display: none;
  }
}
</style> 