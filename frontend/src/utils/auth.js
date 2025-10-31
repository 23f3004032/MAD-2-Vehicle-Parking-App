//==============================================================================
//                           AUTHENTICATION UTILITIES
//                          Token & User Management Helpers
//==============================================================================
// Description: Helper functions for managing JWT tokens and user data
// Features: Token storage, user data caching, authentication state management
// Purpose: Keeps user logged in across browser sessions using localStorage
//==============================================================================

//========================== TOKEN MANAGEMENT =================================//

// Get the JWT token from browser storage
export function getToken() {
  return localStorage.getItem('token')
}

// Save JWT token to browser storage (keeps user logged in)
export function setToken(token) {
  localStorage.setItem('token', token)
}

// Remove token and user data (logout functionality)
export function removeToken() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

//========================== USER DATA MANAGEMENT ==========================//
export function getUser() {
  const userStr = localStorage.getItem('user')
  try {
    return userStr ? JSON.parse(userStr) : null
  } catch (error) {
    console.error('Error parsing user data:', error)
    return null
  }
}

export function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user))
}

export function removeUser() {
  localStorage.removeItem('user')
}

// Auth check
export function isAuthenticated() {
  return !!getToken()
}

export function isAdmin() {
  const user = getUser()
  return user?.role === 'admin'
}

export function isUser() {
  const user = getUser()
  return user?.role === 'user'
}

// Logout
export function logout() {
  removeToken()
  removeUser()
  window.location.href = '/'
}
