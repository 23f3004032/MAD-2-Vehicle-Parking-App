<template>
  <div class="admin-analytics">
    <!-- Navigation Header -->
    <nav class="admin-navbar">
      <div class="container-fluid">
        <div class="admin-nav-content">
          <div class="admin-brand">
            <router-link to="/admin/dashboard" class="brand-link">
              <i class="bi bi-arrow-left me-2"></i>
              <span class="brand-highlight">Back to Dashboard</span>
            </router-link>
          </div>
          
          <div class="admin-nav-actions">
            <div class="admin-user-info">
              <i class="bi bi-person-circle me-2"></i>
              <span>Admin</span>
            </div>
            <button @click="handleLogout" class="btn btn-outline-light btn-sm">
              <i class="bi bi-box-arrow-right me-2"></i>Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Page Header -->
    <div class="analytics-header">
      <h1>
        <i class="bi bi-graph-up me-3"></i>Analytics Dashboard
      </h1>
      <p>Comprehensive insights into your parking business</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner-border text-primary" role="status"></div>
      <p>Loading analytics data...</p>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Overview Cards -->
      <div class="overview-cards" v-if="overview">
        <div class="metric-card revenue">
          <div class="metric-icon">
            <i class="bi bi-currency-rupee"></i>
          </div>
          <div class="metric-content">
            <h3>₹{{ overview.total_revenue.toLocaleString() }}</h3>
            <p>Total Revenue</p>
          </div>
        </div>

        <div class="metric-card bookings">
          <div class="metric-icon">
            <i class="bi bi-calendar-check"></i>
          </div>
          <div class="metric-content">
            <h3>{{ overview.total_bookings.toLocaleString() }}</h3>
            <p>Total Bookings</p>
          </div>
        </div>

        <div class="metric-card active">
          <div class="metric-icon">
            <i class="bi bi-car-front"></i>
          </div>
          <div class="metric-content">
            <h3>{{ overview.active_bookings }}</h3>
            <p>Currently Parked</p>
          </div>
        </div>

        <div class="metric-card users">
          <div class="metric-icon">
            <i class="bi bi-people"></i>
          </div>
          <div class="metric-content">
            <h3>{{ overview.total_users }}</h3>
            <p>Total Users</p>
          </div>
        </div>

        <div class="metric-card duration">
          <div class="metric-icon">
            <i class="bi bi-clock"></i>
          </div>
          <div class="metric-content">
            <h3>{{ overview.avg_duration_hours.toFixed(1) }}h</h3>
            <p>Avg. Duration</p>
          </div>
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid">
        <!-- Revenue Trends -->
        <div class="chart-section full-width">
          <div class="section-controls">
            <h2>Revenue Trends</h2>
            <select v-model="revenuePeriod" @change="loadRevenueTrends" class="form-select">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
          <LineChart
            v-if="revenueTrends"
            :labels="revenueTrends.labels"
            :datasets="[{
              label: 'Daily Revenue',
              data: revenueTrends.revenue
            }]"
            :currency="true"
            theme="revenue"
            subtitle="Track daily revenue performance over time"
          />
        </div>

        <!-- Lot Performance -->
        <div class="chart-section">
          <BarChart
            v-if="lotPerformance"
            title="Lot Performance"
            subtitle="Bookings and revenue by parking lot"
            :labels="lotPerformance.labels"
            :datasets="[
              {
                label: 'Bookings',
                data: lotPerformance.bookings
              },
              {
                label: 'Revenue (₹)',
                data: lotPerformance.revenue
              }
            ]"
            theme="performance"
          />
        </div>

        <!-- Occupancy Trends -->
        <div class="chart-section">
          <BarChart
            v-if="occupancyTrends"
            title="Hourly Occupancy"
            subtitle="Peak usage times throughout the day"
            :labels="occupancyTrends.labels"
            :datasets="[{
              label: 'Bookings',
              data: occupancyTrends.bookings
            }]"
            theme="usage"
          />
        </div>

        <!-- Lot Revenue Distribution -->
        <div class="chart-section">
          <DoughnutChart
            v-if="lotPerformance"
            title="Revenue Distribution"
            subtitle="Revenue share by parking lot"
            :labels="lotPerformance.labels"
            :data="lotPerformance.revenue"
            :currency="true"
          />
        </div>

        <!-- Booking Distribution -->
        <div class="chart-section">
          <DoughnutChart
            v-if="lotPerformance"
            title="Booking Distribution"
            subtitle="Booking share by parking lot"
            :labels="lotPerformance.labels"
            :data="lotPerformance.bookings"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { removeToken } from '@/utils/auth'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

