<template>
  <div class="admin-home">
    <div class="header">
      <h1>Dashboard</h1>
      <AdminProfileDropdown class="profile-dropdown" />
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon students">
          <i class="bi bi-people"></i>
        </div>
        <div class="stat-info">
          <h3>Total Students</h3>
          <p>{{ stats.totalStudents }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon clubs">
          <i class="bi bi-collection"></i>
        </div>
        <div class="stat-info">
          <h3>Active Clubs</h3>
          <p>{{ stats.activeClubs }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon applications">
          <i class="bi bi-file-text"></i>
        </div>
        <div class="stat-info">
          <h3>Pending Applications</h3>
          <p>{{ stats.pendingApplications }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon activities">
          <i class="bi bi-calendar-event"></i>
        </div>
        <div class="stat-info">
          <h3>Recent Activities</h3>
          <p>{{ stats.recentActivities }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminProfileDropdown from '@/components/AdminProfileDropdown.vue'

// 示例数据
const stats = ref({
  totalStudents: 1200,
  activeClubs: 45,
  pendingApplications: 8,
  recentActivities: 24
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
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