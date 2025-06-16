<template>
  <div class="admin-profile">
    <div class="header">
      <h1>Admin Profile</h1>
      <AdminProfileDropdown class="profile-dropdown" />
    </div>

    <div class="content" :class="{ 'loading': loading }">
      <!-- Loading indicator -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <div>Loading profile...</div>
      </div>

      <!-- Error and success messages -->
      <div v-if="error" class="alert alert-error">
        <i class="bi bi-exclamation-triangle"></i> {{ error }}
      </div>
      
      <div v-if="success" class="alert alert-success">
        <i class="bi bi-check-circle"></i> {{ success }}
      </div>

      <div class="profile-section">
        <div class="avatar-section">
          <div class="avatar">
            <i class="bi bi-person-circle"></i>
          </div>
          <div class="user-role">{{ profile.role }}</div>
        </div>

        <div class="info-section">
          <div class="info-group">
            <label>Username</label>
            <input type="text" v-model="profile.username" disabled>
          </div>

          <div class="info-group">
            <label>First Name</label>
            <input type="text" v-model="profile.first_name" placeholder="Enter first name">
          </div>

          <div class="info-group">
            <label>Last Name</label>
            <input type="text" v-model="profile.last_name" placeholder="Enter last name">
          </div>

          <div class="info-group">
            <label>Email</label>
            <input type="email" v-model="profile.email" placeholder="Enter email">
          </div>

          <div class="info-group">
            <label>Last Login</label>
            <input type="text" :value="profile.lastLogin" disabled>
          </div>
        </div>
      </div>

      <div class="security-section">
        <h2>Change Password</h2>
        
        <div class="password-section">
          <div class="info-group">
            <label>Current Password <span class="optional">(optional)</span></label>
            <input type="password" v-model="passwords.current" placeholder="Enter current password if needed">
          </div>

          <div class="info-group">
            <label>New Password</label>
            <input type="password" v-model="passwords.new" placeholder="Enter new password">
          </div>

          <div class="info-group">
            <label>Confirm Password</label>
            <input type="password" v-model="passwords.confirm" placeholder="Confirm new password">
          </div>
        </div>

        <div class="action-buttons">
          <button class="save-btn" @click="saveChanges" :disabled="saving">
            <i class="bi" :class="saving ? 'bi-hourglass-split' : 'bi-check-lg'"></i>
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
          <button class="cancel-btn" @click="resetChanges" :disabled="saving">
            <i class="bi bi-x-lg"></i>
            Cancel
          </button>
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
import { getUser, getToken, setAdminId, getAdminId } from '@/utils/auth'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

const profile = ref({
  name: '',
  email: '',
  role: '',
  lastLogin: '',
  first_name: '',
  last_name: '',
  username: ''
})

const passwords = ref({
  current: '',
  new: '',
  confirm: ''
})

// Configure base URL
const baseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? `http://${window.location.hostname}:8000`
  : `${window.location.protocol}//${window.location.host}`

// Get auth headers
const getAuthHeaders = () => {
  const token = getToken()
  return token ? {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  }
}

// Helper function to update admin ID in storage
const updateStoredAdminId = (adminId) => {
  if (adminId) {
    console.log('Saving admin ID to storage:', adminId)
    setAdminId(adminId)
    profile.value.id = adminId
  }
}

// Fetch admin data
const fetchAdminProfile = async () => {
  const user = getUser()
  if (!user) {
    error.value = 'User data not found. Please log in again.'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    console.log('Fetching admin profile')
    
    // Check for stored admin ID first
    const storedAdminId = getAdminId()
    if (storedAdminId) {
      console.log('Using stored admin ID:', storedAdminId)
      try {
        const response = await axios.get(`${baseUrl}/api/admins/${storedAdminId}/`, {
          headers: getAuthHeaders()
        })
        
        console.log('Admin profile data from stored ID:', response.data)
        
        // Update profile data
        const adminData = response.data
        profile.value = {
          id: adminData.id,
          name: adminData.name || '',
          email: adminData.email || '',
          role: adminData.role || '',
          lastLogin: adminData.lastLogin || 'Never',
          username: adminData.username || '',
          first_name: adminData.first_name || '',
          last_name: adminData.last_name || ''
        }
        return
      } catch (idErr) {
        console.warn('Stored admin ID not valid, trying other methods')
        // If stored ID fails, continue with other methods
      }
    }
    
    // First try to use the /me endpoint
    try {
      const response = await axios.get(`${baseUrl}/api/admins/me/`, {
        headers: getAuthHeaders()
      })
      
      console.log('Admin profile data from /me endpoint:', response.data)
      
      // Update profile data
      const adminData = response.data
      profile.value = {
        id: adminData.id,
        name: adminData.name || '',
        email: adminData.email || '',
        role: adminData.role || '',
        lastLogin: adminData.lastLogin || 'Never',
        username: adminData.username || '',
        first_name: adminData.first_name || '',
        last_name: adminData.last_name || ''
      }
      
      // Save the ID we found
      updateStoredAdminId(adminData.id)
      return
    } catch (meErr) {
      console.warn('Could not fetch from /me endpoint, falling back to ID lookup', meErr)
      // Continue with the ID approach if /me fails
    }
    
    // Try to find admin by ID if we have one
    if (user.id) {
      try {
        const response = await axios.get(`${baseUrl}/api/admins/${user.id}/`, {
          headers: getAuthHeaders()
        })
        
        console.log('Admin profile data by ID:', response.data)
        
        // Update profile data
        const adminData = response.data
        profile.value = {
          id: adminData.id,
          name: adminData.name || '',
          email: adminData.email || '',
          role: adminData.role || '',
          lastLogin: adminData.lastLogin || 'Never',
          username: adminData.username || '',
          first_name: adminData.first_name || '',
          last_name: adminData.last_name || ''
        }
        
        // Save the ID we found
        updateStoredAdminId(adminData.id)
        return
      } catch (idErr) {
        console.warn('Could not fetch by ID, trying to find admin by username', idErr)
        // Continue with listing approach if ID lookup fails
      }
    }
      
    // Last resort: list all admins and find by username
    const adminsResponse = await axios.get(`${baseUrl}/api/admins/`, {
      headers: getAuthHeaders()
    })
    
    // Function to find admin by username
    const findAdmin = (admins, username) => {
      return admins.find(admin => admin.username === username)
    }
    
    let foundAdmin = null
    
    // Handle both array and paginated responses
    if (Array.isArray(adminsResponse.data)) {
      foundAdmin = findAdmin(adminsResponse.data, user.username)
    } else if (adminsResponse.data && adminsResponse.data.results) {
      foundAdmin = findAdmin(adminsResponse.data.results, user.username)
    }
    
    if (foundAdmin) {
      console.log('Found admin by username in listing:', foundAdmin)
      profile.value = {
        id: foundAdmin.id,
        name: foundAdmin.name || '',
        email: foundAdmin.email || '',
        role: foundAdmin.role || '',
        lastLogin: foundAdmin.lastLogin || 'Never',
        username: foundAdmin.username || '',
        first_name: foundAdmin.first_name || '',
        last_name: foundAdmin.last_name || ''
      }
      
      // Save the ID we found
      updateStoredAdminId(foundAdmin.id)
    } else {
      error.value = 'Could not find your admin profile. Please log in again.'
    }
    
  } catch (err) {
    console.error('Error fetching admin profile:', err)
    error.value = 'Failed to load profile. Please try again later.'
  } finally {
    loading.value = false
  }
}

