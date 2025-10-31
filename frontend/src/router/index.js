//==============================================================================
//                           ONLYPARK ROUTING CONFIGURATION
//                          Navigation & Route Protection
//==============================================================================
// Description: Defines all the pages/routes in our app and navigation rules
// Features: Route guards, authentication checks, role-based access
// Purpose: Controls which pages users can visit based on login status
//==============================================================================

import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUser } from '@/utils/auth'  // Authentication helpers

//------Import all page components------//
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

//=============================== PUBLIC ROUTES ===============================/
// These pages can be accessed without logging in
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
  

// User routes These are user-only pages,Means you must be logged in, and role must be "user".
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
  

// Admin routes These are admin-only pages,Means you must be logged in, and role must be "admin".
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

//Creates the router object with your routes + history mode
const router = createRouter({
  history: createWebHistory(),
  routes
})

//Runs before every route change, This ensures security at frontend level.

//If the route requires auth and no token, redirect to /login.
//If the route requires a certain role but user doesn’t match:
//                        Admins → pushed to /admin/dashboard
//                        Users → pushed to /
//                        No role → back to login.

router.beforeEach((to, from, next) => {
  const token = getToken()
  const user = getUser()

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.role && (!user || user.role !== to.meta.role)) {
    if (user?.role === 'admin') {
      return next('/admin/dashboard')
    } else if (user?.role === 'user') {
      return next('/') 
    } else {
      return next('/login')
    }
  }

  next()
})

export default router
