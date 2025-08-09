<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">{{ schema.title || 'List' }}</h1>
        <p v-if="schema.description" class="mt-1 text-sm text-gray-600">
          {{ schema.description }}
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <!-- Custom Actions -->
        <button
          v-for="action in schema.headerActions"
          :key="action.id"
          @click="executeAction(action)"
          :class="getActionClasses(action)"
          class="inline-flex items-center px-4 py-2 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2"
        >
          <component v-if="action.icon" :is="getIcon(action.icon)" class="-ml-1 mr-2 h-5 w-5" />
          {{ action.label }}
        </button>
        
        <!-- Default Actions -->
        <button
          v-if="schema.refreshable !== false"
          @click="refresh"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="-ml-0.5 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Refresh
        </button>
        <button
          v-if="schema.createable !== false"
          @click="createNew"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          {{ schema.createLabel || 'New' }}
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div v-if="schema.searchable || schema.filters" class="mb-6 flex flex-col sm:flex-row gap-4">
      <div v-if="schema.searchable" class="flex-1">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="schema.searchPlaceholder || 'Search...'"
          class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          @input="debouncedSearch"
        >
      </div>
      
      <!-- Dynamic Filters -->
      <template v-for="filter in schema.filters" :key="filter.field">
        <select
          v-if="filter.type === 'select'"
          v-model="filters[filter.field]"
          @change="applyFilters"
          class="block rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
          <option value="">{{ filter.placeholder || `All ${filter.label}` }}</option>
          <option v-for="option in filter.options" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        
        <input
          v-else-if="filter.type === 'date'"
          v-model="filters[filter.field]"
          type="date"
          @change="applyFilters"
          class="block rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        >
      </template>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm text-gray-600">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading...
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="rounded-md bg-red-50 p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div v-else-if="schema.viewType === 'table' && items.length > 0" class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="column in visibleColumns" 
              :key="column.field"
              scope="col" 
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="column.headerClass"
            >
              {{ column.label }}
            </th>
            <th v-if="schema.rowActions?.length" scope="col" class="relative px-6 py-3">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="item in items" 
            :key="getItemKey(item)"
            @click="handleRowClick(item)"
            :class="{ 'hover:bg-gray-50 cursor-pointer': schema.clickable }"
          >
            <td 
              v-for="column in visibleColumns" 
              :key="column.field"
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="column.cellClass"
            >
              <component 
                v-if="column.component"
                :is="column.component"
                :value="getNestedValue(item, column.field)"
                :item="item"
                :column="column"
              />
              <span v-else-if="column.formatter">
                {{ formatValue(getNestedValue(item, column.field), column.formatter, item) }}
              </span>
              <span v-else :class="getCellClass(item, column)">
                {{ getNestedValue(item, column.field) || '-' }}
              </span>
            </td>
            <td v-if="schema.rowActions?.length" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex justify-end space-x-2">
                <button
                  v-for="action in getRowActions(item)"
                  :key="action.id"
                  @click.stop="executeRowAction(action, item)"
                  :class="getActionClasses(action)"
                  class="text-sm"
                >
                  {{ action.label }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Card View -->
    <div v-else-if="schema.viewType === 'cards' && items.length > 0" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="item in items"
        :key="getItemKey(item)"
        @click="handleRowClick(item)"
        class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
        :class="{ 'cursor-pointer': schema.clickable }"
      >
        <div class="px-4 py-5 sm:p-6">
          <template v-for="column in visibleColumns.slice(0, 5)" :key="column.field">
            <div v-if="column.isTitle" class="text-lg font-medium text-gray-900 mb-2">
              {{ getNestedValue(item, column.field) }}
            </div>
            <div v-else class="text-sm text-gray-500">
              <span class="font-medium">{{ column.label }}:</span>
              {{ formatValue(getNestedValue(item, column.field), column.formatter, item) || '-' }}
            </div>
          </template>
        </div>
        <div v-if="schema.rowActions?.length" class="bg-gray-50 px-4 py-3">
          <div class="flex justify-end space-x-2">
            <button
              v-for="action in getRowActions(item)"
              :key="action.id"
              @click.stop="executeRowAction(action, item)"
              :class="getActionClasses(action)"
              class="text-sm"
            >
              {{ action.label }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && items.length === 0" class="text-center py-12">
      <component v-if="schema.emptyIcon" :is="getIcon(schema.emptyIcon)" class="mx-auto h-12 w-12 text-gray-400" />
      <svg v-else class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">{{ schema.emptyTitle || 'No items' }}</h3>
      <p class="mt-1 text-sm text-gray-500">{{ schema.emptyMessage || 'No items to display.' }}</p>
      <div v-if="schema.createable !== false" class="mt-6">
        <button
          @click="createNew"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          {{ schema.createLabel || 'Create First Item' }}
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex items-center justify-between">
      <div class="flex-1 flex justify-between sm:hidden">
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Previous
        </button>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Next
        </button>
      </div>
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
            to
            <span class="font-medium">{{ Math.min(currentPage * pageSize, totalItems) }}</span>
            of
            <span class="font-medium">{{ totalItems }}</span>
            results
          </p>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
            >
              <span class="sr-only">Previous</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
            >
              <span class="sr-only">Next</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

// Props
const props = defineProps<{
  schema: any  // UI schema from service
  endpoint?: string  // Optional direct endpoint
  serviceUrl?: string  // Service base URL
}>()

const emit = defineEmits<{
  'row-click': [item: any]
  'action': [action: any, item?: any]
}>()

const router = useRouter()

// State
const items = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const filters = ref<Record<string, any>>({})
const currentPage = ref(1)
const pageSize = ref(props.schema.pageSize || 20)
const totalItems = ref(0)

// Computed
const totalPages = computed(() => Math.ceil(totalItems.value / pageSize.value))

const visibleColumns = computed(() => {
  return props.schema.columns?.filter((col: any) => col.visible !== false) || []
})

// API URL
const apiUrl = computed(() => {
  if (props.endpoint) return props.endpoint
  if (props.schema.endpoint) {
    return props.serviceUrl ? `${props.serviceUrl}${props.schema.endpoint}` : props.schema.endpoint
  }
  return ''
})

// Fetch data
async function fetchData() {
  if (!apiUrl.value) {
    error.value = 'No endpoint configured'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const params = new URLSearchParams()
    
    // Pagination
    if (props.schema.paginated !== false) {
      params.append('page', currentPage.value.toString())
      params.append('page_size', pageSize.value.toString())
    }
    
    // Search
    if (searchQuery.value && props.schema.searchable) {
      params.append(props.schema.searchParam || 'search', searchQuery.value)
    }
    
    // Filters
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value) params.append(key, value.toString())
    })
    
    const response = await fetch(`${apiUrl.value}?${params}`)
    if (!response.ok) throw new Error('Failed to fetch data')
    
    const data = await response.json()
    
    // Handle different response formats
    if (props.schema.dataPath) {
      items.value = getNestedValue(data, props.schema.dataPath) || []
    } else if (Array.isArray(data)) {
      items.value = data
    } else if (data.items) {
      items.value = data.items
      totalItems.value = data.total || data.items.length
    } else if (data.data) {
      items.value = data.data
      totalItems.value = data.total || data.count || data.data.length
    } else {
      items.value = []
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load data'
    console.error('Error fetching data:', err)
  } finally {
    loading.value = false
  }
}

