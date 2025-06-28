<template>
  <div class="club-detail-page">
    <!-- heading navigation -->
    <nav class="navbar">
      <router-link to="/home" class="nav-back">
        <i class="bi bi-arrow-left"></i>
        <span>Back</span>
      </router-link>
      <div class="nav-title">Club Detail</div>
      <router-link to="/profile" class="nav-profile">
        <i class="bi bi-person"></i>
        <span>My Profile</span>
      </router-link>
    </nav>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading club details...</p>
    </div>

    <div v-else>
      <!-- club information -->
      <div class="club-header">
        <!--<img :src="club.image" :alt="club.name" class="club-banner">-->
        <div class="club-info">
          <h1>{{ club.name }}</h1>
          <div class="club-meta">

          </div>
          <p class="club-description">{{ club.description }}</p>
          <div class="club-actions">
            <button 
              class="action-btn primary"
              :class="{ 'joined': club.isJoined }"
              @click="handleJoin"
            >
              <i :class="club.isJoined ? 'bi bi-check2' : 'bi bi-plus'"></i>
              {{ club.isJoined ? 'Joined' : 'Join Club' }}
            </button>
            <button 
              class="action-btn"
              :class="{ 'active': club.isLiked }"
              @click="handleLike"
            >
              <i class="bi bi-heart-fill"></i>
              <span>{{ club.likeCount || 0 }}</span>
            </button>
            <button 
              class="action-btn"
              :class="{ 'active': club.isFavorited }"
              @click="handleFavorite"
            >
              <i class="bi bi-bookmark-fill"></i>
              <span>Favorite</span>
            </button>
          </div>
        </div>
      </div>

      <!-- activities -->
      <div class="section">
        <h2>Activities</h2>
        <div v-if="club.activities && club.activities.length > 0" class="activities-list">
          <div v-for="activity in club.activities" 
               :key="activity.id" 
               class="activity-card"
          >
            <div class="activity-date">
              <span class="date">{{ activity.date }}</span>
              <span class="time">{{ activity.time }}</span>
            </div>
            <div class="activity-content">
              <h3>{{ activity.title }}</h3>
              <p>{{ activity.description }}</p>
              <div class="activity-meta">
                <span class="location">
                  <i class="bi bi-geo-alt"></i>
                  {{ activity.location }}
                </span>
                <span class="participants">
                  <i class="bi bi-people"></i>
                  {{ activity.participants }} joined
                </span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>No activities scheduled yet.</p>
        </div>
      </div>

      <!-- club member -->
      <div class="section">
        <h2>Members</h2>
        <div v-if="club.members && club.members.length > 0" class="members-grid">
          <div v-for="member in club.members" 
               :key="member.id" 
               class="member-card"
          >
            <img :src="member.avatar" :alt="member.name" class="member-avatar">
            <div class="member-info">
              <h3>{{ member.name }}</h3>
              <span class="member-role">{{ member.role }}</span>
              <p class="member-bio">{{ member.bio || 'No bio available.' }}</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>No members listed yet.</p>
        </div>
      </div>

      <!-- Add comment section after member list -->
      <!--<div class="section">
        <h2>Comments & Feedback</h2>
        
        <!-- Comment form -->
        <!--<div class="comment-form">
          <div class="rating-input">
            <span>Your Rating:</span>
            <div class="stars">
              <i v-for="n in 5" 
                 :key="n"
                 :class="[
                   'bi',
                   userRating >= n ? 'bi-star-fill' : 'bi-star',
                   'star-btn'
                 ]"
                 @click="userRating = n"
              ></i>
            </div>
          </div>
          <textarea 
            v-model="commentText"
            placeholder="Write your comment here..."
            rows="3"
            class="comment-input"
          ></textarea>
          <button class="submit-btn" @click="submitComment">
            <i class="bi bi-send"></i>
            Submit Comment
          </button>
        </div>-->

        <!-- Comment list -->
        <!--<div v-if="club.comments && club.comments.length > 0" class="comments-list">
          <div v-for="comment in club.comments" 
               :key="comment.id" 
               class="comment-card"
          >
            <img :src="comment.avatar" :alt="comment.username" class="comment-avatar">
            <div class="comment-content">
              <div class="comment-header">
                <div class="comment-info">
                  <h4>{{ comment.username }}</h4>
                  <div class="rating">
                    <i v-for="n in 5" 
                       :key="n"
                       :class="[
                         'bi',
                         comment.rating >= n ? 'bi-star-fill' : 'bi-star'
                       ]"
                    ></i>
                  </div>
                </div>
                <span class="comment-date">{{ comment.date }}</span>
              </div>
              <p class="comment-text">{{ comment.content }}</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>No comments yet. Be the first to leave feedback!</p>
        </div>
      </div>-->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const clubId = route.params.id
