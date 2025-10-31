<!--
==============================================================================
                              BAR CHART COMPONENT
                           Reusable Chart.js Bar Chart
==============================================================================
Description: Reusable bar chart component for displaying analytics data
Features: Customizable colors, responsive design, Chart.js integration
Usage: Used in admin and user analytics for revenue, bookings, usage data
==============================================================================
-->

<template>
  <div class="chart-container">
    <!-- Chart title and subtitle section -->
    <div class="chart-header" v-if="title">
      <h3>{{ title }}</h3>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- The actual bar chart rendered here -->
    <div class="chart-wrapper">
      <Bar
        :data="chartData"
        :options="chartOptions"
        :height="height"
      />
    </div>
  </div>
</template>

<script setup>
//------Vue 3 Composition API setup------//
import { computed } from 'vue'

//------Chart.js imports for bar chart functionality------//
import {
  Chart as ChartJS,
  CategoryScale,    // For x-axis labels
  LinearScale,      // For y-axis numbers
  BarElement,       // For drawing bars
  Title,            // For chart title
  Tooltip,          // For hover tooltips
  Legend
} from 'chart.js'
import { Bar } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

// Props
const props = defineProps({
  title: String,
  subtitle: String,
  labels: {
    type: Array,
    required: true
  },
  datasets: {
    type: Array,
    required: true
  },
  height: {
    type: Number,
    default: 400
  },
  currency: {
    type: Boolean,
    default: false
  },
  horizontal: {
    type: Boolean,
    default: false
  },
  theme: {
    type: String,
    default: 'default'
  }
})

// Computed chart data
const chartData = computed(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset, index) => ({
    ...dataset,
    ...getThemeStyles(props.theme, index)
  }))
}))

// Chart options
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: props.horizontal ? 'y' : 'x',
  plugins: {
    legend: {
      labels: {
        color: '#e2e8f0',
        font: {
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#e2e8f0',
      bodyColor: '#e2e8f0',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      callbacks: {
        label: (context) => {
          const label = context.dataset.label || ''
          const value = props.currency ? `₹${context.parsed.y || context.parsed.x}` : (context.parsed.y || context.parsed.x)
          return `${label}: ${value}`
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#94a3b8',
        font: {
          size: 11
        },
        callback: (value, index) => {
          if (props.horizontal && props.currency) {
            return `₹${value}`
          }
          return props.labels[index] || value
        }
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    },
    y: {
      ticks: {
        color: '#94a3b8',
        font: {
          size: 11
        },
        callback: (value) => {
          if (!props.horizontal && props.currency) {
            return `₹${value}`
          }
          return value
        }
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  }
}))

// Theme styles for different chart types
function getThemeStyles(theme, index) {
  const themes = {
    default: [
      {
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: '#3b82f6',
        borderWidth: 1
      },
      {
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: '#10b981',
        borderWidth: 1
      },
      {
        backgroundColor: 'rgba(245, 158, 11, 0.8)',
        borderColor: '#f59e0b',
        borderWidth: 1
      }
    ],
    revenue: [
      {
        backgroundColor: 'rgba(16, 185, 129, 0.8)',
        borderColor: '#10b981',
        borderWidth: 1
      }
    ],
    performance: [
      {
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(168, 85, 247, 0.8)'
        ],
        borderColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#ef4444',
          '#a855f7'
        ],
        borderWidth: 1
      }
    ]
  }
  
  return themes[theme]?.[index] || themes.default[index] || themes.default[0]
}
</script>

<style scoped>
.chart-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-header {
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.chart-header p {
  color: #94a3b8;
  margin: 0;
  font-size: 0.9rem;
}

.chart-wrapper {
  position: relative;
  height: 400px;
}
</style>
