<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Dashboard Header -->
      <div v-if="dashboardConfig">
        <h1 class="text-2xl font-bold">{{ dashboardConfig.title }}</h1>
        <p v-if="dashboardConfig.description" class="mt-2 text-sm">
          {{ dashboardConfig.description }}
          description
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
            <div class="text-h3 font-medium text-red-800">Error loading dashboard</div>
            <div class="mt-2 text-sm">
              <p class="text-red-700">{{ error }}</p>
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
             class="glass-card rounded-lg shadow">
          
          <!-- Widget Header -->
          <div v-if="widget.title || getWidgetIcon(widget)" class="px-6 py-4 border-b border-gray-200/20" :style="getWidgetHeaderStyle(widget)">
            <div class="flex items-center">
              <svg v-if="getWidgetIcon(widget)" :class="['h-6 w-6 mr-2', getFontColorClass(widget)]" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getIconPath(getWidgetIcon(widget))" />
              </svg>
              <div :class="['text-h3 text-lg font-medium', getFontColorClass(widget)]">{{ widget.title }}</div>
            </div>
          </div>
          
          <!-- Widget Content -->
          <div class="p-6">
            <!-- Metric Widget -->
            <div v-if="widget.type === 'metric'">
              <div v-if="widgetData[widget.id]">
                <div :class="['text-3xl font-bold', getFontColorClass(widget)]">
                  {{ formatValue(widgetData[widget.id].value, widget.format) }}
                </div>
                <div v-if="widgetData[widget.id].change" :class="['mt-2 flex items-center text-sm', getFontColorClass(widget)]">
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
                <div :class="['flex items-center justify-center h-full', getFontColorClass(widget)]">
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
                <ul :class="['divide-y divide-gray-200/20', getFontColorClass(widget)]">
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
                          :class="['px-3 py-2 text-left text-xs font-medium uppercase tracking-wider', getFontColorClass(widget)]">
                        {{ column.label }}
                      </th>
                    </tr>
                  </thead>
                  <tbody :class="['divide-y divide-gray-200/20', getFontColorClass(widget)]">
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
               :class="['px-6 py-3 border-t border-gray-200/20 flex justify-end space-x-2', getFontColorClass(widget)]"
               :style="widget.config?.color ? `border-color: ${adjustColor(widget.config.color, -20)}` : ''">
            <button v-for="action in widget.actions" 
                    :key="action.id"
                    @click="() => executeAction(action, widget)"
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
  sales: import.meta.env.VITE_SALES_API || '',
  inventory: import.meta.env.VITE_INVENTORY_API || '',
  purchasing: import.meta.env.VITE_PURCHASING_API || '',
  main: import.meta.env.VITE_API_BASE_URL || ''
}