const club = ref({
  id: null,
  name: '',
  description: '',
  image: '',
  memberCount: 0,
  rating: 0,
  commentCount: 0,
  likeCount: 0,
  foundedDate: '',
  isJoined: false,
  isLiked: false,
  isFavorited: false,
  activities: [],
  comments: [],
  members: []
})
const loading = ref(true)
const userRating = ref(0)
const commentText = ref('')

// Determine base API URL
const baseUrl = window.location.hostname === 'localhost'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Fetch club details
const fetchClubDetails = async () => {
  console.log('fetchClubDetails called for clubId:', clubId)

  // Check if clubId is valid
  if (!clubId || clubId === 'undefined' || clubId === 'null') {
    console.error('Invalid club ID:', clubId)
    loading.value = false
    club.value = {
      id: null,
      name: 'Invalid Club',
      description: 'Club ID is missing or invalid. Please go back and try again.',
      image: '',
      category: '',
      memberCount: 0,
      rating: 0,
      commentCount: 0,
      likeCount: 0,
      foundedDate: '',
      isApplied: false,
      isJoined: false,
      isLiked: false,
      isFavorited: false,
      activities: [],
      comments: [],
      members: []
    }
    return
  }

  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const config = {
      headers: { 'Authorization': `Token ${token}` }
    }
    
    // Get club details
    const response = await axios.get(`${baseUrl}/api/clubs/${clubId}/`, config)
    const clubData = response.data
    
    // Record view interaction - simplified to avoid multiple calls
    try {
      console.log('Recording view interaction for club:', clubId)
      await axios.post(`${baseUrl}/api/interactions/record-view/`, {
        club: clubId  // Backend expects 'club', not 'club_id'
      }, config);
      console.log('View interaction recorded successfully')
    } catch (recordViewError) {
      console.error('Error recording view interaction:', recordViewError)
      if (recordViewError.response) {
        console.error('Error status:', recordViewError.response.status)
        console.error('Error data:', recordViewError.response.data)
      }
      // Don't use fallback to avoid duplicate database operations
    }
    
    // Check if favorited this club
    let isFavorited = false
    try {
      console.log('Checking if club is favorited...')
      const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
      console.log('Saved clubs response:', savedClubsResponse.data)

      // Handle both array and paginated response formats
      const savedClubsData = savedClubsResponse.data.results || savedClubsResponse.data
      isFavorited = Array.isArray(savedClubsData) && savedClubsData.some(savedClub => savedClub.club === parseInt(clubId))
      console.log('Is club favorited:', isFavorited)
    } catch (savedError) {
      console.error('Error checking saved clubs:', savedError)
      if (savedError.response) {
        console.error('Saved clubs error status:', savedError.response.status)
        console.error('Saved clubs error data:', savedError.response.data)
      }
      // Fall back to localStorage
      const favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
      isFavorited = favoritedClubIds.includes(Number(clubId))
      console.log('Using localStorage fallback, is favorited:', isFavorited)
    }
    
    // Get application status
    const appliedClubIds = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
    
    // Merge all data
    club.value = {
      ...clubData,
      isJoined: appliedClubIds.includes(Number(clubId)),
      isLiked: false, // To be implemented
      isFavorited: isFavorited,
      activities: clubData.activities || [],
      comments: clubData.comments || [],
      members: clubData.members || []
    }
  } catch (error) {
    console.error('Error fetching club details:', error)
    alert('Failed to fetch club details')
  } finally {
    loading.value = false
  }
}

