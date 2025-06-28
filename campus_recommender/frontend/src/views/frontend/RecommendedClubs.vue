<template>
  <div class="recommended-page">
    <!-- Heading Navigation -->
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

    <!-- Application status message (same as home page) -->
    <div
      v-if="showApplicationMessage"
      class="application-message"
      :class="applicationStatus"
    >
      <i :class="applicationStatus === 'success' ? 'bi bi-check-circle' : 'bi bi-exclamation-circle'"></i>
      <span>{{ applicationStatus === 'success' ? 'Application submitted successfully! Please wait for admin approval.' : 'Failed to submit application. Please try again.' }}</span>
    </div>

    <!-- Content section -->
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
        <!-- Recommended club list -->
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
                <button class="join-btn" @click.stop="handleJoin(club)" :disabled="joinInProgress || club.isApplied || club.isJoined">
                  <span v-if="joinInProgress && joiningClubId === club.id">
                    <i class="bi bi-hourglass"></i> Processing...
                  </span>
                  <span v-else>
                    {{ club.isJoined ? 'Joined' : club.isApplied ? 'Applied' : 'Join Now' }}
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
const applicationStatus = ref(null)
const showApplicationMessage = ref(false)

// Determine base API URL
const baseUrl = window.location.hostname === 'localhost'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Random color generator - based on club name to generate consistent colors
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
    recommendedClubs.value = await processClubs(response.data || [])
    
  } catch (err) {
    console.error('Error fetching recommendations:', err)
    
    if (err.response) {
      // Handle different HTTP error codes
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
const processClubs = async (clubs) => {
  // Get applied club IDs from localStorage
  const appliedClubIds = JSON.parse(localStorage.getItem('appliedClubs') || '[]')

  // Get application statuses from API if possible
  let applicationStatuses = {}
  const token = localStorage.getItem('token')

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
      console.log('Application statuses:', applicationStatuses)
    } catch (error) {
      console.warn('Could not fetch application statuses:', error)
    }
  }

  return clubs.map(club => {
    // Extract keys to ensure we have all the data we need
    const {
      id,
      name,
      category = 'General',
      description = '',
      score = 0,
      recommendation_type = 'hybrid',
      member_count = 0,
      is_member = false,
      // Other possible fields
      club_name,  // Backend may return club_name instead of name
      club_category, // Backend may return club_category instead of category
    } = club

    // Determine application status
    const applicationStatus = applicationStatuses[id]
    const hasAppliedLocally = appliedClubIds.includes(id)

    let isApplied = false
    let isJoined = false

    if (applicationStatus === 'approved') {
      isJoined = true
    } else if (applicationStatus === 'pending' || hasAppliedLocally) {
      isApplied = true
    } else if (is_member) {
      isJoined = true
    }

    return {
      id: id,
      name: name || club_name || 'Unknown Club',
      category: category || club_category || 'General',
      description: description || '',
      memberCount: member_count || 0,
      score: score,
      recommendationType: recommendation_type,
      image: club.banner_image || null,
      isApplied: isApplied,
      isJoined: isJoined,
      applicationStatus: applicationStatus
    }
  })
}

const goToDetail = (clubId) => {
  router.push(`/club/${clubId}`)
}

const handleJoin = async (club) => {
  // If already joined, applied, or another join request is in progress, do not allow new requests
  if (club.isJoined || club.isApplied || joinInProgress.value) {
    return
  }

  joinInProgress.value = true
  joiningClubId.value = club.id

  try {
    // Get current user info from localStorage (same as home page)
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const token = localStorage.getItem('token')

    console.log('Joining club:', club.name, 'ID:', club.id)

    // Create application data - use same format as home page
    const applicationData = {
      club: club.id,
      status: 'pending'
    }

    // For development/testing without backend (same logic as home page)
    try {
      // Try to submit application to backend - without auth headers for testing (same as home page)
      const response = await axios.post(`${baseUrl}/api/applications/`, applicationData)
      console.log('Application submitted successfully:', response.data)

      // If successful, continue with normal flow
    } catch (apiError) {
      console.error('API Error:', apiError)

      // Only use simulation if it's an auth error (same as home page)
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

    // Store in localStorage that user has applied to this club (same as home page)
    const appliedClubs = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
    if (!appliedClubs.includes(club.id)) {
      appliedClubs.push(club.id)
      localStorage.setItem('appliedClubs', JSON.stringify(appliedClubs))
    }

    // Show success message (same as home page)
    applicationStatus.value = 'success'
    showApplicationMessage.value = true
    setTimeout(() => {
      showApplicationMessage.value = false
    }, 3000)

  } catch (error) {
    console.error('Error applying to club:', error)

    // Show error message (same format as home page)
    applicationStatus.value = 'error'
    showApplicationMessage.value = true
    setTimeout(() => {
      showApplicationMessage.value = false
    }, 3000)

  } finally {
    joinInProgress.value = false
    joiningClubId.value = null
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

/* Navigation bar style consistent with home page */
.navbar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Application message (same as home page) */
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
}

.application-message.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.application-message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
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

/* Content section style */
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

/* Applied state - orange/yellow for pending */
.join-btn.applied {
  background: #f59e0b !important;
}

.join-btn.applied:hover {
  background: #f59e0b !important;
}

/* Joined state - green for approved */
.join-btn.joined {
  background: #059669 !important;
}

.join-btn.joined:hover {
  background: #059669 !important;
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