<template>
  <div class="user-dashboard">
    <!-- User Navigation Header -->
    <nav class="user-navbar">
      <div class="container-fluid">
        <div class="user-nav-content">
          <div class="user-brand">
            <router-link to="/" class="brand-link">
              <i class="bi bi-p-circle-fill me-2"></i>
              <span class="brand-highlight">Only</span>Parks
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

    <!-- Main Dashboard Content -->
    <div class="user-content">
      <div class="container-fluid">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
          <h1 class="dashboard-title">
            <i class="bi bi-speedometer2 me-3"></i>My Parking Dashboard
          </h1>
          <p class="dashboard-subtitle">Find and book parking spots easily</p>
        </div>

        <!-- Navigation Tabs -->
        <div class="user-nav-tabs">
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
            <div class="stat-icon reservations">
              <i class="bi bi-calendar-check-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.total_reservations }}</h3>
              <p>Total Bookings</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon active">
              <i class="bi bi-car-front-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.active_reservations }}</h3>
              <p>Active Parking</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon spent">
              <i class="bi bi-currency-rupee"></i>
            </div>
            <div class="stat-content">
              <h3>₹{{ (stats.total_spent || 0).toFixed(2) }}</h3>
              <p>Total Spent</p>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon completed">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <div class="stat-content">
              <h3>{{ stats.completed_reservations }}</h3>
              <p>Completed</p>
            </div>
          </div>
        </div>

        <!-- Active Reservations Section -->
        <div v-if="activeReservations && activeReservations.length > 0" class="current-reservation-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-car-front-fill me-2"></i>Active Parking Sessions ({{ activeReservations.length }})
            </h2>
          </div>
          
          <div v-for="reservation in activeReservations" :key="reservation.id" class="current-reservation-card">
            <div class="reservation-grid">
              <!-- Location Column -->
              <div class="info-column location-column">
                <div class="column-header">
                  <i class="bi bi-geo-alt-fill"></i>
                  <span>Location</span>
                </div>
                <div class="column-content">
                  <h3>{{ reservation.lot_name }}</h3>
                  <p>{{ reservation.lot_location }}</p>
                </div>
              </div>

              <!-- Parking Details Column -->
              <div class="info-column details-column">
                <div class="column-header">
                  <i class="bi bi-info-circle-fill"></i>
                  <span>Parking Details</span>
                </div>
                <div class="column-content">
                  <div class="detail-row">
                    <span class="detail-label">Spot Number:</span>
                    <span class="spot-badge">{{ reservation.spot_number }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Vehicle:</span>
                    <span class="vehicle-badge">{{ reservation.vehicle_number }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Parked At:</span>
                    <span class="time-text">{{ formatDateTime(reservation.parking_time) }}</span>
                  </div>
                </div>
              </div>

              <!-- Cost & Duration Column -->
              <div class="info-column cost-column">
                <div class="column-header">
                  <i class="bi bi-currency-rupee"></i>
                  <span>Cost & Time</span>
                </div>
                <div class="column-content">
                  <div class="cost-item">
                    <div class="cost-value">₹{{ reservation.estimated_cost }}</div>
                    <div class="cost-label">Estimated Cost</div>
                  </div>
                  <div class="duration-item">
                    <div class="duration-value">{{ reservation.current_duration_hours }}h</div>
                    <div class="duration-label">Duration</div>
                  </div>
                  <div class="rate-item">
                    <span class="rate-text">₹{{ reservation.hourly_rate }}/hour</span>
                  </div>
                </div>
              </div>

              <!-- Actions Column -->
              <div class="info-column actions-column">
                <div class="column-header">
                  <i class="bi bi-gear-fill"></i>
                  <span>Actions</span>
                </div>
                <div class="column-content">
                  <button @click="releaseSpot(reservation.id)" class="btn btn-release" :disabled="releasing === reservation.id">
                    <i class="bi bi-stop-circle me-2"></i>
                    {{ releasing === reservation.id ? 'Releasing...' : 'Release Spot' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Parking Lots Section -->
        <div class="parking-lots-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-building me-2"></i>Available Parking Lots
            </h2>
            <button @click="loadParkingLots" class="btn btn-outline-primary btn-sm" :disabled="loading">
              <i class="bi bi-arrow-clockwise me-2"></i>
              {{ loading ? 'Loading...' : 'Refresh' }}
            </button>
          </div>

          <!-- Search and Filter -->
          <div class="search-section">
            <div class="search-input-group">
              <i class="bi bi-search"></i>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search parking lots..."
                class="search-input"
              >
            </div>
            <div class="filter-group">
              <label>Show:</label>
              <select v-model="availabilityFilter" class="filter-select">
                <option value="all">All Lots</option>
                <option value="available">Available Only</option>
              </select>
            </div>
          </div>

          <!-- Parking Lots Grid -->
          <div class="lots-grid" v-if="filteredLots && filteredLots.length > 0">
            <div v-for="lot in filteredLots" :key="lot.id" class="lot-card">
              <div class="lot-header">
                <h4>{{ lot.name }}</h4>
                <div class="availability-badge" :class="{ 'available': lot.is_available, 'full': !lot.is_available }">
                  <i :class="lot.is_available ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                  {{ lot.is_available ? 'Available' : 'Full' }}
                </div>
              </div>
              
              <div class="lot-details">
                <div class="detail-row">
                  <i class="bi bi-geo-alt me-2"></i>
                  <span>{{ lot.prime_location_name }}</span>
                </div>
                <div class="detail-row">
                  <i class="bi bi-currency-rupee me-2"></i>
                  <span>₹{{ lot.price }}/hour</span>
                </div>
                <div class="detail-row">
                  <i class="bi bi-car-front me-2"></i>
                  <span>{{ lot.available_spots }}/{{ lot.no_of_spots }} available</span>
                </div>
              </div>
              
              <div class="lot-actions">
                <button 
                  @click="selectLot(lot)" 
                  :disabled="!lot.is_available"
                  class="btn btn-primary"
                >
                  <i class="bi bi-plus-circle me-2"></i>
                  {{ !lot.is_available ? 'No Spots Available' : 'Book Now' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="!loading" class="empty-state">
            <i class="bi bi-building-slash"></i>
            <h3>No Parking Lots Found</h3>
            <p>{{ searchQuery ? 'No lots match your search criteria.' : 'No parking lots are currently available.' }}</p>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="loading-state">
            <i class="bi bi-arrow-clockwise"></i>
            <p>Loading parking lots...</p>
          </div>
        </div>

        <!-- Past Bookings Section -->
        <div class="booking-history-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-clock-history me-2"></i>Past Bookings
            </h2>
            <p class="section-subtitle">Your completed parking sessions</p>
          </div>

          <div v-if="reservations && reservations.length > 0" class="history-table">
            <div class="table-header">
              <div class="header-cell">Location</div>
              <div class="header-cell">Vehicle</div>
              <div class="header-cell">Date</div>
              <div class="header-cell">Duration</div>
              <div class="header-cell">Cost</div>
              <div class="header-cell">Status</div>
            </div>
            
            <div 
              v-for="reservation in reservations.slice(0, 10)" 
              :key="reservation.id" 
              class="table-row"
            >
              <div class="cell">
                <div class="lot-name">{{ reservation.lot_name }}</div>
                <div class="spot-info">Spot {{ reservation.spot_number }}</div>
              </div>
              <div class="cell">{{ reservation.vehicle_number }}</div>
              <div class="cell">{{ formatDate(reservation.parking_time) }}</div>
              <div class="cell">
                {{ reservation.duration_hours }}h
              </div>
              <div class="cell">₹{{ (reservation.cost || 0).toFixed(2) }}</div>
              <div class="cell">
                <span class="status-badge completed">
                  {{ reservation.status }}
                </span>
              </div>
            </div>
          </div>

          <div v-else class="empty-history">
            <i class="bi bi-clock-history"></i>
            <p>No completed bookings yet</p>
            <small>Your completed parking sessions will appear here</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>
            <i class="bi bi-plus-circle me-2"></i>Book Parking Spot
          </h3>
          <button @click="closeBookingModal" class="modal-close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="selected-lot-info" v-if="selectedLot">
            <h4>{{ selectedLot.name }}</h4>
            <p>{{ selectedLot.prime_location_name }}</p>
            <div class="lot-pricing">
              <i class="bi bi-currency-rupee me-2"></i>
              <span>₹{{ selectedLot.price }}/hour</span>
            </div>
          </div>
          
          <form @submit.prevent="bookSpot">
            <div class="form-group">
              <label>
                <i class="bi bi-car-front me-2"></i>Vehicle Number
              </label>
              <input
                type="text"
                v-model="bookingForm.vehicle_number"
                class="form-input"
                placeholder="e.g., DL01AB1234"
                required
                pattern="[A-Za-z0-9]+"
                title="Please enter a valid vehicle number"
              >
            </div>
            
            <div v-if="bookingError" class="error-message">
              {{ bookingError }}
            </div>
            
            <div class="modal-actions">
              <button type="button" @click="closeBookingModal" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" :disabled="bookingLoading" class="btn btn-primary">
                <i class="bi bi-check-circle me-2"></i>
                {{ bookingLoading ? 'Booking...' : 'Confirm Booking' }}
              </button>
            </div>
          </form>
        </div>
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
const releasing = ref(null) // Changed to track specific reservation ID being released
const stats = ref(null)
const parkingLots = ref([])
const reservations = ref([])
const activeReservations = ref([]) // Changed from currentReservation to activeReservations array

// Modal and booking
const showBookingModal = ref(false)
const selectedLot = ref(null)
const bookingLoading = ref(false)
const bookingError = ref('')

// Search and filters
const searchQuery = ref('')
const availabilityFilter = ref('available')

// Form data
const bookingForm = reactive({
  vehicle_number: ''
})

// Computed properties
const filteredLots = computed(() => {
  let filtered = parkingLots.value

  // Filter by availability
  if (availabilityFilter.value === 'available') {
    filtered = filtered.filter(lot => lot.is_available)
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(lot => 
      lot.name.toLowerCase().includes(query) ||
      lot.prime_location_name.toLowerCase().includes(query)
    )
  }

  return filtered
})

// Methods
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Reset active reservations first
    activeReservations.value = []
    
    // Load all data in parallel
    const timestamp = Date.now()
    const [statsResponse, lotsResponse, reservationsResponse, activeResponse] = await Promise.all([
      apiService.get(`/user/dashboard-stats?t=${timestamp}`),
      apiService.get(`/user/lots?t=${timestamp}`),
      apiService.get(`/user/reservations?t=${timestamp}`),
      apiService.get(`/user/active-reservations?t=${timestamp}`)
    ])
    
    if (statsResponse.success) {
      stats.value = statsResponse.data
    }
    
    if (lotsResponse.success) {
      parkingLots.value = lotsResponse.data.lots || []
    }
    
    if (reservationsResponse.success) {
      reservations.value = reservationsResponse.data.reservations || []
    }
    
    if (activeResponse.success && activeResponse.data && activeResponse.data.active_reservations) {
      console.log('Active reservations API response:', activeResponse.data)
      activeReservations.value = activeResponse.data.active_reservations
      console.log('Set activeReservations to:', activeReservations.value)
    } else {
      console.log('No active reservations or API failed:', activeResponse)
      activeReservations.value = []
    }
    
  } catch (error) {
    console.error('Failed to load dashboard:', error)
    // Ensure activeReservations is empty on error
    activeReservations.value = []
  } finally {
    loading.value = false
  }
}

const loadParkingLots = async () => {
  try {
    loading.value = true
    const response = await apiService.get('/user/lots')
    
    if (response.success) {
      parkingLots.value = response.data.lots || []
    }
  } catch (error) {
    console.error('Failed to load parking lots:', error)
  } finally {
    loading.value = false
  }
}

const selectLot = (lot) => {
  selectedLot.value = lot
  bookingForm.vehicle_number = ''
  bookingError.value = ''
  showBookingModal.value = true
}

const closeBookingModal = () => {
  showBookingModal.value = false
  selectedLot.value = null
  bookingForm.vehicle_number = ''
  bookingError.value = ''
}

const bookSpot = async () => {
  try {
    bookingLoading.value = true
    bookingError.value = ''
    
    const response = await apiService.post('/user/book-spot', {
      lot_id: selectedLot.value.id,
      vehicle_number: bookingForm.vehicle_number
    })
    
    if (response.success) {
      closeBookingModal()
      await loadDashboardData() // Refresh all data
      alert('Parking spot booked successfully!')
    } else {
      bookingError.value = response.error || 'Failed to book parking spot'
    }
    
  } catch (error) {
    bookingError.value = 'An unexpected error occurred'
  } finally {
    bookingLoading.value = false
  }
}

const releaseSpot = async (reservationId) => {
  if (!reservationId) {
    alert('Error: No reservation ID provided')
    return
  }
  
  if (!confirm('Are you sure you want to release your parking spot?')) {
    return
  }
  
  try {
    releasing.value = reservationId // Set which reservation is being released
    
    const response = await apiService.post(`/user/release-spot/${reservationId}`)
    
    if (response.success) {
      await loadDashboardData() // Refresh all data
      alert(`Spot released! Duration: ${response.data.duration_hours}h, Cost: ₹${response.data.final_cost}`)
    } else {
      alert(response.error || 'Failed to release parking spot')
    }
    
  } catch (error) {
    console.error('Release error:', error)
    alert('An unexpected error occurred')
  } finally {
    releasing.value = null // Clear releasing state
  }
}

const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString()
}

// Navigation
const navigateToAnalytics = () => {
  router.push('/user/analytics')
}

const handleLogout = () => {
  removeToken()
  router.push('/')
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
/* User Dashboard Styles */
.user-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  color: #ffffff;
  font-family: 'Inter', sans-serif;
}

/* User Navigation */
.user-navbar {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
}

.user-nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.user-brand .brand-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
}

.brand-highlight {
  color: #667eea;
}

.user-nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  color: #e2e8f0;
  font-size: 0.9rem;
}

/* Main Content */
.user-content {
  padding: 2rem 0;
}

.container-fluid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Dashboard Header */
.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.dashboard-subtitle {
  font-size: 1.1rem;
  color: #94a3b8;
  margin: 0;
}

/* Navigation Tabs */
.user-nav-tabs {
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
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.08);
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

.stat-icon.reservations {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-icon.active {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.stat-icon.spent {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
}

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
  color: #ffffff;
}

.stat-content p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Current Reservation Section */
.current-reservation-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
}

.section-subtitle {
  margin: 0.5rem 0 0 0;
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 400;
}

.current-reservation-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 0;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #f59e0b;
  overflow: hidden;
}

