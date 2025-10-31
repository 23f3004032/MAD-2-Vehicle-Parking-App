//==============================================================================
//                           ONLYPARK FRONTEND ENTRY POINT
//                          Vue.js Application Initialization
//==============================================================================
// Description: Main entry point where the Vue app starts
// Features: Router setup, Bootstrap CSS integration, app mounting
// Purpose: This connects our Vue app to the HTML and starts everything
//==============================================================================

import { createApp } from 'vue'    // Vue 3 framework
import './style.css'               // Our custom styles
import App from './App.vue'        // Main app component
import router from './router'      // Navigation routes

// Bootstrap CSS framework for styling and responsive design
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

//------Initialize and start the Vue application------//
const app = createApp(App)  // Create Vue app instance
app.use(router)             // Add navigation routing
app.mount('#app')           // Mount to HTML element with id="app"