// Save profile changes
const saveChanges = async () => {
  saving.value = true
  error.value = ''
  success.value = ''

  try {
    // Update profile information
    const profileData = {
      email: profile.value.email,
      first_name: profile.value.first_name,
      last_name: profile.value.last_name
    }

    console.log('Updating profile with:', profileData)
    
    // Use the "me" endpoint directly - this will identify the current user via their token
    await axios.put(`${baseUrl}/api/admins/me/`, profileData, {
      headers: getAuthHeaders()
    })

    // If password change requested
    if (passwords.value.new) {
      console.log('Updating password')
      const passwordData = {
        new_password: passwords.value.new
      }
      
      // Only include current password if provided
      if (passwords.value.current) {
        passwordData.current_password = passwords.value.current
      }
      
      await axios.post(`${baseUrl}/api/admins/me/reset_password/`, 
        passwordData, 
        { headers: getAuthHeaders() }
      )
    }

    success.value = 'Profile updated successfully!'
    
    // Clear password fields
    passwords.value = {
      current: '',
      new: '',
      confirm: ''
    }
    
    // Refresh profile data
    await fetchAdminProfile()
    
  } catch (err) {
    console.error('Error saving profile:', err)
    error.value = err.response?.data?.error || 'Failed to update profile. Please try again later.'
  } finally {
    saving.value = false
  }
}

// Reset changes to original values
const resetChanges = async () => {
  await fetchAdminProfile()
  passwords.value = {
    current: '',
    new: '',
    confirm: ''
  }
  error.value = ''
  success.value = ''
}

// Go back to previous page
const goBack = () => {
  router.back()
}

// Load profile on component mount
onMounted(fetchAdminProfile)
</script>

<style scoped>
.admin-profile {
  padding: 2rem;
  color: #e2e8f0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #07080a;
}

h2 {
  font-size: 1.25rem;
  color: #e2e8f0;
  margin-bottom: 1.5rem;
}

.content {
  background: #2d3748;
  border-radius: 1rem;
  padding: 2rem;
  position: relative;
}

.profile-section {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #4a5568;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: #4338ca;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  color: #e2e8f0;
}

.user-role {
  font-size: 1rem;
  color: #a6b0d0;
  background: #374151;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  text-transform: capitalize;
}

.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.875rem;
  color: #94a3b8;
}

input {
  padding: 0.75rem 1rem;
  background: #1f2937;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  color: #e2e8f0;
  outline: none;
}

input::placeholder {
  color: #64748b;
}

input:disabled {
  background: #374151;
  cursor: not-allowed;
  color: #94a3b8;
}

.password-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.save-btn, .cancel-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #e2e8f0;
}

.save-btn {
  background: #4f46e5;
}

.save-btn:hover:not(:disabled) {
  background: #4338ca;
}

.cancel-btn {
  background: #64748b;
}

.cancel-btn:hover:not(:disabled) {
  background: #475569;
}

.save-btn:disabled, .cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 1rem;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top: 4px solid #4f46e5;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Alert styles */
.alert {
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alert-error {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.alert-success {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

/* Responsive design */
@media (max-width: 768px) {
  .profile-section {
    grid-template-columns: 1fr;
  }
  
  .avatar-section {
    margin-bottom: 2rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .save-btn, .cancel-btn {
    width: 100%;
    justify-content: center;
  }
}

.optional {
  font-size: 0.8rem;
  color: #94a3b8;
  font-style: italic;
  margin-left: 0.25rem;
}
</style> 