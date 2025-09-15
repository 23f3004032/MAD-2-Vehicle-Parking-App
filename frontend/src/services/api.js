import axios from 'axios'
import { getToken, removeToken } from '@/utils/auth'

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Ensures all requests are authenticated automatically.
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

//Keeps app secure when token expires or is invalid.
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

//This avoids repeating try/catch everywhere in components.
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