// Fetch dashboard configuration from service
async function fetchDashboardConfig() {
  try {

      // First try to get from UI Registry
      const uiRegistryUrl = import.meta.env.VITE_UI_REGISTRY_API || '/api'
      const registryEndpoint = `/api/v1/${currentService.value}/dashboard`
      const registryFullUrl = uiRegistryUrl && registryEndpoint.startsWith('/api/v1')
        ? `${uiRegistryUrl.replace(/\/api\/v1$/, '')}${registryEndpoint}`
        : `${uiRegistryUrl}${registryEndpoint}`


      // console.log('uiRegistryUrl====', uiRegistryUrl)
      // console.log('registryFullUrl====', registryFullUrl)

      const registryResponse = await fetch(registryFullUrl)

      // console.log('registryResponse', registryResponse)
      
      if (registryResponse.ok) {
        dashboardConfig.value = await registryResponse.json()
      } else {
        // Fallback to service's own endpoint
        const serviceUrl = serviceUrls[currentService.value]
        if (serviceUrl) {
          const dashboardEndpoint = `/api/v1/${currentService.value}/ui-schemas/dashboard`
          const dashboardFullUrl = serviceUrl && dashboardEndpoint.startsWith('/api/v1')
            ? `${serviceUrl.replace(/\/api\/v1$/, '')}${dashboardEndpoint}`
            : `${serviceUrl}${dashboardEndpoint}`
          console.log('dashboardFullUrl==',dashboardFullUrl)
          const response = await fetch(dashboardFullUrl)

          if (response.ok) {
            dashboardConfig.value = await response.json()

          } else {
            throw new Error(`Dashboard configuration not found: ${response.status}`)
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

  // Get the correct service URL based on current service
  let serviceUrl = serviceUrls[currentService.value]
  
  // For inventory service, use the VITE_INVENTORY_API environment variable
  // if (currentService.value === 'inventory') {
  //   serviceUrl = import.meta.env.VITE_INVENTORY_API || 'http://inventory-service:8005'
  // }
  
  if (!serviceUrl) return

  // Fetch data for each widget in parallel
  const promises = dashboardConfig.value.widgets.map(async (widget: any) => {
    if (widget.endpoint) {
      try {
        // const url = widget.endpoint.startsWith('http') 
        //   ? widget.endpoint 
        //   : `${serviceUrl}${widget.endpoint}`
        const url = widget.endpoint
        
        console.log('widget==', widget)
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
  const color = widget.config.color
  return `col-span-1 lg:col-span-${span} ${height} metric-${color}`
}
// // Get widget style based on configuration
// function getWidgetStyle(widget: any): string {
//   const color = widget.config?.color
//   if (color) {
//     return `background-color: ${color}`;
//   }
//   return '';
// }

// Get widget header style based on configuration
function getWidgetHeaderStyle(widget: any): string {
  const color = widget.config?.color;
  if (color) {
    // Calculate appropriate text color based on background luminance
    const textColor = getTextColorForBackground(color);
    return `background-color: ${color}; color: ${textColor}; border-color: ${adjustColor(color, -20)};`;
  }
  return '';
}

// Get appropriate text color based on background color
function getTextColorForBackground(bgColor: string): string {
  // Convert color to RGB if it's a named color or hex
  let r = 0, g = 0, b = 0;
  
  // Handle named colors
  const namedColors: Record<string, string> = {
    'red': '#FF0000', 'blue': '#0000FF', 'green': '#008000', 'yellow': '#FFFF00',
    'orange': '#FFA500', 'purple': '#800080', 'pink': '#FFC0CB', 'brown': '#A52A2A',
    'black': '#000000', 'white': '#FFFFFF', 'gray': '#808080', 'grey': '#808080',
    'cyan': '#00FFFF', 'magenta': '#FF00FF', 'lime': '#00FF00', 'navy': '#000080',
    'maroon': '#800000', 'olive': '#808000', 'teal': '#008080', 'silver': '#C0C0C0',
    'lightblue': '#ADD8E6', 'lightgreen': '#90EE90', 'lightyellow': '#FFFFE0',
    'lightpink': '#FFB6C1', 'lightgray': '#D3D3D3', 'darkgray': '#A9A9A9',
    'darkblue': '#00008B', 'darkgreen': '#006400', 'darkred': '#8B0000'
  };
  
  let colorToUse = bgColor.toLowerCase();
  if (namedColors[colorToUse]) {
    colorToUse = namedColors[colorToUse];
  }
  
  // Handle hex color
  if (colorToUse.startsWith('#')) {
    const hex = colorToUse.slice(1);
    if (hex.length === 3) {
      r = parseInt(hex[0] + hex[0], 16);
      g = parseInt(hex[1] + hex[1], 16);
      b = parseInt(hex[2] + hex[2], 16);
    } else if (hex.length === 6) {
      r = parseInt(hex.substring(0, 2), 16);
      g = parseInt(hex.substring(2, 4), 16);
      b = parseInt(hex.substring(4, 6), 16);
    }
  } 
  // Handle rgb color
  else if (colorToUse.startsWith('rgb(')) {
    const match = colorToUse.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      r = parseInt(match[1]);
      g = parseInt(match[2]);
      b = parseInt(match[3]);
    }
  }
  // Handle rgba color
  else if (colorToUse.startsWith('rgba(')) {
    const match = colorToUse.match(/rgba\((\d+),\s*(\d+),\s*(\d+),?\s*[\d.]*\)/);
    if (match) {
      r = parseInt(match[1]);
      g = parseInt(match[2]);
      b = parseInt(match[3]);
    }
  }
  
  // Calculate luminance (perceived brightness)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  // Return white for dark backgrounds, black for light backgrounds
  return luminance < 0.6 ? '#FFFFFF' : '#000000';
}

// Adjust color brightness (positive for lighter, negative for darker)
function adjustColor(color: string, percent: number): string {
  let r = 0, g = 0, b = 0;
  
  // Handle named colors
  const namedColors: Record<string, string> = {
    'red': '#FF0000', 'blue': '#0000FF', 'green': '#008000', 'yellow': '#FFFF00',
    'orange': '#FFA500', 'purple': '#800080', 'pink': '#FFC0CB', 'brown': '#A52A2A',
    'black': '#000000', 'white': '#FFFFFF', 'gray': '#808080', 'grey': '#808080',
    'cyan': '#00FFFF', 'magenta': '#FF00FF', 'lime': '#00FF00', 'navy': '#000080',
    'maroon': '#800000', 'olive': '#808000', 'teal': '#008080', 'silver': '#C0C0C0',
    'lightblue': '#ADD8E6', 'lightgreen': '#90EE90', 'lightyellow': '#FFFFE0',
    'lightpink': '#FFB6C1', 'lightgray': '#D3D3D3', 'darkgray': '#A9A9A9',
    'darkblue': '#00008B', 'darkgreen': '#006400', 'darkred': '#8B0000'
  };
  
  let colorToUse = color.toLowerCase();
  if (namedColors[colorToUse]) {
    colorToUse = namedColors[colorToUse];
  }
  
  // Handle hex color
  if (colorToUse.startsWith('#')) {
    const hex = colorToUse.slice(1);
    if (hex.length === 3) {
      r = parseInt(hex[0] + hex[0], 16);
      g = parseInt(hex[1] + hex[1], 16);
      b = parseInt(hex[2] + hex[2], 16);
    } else if (hex.length === 6) {
      r = parseInt(hex.substring(0, 2), 16);
      g = parseInt(hex.substring(2, 4), 16);
      b = parseInt(hex.substring(4, 6), 16);
    }
  } 
  // Handle rgb color
  else if (colorToUse.startsWith('rgb(')) {
    const match = colorToUse.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      r = parseInt(match[1]);
      g = parseInt(match[2]);
      b = parseInt(match[3]);
    }
  }
  // Handle rgba color
  else if (colorToUse.startsWith('rgba(')) {
    const match = colorToUse.match(/rgba\((\d+),\s*(\d+),\s*(\d+),?\s*[\d.]*\)/);
    if (match) {
      r = parseInt(match[1]);
      g = parseInt(match[2]);
      b = parseInt(match[3]);
    }
  }
  
  // Adjust brightness
  r = Math.min(255, Math.max(0, r + Math.floor(r * percent / 100)));
  g = Math.min(255, Math.max(0, g + Math.floor(g * percent / 100)));
  b = Math.min(255, Math.max(0, b + Math.floor(b * percent / 100)));
  
  return `rgb(${r}, ${g}, ${b})`;
}

// Get font color class based on widget background
function getFontColorClass(widget: any): string {
  const color = widget.config?.color;
  if (color) {
    const textColor = getTextColorForBackground(color);
    // Return a class or inline style based on the calculated text color
    return textColor === '#FFFFFF' ? 'text-white' : 'text-gray-900';
  }
  return 'text-gray-900'; // Default to dark text
}

// Get widget icon - supporting both widget.icon and widget.config.icon
function getWidgetIcon(widget: any): string | null {
  // First check if icon is in config (from UI registry)
  if (widget.config && widget.config.icon) {
    return widget.config.icon;
  }
  // Then check if icon is a direct property of the widget
  if (widget.icon) {
    return widget.icon;
  }
  return null;
}

// Helper to get SVG path data for icon name
function getIconPath(iconName: string): string {
  // Define common icons by their SVG path data
  const iconPaths: Record<string, string> = {
    'dollar-sign': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    'file-text': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    'clock': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    'trending-up': 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6',
    'shopping-bag': 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z',
    'shopping-cart': 'M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l-2.5 5m0 0h15m-12 3V7a4 4 0 018 0v8.086M19 19a2 2 0 01-2 2H7a2 2 0 01-2-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 00-2 2v10a2 2 0 002 2m14 0V9a2 2 0 002-2M9 9a2 2 0 00-2 2v10a2 2 0 002 2m6-2a2 2 0 00-2-2V9m0 0a2 2 0 00-2 2v10a2 2 0 002 2',
    'user': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    'users': 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    'bar-chart': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    'grid-3x3': 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
    'cogs': 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
    'eye': 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z',
    'pencil': 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
    'send': 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
    'arrow-right': 'M14 5l7 7m0 0l-7 7m7-7H3',
    'trash': 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
    'x-circle': 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    'truck': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    'calendar': 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
    'bell': 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
    // Default icon for unknown icon names
    'default': 'M13 10V3L4 14h7v7l9-11h-7z'
  };

  return iconPaths[iconName] || iconPaths['default'];
}

// Helper to get icon class for styling
function getIconClass(iconName: string): string {
  // Return appropriate class based on the icon name
  return 'text-gray-500';
}

// Execute widget action
async function executeAction(action: any, widget: any) {
  // First try to execute backend service function if action has endpoint
  if (action.endpoint) {
    try {
      // Get auth token from cookies
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('auth_token='))
        ?.split('=')[1]
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }
      
      // Add authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      // Determine HTTP method (default to POST)
      const method = action.method || 'POST'
      
      // Prepare request body if needed
      let body = undefined
      if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
        body = JSON.stringify({
          action: action.id,
          widget: widget.id,
          data: widgetData.value[widget.id]
        })
      }
      
      const response = await fetch(action.endpoint, {
        method,
        headers,
        body
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      
      // If there's a success handler, call it
      if (action.onSuccess) {
        action.onSuccess(result)
      }
      
      // Refresh widget data after successful action
      await fetchWidgetData()
      
      return result
    } catch (error) {
      console.error('Error executing backend action:', error)
      
      // If there's an error handler, call it
      if (action.onError) {
        action.onError(error)
      }
      
      throw error
    }
  } 
  // Fallback to existing behavior
  else if (action.route) {
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

<style scoped>
.metric-blue{
  background: blue;
}
.metric-red{
  background: red;
}
.metric-orange{
  background: orange;
}
.metric-green{
  background:green;
}
.metric-purple{
  background:purple;
}
</style>
