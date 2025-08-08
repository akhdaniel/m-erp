<template>
  <AppLayout>
    <div class="min-h-screen">
      <!-- Dashboard Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Sales Dashboard</h1>
            <p class="mt-2 text-gray-600">
              Real-time overview of sales performance, quotes, and orders
            </p>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="refreshAllWidgets"
              :disabled="isRefreshing"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <svg class="w-4 h-4 mr-2" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ isRefreshing ? 'Refreshing...' : 'Refresh All' }}
            </button>
            <div class="text-sm text-gray-500">
              Last updated: {{ lastUpdated }}
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p class="mt-2 text-gray-600">Loading dashboard...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Dashboard Loading Error
            </h3>
            <p class="mt-2 text-sm text-red-700">
              {{ error }}
            </p>
            <div class="mt-3">
              <button
                @click="loadDashboard"
                class="text-sm font-medium text-red-800 hover:text-red-600"
              >
                Try again →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Grid -->
      <div v-else-if="widgets && widgets.length > 0">
        <!-- Metrics Row (Top KPIs) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <template v-for="widget in metricsWidgets" :key="widget.id">
            <DashboardWidget
              :widget="widget"
              :data="widgetData[widget.id]"
              :loading="widgetLoading[widget.id]"
              :error="widgetErrors[widget.id]"
              @refresh="refreshWidget(widget.id)"
            />
          </template>
        </div>

        <!-- Charts and Lists Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <template v-for="widget in chartWidgets" :key="widget.id">
            <DashboardWidget
              :widget="widget"
              :data="widgetData[widget.id]"
              :loading="widgetLoading[widget.id]"
              :error="widgetErrors[widget.id]"
              @refresh="refreshWidget(widget.id)"
              class="lg:col-span-1"
            />
          </template>
        </div>

        <!-- Large Widgets Row (Tables, Complex Charts) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <template v-for="widget in tableWidgets" :key="widget.id">
            <DashboardWidget
              :widget="widget"
              :data="widgetData[widget.id]"
              :loading="widgetLoading[widget.id]"
              :error="widgetErrors[widget.id]"
              @refresh="refreshWidget(widget.id)"
              class="lg:col-span-1"
            />
          </template>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <div class="mx-auto h-24 w-24 text-gray-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="mt-4 text-lg font-medium text-gray-900">No Dashboard Widgets</h3>
        <p class="mt-2 text-gray-600">Dashboard widgets are not configured or unavailable.</p>
        <div class="mt-6">
          <button
            @click="loadDashboard"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
          >
            Reload Dashboard
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import DashboardWidget from '@/components/DashboardWidget.vue'

// State management
const isLoading = ref(true)
const isRefreshing = ref(false)
const error = ref('')
const lastUpdated = ref('')

// Widget management
const widgets = ref<any[]>([])
const widgetData = ref<Record<string, any>>({})
const widgetLoading = ref<Record<string, boolean>>({})
const widgetErrors = ref<Record<string, string>>({})

// Service URLs
const SALES_SERVICE_URL = 'http://localhost:8006'
const UI_REGISTRY_URL = 'http://localhost:8010'  // If we had a UI registry

// Computed widget categories
const metricsWidgets = computed(() => 
  widgets.value.filter(w => w.type === 'metric' && w.size === 'small')
)

const chartWidgets = computed(() => 
  widgets.value.filter(w => w.type === 'chart' && ['medium', 'large'].includes(w.size))
)

const tableWidgets = computed(() => 
  widgets.value.filter(w => ['list', 'table'].includes(w.type))
)

