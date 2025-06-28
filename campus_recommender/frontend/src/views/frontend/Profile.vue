<template>
  <div class="profile-page">
    <!-- Naviagtion Bar -->
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
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading profile...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ error }}</p>
        <button @click="fetchStudentProfile" class="retry-btn">
          <i class="bi bi-arrow-clockwise"></i> Retry
        </button>
      </div>

      <!-- Profile Content -->
      <template v-else>
        <!-- Personal Information -->
        <div class="profile-card">
          <div class="avatar-section">
            <h1>{{ studentProfile.user.username }}</h1>
            <p class="student-id">Student ID: {{ studentProfile.student_id }}</p>
            <p class="course">Course: {{ studentProfile.course }}</p>
            <p class="status">Status: <span :class="`status-${studentProfile.status}`">{{ studentProfile.status }}</span></p>
          </div>
        </div>

        <!-- My Clubs -->
        <div class="section-card">
          <div class="section-header">
            <h2>My Clubs</h2>
            <span class="club-count">{{ userClubs.length }} clubs joined</span>
          </div>
          <div v-if="userClubs.length === 0" class="empty-state">
            <i class="bi bi-collection"></i>
            <p>You haven't joined any clubs yet</p>
            <router-link to="/home" class="join-clubs-btn">
              <i class="bi bi-plus"></i> Explore Clubs
            </router-link>
          </div>
          <div v-else class="clubs-grid">
            <div v-for="club in userClubs" :key="club.id" class="club-item">
              <div class="club-info">
                <h3>{{ club.name }}</h3>
                <p class="club-category">{{ club.category }}</p>
                <p class="club-description">{{ club.description }}</p>
                <router-link :to="`/club/${club.id}`" class="view-btn">
                  View Details
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Settings -->
        <div class="section-card">
          <div class="section-header">
            <h2>Account Settings</h2>
          </div>
          <form @submit.prevent="updateProfile" class="settings-form">

            <div class="form-row">
              <div class="form-group">
                <label>Username</label>
                <input
                  v-model="form.username"
                  type="text"
                  placeholder="Your username"
                  required
                >
              </div>
              <div class="form-group">
                <label>Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  placeholder="Your email"
                  required
                >
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Course</label>
                <input
                  v-model="form.course"
                  type="text"
                  placeholder="Your course/major"
                >
              </div>
              <div class="form-group">
                <label>Gender</label>
                <select v-model="form.gender">
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>New Password</label>
              <input
                v-model="form.newPassword"
                type="password"
                placeholder="Enter new password (leave blank to keep current)"
              >
            </div>

            <button type="submit" :disabled="profileLoading" class="save-btn">
              <i v-if="profileLoading" class="bi bi-arrow-clockwise spinning"></i>
              <i v-else class="bi bi-check2"></i>
              {{ profileLoading ? 'Saving...' : 'Save Changes' }}
            </button>
          </form>
        </div>


      </template>
    </div>

    <!-- Notifications -->
    <NotificationToast
      v-for="notification in notifications"
      :key="notification.id"
      :show="notification.show"
      :type="notification.type"
      :title="notification.title"
      :message="notification.message"
      :duration="notification.duration"
      :auto-close="notification.autoClose"
      @close="removeNotification(notification.id)"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNotifications } from '@/composables/useNotifications'
import NotificationToast from '@/components/NotificationToast.vue'
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore()
const { notifications, success, error: notifyError, removeNotification } = useNotifications()

// Reactive data
const loading = ref(true)
const error = ref('')
const profileLoading = ref(false)

// Student profile data
const studentProfile = ref({
  id: null,
  student_id: '',
  user: {
    username: '',
    email: '',
    date_joined: ''
  },
  course: '',
  gender: '',
  status: '',
  created_at: '',
  updated_at: ''
})

// User clubs and activities
const userClubs = ref([])
const userActivities = ref([])

// Initialize form with empty values
const form = reactive({
  username: '',
  email: '',
  course: '',
  gender: '',
  newPassword: ''
})

// Get API base URL
const getBaseUrl = () => {
  return window.location.hostname === 'localhost' ?
    `http://${window.location.hostname}:8000` :
    `${window.location.protocol}//${window.location.host}`
}

