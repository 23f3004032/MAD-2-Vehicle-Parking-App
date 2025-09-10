<template>
  <div class="home-page">
    <!-- Minimal Navigation -->
    <nav class="navbar navbar-expand-lg">
      <div class="container">
        <div class="navbar-brand">
          <h2 class="brand-text">
            <i class="bi bi-p-circle-fill me-2"></i>OnlyParks
          </h2>
        </div>
        
        <div class="nav-actions">
          <router-link to="/login" class="btn btn-ghost">
            <i class="bi bi-box-arrow-in-right me-2"></i>Login
          </router-link>
          <router-link to="/register" class="btn btn-primary">
            <i class="bi bi-person-plus-fill me-2"></i>Sign Up
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-content">
          <div class="hero-text">
            <h1 class="hero-title">
              <i class="bi bi-geo-alt-fill me-3" style="color: #667eea;"></i>
              <span class="brand-highlight">Only</span>Parks
            </h1>
            <p class="hero-subtitle">
              <i class="bi bi-lightning-charge-fill me-2"></i>
              Smart parking solutions for modern cities
            </p>
            <div class="hero-actions">
              <router-link to="/register" class="btn btn-primary btn-lg">
                <i class="bi bi-rocket-takeoff-fill me-2"></i>Get Started
              </router-link>
              <router-link to="/login" class="btn btn-outline btn-lg">
                <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <p>&copy; 2025 OnlyParks. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Clean landing page
</script>

<style scoped>
/* Modern Dark Theme */
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  color: #ffffff;
  font-family: 'Inter', sans-serif;
}

/* Navigation */
.navbar {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 0;
}

.brand-text {
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.nav-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

/* Hero Section */
.hero-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80vh;
  text-align: center;
}

.hero-content {
  max-width: 600px;
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  line-height: 1.1;
}

.brand-highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2.5rem;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Buttons */
.btn {
  padding: 0.75rem 2rem;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
  color: white;
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
  transform: translateY(-2px);
}

.btn-ghost {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem 1.5rem;
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.btn-lg {
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
}

/* Footer */
.footer {
  position: absolute;
  bottom: 0;
  width: 100%;
  text-align: center;
  padding: 2rem 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
  
  .nav-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .brand-text {
    font-size: 1.5rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .navbar {
    padding: 0.5rem 0;
  }
}
</style>
