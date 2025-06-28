<template>
  <div class="admin-home">
    <div class="header">
      <h1>Dashboard</h1>
      <div class="header-actions">
        <button
          @click="fetchDashboardStats"
          :disabled="loading"
          class="refresh-btn"
          title="Refresh Statistics"
        >
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
          Refresh
        </button>
        <AdminProfileDropdown class="profile-dropdown" />
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <i class="bi bi-exclamation-triangle"></i>
      {{ error }}
      <button @click="fetchDashboardStats" class="retry-btn">
        <i class="bi bi-arrow-clockwise"></i> Retry
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading dashboard statistics...</p>
    </div>

    <!-- Statistic Cards -->
    <div v-else class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon students">
          <i class="bi bi-people"></i>
        </div>
        <div class="stat-info">
          <h3>Total Students</h3>
          <p>{{ stats.totalStudents.toLocaleString() }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon clubs">
          <i class="bi bi-collection"></i>
        </div>
        <div class="stat-info">
          <h3>Active Clubs</h3>
          <p>{{ stats.activeClubs.toLocaleString() }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon applications">
          <i class="bi bi-file-text"></i>
        </div>
        <div class="stat-info">
          <h3>Pending Applications</h3>
          <p>{{ stats.pendingApplications.toLocaleString() }}</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon activities">
          <i class="bi bi-calendar-event"></i>
        </div>
        <div class="stat-info">
          <h3>Recent Activities</h3>
          <p>{{ stats.recentActivities.toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Charts -->
    <div v-if="!loading" class="charts-section">
      <DashboardChart
        title="Application Status Distribution"
        :data="applicationStats"
        chart-type="applications"
        :loading="loading"
        :error="error"
      />
      <DashboardChart
        title="System Overview"
        :data="systemStats"
        chart-type="stats"
        :loading="loading"
        :error="error"
      />
    </div>

    <!-- Recent Activities Section -->
    <div v-if="!loading" class="recent-activities">
      <div class="section-header">
        <h2>Recent Activities</h2>
        <router-link to="/admin/applications" class="view-all-btn">
          View All Applications
        </router-link>
      </div>
      <div class="activities-grid">
        <div class="activity-card">
          <div class="activity-icon pending">
            <i class="bi bi-clock"></i>
          </div>
          <div class="activity-content">
            <h4>Pending Applications</h4>
            <p>{{ stats.pendingApplications }} applications awaiting review</p>
            <router-link to="/admin/applications?status=pending" class="activity-link">
              Review Now →
            </router-link>
          </div>
        </div>

        <div class="activity-card">
          <div class="activity-icon students">
            <i class="bi bi-people"></i>
          </div>
          <div class="activity-content">
            <h4>Student Management</h4>
            <p>{{ stats.totalStudents }} students registered</p>
            <router-link to="/admin/students" class="activity-link">
              Manage Students →
            </router-link>
          </div>
        </div>

        <div class="activity-card">
          <div class="activity-icon clubs">
            <i class="bi bi-collection"></i>
          </div>
          <div class="activity-content">
            <h4>Club Management</h4>
            <p>{{ stats.activeClubs }} active clubs</p>
            <router-link to="/admin/clubs" class="activity-link">
              Manage Clubs →
            </router-link>
          </div>
        </div>
      </div>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'
import DashboardChart from '@/components/DashboardChart.vue'
import NotificationToast from '@/components/NotificationToast.vue'
import { useNotifications } from '@/composables/useNotifications'
import axios from 'axios'

// Reactive data
const stats = ref({
  totalStudents: 0,
  activeClubs: 0,
  pendingApplications: 0,
  recentActivities: 0
})

const extendedStats = ref({
  totalApplications: 0,
  approvedApplications: 0,
  rejectedApplications: 0,
  totalCategories: 0
})

const loading = ref(true)
const error = ref('')
let refreshInterval = null

// Notifications
const { notifications, success, error: notifyError, removeNotification } = useNotifications()

// Computed properties for chart data
const applicationStats = computed(() => ({
  pending: stats.value.pendingApplications,
  approved: extendedStats.value.approvedApplications,
  rejected: extendedStats.value.rejectedApplications
}))

const systemStats = computed(() => ({
  totalStudents: stats.value.totalStudents,
  activeClubs: stats.value.activeClubs,
  totalCategories: extendedStats.value.totalCategories,
  totalApplications: extendedStats.value.totalApplications
}))

// Get API base URL
const getBaseUrl = () => {
  return window.location.hostname === 'localhost' ?
    `http://${window.location.hostname}:8000` :
    `${window.location.protocol}//${window.location.host}`
}

// Fetch dashboard statistics
const fetchDashboardStats = async () => {
  try {
    loading.value = true
    error.value = ''
    const baseUrl = getBaseUrl()

    // Use the new dashboard stats endpoint
    const response = await axios.get(`${baseUrl}/api/dashboard/stats/`)

    // Update stats with real data from the dedicated endpoint
    stats.value = {
      totalStudents: response.data.totalStudents || 0,
      activeClubs: response.data.activeClubs || 0,
      pendingApplications: response.data.pendingApplications || 0,
      recentActivities: response.data.recentActivities || 0
    }

    // Update extended stats for charts
    extendedStats.value = {
      totalApplications: response.data.totalApplications || 0,
      approvedApplications: response.data.approvedApplications || 0,
      rejectedApplications: response.data.rejectedApplications || 0,
      totalCategories: response.data.totalCategories || 0
    }

    console.log('Dashboard stats loaded:', stats.value)
    console.log('Extended stats loaded:', extendedStats.value)

    // Show success notification on successful load
    success('Dashboard Updated', 'Statistics have been refreshed successfully')
  } catch (err) {
    console.error('Error fetching dashboard stats:', err)
    error.value = 'Failed to load dashboard statistics'
    notifyError('Failed to Load Statistics', 'Unable to fetch dashboard data. Please try again.')

    // Fallback: try to fetch individual endpoints
    try {
      console.log('Trying fallback method...')
      const [studentsRes, clubsRes, applicationsRes, interactionsRes] = await Promise.all([
        axios.get(`${baseUrl}/api/students/`),
        axios.get(`${baseUrl}/api/clubs/`),
        axios.get(`${baseUrl}/api/applications/?status=pending`),
        axios.get(`${baseUrl}/api/interactions/`)
      ])

      stats.value = {
        totalStudents: studentsRes.data.count || studentsRes.data.length || 0,
        activeClubs: clubsRes.data.count || clubsRes.data.length || 0,
        pendingApplications: applicationsRes.data.count || applicationsRes.data.results?.length || 0,
        recentActivities: interactionsRes.data.count || interactionsRes.data.length || 0
      }

      error.value = '' // Clear error if fallback works
    } catch (fallbackErr) {
      console.error('Fallback also failed:', fallbackErr)
      // Keep default values on error
      stats.value = {
        totalStudents: 0,
        activeClubs: 0,
        pendingApplications: 0,
        recentActivities: 0
      }
    }
  } finally {
    loading.value = false
  }
}

// Initialize dashboard
onMounted(() => {
  fetchDashboardStats()

  // Set up auto-refresh every 5 minutes
  refreshInterval = setInterval(() => {
    fetchDashboardStats()
  }, 5 * 60 * 1000) // 5 minutes
})

// Cleanup on unmount
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.admin-home {
  width: 100%;
  min-height: 100vh;
  padding: 1rem;
  background: #f3f4f6;
}

h1 {
  margin-bottom: 2rem;
  color: #111827;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #2563eb;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

.error-message {
  background: #fee2e2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.retry-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.retry-btn:hover {
  background: #b91c1c;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.recent-activities {
  margin-top: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.view-all-btn {
  background: #6b7280;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: background 0.2s;
}

.view-all-btn:hover {
  background: #4b5563;
}

.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.activity-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.activity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  flex-shrink: 0;
}

.activity-icon.pending {
  background: #f59e0b;
}

.activity-icon.students {
  background: #3b82f6;
}

.activity-icon.clubs {
  background: #10b981;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.125rem;
}

.activity-content p {
  margin: 0 0 1rem 0;
  color: #64748b;
  font-size: 0.875rem;
}

.activity-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.activity-link:hover {
  color: #2563eb;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-home {
    padding: 1rem;
  }

  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .charts-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .activities-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .activity-card {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 1rem;
  }

  .refresh-btn {
    padding: 0.5rem;
    font-size: 0.75rem;
  }
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.students {
  background: #eef2ff;
  color: #4338ca;
}

.stat-icon.clubs {
  background: #f0fdf4;
  color: #16a34a;
}

.stat-icon.applications {
  background: #fff7ed;
  color: #ea580c;
}

.stat-icon.activities {
  background: #fef2f2;
  color: #dc2626;
}

.stat-info h3 {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-info p {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.profile-dropdown {
  margin-left: 1rem;
}
</style> 