import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUser } from '@/utils/auth'

// Import views
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  
  // User routes
  {
    path: '/user/dashboard',
    name: 'UserDashboard',
    component: () => import('@/views/UserDashboard.vue'),
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/user/analytics',
    name: 'UserAnalytics',
    component: () => import('@/views/UserAnalytics.vue'),
    meta: { requiresAuth: true, role: 'user' }
  },
  
  // Admin routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/admin/AdminDashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/analytics',
    name: 'AdminAnalytics',
    component: () => import('@/views/AdminAnalytics.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = getToken()
  const user = getUser()

  // Redirect unauthenticated users away from protected pages
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // Check role-based access for protected routes
  if (to.meta.role && (!user || user.role !== to.meta.role)) {
    // If user is authenticated but wrong role, redirect to appropriate page
    if (user?.role === 'admin') {
      return next('/admin/dashboard')
    } else if (user?.role === 'user') {
      return next('/') // Will redirect to user dashboard when it exists
    } else {
      return next('/login')
    }
  }

  next()
})

export default router
