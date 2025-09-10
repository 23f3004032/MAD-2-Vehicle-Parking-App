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
  
  // User routes (will be added in later prompts)
  // {
  //   path: '/user/dashboard',
  //   name: 'UserDashboard',
  //   component: () => import('@/views/user/UserDashboard.vue'),
  //   meta: { requiresAuth: true, role: 'user' }
  // },
  
  // Admin routes (will be added in later prompts)
  // {
  //   path: '/admin/dashboard',
  //   name: 'AdminDashboard',
  //   component: () => import('@/views/admin/AdminDashboard.vue'),
  //   meta: { requiresAuth: true, role: 'admin' }
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = getToken()
  const user = getUser()

  // For now, allow access to login/register pages regardless of auth status
  // This will be properly implemented when we create dashboard pages
  
  // Redirect unauthenticated users away from protected pages
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // Check role-based access for protected routes (when they exist)
  if (to.meta.role && (!user || user.role !== to.meta.role)) {
    return next('/')
  }

  next()
})

export default router
