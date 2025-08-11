<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Dashboard Header -->
      <div v-if="dashboardConfig">
        <h1 class="text-2xl font-bold">{{ dashboardConfig.title }}</h1>
        <p v-if="dashboardConfig.description" class="mt-2 text-sm">
          {{ dashboardConfig.description }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading dashboard...
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Dashboard Grid -->
      <div v-else-if="dashboardConfig && dashboardConfig.widgets" 
           :class="getGridClass(dashboardConfig.layout)">
        
        <!-- Render each widget dynamically -->
        <div v-for="widget in dashboardConfig.widgets" 
             :key="widget.id"
             :class="getWidgetClass(widget)"
             class="glass-card">
          
          <!-- Widget Header -->
          <div v-if="widget.title || widget.icon" class="px-6 py-4 border-b border-gray-200/20">
            <div class="flex items-center">
              <component v-if="widget.icon" :is="getIcon(widget.icon)" class="h-5 w-5 mr-2" />
              <h3 class="text-lg font-medium">{{ widget.title }}</h3>
            </div>
          </div>
          
          <!-- Widget Content -->
          <div class="p-6">
            <!-- Metric Widget -->
            <div v-if="widget.type === 'metric'">
              <div v-if="widgetData[widget.id]">
                <div class="text-3xl font-bold">
                  {{ formatValue(widgetData[widget.id].value, widget.format) }}
                </div>
                <div v-if="widgetData[widget.id].change" class="mt-2 flex items-center text-sm">
                  <span :class="widgetData[widget.id].change > 0 ? 'text-green-600' : 'text-red-600'">
                    {{ widgetData[widget.id].change > 0 ? '+' : '' }}{{ widgetData[widget.id].change }}%
                  </span>
                  <span class="ml-2">from last period</span>
                </div>
              </div>
              <div v-else class="animate-pulse">
                <div class="h-8 bg-gray-200 rounded w-24"></div>
              </div>
            </div>

            <!-- Chart Widget -->
            <div v-else-if="widget.type === 'chart'">
              <div v-if="widgetData[widget.id]" class="h-64">
                <!-- Chart would be rendered here using a charting library -->
                <div class="flex items-center justify-center h-full text-gray-400">
                  <svg class="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
              <div v-else class="animate-pulse h-64">
                <div class="h-full bg-gray-200 rounded"></div>
              </div>
            </div>

            <!-- List Widget -->
            <div v-else-if="widget.type === 'list'">
              <div v-if="widgetData[widget.id]">
                <ul class="divide-y divide-gray-200/20">
                  <li v-for="(item, index) in widgetData[widget.id].items?.slice(0, widget.limit || 5)" 
                      :key="index" 
                      class="py-3">
                    <div class="flex justify-between">
                      <div>
                        <p class="text-sm font-medium">{{ item.title || item.name }}</p>
                        <p v-if="item.subtitle" class="text-xs">{{ item.subtitle }}</p>
                      </div>
                      <div v-if="item.value" class="text-sm font-medium">
                        {{ formatValue(item.value, widget.valueFormat) }}
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
              <div v-else class="animate-pulse space-y-3">
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
              </div>
            </div>

            <!-- Table Widget -->
            <div v-else-if="widget.type === 'table'">
              <div v-if="widgetData[widget.id]" class="overflow-x-auto">
                <table class="min-w-full">
                  <thead>
                    <tr>
                      <th v-for="column in widget.columns" :key="column.field" 
                          class="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">
                        {{ column.label }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200/20">
                    <tr v-for="(row, index) in widgetData[widget.id].rows?.slice(0, widget.limit || 5)" :key="index">
                      <td v-for="column in widget.columns" :key="column.field" 
                          class="px-3 py-2 text-sm">
                        {{ formatValue(row[column.field], column.formatter) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="animate-pulse space-y-3">
                <div class="h-4 bg-gray-200 rounded"></div>
                <div class="h-4 bg-gray-200 rounded"></div>
              </div>
            </div>

            <!-- Custom Widget -->
            <div v-else-if="widget.type === 'custom' && widget.component">
              <component :is="widget.component" :data="widgetData[widget.id]" :config="widget" />
            </div>

            <!-- Unknown Widget Type -->
            <div v-else>
              <p class="text-gray-400">Widget type "{{ widget.type }}" not supported</p>
            </div>
          </div>

          <!-- Widget Footer with Actions -->
          <div v-if="widget.actions && widget.actions.length > 0" 
               class="px-6 py-3 border-t border-gray-200/20 flex justify-end space-x-2">
            <button v-for="action in widget.actions" 
                    :key="action.id"
                    @click="executeAction(action, widget)"
                    class="text-sm font-medium hover:underline"
                    :class="action.class || 'text-primary-600'">
              {{ action.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && !error" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium">No dashboard configured</h3>
        <p class="mt-1 text-sm">This service hasn't configured a dashboard yet.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const router = useRouter()

// Props could be passed or derived from route
const props = defineProps<{
  serviceName?: string
}>()

// State
const loading = ref(true)
const error = ref('')
const dashboardConfig = ref<any>(null)
const widgetData = ref<Record<string, any>>({})
const refreshInterval = ref<number | null>(null)

// Computed service name from route or props
const currentService = computed(() => {
  // Extract service name from route path (e.g., /sales/dashboard -> sales)
  const pathSegments = route.path.split('/')
  return props.serviceName || pathSegments[1] || 'main'
})

// Service URL mapping
const serviceUrls: Record<string, string> = {
  sales: 'http://localhost:8006',
  inventory: 'http://localhost:8005',
  purchasing: 'http://localhost:8004',
  main: 'http://localhost:8001'
}

// Fetch dashboard configuration from service
async function fetchDashboardConfig() {
  try {
    // First try to get from UI Registry
    const registryResponse = await fetch(`http://localhost:8010/api/v1/services/${currentService.value}/dashboard`)
    
    if (registryResponse.ok) {
      dashboardConfig.value = await registryResponse.json()
    } else {
      // Fallback to service's own endpoint
      const serviceUrl = serviceUrls[currentService.value]
      if (serviceUrl) {
        const response = await fetch(`${serviceUrl}/api/v1/ui-schemas/dashboard`)
        if (response.ok) {
          dashboardConfig.value = await response.json()
        } else {
          throw new Error('Dashboard configuration not found')
        }
      }
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load dashboard configuration'
    console.error('Error loading dashboard config:', err)
  }
}

// Fetch data for all widgets
async function fetchWidgetData() {
  if (!dashboardConfig.value || !dashboardConfig.value.widgets) return

  const serviceUrl = serviceUrls[currentService.value]
  if (!serviceUrl) return

  // Fetch data for each widget in parallel
  const promises = dashboardConfig.value.widgets.map(async (widget: any) => {
    if (widget.endpoint) {
      try {
        const url = widget.endpoint.startsWith('http') 
          ? widget.endpoint 
          : `${serviceUrl}${widget.endpoint}`
          
        const response = await fetch(url)
        if (response.ok) {
          const data = await response.json()
          
          // Process data based on widget type
          if (widget.type === 'metric') {
            // Extract the value using the valueField configuration
            let value = 0
            if (widget.valueField) {
              // Handle nested field paths like "data.count"
              const fields = widget.valueField.split('.')
              value = fields.reduce((obj, field) => obj?.[field], data) || 0
            } else if (widget.valueField === 'count' && Array.isArray(data)) {
              // Special case: if expecting count and data is array, use length
              value = data.length
            } else {
              value = data.value || data || 0
            }
            
            widgetData.value[widget.id] = {
              value: value,
              // Include other fields if they exist
              change: data.change,
              trend: data.trend,
              label: data.label || widget.title
            }
          } else if (widget.type === 'list') {
            // Handle list data - could be an array or object with items
            widgetData.value[widget.id] = {
              items: Array.isArray(data) ? data : (data.items || data.data || [])
            }
          } else if (widget.type === 'table') {
            // Handle table data
            widgetData.value[widget.id] = {
              rows: Array.isArray(data) ? data : (data.rows || data.data || [])
            }
          } else {
            // For other widget types, store data as-is
            widgetData.value[widget.id] = data
          }
        }
      } catch (err) {
        console.error(`Error fetching data for widget ${widget.id}:`, err)
      }
    }
  })

  await Promise.all(promises)
}

// Initialize dashboard
async function initDashboard() {
  loading.value = true
  error.value = ''
  
  await fetchDashboardConfig()
  
  if (dashboardConfig.value) {
    await fetchWidgetData()
    
    // Set up auto-refresh if configured
    if (dashboardConfig.value.refreshInterval) {
      refreshInterval.value = window.setInterval(() => {
        fetchWidgetData()
      }, dashboardConfig.value.refreshInterval)
    }
  }
  
  loading.value = false
}

// Format value based on type
function formatValue(value: any, format?: string): string {
  if (value === null || value === undefined) return '-'
  
  switch (format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    case 'number':
      return Number(value).toLocaleString()
    case 'percentage':
      return `${(value * 100).toFixed(1)}%`
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'datetime':
      return new Date(value).toLocaleString()
    default:
      return String(value)
  }
}

// Get grid class based on layout configuration
function getGridClass(layout?: any): string {
  if (!layout) return 'grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3'
  
  const cols = layout.columns || 3
  return `grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-${cols}`
}

// Get widget class based on span configuration
function getWidgetClass(widget: any): string {
  const span = widget.span || 1
  const height = widget.height ? `h-${widget.height}` : ''
  return `col-span-1 lg:col-span-${span} ${height}`
}

// Get icon component (would need icon library integration)
function getIcon(iconName: string): any {
  // This would map icon names to actual icon components
  return null
}

// Execute widget action
function executeAction(action: any, widget: any) {
  if (action.route) {
    router.push(action.route)
  } else if (action.handler) {
    // Custom action handler
    action.handler(widget, widgetData.value[widget.id])
  }
}

// Watch for service changes
watch(currentService, () => {
  initDashboard()
})

// Lifecycle
onMounted(() => {
  initDashboard()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>