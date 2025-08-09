<template>
  <AppLayout>
    <!-- Loading Schema -->
    <div v-if="loadingSchema" class="flex justify-center py-12">
      <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm text-gray-600">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Loading view configuration...
      </div>
    </div>

    <!-- Schema Error -->
    <div v-else-if="schemaError" class="rounded-md bg-red-50 p-4 m-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">View Configuration Error</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ schemaError }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Dynamic Component -->
    <component 
      v-else-if="schema && componentType"
      :is="componentType"
      :schema="schema"
      :service-url="serviceUrl"
      :id="recordId"
      @row-click="handleRowClick"
      @action="handleAction"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />

    <!-- No Schema -->
    <div v-else class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No View Configuration</h3>
      <p class="mt-1 text-sm text-gray-500">This view has not been configured yet.</p>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import GenericListView from '@/components/generic/GenericListView.vue'
import GenericFormView from '@/components/generic/GenericFormView.vue'

const route = useRoute()
const router = useRouter()

// State
const schema = ref<any>(null)
const loadingSchema = ref(true)
const schemaError = ref('')

// Service mapping - would normally come from a registry
const SERVICE_MAPPING: Record<string, string> = {
  'inventory': 'http://localhost:8005',
  'sales': 'http://localhost:8006',
  'partners': 'http://localhost:8002',
  'users': 'http://localhost:8001'
}

// Computed
const serviceName = computed(() => {
  // Extract service name from route (e.g., /inventory/products -> inventory)
  const pathParts = route.path.split('/')
  return pathParts[1] || ''
})

const serviceUrl = computed(() => {
  return SERVICE_MAPPING[serviceName.value] || ''
})

const viewType = computed(() => {
  // Determine view type from route
  const path = route.path
  
  if (path.endsWith('/new')) return 'form-create'
  if (path.endsWith('/edit')) return 'form-edit'
  if (path.includes('/tree')) return 'tree'
  
  // Check route name or path patterns
  if (route.name?.includes('List')) return 'list'
  if (route.name?.includes('Form')) return 'form'
  if (route.name?.includes('Dashboard')) return 'dashboard'
  
  // Default based on path
  const lastSegment = path.split('/').pop()
  if (lastSegment === 'products' || lastSegment === 'warehouses' || lastSegment === 'stock') {
    return 'list'
  }
  
  return 'list' // default
})

const recordId = computed(() => {
  return route.params.id as string
})

const componentType = computed(() => {
  if (!schema.value) return null
  
  // Map view types to components
  switch (schema.value.viewType || viewType.value) {
    case 'list':
    case 'table':
    case 'cards':
      return GenericListView
    case 'form':
    case 'form-create':
    case 'form-edit':
      return GenericFormView
    case 'tree':
      // Would import GenericTreeView when implemented
      return null
    case 'dashboard':
      // Would import GenericDashboard
      return null
    default:
      return null
  }
})

// Schema loading
async function loadSchema() {
  if (!serviceUrl.value) {
    schemaError.value = 'Service not configured'
    loadingSchema.value = false
    return
  }
  
  loadingSchema.value = true
  schemaError.value = ''
  
  try {
    // Determine schema endpoint based on route
    const schemaEndpoint = getSchemaEndpoint()
    if (!schemaEndpoint) {
      schemaError.value = 'No schema endpoint configured for this view'
      return
    }
    
    const response = await fetch(`${serviceUrl.value}${schemaEndpoint}`)
    if (!response.ok) {
      throw new Error(`Failed to load schema: ${response.status}`)
    }
    
    schema.value = await response.json()
    
    // Process schema - convert function strings to actual functions
    processSchema(schema.value)
    
  } catch (err: any) {
    console.error('Error loading schema:', err)
    schemaError.value = err.message || 'Failed to load view configuration'
  } finally {
    loadingSchema.value = false
  }
}

function getSchemaEndpoint(): string {
  const path = route.path
  
  // Map routes to schema endpoints
  if (path.includes('/products')) {
    if (path.includes('/new') || path.includes('/edit')) {
      return '/api/v1/ui-schemas/products/form'
    }
    return '/api/v1/ui-schemas/products/list'
  }
  
  if (path.includes('/warehouses')) {
    if (path.includes('/new') || path.includes('/edit')) {
      return '/api/v1/ui-schemas/warehouses/form'
    }
    return '/api/v1/ui-schemas/warehouses/list'
  }
  
  if (path.includes('/stock/movements')) {
    return '/api/v1/ui-schemas/stock/movements'
  }
  
  if (path.includes('/categories')) {
    return '/api/v1/ui-schemas/categories/tree'
  }
  
  return ''
}

function processSchema(schema: any) {
  // Convert function strings to actual functions
  if (schema.columns) {
    schema.columns.forEach((col: any) => {
      if (col.cellClassFunction && typeof col.cellClassFunction === 'string') {
        try {
          col.cellClassFunction = new Function('value', 'item', col.cellClassFunction.replace(/^function\s*\([^)]*\)\s*{/, '').replace(/}$/, ''))
        } catch (e) {
          console.error('Error parsing cellClassFunction:', e)
        }
      }
      if (col.formatter && typeof col.formatter === 'string' && col.formatter.includes('function')) {
        try {
          col.formatter = new Function('value', 'item', col.formatter.replace(/^function\s*\([^)]*\)\s*{/, '').replace(/}$/, ''))
        } catch (e) {
          console.error('Error parsing formatter:', e)
        }
      }
    })
  }
  
  if (schema.sections) {
    schema.sections.forEach((section: any) => {
      section.fields?.forEach((field: any) => {
        if (field.compute && typeof field.compute === 'string') {
          try {
            field.compute = new Function('data', field.compute.replace(/^function\s*\([^)]*\)\s*{/, '').replace(/}$/, ''))
          } catch (e) {
            console.error('Error parsing compute function:', e)
          }
        }
        if (field.validate && typeof field.validate === 'string') {
          try {
            field.validate = new Function('value', 'data', field.validate.replace(/^function\s*\([^)]*\)\s*{/, '').replace(/}$/, ''))
          } catch (e) {
            console.error('Error parsing validate function:', e)
          }
        }
      })
    })
  }
}

// Event handlers
function handleRowClick(item: any) {
  if (schema.value?.editRoute) {
    const route = schema.value.editRoute.replace('{id}', item.id)
    router.push(route)
  }
}

function handleAction(action: any, item?: any) {
  console.log('Action:', action, item)
  
  if (action.id === 'create') {
    if (schema.value?.createRoute) {
      router.push(schema.value.createRoute)
    }
  } else if (action.route) {
    const route = item 
      ? action.route.replace('{id}', item.id)
      : action.route
    router.push(route)
  }
}

function handleSubmit(data: any) {
  console.log('Form submitted:', data)
  // Navigate back to list or show success message
  if (schema.value?.successRoute) {
    router.push(schema.value.successRoute)
  }
}

function handleCancel() {
  if (schema.value?.cancelRoute) {
    router.push(schema.value.cancelRoute)
  } else {
    router.back()
  }
}

// Watch route changes
watch(() => route.path, () => {
  loadSchema()
})

// Initialize
onMounted(() => {
  loadSchema()
})
</script>