// Handle likes
const handleLike = () => {
  club.value.isLiked = !club.value.isLiked
  if (club.value.isLiked) {
    club.value.likeCount++
  } else {
    club.value.likeCount--
  }
}

// Handle favorites
const handleFavorite = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      router.push('/login')
      return
    }
    
    const config = {
      headers: { 'Authorization': `Token ${token}` }
    }
    
    // Temporarily update UI status, provide immediate feedback
    club.value.isFavorited = !club.value.isFavorited
    
    if (club.value.isFavorited) {
      // Add to favorites
      await axios.post(`${baseUrl}/api/saved-clubs/`, {
        club: club.value.id
      }, config)
      console.log('Club added to favorites')
    } else {
      // Remove from favorites (need to get saved ID first)
      const savedClubsResponse = await axios.get(`${baseUrl}/api/saved-clubs/`, config)
      const savedClub = savedClubsResponse.data.find(item => item.club === club.value.id)
      
      if (savedClub) {
        await axios.delete(`${baseUrl}/api/saved-clubs/${savedClub.id}/`, config)
        console.log('Club removed from favorites')
      }
    }
    
    // Simultaneously update localStorage, as backup and to improve UI response speed
    const favoritedClubIds = JSON.parse(localStorage.getItem('favoritedClubs') || '[]')
    if (club.value.isFavorited) {
      if (!favoritedClubIds.includes(Number(clubId))) {
        favoritedClubIds.push(Number(clubId))
      }
    } else {
      const index = favoritedClubIds.indexOf(Number(clubId))
      if (index > -1) {
        favoritedClubIds.splice(index, 1)
      }
    }
    localStorage.setItem('favoritedClubs', JSON.stringify(favoritedClubIds))
    
  } catch (error) {
    // If API call fails, restore UI status
    club.value.isFavorited = !club.value.isFavorited
    console.error('Error updating favorite status:', error)
    alert('Failed to update favorite status')
  }
}

// Handle join
const handleJoin = async () => {
  if (club.value.isJoined) {
    // If already joined, do nothing or implement leave club functionality
    return
  }
  
  try {
    // Create application data for testing
    const applicationData = {
      club: club.value.id,
      status: 'pending'
    }
    
    try {
      // Submit application to backend - without auth headers for testing
      const response = await axios.post(`${baseUrl}/api/applications/`, applicationData)
      console.log('Application submitted successfully', response.data)
    } catch (apiError) {
      console.error('API Error:', apiError)
      throw apiError
    }
    
    // Update UI
    club.value.isJoined = true
    club.value.memberCount++
    
    // Store in localStorage that user has applied to this club
    const appliedClubs = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
    if (!appliedClubs.includes(club.value.id)) {
      appliedClubs.push(club.value.id)
      localStorage.setItem('appliedClubs', JSON.stringify(appliedClubs))
    }
    
    // Show success message (using alert for simplicity)
    alert('Application submitted successfully! Please wait for admin approval.')
    
  } catch (error) {
    console.error('Error applying to club:', error)
    alert('Failed to submit application. Please try again.')
  }
}

// Submit comment
const submitComment = () => {
  if (!userRating.value || !commentText.value.trim()) {
    alert('Please fill in the rating and comment content')
    return
  }
  
  // Create new comment
  const newComment = {
    id: Date.now(),
    username: 'Current User', // Ideally get from user profile
    avatar: '/images/avatar.jpg',
    rating: userRating.value,
    content: commentText.value,
    date: new Date().toISOString().split('T')[0]
  }
  
  // Add comment to list
  club.value.comments.unshift(newComment)
  
  // Reset form
  userRating.value = 0
  commentText.value = ''
  
  // Ideally, send to API
  // axios.post(`${baseUrl}/api/clubs/${clubId}/comments/`, newComment)
}

