<template>
  <div class="register-page">
    <div class="register-container">
      <!-- Left side - Branding -->
      <div class="register-brand">
        <div class="brand-content">
          <router-link to="/" class="brand-title-link">
            <h1 class="brand-title">
              <i class="bi bi-p-circle-fill me-2"></i>
              <span class="brand-highlight">Only</span>Parks
            </h1>
          </router-link>
          <p class="brand-subtitle">
            Join thousands of users who trust us with their parking needs
          </p>
        </div>
      </div>

      <!-- Right side - Register Form -->
      <div class="register-form-section">
        <div class="form-container">
          <div class="form-header">
            <h2>Create Account</h2>
            <p>Fill in your details to get started</p>
          </div>

          <form @submit.prevent="handleRegister" class="register-form">
            <!-- Full Name Field -->
            <div class="form-group">
              <label for="fullname">
                <i class="bi bi-person-fill me-2"></i>Full Name
              </label>
              <input
                id="fullname"
                v-model="form.fullname"
                type="text"
                class="form-input"
                placeholder="Enter your full name"
                required
                :disabled="loading"
              />
            </div>

            <!-- Email Field -->
            <div class="form-group">
              <label for="email">
                <i class="bi bi-envelope-fill me-2"></i>Email Address
              </label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="form-input"
                placeholder="Enter your email"
                required
                :disabled="loading"
              />
            </div>

            <!-- Password Field -->
            <div class="form-group">
              <label for="password">
                <i class="bi bi-lock-fill me-2"></i>Password
              </label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="Create a strong password"
                required
                minlength="6"
                :disabled="loading"
              />
            </div>

            <!-- Confirm Password Field -->
            <div class="form-group">
              <label for="confirmPassword">
                <i class="bi bi-shield-lock-fill me-2"></i>Confirm Password
              </label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                class="form-input"
                placeholder="Confirm your password"
                required
                :disabled="loading"
              />
            </div>

            <!-- Error Message -->
            <div v-if="error" class="error-message">
              {{ error }}
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              class="btn btn-primary btn-full"
              :disabled="loading || !isFormValid"
            >
              <i class="bi bi-person-plus-fill me-2"></i>
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? 'Creating Account...' : 'Create Account' }}
            </button>
          </form>

          <!-- Login Link -->
          <div class="form-footer">
            <p>
              Already have an account?
              <router-link to="/login" class="link">Sign in here</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth'
import { getUser } from '@/utils/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  fullname: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isFormValid = computed(() => {
  return form.fullname.trim() && 
         form.email.trim() && 
         form.password.length >= 6 && 
         form.password === form.confirmPassword
})

const handleRegister = async () => {
  if (loading.value || !isFormValid.value) return
  
  // Validate passwords match
  if (form.password !== form.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''

  try {
    const userData = {
      fullname: form.fullname.trim(),
      email: form.email.trim(),
      password: form.password
    }

    const result = await authService.register(userData)
    
    if (result.success) {
      const user = getUser()
      // For now, redirect to home page since dashboard routes don't exist yet
      // This will be updated when we create dashboard pages
      router.push('/')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.register-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1000px;
  width: 100%;
  min-height: 700px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

/* Left Side - Branding */
.register-brand {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  position: relative;
  overflow: hidden;
}

.register-brand::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)" /></svg>');
  opacity: 0.3;
}

.brand-content {
  text-align: center;
  color: white;
  position: relative;
  z-index: 1;
}

.brand-title-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: transform 0.3s ease;
}

.brand-title-link:hover {
  transform: scale(1.05);
  color: inherit;
}

.brand-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  line-height: 1.1;
  cursor: pointer;
}

.brand-highlight {
  color: rgba(255, 255, 255, 0.9);
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
}

/* Right Side - Form */
.register-form-section {
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  overflow-y: auto;
}

.form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.form-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.register-form {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .register-container {
    grid-template-columns: 1fr;
    max-width: 400px;
  }
  
  .register-brand {
    padding: 2rem;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .register-form-section {
    padding: 2rem;
  }
}

@media (max-width: 480px) {
  .register-page {
    padding: 0.5rem;
  }
  
  .register-container {
    min-height: 600px;
  }
  
  .brand-title {
    font-size: 1.75rem;
  }
  
  .form-header h2 {
    font-size: 1.5rem;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
}
</style>
