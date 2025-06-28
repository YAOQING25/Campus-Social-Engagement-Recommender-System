<template>
  <div class="home-container">
    <!-- Navigation -->
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

    <!-- Application status message -->
    <div 
      v-if="showApplicationMessage" 
      class="application-message"
      :class="applicationStatus"
    >
      <i :class="applicationStatus === 'success' ? 'bi bi-check-circle' : 'bi bi-exclamation-circle'"></i>
      <span>{{ applicationStatus === 'success' ? 'Application submitted successfully! Please wait for admin approval.' : 'Failed to submit application. Please try again.' }}</span>
    </div>

    <!-- search section -->
    <div class="search-section">
      <div class="search-wrapper">
        <i class="bi bi-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search clubs..."
        >
      </div>
      <div class="category-wrapper">
        <select v-model="selectedCategory">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>
    </div>

    <!-- Club List -->
    <div class="clubs-grid">
      <div v-for="club in filteredClubs" 
           :key="club.id" 
           class="club-card"
           @click="goToDetail(club.id)"
      >
        <div class="card-header">
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
          <h3>{{ club.name }}</h3>
          <p>{{ club.description }}</p>
          <div class="card-stats">
            <div class="stat">
              <i class="bi bi-people"></i>
              <span>{{ club.memberCount }} members</span>
            </div>
            <!--<div class="stat">
              <i class="bi bi-star-fill"></i>
              <span>{{ club.rating }}/5.0</span>
            </div>-->
          </div>
          <div class="card-actions" @click.stop>
            <button
              class="join-btn"
              :class="{ 'joined': club.isJoined, 'applied': club.isApplied }"
              @click="toggleJoin(club)"
              :disabled="club.isApplied || club.isJoined"
            >
              <i :class="club.isJoined ? 'bi bi-check2' : club.isApplied ? 'bi bi-clock' : 'bi bi-plus'"></i>
              {{ club.isJoined ? 'Joined' : club.isApplied ? 'Applied' : 'Join Club' }}
            </button>
            <div class="action-icons">
              <button 
                class="icon-btn" 
                :class="{ 'liked': club.isLiked }"
                @click="toggleLike(club)"
              >
                <i class="bi bi-heart-fill"></i>
              </button>
              <button 
                class="icon-btn"
                :class="{ 'favorited': club.isFavorited }"
                @click="toggleFavorite(club)"
              >
                <i class="bi bi-bookmark-fill"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const searchQuery = ref('')
const selectedCategory = ref('')
const clubs = ref([])
const categories = ref([])
const loading = ref(false)
const applicationStatus = ref(null)
const showApplicationMessage = ref(false)

// Determine base API URL
const baseUrl = window.location.hostname === 'localhost'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Fetch categories from backend
const fetchCategories = async () => {
  try {
    const response = await axios.get(`${baseUrl}/api/categories/`)
    const categoriesData = response.data.results || response.data
    categories.value = categoriesData.map(category => category.name)
  } catch (error) {
    console.error('Error fetching categories:', error)
    alert('Failed to fetch categories')
  }
}

// Fetch clubs from backend
const fetchClubs = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${baseUrl}/api/clubs/`)
    const clubsData = response.data.results || response.data

    // Get favorited club IDs from API (with fallback to localStorage)
    let favoritedClubIds = []
    const token = localStorage.getItem('token')

    if (token) {
      try {
        const config = {
          headers: { 'Authorization': `Token ${token}` }
        }
        const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
        const savedClubsData = savedClubsResponse.data.results || savedClubsResponse.data
        favoritedClubIds = savedClubsData.map(savedClub => savedClub.club)
        console.log('Loaded favorite clubs from API:', favoritedClubIds)

        // Update localStorage with API data
        localStorage.setItem('favoritedClubs', JSON.stringify(favoritedClubIds))
      } catch (savedError) {
        console.error('Error fetching saved clubs:', savedError)
        // Fallback to localStorage
        favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
        console.log('Using localStorage fallback for favorites:', favoritedClubIds)
      }
    } else {
      // No token, use localStorage only
      favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
    }

    // Get application statuses from API if user is authenticated
    let applicationStatuses = {}
    let appliedClubIds = []

    if (token) {
      try {
        const config = {
          headers: { 'Authorization': `Token ${token}` }
        }
        const applicationsResponse = await axios.get(`${baseUrl}/api/applications/`, config)
        const applications = applicationsResponse.data.results || applicationsResponse.data

        // Create a map of club_id -> application_status
        applications.forEach(app => {
          applicationStatuses[app.club] = app.status
        })
        console.log('Application statuses from API:', applicationStatuses)

        // Only use localStorage as fallback for UI state, not as source of truth
        appliedClubIds = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
      } catch (error) {
        console.warn('Could not fetch application statuses:', error)
        // If API fails and user is authenticated, still try localStorage as fallback
        appliedClubIds = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
      }
    } else {
      // For unauthenticated users, don't show any applied status
      console.log('User not authenticated, showing clean state')
      appliedClubIds = []
    }

    clubs.value = clubsData.map(club => {
      // Determine application status - prioritize API data over localStorage
      const applicationStatus = applicationStatuses[club.id]
      const hasAppliedLocally = appliedClubIds.includes(club.id)

      let isApplied = false
      let isJoined = false

      // Only use API data if user is authenticated
      if (token && applicationStatus) {
        if (applicationStatus === 'approved') {
          isJoined = true
        } else if (applicationStatus === 'pending') {
          isApplied = true
        }
      } else if (token && hasAppliedLocally) {
        // Only use localStorage if authenticated and no API data
        isApplied = true
      }
      // For unauthenticated users, both remain false

      return {
        ...club,
        isApplied: isApplied,
        isJoined: isJoined,
        isLiked: false,
        isFavorited: favoritedClubIds.includes(club.id),
        applicationStatus: applicationStatus
      }
    })

    console.log('Clubs loaded with favorite status:', clubs.value.filter(c => c.isFavorited).map(c => c.name))
  } catch (error) {
    console.error('Error fetching clubs:', error)
    alert('Failed to fetch clubs')
  } finally {
    loading.value = false
  }
}

function getColorFromString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 80%)`;
}

