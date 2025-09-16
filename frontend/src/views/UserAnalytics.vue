<template>
  <div class="user-analytics">
<!------------------ Navigation Header------------------------ -->
    <nav class="user-navbar">
      <div class="container-fluid">
        <div class="user-nav-content">
          <div class="user-brand">
            <router-link to="/user/dashboard" class="brand-link">
              <i class="bi bi-arrow-left me-2"></i>
              <span class="brand-highlight">Back to Dashboard</span>
            </router-link>
          </div>
          
          <div class="user-nav-actions">
            <div class="user-info">
              <i class="bi bi-person-circle me-2"></i>
              <span>{{ user?.fullname || 'User' }}</span>
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
      <div class="header-content">
        <div class="header-text">
          <h1>
            <i class="bi bi-graph-up me-3"></i>My Parking Analytics
          </h1>
          <p>Insights into your parking habits and spending patterns</p>
        </div>
        <div class="header-actions">
          <button 
            @click="initiateExport" 
            :disabled="exportLoading"
            class="btn btn-export"
            :class="{ 'loading': exportLoading }"
          >
            <i v-if="!exportLoading" class="bi bi-download me-2"></i>
            <div v-else class="spinner-border spinner-border-sm me-2" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            {{ exportLoading ? 'Generating...' : 'Export Data' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner-border text-primary" role="status"></div>
      <p>Loading your analytics data...</p>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">

<!----------------- Overview Cards --------------------------->
      <div class="overview-cards" v-if="overview">
        <div class="metric-card spending">
          <div class="metric-icon">
            <i class="bi bi-currency-rupee"></i>
          </div>
          <div class="metric-content">
            <h3>₹{{ overview.total_spent.toLocaleString() }}</h3>
            <p>Total Spent</p>
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

        <div class="metric-card average">
          <div class="metric-icon">
            <i class="bi bi-calculator"></i>
          </div>
          <div class="metric-content">
            <h3>₹{{ overview.avg_cost_per_booking.toFixed(0) }}</h3>
            <p>Avg. Cost/Booking</p>
          </div>
        </div>

        <div class="metric-card favorite">
          <div class="metric-icon">
            <i class="bi bi-heart-fill"></i>
          </div>
          <div class="metric-content">
            <h3>{{ overview.favorite_lot || 'None' }}</h3>
            <p>Favorite Lot</p>
          </div>
        </div>
      </div>

<!----------------------- Charts Grid -------------------------------->
      <div class="charts-grid">
        <!-- Spending Trends -->
        <div class="chart-section full-width">
          <div class="section-controls">
            <h2>Your Spending Trends</h2>
            <select v-model="spendingPeriod" @change="loadSpendingTrends" class="form-select">
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
          </div>
          <LineChart
            v-if="spendingTrends"
            :labels="spendingTrends.labels"
            :datasets="[{
              label: 'Daily Spending',
              data: spendingTrends.spending
            }]"
            :currency="true"
            theme="revenue"
            subtitle="Track your daily parking expenses over time"
          />
        </div>

        <!-- Lot Usage -->
        <div class="chart-section">
          <BarChart
            v-if="lotUsage"
            title="Parking Lot Usage"
            subtitle="Your bookings and spending by location"
            :labels="lotUsage.labels"
            :datasets="[
              {
                label: 'Bookings',
                data: lotUsage.bookings
              },
              {
                label: 'Spending (₹)',
                data: lotUsage.spending
              }
            ]"
            theme="performance"
          />
        </div>

        <!-- Spending Distribution -->
        <div class="chart-section">
          <DoughnutChart
            v-if="lotUsage && lotUsage.spending.length > 0"
            title="Spending Distribution"
            subtitle="How much you spend at each location"
            :labels="lotUsage.labels"
            :data="lotUsage.spending"
            :currency="true"
          />
        </div>

        <!-- Booking Distribution -->
        <div class="chart-section">
          <DoughnutChart
            v-if="lotUsage && lotUsage.bookings.length > 0"
            title="Booking Distribution"
            subtitle="Your preferred parking locations"
            :labels="lotUsage.labels"
            :data="lotUsage.bookings"
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
import { getUser, removeToken } from '@/utils/auth'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

const router = useRouter()
const user = ref(getUser())

// State
const loading = ref(true)
const overview = ref(null)
const spendingTrends = ref(null)
const lotUsage = ref(null)
const spendingPeriod = ref(30)

// Export functionality
const exportLoading = ref(false)

// Methods
const loadOverview = async () => {
  try {
    const response = await apiService.get('/analytics/user/spending-overview')
    if (response.success) {
      overview.value = response.data
    }
  } catch (error) {
    console.error('Failed to load overview:', error)
  }
}

const loadSpendingTrends = async () => {
  try {
    const response = await apiService.get(`/analytics/user/spending-trends?days=${spendingPeriod.value}`)
    if (response.success) {
      spendingTrends.value = response.data
    }
  } catch (error) {
    console.error('Failed to load spending trends:', error)
  }
}

const loadLotUsage = async () => {
  try {
    const response = await apiService.get('/analytics/user/lot-usage')
    if (response.success) {
      lotUsage.value = response.data
    }
  } catch (error) {
    console.error('Failed to load lot usage:', error)
  }
}

const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadOverview(),
      loadSpendingTrends(),
      loadLotUsage()
    ])
  } finally {
    loading.value = false
  }
}

// Export functionality
const initiateExport = async () => {
  try {
    exportLoading.value = true
    
    const response = await apiService.exportData('all')
    
    if (response.success) {
      alert('✅ Export initiated successfully! You will receive an email with your data shortly.')
    } else {
      alert(`❌ ${response.error || 'Failed to initiate export'}`)
    }
    
  } catch (error) {
    console.error('Export error:', error)
    alert('❌ An unexpected error occurred while initiating export')
  } finally {
    exportLoading.value = false
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
.user-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
}

/* Navigation */
.user-navbar {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.user-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-brand .brand-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  transition: color 0.3s ease;
}

.user-brand .brand-link:hover {
  color: #3b82f6;
}

.brand-highlight {
  color: #3b82f6;
}

.user-nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  color: #e2e8f0;
  font-size: 0.9rem;
}

.analytics-content {
  padding: 0 2rem 2rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.analytics-header {
  padding: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-text {
  text-align: left;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.analytics-header h1 {
  color: #ffffff;
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.analytics-header p {
  color: #94a3b8;
  font-size: 1.1rem;
  margin: 0;
}

/* Export Button */
.btn-export {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
}

.btn-export:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-export.loading {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
}

/* Responsive header */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-text {
    text-align: center;
  }
  
  .analytics-header h1 {
    font-size: 2rem;
  }
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

.metric-card.spending .metric-icon {
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

.metric-card.average .metric-icon {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.metric-card.favorite .metric-icon {
  background: linear-gradient(135deg, #ec4899, #db2777);
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
</style>