.reservation-grid {
  display: grid;
  grid-template-columns: 2fr 2fr 1.5fr 1fr;
  gap: 0;
  min-height: 180px;
}

.info-column {
  padding: 1.5rem;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.info-column:last-child {
  border-right: none;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.column-header i {
  font-size: 1rem;
}

.column-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* Location Column */
.location-column .column-content h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.location-column .column-content p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

/* Details Column */
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.detail-label {
  color: #94a3b8;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.spot-badge {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.vehicle-badge {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.85rem;
}

.time-text {
  color: #e2e8f0;
  font-size: 0.85rem;
}

/* Cost Column */
.cost-item, .duration-item {
  text-align: center;
  margin-bottom: 1rem;
}

.cost-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #10b981;
  margin-bottom: 0.25rem;
}

.cost-label {
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.duration-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #3b82f6;
  margin-bottom: 0.25rem;
}

.duration-label {
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.rate-item {
  text-align: center;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.rate-text {
  color: #f59e0b;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Actions Column */
.actions-column {
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-release {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 120px;
}

.btn-release:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-release:disabled {
  background: #64748b;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .reservation-grid {
    grid-template-columns: 1fr;
    gap: 1px;
  }
  
  .info-column {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 1rem;
  }
  
  .info-column:last-child {
    border-bottom: none;
  }
  
  .actions-column {
    background: rgba(255, 255, 255, 0.05);
  }
}

/* Parking Lots Section */
.parking-lots-section {
  margin-bottom: 3rem;
}

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.search-input-group {
  flex: 1;
  position: relative;
}

.search-input-group i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.9rem;
}

.filter-select option {
  background: #1a1a2e;
  color: #ffffff;
}

/* Lots Grid */
.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.lot-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.lot-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.08);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.lot-header h4 {
  margin: 0;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.availability-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.availability-badge.available {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.availability-badge.full {
  background: rgba(245, 87, 108, 0.2);
  color: #f87171;
  border: 1px solid rgba(245, 87, 108, 0.3);
}

.lot-details {
  margin-bottom: 1.5rem;
}

.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.lot-actions {
  text-align: center;
}

/* Booking History */
.booking-history-section {
  margin-bottom: 2rem;
}

.history-table {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  font-weight: 600;
  color: #ffffff;
  font-size: 0.9rem;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: background 0.2s ease;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.table-row:last-child {
  border-bottom: none;
}

.cell {
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #e2e8f0;
  font-size: 0.9rem;
}

.lot-name {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.25rem;
}

.spot-info {
  font-size: 0.8rem;
  color: #94a3b8;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  width: fit-content;
}

.status-badge.active {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}

.status-badge.active-with-action {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
}

.status-badge.active-with-action .status-text {
  text-transform: uppercase;
  font-weight: 600;
  font-size: 0.75rem;
}

.release-btn {
  font-size: 0.7rem !important;
  padding: 0.15rem 0.4rem !important;
  border-radius: 6px !important;
  background: #dc2626 !important;
  border: none !important;
  color: white !important;
  transition: all 0.2s ease !important;
}

.release-btn:hover:not(:disabled) {
  background: #b91c1c !important;
  transform: translateY(-1px);
}

.release-btn:disabled {
  opacity: 0.6 !important;
  cursor: not-allowed !important;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}

/* Empty States */
.empty-state,
.empty-history,
.loading-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state i,
.empty-history i,
.loading-state i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: #475569;
}

.loading-state i {
  animation: spin 1s linear infinite;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #94a3b8;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: rgba(26, 26, 46, 0.95);
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
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
  color: #ffffff;
  font-size: 1.25rem;
}

.modal-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 1.5rem;
}

.selected-lot-info {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.selected-lot-info h4 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
}

.selected-lot-info p {
  margin: 0 0 0.5rem 0;
  color: #94a3b8;
  font-size: 0.9rem;
}

.lot-pricing {
  display: flex;
  align-items: center;
  color: #667eea;
  font-weight: 600;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #e2e8f0;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.15);
}

.form-input::placeholder {
  color: #94a3b8;
}

.error-message {
  background: rgba(245, 87, 108, 0.1);
  border: 1px solid rgba(245, 87, 108, 0.3);
  border-radius: 8px;
  padding: 0.75rem;
  color: #f87171;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* Button Styles */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #ffffff;
  border: 1px solid transparent;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.btn-danger {
  background: linear-gradient(135deg, #f5576c, #f093fb);
  color: #ffffff;
  border: 1px solid transparent;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 87, 108, 0.3);
}

.btn-outline-primary {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-outline-primary:hover:not(:disabled) {
  background: #667eea;
  color: #ffffff;
}

.btn-outline-light {
  background: transparent;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-outline-light:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
}

/* Animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .user-nav-content {
    flex-direction: column;
    gap: 1rem;
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
  
  .search-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .reservation-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .spot-info {
    text-align: left;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .header-cell {
    display: none;
  }
  
  .cell {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .cell:before {
    content: attr(data-label);
    font-weight: 600;
    color: #94a3b8;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}
</style>