// Actions
function refresh() {
  fetchData()
}

function createNew() {
  if (props.schema.createRoute) {
    router.push(props.schema.createRoute)
  } else {
    emit('action', { id: 'create' })
  }
}

function handleRowClick(item: any) {
  if (props.schema.clickable === false) return
  
  if (props.schema.editRoute) {
    const route = props.schema.editRoute.replace('{id}', getItemKey(item))
    router.push(route)
  } else {
    emit('row-click', item)
  }
}

function executeAction(action: any) {
  emit('action', action)
}

function executeRowAction(action: any, item: any) {
  if (action.route) {
    const route = action.route.replace('{id}', getItemKey(item))
    router.push(route)
  } else {
    emit('action', action, item)
  }
}

// Search and filter
let searchTimeout: NodeJS.Timeout
function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, props.schema.searchDebounce || 300)
}

function applyFilters() {
  currentPage.value = 1
  fetchData()
}

// Pagination
function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchData()
  }
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchData()
  }
}

// Utility functions
function getItemKey(item: any): string {
  const keyField = props.schema.keyField || 'id'
  return item[keyField]?.toString() || ''
}

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((curr, prop) => curr?.[prop], obj)
}

function formatValue(value: any, formatter: any, item?: any): string {
  if (value === null || value === undefined) return ''
  
  if (typeof formatter === 'function') {
    return formatter(value, item)
  }
  
  switch (formatter) {
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
    case 'boolean':
      return value ? 'Yes' : 'No'
    default:
      return value.toString()
  }
}

function getCellClass(item: any, column: any): string {
  if (column.cellClassFunction) {
    return column.cellClassFunction(getNestedValue(item, column.field), item)
  }
  return column.cellClass || ''
}

function getActionClasses(action: any): string {
  const baseClasses = action.variant === 'primary' 
    ? 'border-transparent text-white bg-primary-600 hover:bg-primary-700'
    : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
  return `${baseClasses} ${action.class || ''}`
}

function getRowActions(item: any): any[] {
  if (!props.schema.rowActions) return []
  return props.schema.rowActions.filter((action: any) => {
    if (action.condition) {
      return action.condition(item)
    }
    return true
  })
}

function getIcon(iconName: string): any {
  // This would normally import icons dynamically
  // For now, return null
  return null
}

// Watch for schema changes
watch(() => props.schema, () => {
  fetchData()
}, { deep: true })

// Initialize
onMounted(() => {
  if (props.schema.autoLoad !== false) {
    fetchData()
  }
})

// Expose methods for parent components
defineExpose({
  refresh,
  fetchData
})
</script>