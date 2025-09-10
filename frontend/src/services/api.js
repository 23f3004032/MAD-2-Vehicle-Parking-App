import axios from 'axios'
import { getToken, removeToken } from '@/utils/auth'

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API Service wrapper with error handling
export const apiService = {
  async get(url) {
    try {
      const response = await api.get(url)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Request failed' 
      }
    }
  },

  async post(url, data) {
    try {
      const response = await api.post(url, data)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Request failed' 
      }
    }
  },

  async put(url, data) {
    try {
      const response = await api.put(url, data)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Request failed' 
      }
    }
  },

  async delete(url) {
    try {
      const response = await api.delete(url)
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Request failed' 
      }
    }
  }
}