// Load data on component mount
onMounted(() => {
  fetchClubDetails()
})
</script>

<style scoped>
.club-detail-page {
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

.nav-back, .nav-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: #4b5563;
  text-decoration: none;
  transition: all 0.3s;
}

.nav-back:hover, .nav-profile:hover {
  background: #f3f4f6;
}

.club-header {
  position: relative;
  background: white;
  margin-bottom: 2rem;
}

.club-banner {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.club-info {
  padding: 2rem;
}

.club-info h1 {
  font-size: 2rem;
  color: #111827;
  margin-bottom: 1rem;
}

.club-meta {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
}

.meta-item i {
  color: #4338ca;
}

.club-description {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.club-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.primary {
  background: #4338ca;
  color: white;
}

.action-btn.primary:hover {
  background: #4f46e5;
}

.action-btn.primary.joined {
  background: #059669;
}

.action-btn.active {
  background: #eef2ff;
  color: #4338ca;
}

.section {
  background: white;
  margin: 0 2rem 2rem;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.section h2 {
  font-size: 1.5rem;
  color: #111827;
  margin-bottom: 1.5rem;
}

.activities-list {
  display: grid;
  gap: 1.5rem;
}

.activity-card {
  display: flex;
  gap: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.activity-date {
  text-align: center;
  min-width: 100px;
}

.activity-date .date {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
  color: #4338ca;
}

.activity-date .time {
  color: #6b7280;
}

.activity-content h3 {
  margin: 0 0 0.5rem;
  color: #111827;
}

.activity-meta {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
  color: #6b7280;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.member-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.member-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info h3 {
  margin: 0 0 0.25rem;
  color: #111827;
}

.member-role {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #eef2ff;
  color: #4338ca;
  border-radius: 9999px;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.member-bio {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.comment-form {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stars {
  display: flex;
  gap: 0.5rem;
}

.star-btn {
  font-size: 1.25rem;
  color: #d1d5db;
  cursor: pointer;
  transition: all 0.2s;
}

.star-btn:hover,
.bi-star-fill {
  color: #fbbf24;
}

.comment-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  resize: vertical;
  min-height: 100px;
  margin-bottom: 1rem;
  font-family: inherit;
}

.comment-input:focus {
  outline: none;
  border-color: #4338ca;
  box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.1);
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #4338ca;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover {
  background: #4f46e5;
}

.comments-list {
  display: grid;
  gap: 1.5rem;
}

.comment-card {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.comment-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.comment-info h4 {
  margin: 0 0 0.25rem;
  color: #111827;
}

.rating {
  display: flex;
  gap: 0.25rem;
  color: #fbbf24;
  font-size: 0.875rem;
}

.comment-date {
  color: #6b7280;
  font-size: 0.875rem;
}

.comment-text {
  color: #4b5563;
  line-height: 1.5;
  margin: 0;
}

@media (max-width: 768px) {
  .club-meta {
    flex-direction: column;
    gap: 1rem;
  }
  
  .club-actions {
    flex-direction: column;
  }
  
  .section {
    margin: 0 1rem 1rem;
    padding: 1rem;
  }
  
  .activity-card {
    flex-direction: column;
    gap: 1rem;
  }
  
  .activity-date {
    text-align: left;
  }
  
  .comment-card {
    flex-direction: column;
  }
  
  .comment-avatar {
    width: 40px;
    height: 40px;
  }
  
  .comment-header {
    flex-direction: column;
    gap: 0.5rem;
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f4f6;
  border-top: 5px solid #4338ca;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 12px;
}
</style> 