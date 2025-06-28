<template>
  <div class="dashboard-chart">
    <h3>{{ title }}</h3>
    <div class="chart-container">
      <div v-if="loading" class="chart-loading">
        <div class="spinner"></div>
        <p>Loading chart data...</p>
      </div>
      <div v-else-if="error" class="chart-error">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ error }}</p>
      </div>
      <div v-else class="chart-content">
        <!-- Simple bar chart for application status -->
        <div v-if="chartType === 'applications'" class="bar-chart">
          <div class="chart-bars">
            <div class="bar-group">
              <div class="bar pending" :style="{ height: getPendingHeight() }">
                <span class="bar-value">{{ data.pending || 0 }}</span>
              </div>
              <label>Pending</label>
            </div>
            <div class="bar-group">
              <div class="bar approved" :style="{ height: getApprovedHeight() }">
                <span class="bar-value">{{ data.approved || 0 }}</span>
              </div>
              <label>Approved</label>
            </div>
            <div class="bar-group">
              <div class="bar rejected" :style="{ height: getRejectedHeight() }">
                <span class="bar-value">{{ data.rejected || 0 }}</span>
              </div>
              <label>Rejected</label>
            </div>
          </div>
        </div>
        
        <!-- Simple stats display for other types -->
        <div v-else class="stats-display">
          <div class="stat-item" v-for="(value, key) in data" :key="key">
            <span class="stat-label">{{ formatLabel(key) }}</span>
            <span class="stat-value">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Object,
    default: () => ({})
  },
  chartType: {
    type: String,
    default: 'stats'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
})

// Calculate bar heights for application chart
const maxValue = computed(() => {
  if (props.chartType === 'applications') {
    return Math.max(
      props.data.pending || 0,
      props.data.approved || 0,
      props.data.rejected || 0,
      1 // Minimum 1 to avoid division by zero
    )
  }
  return 1
})

const getPendingHeight = () => {
  const height = ((props.data.pending || 0) / maxValue.value) * 100
  return `${Math.max(height, 10)}%` // Minimum 10% height for visibility
}

const getApprovedHeight = () => {
  const height = ((props.data.approved || 0) / maxValue.value) * 100
  return `${Math.max(height, 10)}%`
}

const getRejectedHeight = () => {
  const height = ((props.data.rejected || 0) / maxValue.value) * 100
  return `${Math.max(height, 10)}%`
}

const formatLabel = (key) => {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())
}
</script>

<style scoped>
.dashboard-chart {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: 300px;
  display: flex;
  flex-direction: column;
}

.dashboard-chart h3 {
  margin: 0 0 1rem 0;
  color: #1f2937;
  font-size: 1.125rem;
}

.chart-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading, .chart-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.chart-content {
  width: 100%;
  height: 100%;
}

.bar-chart {
  height: 100%;
  display: flex;
  align-items: end;
  justify-content: center;
}

.chart-bars {
  display: flex;
  gap: 2rem;
  align-items: end;
  height: 80%;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.bar {
  width: 60px;
  min-height: 20px;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: end;
  justify-content: center;
  position: relative;
  transition: all 0.3s ease;
}

.bar.pending {
  background: #f59e0b;
}

.bar.approved {
  background: #10b981;
}

.bar.rejected {
  background: #ef4444;
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 0.25rem;
}

.bar-group label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.stats-display {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
  height: 100%;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  color: #1f2937;
  font-weight: 600;
  font-size: 1.125rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
