<!--
==============================================================================
                            LINE CHART COMPONENT
                         Reusable Chart.js Line Chart
==============================================================================
Description: Line chart component for displaying trends over time
Features: Smooth animations, responsive design, customizable styling
Usage: Perfect for showing revenue trends, booking patterns over time
==============================================================================
-->

<template>
  <div class="chart-container">
    <!-- Chart title and description -->
    <div class="chart-header" v-if="title">
      <h3>{{ title }}</h3>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- The line chart visualization -->
    <div class="chart-wrapper">
      <Line
        :data="chartData"
        :options="chartOptions"
        :height="height"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
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
  theme: {
    type: String,
    default: 'default' // 'default', 'revenue', 'usage'
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
          const value = props.currency ? `₹${context.parsed.y}` : context.parsed.y
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
          return props.currency ? `₹${value}` : value
        }
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)'
      }
    }
  },
  elements: {
    line: {
      tension: 0.4
    },
    point: {
      radius: 4,
      hoverRadius: 6
    }
  }
}))

// Theme styles for different chart types
function getThemeStyles(theme, index) {
  const themes = {
    default: [
      {
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true
      },
      {
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true
      }
    ],
    revenue: [
      {
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        fill: true
      }
    ],
    usage: [
      {
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true
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
