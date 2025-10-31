<!--
==============================================================================
                              ADMIN DASHBOARD
                          Administrative Control Panel
==============================================================================
Description: Complete admin interface for managing the parking system
Features: User management, parking lot management, analytics, system monitoring
Access: Admin role required - full control over the platform
==============================================================================
-->

<template>
  <div class="admin-dashboard">
    
    <!-- Admin navigation bar with admin badge and controls -->
    <nav class="admin-navbar">
      <div class="container-fluid">
        <div class="admin-nav-content">
          <div class="admin-brand">
            <router-link to="/" class="brand-link">
              <i class="bi bi-p-circle-fill me-2"></i>
              <span class="brand-highlight">Only</span>Parks
            </router-link>
            <span class="admin-badge">
              <i class="bi bi-shield-check-fill me-1"></i>Admin
            </span>
          </div>
          
          <div class="admin-nav-actions">
            <div class="admin-user-info">
              <i class="bi bi-person-circle me-2"></i>
              <span>{{ user?.fullname || 'Admin' }}</span>
            </div>
            <button @click="handleLogout" class="btn btn-outline-light btn-sm">
              <i class="bi bi-box-arrow-right me-2"></i>Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Dashboard Content -->
    <div class="admin-content">
      <div class="container-fluid">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
          <h1 class="dashboard-title">
            <i class="bi bi-speedometer2 me-3"></i>Admin Dashboard
          </h1>
          <p class="dashboard-subtitle">Manage parking lots and monitor system performance</p>
        </div>

        <!-- Navigation Tabs -->
        <div class="admin-nav-tabs">
          <button 
            class="nav-tab active"
            @click="currentTab = 'dashboard'"
            :class="{ active: currentTab === 'dashboard' }"
          >
            <i class="bi bi-speedometer2 me-2"></i>Dashboard
          </button>
          <button 
            class="nav-tab"
            @click="navigateToAnalytics"
            :class="{ active: currentTab === 'analytics' }"
          >
            <i class="bi bi-graph-up me-2"></i>Analytics
          </button>
        </div>

        <!-- Statistics Cards -->
        <div class="stats-grid" v-if="stats">
          <div class="stat-card">
            <div class="stat-icon users">
              <i class="bi bi-people-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_users }}</h3>
              <p>Total Users</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon lots">
              <i class="bi bi-building-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_lots }}</h3>
              <p>Parking Lots</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon spots">
              <i class="bi bi-car-front-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_spots }}</h3>
              <p>Total Spots</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon revenue">
              <i class="bi bi-currency-dollar"></i>
            </div>
            <div class="stat-content">
              <h3>₹{{ (stats.total_revenue || 0).toFixed(2) }}</h3>
              <p>Total Revenue</p>
            </div>
          </div>
        </div>

<!---------------- Parking Lots Management Section ------------------>
        <div class="management-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-building me-2"></i>Parking Lots Management
            </h2>
            <button @click="showCreateModal = true" class="btn btn-primary">
              <i class="bi bi-plus-circle-fill me-2"></i>Add New Lot
            </button>
          </div>

      <!------------- Lots Card ------------------->
          <div class="lots-grid" v-if="lots && lots.length > 0">
            <div v-for="lot in lots" :key="lot.id" class="lot-card">
              <div class="lot-header">
                <h4>{{ lot.name }}</h4>
                <div class="lot-actions">
                  <button @click="editLot(lot)" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-pencil-fill"></i>
                  </button>
                  <button @click="deleteLot(lot)" class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </div>
              </div>
              
              <div class="lot-details">
                <p class="lot-location">
                  <i class="bi bi-geo-alt-fill me-2"></i>{{ lot.prime_location_name }}
                </p>
                <p class="lot-price">
                  <i class="bi bi-currency-rupee me-2"></i>₹{{ lot.price }}/hour
                </p>
                <p class="lot-pincode">
                  <i class="bi bi-mailbox-flag me-2"></i>{{ lot.pincode }}
                </p>
              </div>
              
              <div class="lot-stats">
                <div class="stat-item available">
                  <span class="stat-number">{{ lot.available_spots }}</span>
                  <span class="stat-label">Available</span>
                </div>
                <div class="stat-item occupied">
                  <span class="stat-number">{{ lot.occupied_spots }}</span>
                  <span class="stat-label">Occupied</span>
                </div>
                <div class="stat-item total">
                  <span class="stat-number">{{ lot.no_of_spots }}</span>
                  <span class="stat-label">Total</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="empty-state">
            <i class="bi bi-building-slash"></i>
            <h3>No Parking Lots Yet</h3>
            <p>Start by creating your first parking lot to manage spots and reservations.</p>
            <button @click="showCreateModal = true" class="btn btn-primary">
              <i class="bi bi-plus-circle-fill me-2"></i>Create First Lot
            </button>
          </div>
        </div>

