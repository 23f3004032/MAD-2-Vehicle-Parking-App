<!--
==============================================================================
                           DOUGHNUT CHART COMPONENT
                          Reusable Chart.js Doughnut Chart
==============================================================================
Description: Circular chart component for displaying proportional data
Features: Customizable colors, responsive, perfect for showing percentages
Usage: Used for showing parking spot distribution, booking types, etc.
==============================================================================
-->

<template>
  <div class="chart-container">
    <!-- Chart title section -->
    <div class="chart-header" v-if="title">
      <h3>{{ title }}</h3>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    
    <!-- The doughnut chart display -->
    <div class="chart-wrapper">
      <Doughnut
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
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'
import { Doughnut } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend)

// Props
const props = defineProps({
  title: String,
  subtitle: String,
  labels: {
    type: Array,
    required: true
  },
  data: {
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
  colors: {
    type: Array,
    default: () => [
      'rgba(59, 130, 246, 0.8)',
      'rgba(16, 185, 129, 0.8)',
      'rgba(245, 158, 11, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(168, 85, 247, 0.8)',
      'rgba(6, 182, 212, 0.8)'
    ]
  }
})

// Computed chart data
const chartData = computed(() => ({
  labels: props.labels,
  datasets: [{
    data: props.data,
    backgroundColor: props.colors,
    borderColor: props.colors.map(color => color.replace('0.8', '1')),
    borderWidth: 2
  }]
}))

// Chart options
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#e2e8f0',
        font: {
          size: 12
        },
        padding: 20,
        usePointStyle: true,
        pointStyle: 'circle'
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
          const label = context.label || ''
          const value = props.currency ? `₹${context.parsed}` : context.parsed
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = ((context.parsed / total) * 100).toFixed(1)
          return `${label}: ${value} (${percentage}%)`
        }
      }
    }
  },
  cutout: '50%'
}))
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
  text-align: center;
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