// API Client for sales service
const apiClient = {
  async get(endpoint: string) {
    const response = await fetch(`${SALES_SERVICE_URL}${endpoint}`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    return response.json()
  }
}

// Widget definitions (normally would come from UI Registry)
const DEFAULT_WIDGETS = [
  {
    id: "total-quotes",
    title: "Active Quotes",
    type: "metric",
    size: "small",
    data_endpoint: "/api/v1/quotes/stats",
    refresh_interval: 300,
    config: {
      field: "active_quotes",
      format: "number",
      color: "blue",
      icon: "file-text",
      link: "/sales/quotes"
    }
  },
  {
    id: "pending-orders",
    title: "Pending Orders",
    type: "metric",
    size: "small",
    data_endpoint: "/orders/stats",
    refresh_interval: 60,
    config: {
      field: "pending_orders",
      format: "number",
      color: "orange",
      icon: "clock",
      link: "/sales/orders?status=pending"
    }
  },
  {
    id: "monthly-revenue",
    title: "Monthly Revenue",
    type: "metric",
    size: "small",
    data_endpoint: "/api/v1/orders/analytics/summary",
    refresh_interval: 3600,
    config: {
      field: "total_revenue",
      format: "currency",
      color: "green",
      icon: "dollar-sign"
    }
  },
  {
    id: "conversion-rate",
    title: "Quote Conversion Rate",
    type: "metric",
    size: "small",
    data_endpoint: "/api/v1/quotes/analytics",
    refresh_interval: 3600,
    config: {
      field: "conversion_rate",
      format: "percentage",
      color: "purple",
      icon: "trending-up"
    }
  },
  {
    id: "revenue-chart",
    title: "Revenue Trend",
    type: "chart",
    size: "large",
    data_endpoint: "/orders/analytics/revenue-trend",
    refresh_interval: 3600,
    config: {
      chart_type: "line",
      x_field: "date",
      y_field: "revenue",
      period: "last_30_days"
    }
  },
  {
    id: "sales-pipeline",
    title: "Sales Pipeline",
    type: "chart",
    size: "large",
    data_endpoint: "/api/v1/quotes/pipeline",
    refresh_interval: 600,
    config: {
      chart_type: "funnel",
      stages: ["draft", "sent", "viewed", "accepted", "rejected"]
    }
  },
  {
    id: "recent-orders",
    title: "Recent Orders",
    type: "list",
    size: "large",
    data_endpoint: "/api/v1/dashboard/recent/orders?limit=10",
    refresh_interval: 60,
    config: {
      limit: 10,
      columns: ["order_number", "customer_name", "total_amount", "status", "order_date"],
      link_pattern: "/sales/orders/{id}"
    }
  },
  {
    id: "top-customers",
    title: "Top Customers",
    type: "table",
    size: "large",
    data_endpoint: "/api/v1/dashboard/analytics/top-customers",
    refresh_interval: 3600,
    config: {
      columns: ["customer_name", "order_count", "total_revenue", "average_order"],
      limit: 5,
      sortable: true
    }
  }
]

// Load dashboard configuration
async function loadDashboard() {
  try {
    isLoading.value = true
    error.value = ''
    
    // In a full implementation, this would fetch from UI Registry
    // For now, use the default widget definitions
    widgets.value = DEFAULT_WIDGETS
    
    console.log('Loaded dashboard widgets:', widgets.value.length)
    
    // Load data for all widgets
    await loadAllWidgets()
    
  } catch (err: any) {
    console.error('Error loading dashboard:', err)
    error.value = err.message || 'Failed to load dashboard'
  } finally {
    isLoading.value = false
  }
}

// Load data for all widgets
async function loadAllWidgets() {
  const loadPromises = widgets.value.map(widget => loadWidgetData(widget.id))
  await Promise.allSettled(loadPromises)
  updateLastUpdated()
}

// Load data for a specific widget
async function loadWidgetData(widgetId: string) {
  const widget = widgets.value.find(w => w.id === widgetId)
  if (!widget) return

  try {
    widgetLoading.value[widgetId] = true
    widgetErrors.value[widgetId] = ''
    
    console.log(`Loading data for widget: ${widgetId}`)
    console.log(`Endpoint: ${widget.data_endpoint}`)
    
    const data = await apiClient.get(widget.data_endpoint)
    widgetData.value[widgetId] = data
    
    console.log(`Loaded data for ${widgetId}:`, data)
    
  } catch (err: any) {
    console.error(`Error loading widget ${widgetId}:`, err)
    widgetErrors.value[widgetId] = err.message || 'Failed to load data'
  } finally {
    widgetLoading.value[widgetId] = false
  }
}

// Refresh a specific widget
async function refreshWidget(widgetId: string) {
  await loadWidgetData(widgetId)
  updateLastUpdated()
}

// Refresh all widgets
async function refreshAllWidgets() {
  try {
    isRefreshing.value = true
    await loadAllWidgets()
  } catch (err) {
    console.error('Error refreshing widgets:', err)
  } finally {
    isRefreshing.value = false
  }
}

// Update last updated timestamp
function updateLastUpdated() {
  const now = new Date()
  lastUpdated.value = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  })
}

// Setup auto-refresh for widgets
function setupAutoRefresh() {
  widgets.value.forEach(widget => {
    if (widget.refresh_interval && widget.refresh_interval > 0) {
      setInterval(() => {
        loadWidgetData(widget.id)
      }, widget.refresh_interval * 1000)
    }
  })
}

// Initialize dashboard on mount
onMounted(async () => {
  console.log('Sales Dashboard mounted - loading dashboard...')
  await loadDashboard()
  setupAutoRefresh()
})
</script>