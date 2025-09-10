import api from './api'
import { setToken, setUser, removeToken, removeUser } from '@/utils/auth'

export const authService = {
  // Register new user
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      const { access_token, user } = response.data
      
      setToken(access_token)
      setUser(user)
      
      return { success: true, user }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Registration failed' 
      }
    }
  },

  // Login user
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, user } = response.data
      
      setToken(access_token)
      setUser(user)
      
      return { success: true, user }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      }
    }
  },

  // Logout user
  logout() {
    removeToken()
    removeUser()
    window.location.href = '/'
  },

  // Verify token
  async verifyToken() {
    try {
      const response = await api.post('/auth/verify-token')
      return { success: true, user: response.data.user }
    } catch (error) {
      return { success: false }
    }
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me')
      return { success: true, user: response.data.user }
    } catch (error) {
      return { success: false }
    }
  }
}