<!------------------- Real-time Spots Status Section ------------------->
        <div class="spots-status-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-eye-fill me-2"></i>Real-time Spot Status
            </h2>
            <div class="section-actions">
              <button @click="loadSpotsStatus" class="btn btn-outline-primary btn-sm" :disabled="spotsLoading">
                <i class="bi bi-arrow-clockwise me-2"></i>
                {{ spotsLoading ? 'Refreshing...' : 'Refresh' }}
              </button>
            </div>
          </div>

          <!-- Filters -->
          <div class="filters-section">
            <div class="filter-group">
              <label>
                <i class="bi bi-building me-2"></i>Filter by Lot:
              </label>
              <select v-model="filterLot" class="filter-select">
                <option value="">All Lots</option>
                <option v-for="lot in lots" :key="lot.id" :value="lot.id">{{ lot.name }}</option>
              </select>
            </div>
            
            <div class="filter-group">
              <label>
                <i class="bi bi-funnel me-2"></i>Filter by Status:
              </label>
              <select v-model="filterStatus" class="filter-select">
                <option value="">All Status</option>
                <option value="A">Available</option>
                <option value="O">Occupied</option>
              </select>
            </div>

            <div class="search-group">
              <label>
                <i class="bi bi-search me-2"></i>Search:
              </label>
              <input
                v-model="searchQuery"
                type="text"
                class="filter-input"
                placeholder="Search by vehicle no, user name, lot name, spot no, or location..."
              >
            </div>
          </div>

          <!-- Summary Stats -->
          <div v-if="spotsSummary" class="spots-summary">
            <div class="summary-card">
              <i class="bi bi-car-front-fill"></i>
              <span class="summary-number">{{ spotsSummary.total_spots }}</span>
              <span class="summary-label">Total Spots</span>
            </div>
            <div class="summary-card available">
              <i class="bi bi-check-circle-fill"></i>
              <span class="summary-number">{{ spotsSummary.available_spots }}</span>
              <span class="summary-label">Available</span>
            </div>
            <div class="summary-card occupied">
              <i class="bi bi-x-circle-fill"></i>
              <span class="summary-number">{{ spotsSummary.occupied_spots }}</span>
              <span class="summary-label">Occupied</span>
            </div>
            <div class="summary-card rate">
              <i class="bi bi-percent"></i>
              <span class="summary-number">{{ spotsSummary.occupancy_rate }}%</span>
              <span class="summary-label">Occupancy Rate</span>
            </div>
          </div>

          <!-- Spots Grid -->
          <div v-if="filteredSpots && filteredSpots.length > 0" class="spots-grid">
            <div
              v-for="spot in filteredSpots"
              :key="spot.spot_id"
              class="spot-card"
              :class="{ 'occupied': spot.status === 'O', 'available': spot.status === 'A' }"
            >
              <div class="spot-header">
                <div class="spot-info">
                  <span class="spot-number">{{ spot.lot_name }}-{{ spot.spot_number }}</span>
                  <span class="spot-status" :class="spot.status === 'O' ? 'occupied' : 'available'">
                    <i :class="spot.status === 'O' ? 'bi bi-car-front-fill' : 'bi bi-check-circle'"></i>
                    {{ spot.status === 'O' ? 'Occupied' : 'Available' }}
                  </span>
                </div>
              </div>
              
              <div class="spot-details">
                <p class="spot-location">
                  <i class="bi bi-geo-alt me-2"></i>{{ spot.location }}
                </p>
                
                <div v-if="spot.status === 'O'" class="occupancy-details">
                  <p class="vehicle-info">
                    <i class="bi bi-car-front me-2"></i>
                    <strong>{{ spot.vehicle_number }}</strong>
                  </p>
                  <p class="user-info">
                    <i class="bi bi-person me-2"></i>
                    {{ spot.user_name }}
                  </p>
                </div>
                
                <div v-else class="availability-info">
                  <p class="available-text">
                    <i class="bi bi-check-circle me-2"></i>
                    Ready for booking
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="!spotsLoading" class="empty-spots-state">
            <i class="bi bi-car-front-fill"></i>
            <h3>No Spots Found</h3>
            <p>{{ allSpots.length === 0 ? 'No parking spots available in the system.' : 'No spots match your current filters.' }}</p>
          </div>

          <!-- Loading State -->
          <div v-if="spotsLoading" class="spots-loading">
            <i class="bi bi-arrow-clockwise"></i>
            <p>Loading spots status...</p>
          </div>
        </div>
      </div>
    </div>

