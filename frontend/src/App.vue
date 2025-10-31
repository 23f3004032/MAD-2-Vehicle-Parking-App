<!--
==============================================================================
                              ONLYPARK MAIN APP
                           Root Vue Component
==============================================================================
Description: Main app wrapper that holds all our pages and components
Features: Global styling, theme colors, router outlet
Purpose: The main container where all our app content gets rendered
==============================================================================
-->

<template>
  <div id="app">
    <!-- This is where all our pages (Login, Dashboard, etc.) get displayed -->
    <router-view />
  </div>
</template>

<style>
/* Global styles for the entire OnlyPark application */

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;  /* Makes text look smoother */
  -moz-osx-font-smoothing: grayscale;   /* For Firefox */
  min-height: 100vh;  /* Full screen height */
}

/* App-wide color scheme - I chose these colors for a professional look */
:root {
  --primary-color: #3b82f6;     /* Main blue color */
  --secondary-color: #1e40af;   /* Darker blue */
  --success-color: #10b981;     /* Green for success messages */
  --danger-color: #ef4444;      /* Red for errors */
  --warning-color: #f59e0b;     /* Orange for warnings */
  --light-bg: #f8fafc;
  --dark-bg: #1e293b;
  --border-color: #e2e8f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--light-bg);
  color: #334155;
}

.btn-primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
}

.card {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.5rem;
}

.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25);
}
</style>