// Get auth headers
const getAuthHeaders = () => {
  const token = authStore.token || localStorage.getItem('token')
  return {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
}

// Fetch student profile data
const fetchStudentProfile = async () => {
  try {
    loading.value = true
    error.value = ''
    const baseUrl = getBaseUrl()

    // Fetch student profile using the /me endpoint
    const response = await axios.get(`${baseUrl}/api/students/me/`, {
      headers: getAuthHeaders()
    })

    console.log('Student profile data:', response.data)
    studentProfile.value = response.data

    // Update form with current data
    form.username = response.data.user.username || ''
    form.email = response.data.user.email || ''
    form.course = response.data.course || ''
    form.gender = response.data.gender || ''

  } catch (err) {
    console.error('Error fetching student profile:', err)
    error.value = 'Failed to load profile data'

    if (err.response?.status === 401) {
      await authStore.logout()
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

// Fetch user's clubs (applications that were approved)
const fetchUserClubs = async () => {
  try {
    const baseUrl = getBaseUrl()

    // Fetch user's applications
    const response = await axios.get(`${baseUrl}/api/applications/`, {
      headers: getAuthHeaders()
    })

    const applications = response.data.results || response.data

    // Filter approved applications
    const approvedApplications = applications.filter(app => app.status === 'approved')

    // Fetch full club details for each approved application
    const clubPromises = approvedApplications.map(async (app) => {
      try {
        // app.club is the club ID, so fetch the full club details
        // Try with auth headers first, then without
        let clubResponse
        try {
          clubResponse = await axios.get(`${baseUrl}/api/clubs/${app.club}/`, {
            headers: getAuthHeaders()
          })
        } catch (authError) {
          console.warn('Auth error, trying without headers:', authError)
          clubResponse = await axios.get(`${baseUrl}/api/clubs/${app.club}/`)
        }

        return {
          id: clubResponse.data.id,
          name: clubResponse.data.name,
          category: clubResponse.data.category,
          description: clubResponse.data.description,
          joinDate: new Date(app.apply_date).toLocaleDateString(),
          applicationId: app.id
        }
      } catch (clubError) {
        console.error(`Error fetching club ${app.club}:`, clubError)
        // Return a fallback object with the club ID
        return {
          id: app.club,
          name: `Club ${app.club}`,
          category: 'Unknown',
          description: 'Club details unavailable',
          joinDate: new Date(app.apply_date).toLocaleDateString(),
          applicationId: app.id
        }
      }
    })

    userClubs.value = await Promise.all(clubPromises)
    console.log('User clubs:', userClubs.value)
  } catch (err) {
    console.error('Error fetching user clubs:', err)
    // Fallback to localStorage if API fails
    const appliedClubs = JSON.parse(localStorage.getItem('appliedClubs') || '[]')
    userClubs.value = appliedClubs.map(clubId => ({
      id: clubId,
      name: `Club ${clubId}`,
      category: 'Unknown',
      description: 'Club details unavailable',
      joinDate: 'Unknown',
      applicationId: null
    }))
  }
}

// Fetch user's activity history
const fetchUserActivities = async () => {
  try {
    const baseUrl = getBaseUrl()

    // Fetch user's interactions
    const [interactionsRes, applicationsRes] = await Promise.all([
      axios.get(`${baseUrl}/api/interactions/`, {
        headers: getAuthHeaders()
      }),
      axios.get(`${baseUrl}/api/applications/`, {
        headers: getAuthHeaders()
      })
    ])

    const interactions = interactionsRes.data.results || interactionsRes.data
    const applications = applicationsRes.data.results || applicationsRes.data

    // Combine interactions and applications into activity timeline
    const activities = []

    // Add interactions
    interactions.forEach(interaction => {
      activities.push({
        id: `interaction-${interaction.id}`,
        icon: 'bi bi-eye',
        title: `Viewed ${interaction.club.name}`,
        description: `Viewed club details`,
        date: new Date(interaction.timestamp).toLocaleDateString(),
        timestamp: new Date(interaction.timestamp)
      })
    })

    // Add applications
    applications.forEach(application => {
      let icon = 'bi bi-file-text'
      let title = `Applied to ${application.club.name}`
      let description = `Application status: ${application.status}`

      if (application.status === 'approved') {
        icon = 'bi bi-check-circle'
        title = `Joined ${application.club.name}`
        description = 'Application approved - Welcome to the club!'
      } else if (application.status === 'rejected') {
        icon = 'bi bi-x-circle'
        title = `Application to ${application.club.name} declined`
        description = 'Application was not approved'
      }

      activities.push({
        id: `application-${application.id}`,
        icon,
        title,
        description,
        date: new Date(application.apply_date).toLocaleDateString(),
        timestamp: new Date(application.apply_date)
      })
    })

    // Sort by timestamp (newest first)
    userActivities.value = activities.sort((a, b) => b.timestamp - a.timestamp)

    console.log('User activities:', userActivities.value)
  } catch (err) {
    console.error('Error fetching user activities:', err)
  }
}

// No tag management functions needed for simplified form

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('isAdmin')
  router.push('/login')
}

const validateForm = () => {
  if (!form.username.trim()) {
    notifyError('Validation Error', 'Username is required')
    return false
  }
  if (!form.email.trim()) {
    notifyError('Validation Error', 'Email is required')
    return false
  }
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    notifyError('Validation Error', 'Please enter a valid email address')
    return false
  }
  if (form.newPassword && form.newPassword.length < 6) {
    notifyError('Validation Error', 'Password must be at least 6 characters long')
    return false
  }
  return true
}

const updateProfile = async () => {
  if (!validateForm()) {
    return
  }

  try {
    profileLoading.value = true
    console.log('Starting profile update with simplified form data:', form);

    const updateData = {
      user: {
        username: form.username,
        email: form.email
      },
      course: form.course,
      gender: form.gender
    }

    // Only include password in update if it's provided
    if (form.newPassword) {
      updateData.user.password = form.newPassword
    }

    console.log('Prepared update data:', updateData);
    console.log('Auth token:', authStore.token ? 'Present' : 'Missing');

    // Check if token exists
    const token = authStore.token || localStorage.getItem('token')
    if (!token) {
      console.error('No auth token found');
      alert('You are not logged in. Please log in again.')
      router.push('/login')
      return
    }

    const headers = getAuthHeaders()
    const baseUrl = getBaseUrl()

    console.log('Updating profile using /me endpoint');

    // Use the /me endpoint for student self-updates
    console.log(`Sending PATCH request to /api/students/me/`);
    const updateResponse = await axios.patch(`${baseUrl}/api/students/me/`, updateData, {
      headers
    })

    console.log('Profile update response:', updateResponse.data);

    if (updateResponse.data) {
      // Update local profile data
      studentProfile.value = updateResponse.data

      // Update the auth store with new user data
      authStore.updateUser({
        username: form.username,
        email: form.email
      })

      // Clear password field after update
      form.newPassword = ''

      // Show success notification
      success('Profile Updated', 'Your profile has been updated successfully!')
    }
  } catch (error) {
    console.error('Failed to update profile:', error)
    if (error.response) {
      console.error('Error response:', error.response.data)
      console.error('Error status:', error.response.status)
    }

    if (error.response?.status === 401) {
      notifyError('Session Expired', 'Please login again.')
      await authStore.logout()
      router.push('/login')
    } else if (error.response?.status === 403) {
      notifyError('Permission Denied', 'You do not have permission to update this profile.')
    } else if (error.response?.status === 400) {
      // Handle validation errors
      const errorData = error.response.data
      let errorMessage = 'Please check your input and try again.'

      if (errorData.user) {
        const userErrors = Object.values(errorData.user).flat()
        errorMessage = userErrors.join(', ')
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.error) {
        errorMessage = errorData.error
      }

      notifyError('Validation Error', errorMessage)
    } else {
      notifyError('Update Failed', error.response?.data?.error || error.message || 'Failed to update profile')
    }
  } finally {
    profileLoading.value = false
  }
}

// Initialize profile data on component mount
onMounted(async () => {
  await fetchStudentProfile()
  await Promise.all([
    fetchUserClubs(),
    fetchUserActivities()
  ])
})
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

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4338ca;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-state {
  color: #dc2626;
}

.retry-btn {
  background: #4338ca;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-btn:hover {
  background: #4f46e5;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
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

.course, .status {
  color: #6b7280;
  margin: 0.25rem 0;
}

.status-active {
  color: #10b981;
  font-weight: 600;
}

.status-inactive {
  color: #ef4444;
  font-weight: 600;
}

.status-pending {
  color: #f59e0b;
  font-weight: 600;
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

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #d1d5db;
}

.empty-description {
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.join-clubs-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #4338ca;
  color: white;
  text-decoration: none;
  padding: 0.5rem 0.5rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  transition: background 0.3s;
}

.join-clubs-btn:hover {
  background: #4f46e5;
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

.club-category {
  color: #4338ca;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.join-date {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.club-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.4;
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

.form-group input:focus, .form-group select:focus {
  border-color: #4338ca;
  outline: none;
  box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.1);
}

.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  transition: all 0.3s;
}

.tags-input {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.5rem;
  min-height: 3rem;
  transition: all 0.3s;
}

.tags-input:focus-within {
  border-color: #4338ca;
  box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.1);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.tag {
  background: #4338ca;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  margin-left: 0.25rem;
}

.tag-remove:hover {
  opacity: 0.7;
}

.tag-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 150px;
  padding: 0.25rem;
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

.show-more {
  text-align: center;
  margin-top: 1.5rem;
}

.show-more-btn {
  background: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.show-more-btn:hover {
  background: #e5e7eb;
}

/* Mobile Responsive Design */
@media (max-width: 768px) {
  .navbar {
    padding: 0.75rem 1rem;
  }

  .nav-back, .logout-btn {
    padding: 0.5rem;
    font-size: 0.875rem;
  }

  .nav-back span, .logout-btn span {
    display: none;
  }

  .nav-title {
    font-size: 1.125rem;
  }

  .profile-content {
    padding: 1rem;
    margin: 1rem auto;
    gap: 1.5rem;
  }

  .profile-card, .section-card {
    padding: 1.5rem;
    border-radius: 12px;
  }

  .avatar-wrapper {
    width: 80px;
    height: 80px;
    margin-bottom: 1rem;
  }

  .avatar-section h1 {
    font-size: 1.25rem;
    margin: 0.5rem 0;
  }

  .student-id, .course, .status {
    font-size: 0.875rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .section-header h2 {
    font-size: 1.25rem;
  }

  .club-count {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-group input, .form-group select {
    padding: 0.625rem;
    font-size: 0.875rem;
  }

  .save-btn {
    justify-self: stretch;
    padding: 0.75rem;
    font-size: 0.875rem;
  }

  .clubs-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .club-item {
    border-radius: 8px;
  }

  .club-info {
    padding: 1rem;
  }

  .empty-state {
    padding: 2rem 1rem;
  }

  .empty-state i {
    font-size: 2.5rem;
  }

  .join-clubs-btn {
    padding: 0.625rem 1rem;
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.5rem 0.75rem;
  }

  .profile-content {
    padding: 0.75rem;
    margin: 0.5rem auto;
    gap: 1rem;
  }

  .profile-card, .section-card {
    padding: 1rem;
    border-radius: 8px;
  }

  .avatar-wrapper {
    width: 60px;
    height: 60px;
  }

  .avatar-section h1 {
    font-size: 1.125rem;
  }

  .student-id, .course, .status {
    font-size: 0.8rem;
  }

  .section-header h2 {
    font-size: 1.125rem;
  }

  .form-group {
    margin-bottom: 0.75rem;
  }

  .form-group label {
    font-size: 0.875rem;
    margin-bottom: 0.375rem;
  }

  .form-group input, .form-group select {
    padding: 0.5rem;
    font-size: 0.8rem;
  }

  .save-btn {
    padding: 0.625rem;
    font-size: 0.8rem;
  }

  .club-info {
    padding: 0.75rem;
  }

  .club-info h3 {
    font-size: 1rem;
  }

  .club-category, .join-date, .club-description {
    font-size: 0.8rem;
  }

  .view-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.8rem;
  }

  .empty-state {
    padding: 1.5rem 0.75rem;
  }

  .empty-state i {
    font-size: 2rem;
  }

  .join-clubs-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
}
</style> 