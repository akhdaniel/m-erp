<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Purchasing Dashboard</h1>
      <p class="mt-1 text-sm text-gray-500">Overview of purchasing operations and metrics</p>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Orders -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <DocumentTextIcon class="h-6 w-6 text-gray-400" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Orders</dt>
                <dd class="flex items-baseline">
                  <div class="text-2xl font-semibold text-gray-900">{{ metrics.total_orders || 0 }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Approval -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <ClockIcon class="h-6 w-6 text-gray-400" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Pending Approval</dt>
                <dd class="flex items-baseline">
                  <div class="text-2xl font-semibold text-gray-900">{{ metrics.pending_approval || 0 }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Suppliers -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <TruckIcon class="h-6 w-6 text-gray-400" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Suppliers</dt>
                <dd class="flex items-baseline">
                  <div class="text-2xl font-semibold text-gray-900">{{ metrics.active_suppliers || 0 }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Month Spend -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CurrencyDollarIcon class="h-6 w-6 text-gray-400" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Month Spend</dt>
                <dd class="flex items-baseline">
                  <div class="text-2xl font-semibold text-gray-900">{{ formatCurrency(metrics.month_spend || 0) }}</div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts and Lists -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Spending Trend Chart -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Spending Trend</h3>
        <div class="h-80">
          <canvas ref="spendingChartRef"></canvas>
        </div>
      </div>

      <!-- Supplier Distribution Chart -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Supplier Distribution</h3>
        <div class="h-80">
          <canvas ref="supplierChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Orders -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Recent Orders</h3>
        </div>
        <div class="divide-y divide-gray-200">
          <div v-for="order in recentOrders" :key="order.id" class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-primary-600">{{ order.po_number }}</p>
                <p class="text-sm text-gray-500">{{ order.supplier }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">{{ formatCurrency(order.amount) }}</p>
                <p class="text-sm text-gray-500">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass(order.status)">
                    {{ order.status }}
                  </span>
                </p>
              </div>
            </div>
          </div>
          <div v-if="recentOrders.length === 0" class="px-6 py-12 text-center">
            <p class="text-sm text-gray-500">No recent orders</p>
          </div>
        </div>
      </div>

      <!-- Top Suppliers -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Top Suppliers</h3>
        </div>
        <div class="divide-y divide-gray-200">
          <div v-for="supplier in topSuppliers" :key="supplier.id" class="px-6 py-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-900">{{ supplier.name }}</p>
                <div class="flex items-center mt-1">
                  <StarIcon v-for="n in 5" :key="n" class="h-4 w-4 flex-shrink-0" :class="n <= Math.round(supplier.rating) ? 'text-yellow-400' : 'text-gray-300'" />
                  <span class="ml-1 text-xs text-gray-500">{{ supplier.rating.toFixed(1) }}</span>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">{{ formatCurrency(supplier.spend) }}</p>
                <p class="text-sm text-gray-500">{{ supplier.orders }} orders</p>
              </div>
            </div>
          </div>
          <div v-if="topSuppliers.length === 0" class="px-6 py-12 text-center">
            <p class="text-sm text-gray-500">No supplier data available</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  DocumentTextIcon,
  ClockIcon,
  TruckIcon,
  CurrencyDollarIcon,
  StarIcon
} from '@heroicons/vue/24/outline'
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { usePurchasingStore } from '@/stores/purchasing'

// Register Chart.js components
Chart.register(
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  LineController,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

// Stores
const purchasingStore = usePurchasingStore()

// Local state
const metrics = ref({
  total_orders: 0,
  pending_approval: 0,
  active_suppliers: 0,
  month_spend: 0
})

const recentOrders = ref([])
const topSuppliers = ref([])
const spendingChartRef = ref(null)
const supplierChartRef = ref(null)
const spendingChart = ref(null)
const supplierChart = ref(null)

// Methods
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    draft: 'bg-gray-100 text-gray-800',
    approved: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const loadDashboardData = async () => {
  try {
    // Load metrics
    const metricsData = await purchasingStore.$purchasingService.getDashboardMetrics()
    metrics.value = metricsData

    // Load recent orders
    const recentOrdersData = await purchasingStore.$purchasingService.getRecentOrders(5)
    recentOrders.value = recentOrdersData.orders || []

    // Load top suppliers
    const topSuppliersData = await purchasingStore.$purchasingService.getTopSuppliers(5)
    topSuppliers.value = topSuppliersData.suppliers || []

    // Load chart data
    const spendingData = await purchasingStore.$purchasingService.getSpendingTrend()
    const supplierData = await purchasingStore.$purchasingService.getSupplierDistribution()

    // Render charts
    renderSpendingChart(spendingData)
    renderSupplierChart(supplierData)
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
}

const renderSpendingChart = (data) => {
  if (spendingChartRef.value && data.labels && data.datasets) {
    if (spendingChart.value) {
      spendingChart.value.destroy()
    }

    spendingChart.value = new Chart(spendingChartRef.value, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: data.datasets.map(dataset => ({
          ...dataset,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }
        }
      }
    })
  }
}

const renderSupplierChart = (data) => {
  if (supplierChartRef.value && data.labels && data.datasets) {
    if (supplierChart.value) {
      supplierChart.value.destroy()
    }

    supplierChart.value = new Chart(supplierChartRef.value, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: data.datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
          }
        },
        cutout: '60%'
      }
    })
  }
}

// Lifecycle hooks
onMounted(() => {
  loadDashboardData()
})

onUnmounted(() => {
  // Clean up charts
  if (spendingChart.value) {
    spendingChart.value.destroy()
  }
  if (supplierChart.value) {
    supplierChart.value.destroy()
  }
})
</script>