const router = useRouter()

// State
const loading = ref(true)
const overview = ref(null)
const revenueTrends = ref(null)
const lotPerformance = ref(null)
const occupancyTrends = ref(null)
const revenuePeriod = ref(30)

// Methods
const loadOverview = async () => {
  try {
    const response = await apiService.get('/analytics/admin/overview')
    if (response.success) {
      overview.value = response.data
    }
  } catch (error) {
    console.error('Failed to load overview:', error)
  }
}

const loadRevenueTrends = async () => {
  try {
    const response = await apiService.get(`/analytics/admin/revenue-trends?days=${revenuePeriod.value}`)
    if (response.success) {
      revenueTrends.value = response.data
    }
  } catch (error) {
    console.error('Failed to load revenue trends:', error)
  }
}

const loadLotPerformance = async () => {
  try {
    const response = await apiService.get('/analytics/admin/lot-performance')
    if (response.success) {
      lotPerformance.value = response.data
    }
  } catch (error) {
    console.error('Failed to load lot performance:', error)
  }
}

const loadOccupancyTrends = async () => {
  try {
    const response = await apiService.get('/analytics/admin/occupancy-trends')
    if (response.success) {
      occupancyTrends.value = response.data
    }
  } catch (error) {
    console.error('Failed to load occupancy trends:', error)
  }
}

const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadRevenueTrends(),
      loadLotPerformance(),
      loadOccupancyTrends()
    ])
  } finally {
    loading.value = false
  }
}

// Navigation
const handleLogout = () => {
  removeToken()
  router.push('/')
}

// Lifecycle
onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
/* Navigation Styles */
.admin-navbar {
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  margin-bottom: 2rem;
}

.admin-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.admin-brand .brand-link {
  color: #e2e8f0;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  transition: color 0.3s ease;
}

.admin-brand .brand-link:hover {
  color: #3b82f6;
}

.brand-highlight {
  color: #3b82f6;
}

.admin-nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-user-info {
  color: #94a3b8;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

.btn-outline-light {
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e2e8f0;
  background: transparent;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.admin-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
}
.admin-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
}

.analytics-content {
  padding: 0 2rem 2rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.analytics-header {
  margin-bottom: 2rem;
  text-align: center;
}

.analytics-header h1 {
  color: #ffffff;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.analytics-header p {
  color: #94a3b8;
  font-size: 1.1rem;
  margin: 0;
}

.loading-state {
  text-align: center;
  padding: 4rem 0;
  color: #94a3b8;
}

.loading-state .spinner-border {
  margin-bottom: 1rem;
}

/* Overview Cards */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.metric-card.revenue .metric-icon {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.metric-card.bookings .metric-icon {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.metric-card.active .metric-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.metric-card.users .metric-icon {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.metric-card.duration .metric-icon {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  color: white;
}

.metric-content h3 {
  color: #ffffff;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.metric-content p {
  color: #94a3b8;
  margin: 0;
  font-size: 0.9rem;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-section.full-width {
  grid-column: 1 / -1;
}

.section-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-controls h2 {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  max-width: 150px;
}

.form-select:focus {
  background: rgba(255, 255, 255, 0.15);
  border-color: #3b82f6;
  box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25);
  color: #ffffff;
}

.form-select option {
  background: #1e293b;
  color: #ffffff;
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-analytics {
    padding: 1rem;
  }
  
  .analytics-header h1 {
    font-size: 2rem;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .section-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