<!---------------- Create/Edit Lot Modal ------------------->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="bi bi-building-add me-2"></i>
            {{ showEditModal ? 'Edit Parking Lot' : 'Create New Parking Lot' }}
          </h3>
          <button @click="closeModals" class="modal-close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <form @submit.prevent="submitLot" class="modal-body">
          <div class="form-group">
            <label>
              <i class="bi bi-building-fill me-2"></i>Lot Name
            </label>
            <input
              type="text"
              v-model="lotForm.name"
              class="form-input"
              placeholder="Enter parking lot name"
              required
            >
          </div>
          
          <div class="form-group">
            <label>
              <i class="bi bi-geo-alt-fill me-2"></i>Prime Location
            </label>
            <input
              type="text"
              v-model="lotForm.prime_location_name"
              class="form-input"
              placeholder="e.g., City Center, Mall, Airport"
              required
            >
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>
                <i class="bi bi-currency-rupee me-2"></i>Price per Hour
              </label>
              <input
                type="number"
                v-model="lotForm.price"
                class="form-input"
                placeholder="0.00"
                step="0.01"
                min="0"
                required
              >
            </div>
            
            <div class="form-group">
              <label>
                <i class="bi bi-car-front-fill me-2"></i>Number of Spots
              </label>
              <input
                type="number"
                v-model="lotForm.no_of_spots"
                class="form-input"
                placeholder="50"
                min="1"
                max="1000"
                required
              >
            </div>
          </div>
          
          <div class="form-group">
            <label>
              <i class="bi bi-mailbox-flag me-2"></i>Pincode
            </label>
            <input
              type="number"
              v-model="lotForm.pincode"
              class="form-input"
              placeholder="123456"
              min="100000"
              max="999999"
              required
            >
          </div>
          
          <div v-if="lotError" class="error-message">
            {{ lotError }}
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="closeModals" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="lotLoading">
              <i class="bi bi-check-circle-fill me-2"></i>
              {{ lotLoading ? 'Saving...' : (showEditModal ? 'Update Lot' : 'Create Lot') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <i class="bi bi-arrow-clockwise"></i>
        <p>Loading dashboard...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api'
import { getUser, removeToken } from '@/utils/auth'

const router = useRouter()
const user = ref(getUser())

// Navigation state
const currentTab = ref('dashboard')

// Data
const loading = ref(true)
const stats = ref(null)
const lots = ref([])

// Spots status data
const spotsLoading = ref(false)
const allSpots = ref([])
const spotsSummary = ref(null)
const filterLot = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

// Modal states
const showCreateModal = ref(false)
const showEditModal = ref(false)
const lotLoading = ref(false)
const lotError = ref('')
const editingLot = ref(null)

// Form data
const lotForm = reactive({
  name: '',
  prime_location_name: '',
  price: '',
  no_of_spots: '',
  pincode: ''
})

// Computed properties
const filteredSpots = computed(() => {
  let filtered = allSpots.value

  // Filter by lot
  if (filterLot.value) {
    filtered = filtered.filter(spot => spot.lot_id === parseInt(filterLot.value))
  }

  // Filter by status
  if (filterStatus.value) {
    filtered = filtered.filter(spot => spot.status === filterStatus.value)
  }

  // Search by vehicle number or user name
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(spot => {
      // Search in vehicle number (only for occupied spots)
      if (spot.vehicle_number && spot.vehicle_number.toLowerCase().includes(query)) {
        return true
      }
      
      // Search in user name (only for occupied spots)
      if (spot.user_name && spot.user_name.toLowerCase().includes(query)) {
        return true
      }
    })
  }

  return filtered
})

// Methods
// Spots status methods
const loadSpotsStatus = async () => {
  try {
    console.log('Loading spots status...')
    spotsLoading.value = true
    const response = await apiService.get('/admin/spots/status')
    
    console.log('Spots API response:', response)
    
    if (response.success) {
      allSpots.value = response.data.spots || []
      spotsSummary.value = response.data.summary || null
      console.log('Loaded spots:', allSpots.value.length)
      console.log('Summary:', spotsSummary.value)
    } else {
      console.error('Failed to load spots status:', response.error)
      allSpots.value = []
      spotsSummary.value = null
    }
  } catch (error) {
    console.error('Error loading spots status:', error)
    allSpots.value = []
    spotsSummary.value = null
  } finally {
    spotsLoading.value = false
  }
}

const formatParkingTime = (timestamp) => {
  if (!timestamp) return 'Unknown'
  
  const now = new Date()
  const parkedTime = new Date(timestamp)
  const diff = now - parkedTime
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ago`
  } else {
    return `${minutes}m ago`
  }
}

// Existing methods
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Load stats and lots sequentially to avoid overwhelming the server
    const statsResponse = await apiService.get('/admin/dashboard-stats')
    const lotsResponse = await apiService.get('/admin/lots')
    
    if (statsResponse.success) {
      stats.value = statsResponse.data
    } else {
      console.error('Failed to load stats:', statsResponse.error)
      // Set default stats if failed
      stats.value = {
        total_users: 0,
        total_lots: 0,
        total_spots: 0,
        occupied_spots: 0,
        available_spots: 0,
        total_revenue: 0,
        recent_bookings: []
      }
    }
    
    if (lotsResponse.success) {
      lots.value = lotsResponse.data.lots || []
    } else {
      console.error('Failed to load lots:', lotsResponse.error)
      lots.value = []
    }
    
  } catch (error) {
    console.error('Failed to load dashboard:', error)
    // Set default values
    stats.value = {
      total_users: 0,
      total_lots: 0,
      total_spots: 0,
      occupied_spots: 0,
      available_spots: 0,
      total_revenue: 0,
      recent_bookings: []
    }
    lots.value = []
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.keys(lotForm).forEach(key => {
    lotForm[key] = ''
  })
  lotError.value = ''
  editingLot.value = null
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  resetForm()
}

const editLot = (lot) => {
  editingLot.value = lot
  Object.keys(lotForm).forEach(key => {
    lotForm[key] = lot[key] || ''
  })
  showEditModal.value = true
}

const submitLot = async () => {
  try {
    lotLoading.value = true
    lotError.value = ''
    
    const lotData = { ...lotForm }
    
    let response
    if (showEditModal.value) {
      response = await apiService.put(`/admin/lots/${editingLot.value.id}`, lotData)
    } else {
      response = await apiService.post('/admin/lots', lotData)
    }
    
    if (response.success) {
      closeModals()
      await loadDashboardData() // Refresh data
    } else {
      lotError.value = response.error || 'Failed to save parking lot'
    }
    
  } catch (error) {
    lotError.value = 'An unexpected error occurred'
  } finally {
    lotLoading.value = false
  }
}

const deleteLot = async (lot) => {
  if (!confirm(`Are you sure you want to delete "${lot.name}"? This action cannot be undone.`)) {
    return
  }
  
  try {
    const response = await apiService.delete(`/admin/lots/${lot.id}`)
    
    if (response.success) {
      await loadDashboardData() // Refresh data
    } else {
      alert(response.error || 'Failed to delete parking lot')
    }
    
  } catch (error) {
    alert('An unexpected error occurred')
  }
}

// Navigation
const navigateToAnalytics = () => {
  router.push('/admin/analytics')
}

const handleLogout = () => {
  removeToken()
  router.push('/')
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
  loadSpotsStatus()
})
</script>

<style scoped>
/* Admin Dashboard Styles */
.admin-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  color: #ffffff;
  font-family: 'Inter', sans-serif;
}

/* Admin Navigation */
.admin-navbar {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.admin-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-link {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
  transition: transform 0.3s ease;
}

.brand-link:hover {
  transform: scale(1.05);
}

.admin-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.admin-nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-user-info {
  display: flex;
  align-items: center;
  font-weight: 500;
  opacity: 0.9;
}

/* Dashboard Content */
.admin-content {
  padding: 2rem 0;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-subtitle {
  font-size: 1.1rem;
  opacity: 0.8;
  margin: 0;
}

/* Navigation Tabs */
.admin-nav-tabs {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 3rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 3rem;
}

.nav-tab {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.nav-tab.active {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.nav-tab i {
  font-size: 1rem;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-icon.users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.lots { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.spots { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.revenue { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
}

.stat-content p {
  margin: 0;
  opacity: 0.8;
}

/* Management Section */
.management-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

/* Lots Grid */
.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.lot-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.lot-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.lot-header h4 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #667eea;
}

.lot-actions {
  display: flex;
  gap: 0.5rem;
}

.lot-details p {
  margin: 0.5rem 0;
  display: flex;
  align-items: center;
  opacity: 0.9;
}

.lot-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.8;
}

.stat-item.available .stat-number { color: #43e97b; }
.stat-item.occupied .stat-number { color: #f5576c; }
.stat-item.total .stat-number { color: #4facfe; }

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem;
  opacity: 0.8;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #667eea;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.08);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* Buttons */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-outline-primary {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-outline-primary:hover {
  background: #667eea;
  color: white;
}

.btn-outline-danger {
  background: transparent;
  color: #f5576c;
  border: 1px solid #f5576c;
}

.btn-outline-danger:hover {
  background: #f5576c;
  color: white;
}

.btn-outline-light {
  background: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-outline-light:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

/* Error Message */
.error-message {
  background: rgba(245, 87, 108, 0.1);
  border: 1px solid rgba(245, 87, 108, 0.3);
  border-radius: 8px;
  padding: 1rem;
  color: #f5576c;
  margin-bottom: 1rem;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 15, 35, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
}

.loading-spinner i {
  font-size: 3rem;
  animation: spin 1s linear infinite;
  color: #667eea;
  margin-bottom: 1rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Spots Status Section */
.spots-status-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 2rem;
}

.section-actions {
  display: flex;
  gap: 0.5rem;
}

/* Filters Section */
.filters-section {
  display: grid;
  grid-template-columns: 1fr 1fr 2fr;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.filter-group,
.search-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label,
.search-group label {
  font-weight: 500;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.filter-select,
.filter-input {
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
}

.filter-select option {
  background: #1a1a2e;
  color: #ffffff;
}

/* Summary Stats */
.spots-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
}

.summary-card i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #667eea;
}

.summary-card.available i {
  color: #10b981;
}

.summary-card.occupied i {
  color: #f59e0b;
}

.summary-card.rate i {
  color: #8b5cf6;
}

.summary-number {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.summary-label {
  display: block;
  font-size: 0.875rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Spots Grid */
.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.spot-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.spot-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
}

.spot-card.occupied {
  border-left: 4px solid #f59e0b;
}

.spot-card.available {
  border-left: 4px solid #10b981;
}

.spot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.spot-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.spot-number {
  font-size: 1.125rem;
  font-weight: 700;
  color: #ffffff;
}

.spot-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.spot-status.occupied {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.spot-status.available {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.spot-details p {
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: #cbd5e1;
}

.spot-details p:last-child {
  margin-bottom: 0;
}

.vehicle-info strong {
  color: #ffffff;
  font-weight: 600;
}

.user-info {
  color: #94a3b8;
}

.time-info {
  color: #64748b;
  font-size: 0.8rem;
}

.available-text {
  color: #34d399;
  font-style: italic;
}

/* Empty State */
.empty-spots-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-spots-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #475569;
}

.empty-spots-state h3 {
  margin: 0 0 0.5rem 0;
  color: #94a3b8;
}

/* Loading State */
.spots-loading {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.spots-loading i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #667eea;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .admin-nav-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .admin-brand {
    flex-direction: column;
    text-align: center;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .lots-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    text-align: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .filters-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .spots-summary {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .spots-grid {
    grid-template-columns: 1fr;
  }
}
</style>