// Load data on component mount
onMounted(() => {
  fetchCategories()
  fetchClubs()
})

const filteredClubs = computed(() => {
  return clubs.value.filter(club => {
    const matchesSearch = club.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = !selectedCategory.value || club.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const toggleJoin = async (club) => {
  if (club.isJoined || club.isApplied) {
    // If already joined or applied, do nothing
    return
  }
  
  try {
    // Get current user info from localStorage
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const token = localStorage.getItem('token')
    
    // For testing, don't require login
    /*if (!user || !user.id) {
      alert('Please log in to join a club')
      router.push('/login')
      return
    }
    
    if (!token) {
      alert('Your session has expired. Please log in again.')
      router.push('/login')
      return
    }*/
    
    // Create application data - use simplified data for testing
    const applicationData = {
      club: club.id,
      status: 'pending'
    }
    
    // For development/testing without backend
    // Just simulate the application process if API is not available
    let simulateSuccess = true
    
    try {
      // Try to submit application to backend - without auth headers for testing
      const response = await axios.post(`${baseUrl}/api/applications/`, applicationData)
      console.log('Application submitted successfully', response.data)
      
      // If successful, continue with normal flow
    } catch (apiError) {
      console.error('API Error:', apiError)
      
      // Only use simulation if it's an auth error
      if (apiError.response && apiError.response.status === 401) {
        console.log('Using simulation mode due to auth error')
        // Continue with simulation
      } else {
        // For other errors, rethrow
        throw apiError
      }
    }
    
    // Update UI - set to applied status (pending approval)
    club.isApplied = true
    club.isJoined = false
    
    // Store in localStorage that user has applied to this club
    const appliedClubs = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
    if (!appliedClubs.includes(club.id)) {
      appliedClubs.push(club.id)
      localStorage.setItem('appliedClubs', JSON.stringify(appliedClubs))
    }
    
    // Show success message
    applicationStatus.value = 'success'
    showApplicationMessage.value = true
    setTimeout(() => {
      showApplicationMessage.value = false
    }, 3000)
    
  } catch (error) {
    console.error('Error applying to club:', error)
    
    // Show error message
    applicationStatus.value = 'error'
    showApplicationMessage.value = true
    setTimeout(() => {
      showApplicationMessage.value = false
    }, 3000)
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  router.push('/login')
}

const toggleLike = (club) => {
  club.isLiked = !club.isLiked
}

const toggleFavorite = async (club) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('Please login to save clubs')
      return
    }

    const config = {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    }

    console.log('Toggling favorite for club:', club.id, 'Current status:', club.isFavorited)

    // Store original state for rollback
    const originalState = club.isFavorited

    // Temporarily update UI for immediate feedback
    club.isFavorited = !club.isFavorited

    if (club.isFavorited) {
      // Add to favorites
      console.log('Adding club to favorites...')
      const response = await axios.post(`${baseUrl}/api/saved-clubs/`, {
        club: club.id
      }, config)
      console.log('Club added to favorites successfully:', response.data)
    } else {
      // Remove from favorites (need to get saved ID first)
      console.log('Removing club from favorites...')
      const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
      console.log('Saved clubs response for removal:', savedClubsResponse.data)

      // Handle both array and paginated response formats
      const savedClubsData = savedClubsResponse.data.results || savedClubsResponse.data
      const savedClub = savedClubsData.find(item => item.club === club.id)

      if (savedClub) {
        await axios.delete(`${baseUrl}/api/saved-clubs/${savedClub.id}/`, config)
        console.log('Club removed from favorites successfully')
      } else {
        console.warn('Saved club not found in API response')
      }
    }

    // Update localStorage as backup
    const favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
    if (club.isFavorited) {
      if (!favoritedClubIds.includes(club.id)) {
        favoritedClubIds.push(club.id)
      }
    } else {
      const index = favoritedClubIds.indexOf(club.id)
      if (index > -1) {
        favoritedClubIds.splice(index, 1)
      }
    }
    localStorage.setItem('favoritedClubs', JSON.stringify(favoritedClubIds))

    // Show success message
    const message = club.isFavorited ? 'Club saved to favorites!' : 'Club removed from favorites!'
    console.log(message)

  } catch (error) {
    // If API call fails, restore UI status
    club.isFavorited = !club.isFavorited
    console.error('Error updating favorite status:', error)

    // More detailed error handling
    if (error.response) {
      console.error('Error response:', error.response.data)
      console.error('Error status:', error.response.status)

      if (error.response.status === 401) {
        alert('Session expired. Please login again.')
        router.push('/login')
      } else if (error.response.status === 400) {
        alert('Invalid request. Please try again.')
      } else {
        alert(`Failed to update favorite status: ${error.response.data.detail || error.response.data.error || 'Unknown error'}`)
      }
    } else {
      alert('Network error. Please check your connection and try again.')
    }
  }
}

const goToDetail = (clubId) => {
  router.push(`/club/${clubId}`)
}

</script>

<style scoped>
.home-container {
  min-height: 100vh;
  width: 100vw;
  background: #f3f4f6;
  overflow-x: hidden;
}

/* Application message */
.application-message {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1000;
  animation: slideDown 0.3s ease-out;
}

.application-message.success {
  background: #d1fae5;
  border-left: 4px solid #10b981;
  color: #065f46;
}

.application-message.error {
  background: #fee2e2;
  border-left: 4px solid #ef4444;
  color: #b91c1c;
}

.application-message i {
  font-size: 1.25rem;
}

@keyframes slideDown {
  from {
    transform: translate(-50%, -20px);
    opacity: 0;
  }
  to {
    transform: translate(-50%, 0);
    opacity: 1;
  }
}

/* Navigation bar style */
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

/* Search section style */
.search-section {
  width: 100%;
  padding: 2rem;
  display: flex;
  gap: 1rem;
  background: white;
  margin-bottom: 2rem;
}

.search-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f3f4f6;
  border-radius: 12px;
  padding: 0 1.25rem;
}

.search-wrapper i {
  color: #9ca3af;
  font-size: 1.25rem;
}

.search-wrapper input {
  flex: 1;
  padding: 1rem;
  border: none;
  outline: none;
  font-size: 1rem;
  background: transparent;
}

.category-wrapper select {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  background: white;
  font-size: 1rem;
  color: #4b5563;
  cursor: pointer;
  outline: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

/* Club card grid */
.clubs-grid {
  width: 100%;
  padding: 0 2rem 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 0 auto;
}

.club-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
  cursor: pointer;
  transition: all 0.3s ease;
}

.club-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.card-header {
  position: relative;
  height: 180px;
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
  display: flex;
  align-items: flex-start;
  padding: 1rem;
}

.category-tag {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  text-transform: capitalize;
}

.category-tag.sports { background: linear-gradient(45deg, #ef4444, #f87171); }
.category-tag.academic { background: linear-gradient(45deg, #3b82f6, #60a5fa); }
.category-tag.arts { background: linear-gradient(45deg, #ec4899, #f472b6); }
.category-tag.technology { background: linear-gradient(45deg, #10b981, #34d399); }
.category-tag.music { background: linear-gradient(45deg, #9b59b6, #8e44ad); }
.category-tag.culture { background: linear-gradient(45deg, #e67e22, #d35400); }
.category-tag.language { background: linear-gradient(45deg, #27ae60, #2ecc71); }
.category-tag.science { background: linear-gradient(45deg, #16a085, #1abc9c); }

.card-body {
  padding: 1.5rem;
}

.card-body h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.card-body p {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.card-stats {
  display: flex;
  gap: 1.5rem;
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
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 2;
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

.join-btn.applied {
  background: linear-gradient(45deg, #f59e0b, #fbbf24);
  cursor: not-allowed;
}

.join-btn.joined {
  background: linear-gradient(45deg, #059669, #10b981);
  cursor: not-allowed;
}

.join-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.action-icons {
  display: flex;
  gap: 0.75rem;
  margin-left: 1rem;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #e5e7eb;
  color: #4338ca;
}

.icon-btn.liked {
  background: #ff4757;
  color: white;
}

.icon-btn.favorited {
  background: #ffd700;
  color: white;
}

@media (max-width: 768px) {
  .clubs-grid {
    padding: 1rem;
    gap: 1rem;
    grid-template-columns: 1fr;
  }
  
  .search-section {
    flex-direction: column;
    padding: 1rem;
  }
  
  .nav-right a span {
    display: none;
  }
}

@media (max-width: 480px) {
  .nav-right a span {
    display: none;
  }
  
  .nav-right {
    gap: 0.5rem;
  }
  
  .nav-right a {
    padding: 0.5rem;
  }
  
  .card-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .action-icons {
    width: 100%;
    justify-content: center;
  }
}
</style> 