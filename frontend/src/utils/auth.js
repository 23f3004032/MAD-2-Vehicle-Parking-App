// Token management
export function getToken() {
  return localStorage.getItem('token')
}

export function setToken(token) {
  localStorage.setItem('token', token)
}

export function removeToken() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

// User management
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
