<template>
  <div class="bg-white overflow-hidden shadow rounded-lg h-full">
    <div class="p-5">
      <!-- Widget Header -->
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-medium text-gray-900">{{ widget.title }}</h3>
        <button
          v-if="widget.refresh_interval > 0"
          @click="$emit('refresh')"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      <!-- Widget Content based on type -->
      <div class="widget-content">
        <!-- Metric Widget -->
        <div v-if="widget.type === 'metric'" class="metric-widget">
          <div class="flex items-center">
            <div v-if="widget.config.icon" class="flex-shrink-0 mr-4">
              <div :class="`bg-${widget.config.color || 'blue'}-100 rounded-full p-3`">
                <svg class="h-6 w-6" :class="`text-${widget.config.color || 'blue'}-600`" 
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <!-- Icon would be dynamically rendered based on widget.config.icon -->
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500 truncate">{{ widget.title }}</p>
              <p class="mt-1 text-3xl font-semibold text-gray-900">
                {{ formatValue(getValue(), widget.config.format) }}
              </p>
            </div>
          </div>
          <div v-if="widget.config.link" class="mt-4">
            <router-link :to="widget.config.link" 
              class="text-sm font-medium text-primary-600 hover:text-primary-500">
              View details →
            </router-link>
          </div>
        </div>

        <!-- Chart Widget -->
        <div v-else-if="widget.type === 'chart'" class="chart-widget">
          <div class="h-48 flex items-center justify-center text-gray-400">
            Chart: {{ widget.id }}
            <!-- Chart component would be rendered here -->
          </div>
        </div>

        <!-- List Widget -->
        <div v-else-if="widget.type === 'list'" class="list-widget">
          <div v-if="!listData || listData.length === 0" class="text-gray-500 text-sm">
            No data available
          </div>
          <ul v-else class="-my-5 divide-y divide-gray-200">
            <li v-for="(item, index) in listData.slice(0, widget.config.limit || 5)" 
              :key="index" class="py-3">
              <div class="flex items-center space-x-4">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ getListItemTitle(item) }}
                  </p>
                  <p class="text-sm text-gray-500">
                    {{ getListItemSubtitle(item) }}
                  </p>
                </div>
                <div v-if="getListItemValue(item)" class="text-right">
                  <div class="text-sm font-medium text-gray-900">
                    {{ getListItemValue(item) }}
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Table Widget -->
        <div v-else-if="widget.type === 'table'" class="table-widget">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th v-for="col in widget.config.columns" :key="col"
                    class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(row, index) in tableData" :key="index">
                  <td v-for="col in widget.config.columns" :key="col"
                    class="px-3 py-2 whitespace-nowrap text-sm text-gray-900">
                    {{ row[col] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Custom Widget -->
        <div v-else class="custom-widget">
          <component 
            v-if="customComponent"
            :is="customComponent"
            :widget="widget"
            :data="data"
          />
          <div v-else class="text-gray-500 text-sm">
            Widget type not supported: {{ widget.type }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DashboardWidget } from '@/services/uiRegistry'

const props = defineProps<{
  widget: DashboardWidget
  data: any
}>()

const emit = defineEmits<{
  refresh: []
}>()

// Extract list data from response (handles both array and object with data property)
const listData = computed(() => {
  if (!props.data) return []
  if (Array.isArray(props.data)) return props.data
  if (props.data.data && Array.isArray(props.data.data)) return props.data.data
  return []
})

// Extract table data from response (handles both array and object with data property)
const tableData = computed(() => {
  if (!props.data) return []
  if (Array.isArray(props.data)) return props.data
  if (props.data.data && Array.isArray(props.data.data)) return props.data.data
  return []
})

// Get value from data based on widget config
const getValue = () => {
  if (!props.data) return 0
  const field = props.widget.config.field
  if (!field) return props.data
  return props.data[field] || 0
}

// Format value based on type
const formatValue = (value: any, format?: string) => {
  if (value === null || value === undefined) return '-'
  
  switch (format) {
    case 'number':
      return Number(value).toLocaleString()
    case 'currency':
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value)
    case 'percentage':
      return `${(value * 100).toFixed(1)}%`
    case 'boolean':
      return value ? 'Yes' : 'No'
    default:
      return value
  }
}

// List widget helpers
const getListItemTitle = (item: any) => {
  const columns = props.widget.config.columns || []
  if (columns.length > 0) {
    return item[columns[0]] || ''
  }
  return item.name || item.title || item.id || ''
}

const getListItemSubtitle = (item: any) => {
  const columns = props.widget.config.columns || []
  if (columns.length > 1) {
    const values = columns.slice(1, 3).map(col => item[col]).filter(Boolean)
    return values.join(' • ')
  }
  return item.description || ''
}

const getListItemValue = (item: any) => {
  const columns = props.widget.config.columns || []
  if (columns.length > 3) {
    return item[columns[3]] || ''
  }
  return item.value || item.quantity || ''
}

// Custom component loading (would be implemented based on widget type)
const customComponent = computed(() => {
  // This would dynamically load custom widget components
  return null
})
</script>

<style scoped>
.widget-content {
  min-height: 100px;
}

.metric-widget {
  display: flex;
  flex-direction: column;
}

.chart-widget,
.list-widget,
.table-widget {
  max-height: 300px;
  overflow-y: auto;
}
</style>