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
      <p class="mt-1 text-sm text-gray-900">This view has not been configured yet.</p>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import GenericListView from '@/components/generic/GenericListView.vue'
import GenericFormView from '@/components/generic/GenericFormView.vue'
import GenericDetailView from '@/components/generic/GenericDetailView.vue'
import GenericDashboard from '@/components/generic/GenericDashboard.vue'
import Breadcrumb from '@/components/generic/Breadcrumb.vue'

const route = useRoute()
const router = useRouter()

// State
const schema = ref<any>(null)
const loadingSchema = ref(true)
const schemaError = ref('')

// Service mapping - would normally come from a registry
// All requests go through Kong API Gateway
const SERVICE_MAPPING: Record<string, string> = {
  'inventory': import.meta.env.VITE_INVENTORY_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'sales': import.meta.env.VITE_SALES_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'purchasing': import.meta.env.VITE_PURCHASING_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'partners': import.meta.env.VITE_PARTNERS_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'users': import.meta.env.VITE_USERS_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'menu': import.meta.env.VITE_MENU_API || import.meta.env.VITE_API_URL || 'http://localhost:8000',
  'base': import.meta.env.VITE_BASE_API || import.meta.env.VITE_API_URL || 'http://localhost:8002'
}

// Computed
const serviceName = computed(() => {
  // Extract service name from route (e.g., /inventory/products -> inventory)
  const pathParts = route.path.split('/')
  const firstSegment = pathParts[1] || ''
  
  // Handle special cases
  // if (firstSegment === 'inventory') return 'inventory'
  // if (firstSegment === 'sales') return 'sales'
  // if (firstSegment === 'purchasing') return 'purchasing'
  // if (firstSegment === 'settings') return 'menu' // Settings routes go to menu service
  
  return firstSegment
})

const serviceUrl = computed(() => {
  // console.log('serviceUrl === ', SERVICE_MAPPING[serviceName.value])
  return SERVICE_MAPPING[serviceName.value] || ''
})

const viewType = computed(() => {
  // Determine view type from route
  const path = route.path
  
  // console.log('view type ===', route.name, 'path==',path)

  if (path.endsWith('/new')) return 'form-create'
  if (path.endsWith('/edit')) return 'form-edit'
  if (path.includes('/tree')) return 'tree'
  
  // Check route name or path patterns
  if (route.name?.includes('List')) return 'list'
  if (route.name?.includes('Form')) return 'form'
  if (route.name?.includes('Dashboard')) return 'dashboard'
  
  // console.log('return === list')
  return 'list' // default
})

const recordId = computed(() => {
  return route.params.id as string
})

const componentType = computed(() => {
  if (!schema.value) return null
  
  // console.log('schema.value.viewType==', schema.value.viewType , viewType.value)
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
    case 'detail':
    case 'view':      
      return GenericDetailView
    case 'tree':
      // Would import GenericTreeView when implemented
      return null
    case 'dashboard':
      // Would import GenericDashboard
      return GenericDashboard

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
    
    // Ensure we don't duplicate /api/v1 in the URL
    const fullUrl = serviceUrl.value && schemaEndpoint.startsWith('/api/v1') 
      ? `${serviceUrl.value.replace(/\/api\/v1$/, '')}${schemaEndpoint}`
      : `${serviceUrl.value}${schemaEndpoint}`
    const response = await fetch(fullUrl)
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

  console.log('getSchemaEndpoint path=',path)
  if (path.includes('dashboard'))
  {
    // console.log('dashboard includes', path)
    return '/api/v1'+path+'/ui-schemas'
  }
  else if(path.includes('/new')){
    // /sales/order/new => /sales/order/ui-schemas/form
    const segments = path.split("/").filter(segment => segment !== "");
    // console.log('segement includes', segments)
    return '/api/v1/'+segments[0]+'/'+segments[1]+'/ui-schemas/form'
  }
  else if(path.includes('/edit')){
    // /inventory/products/14/edit => /inventory/products/ui-schemas/form
    const segments = path.split("/").filter(segment => segment !== "");
    // console.log('segement', segments)
    return '/api/v1/'+segments[0]+'/'+segments[1]+'/ui-schemas/form'
  }
  else if(/\d+$/.test(path)) {
    // /inventory/products/14 => /inventory/products/ui-schemas/form
    const segments = path.split("/").filter(segment => segment !== "");
    // console.log('segement test', segments)
    return '/api/v1/'+segments[0]+'/'+segments[1]+'/ui-schemas/detail'
  }
  else{
    const res = '/api/v1'+path+'/ui-schemas/'+viewType.value
    // console.log('segement path res', path, res)
    return res 
  }

}

function processSchema(schema: any) {
  // Convert function strings to actual functions
  if (schema.columns) {
    schema.columns.forEach((col: any) => {
      if (col.cellClassFunction && typeof col.cellClassFunction === 'string') {
        try {
          // Clean up the function string
          let funcStr = col.cellClassFunction.trim()
          
          // Check if it's wrapped as a function declaration
          if (funcStr.startsWith('function')) {
            // Extract just the function body
            const match = funcStr.match(/function\s*\([^)]*\)\s*{\s*([\s\S]*)\s*}/)
            if (match) {
              funcStr = match[1]
            }
          }
          
          // Create the function
          col.cellClassFunction = new Function('value', 'item', funcStr)
        } catch (e) {
          console.error('Error parsing cellClassFunction:', e, col.cellClassFunction)
        }
      }
      
      if (col.formatter && typeof col.formatter === 'string') {
        try {
          let funcStr = col.formatter.trim()
          
          // Check if it's a function string
          if (funcStr.startsWith('function')) {
            const match = funcStr.match(/function\s*\([^)]*\)\s*{\s*([\s\S]*)\s*}/)
            if (match) {
              funcStr = match[1]
            }
            col.formatter = new Function('value', 'item', funcStr)
          }
          // Otherwise leave it as a string formatter name (like 'currency', 'number', etc.)
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
            let funcStr = field.compute.trim()
            if (funcStr.startsWith('function')) {
              const match = funcStr.match(/function\s*\([^)]*\)\s*{\s*([\s\S]*)\s*}/)
              if (match) {
                funcStr = match[1]
              }
            }
            field.compute = new Function('data', funcStr)
          } catch (e) {
            console.error('Error parsing compute function:', e)
          }
        }
        
        if (field.validate && typeof field.validate === 'string') {
          try {
            let funcStr = field.validate.trim()
            if (funcStr.startsWith('function')) {
              const match = funcStr.match(/function\s*\([^)]*\)\s*{\s*([\s\S]*)\s*}/)
              if (match) {
                funcStr = match[1]
              }
            }
            field.validate = new Function('value', 'data', funcStr)
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
    schema.value = 'form'
    router.push(route)
  }
}

async function handleAction(action: any, item?: any) {
  // console.log('Action:', action, item)
  
  if (action.id === 'create') {
    if (schema.value?.createRoute) {
      router.push(schema.value.createRoute)
    }
  } else if (action.route) {
    const route = item 
      ? action.route.replace('{id}', item.id)
      : action.route
    router.push(route)
  } else if (action.id === 'confirm' || action.id === 'back') {
    // Handle state transition actions
    // Map action.id to the actual action type expected by handleStateTransition
    const actionType = action.id === 'confirm' ? 'confirm_transaction' : 'back_transaction';
    await handleStateTransition(actionType, item)
  } else if (action.action === 'confirm_transaction' || action.action === 'back_transaction') {
    // Handle state transition actions (backward compatibility)
    await handleStateTransition(action.action, item)
  }
}

// Handle state transition actions
async function handleStateTransition(actionType: string, item?: any) {
  if (!item?.id) {
    console.error('No transaction ID provided for state transition')
    return
  }
  
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
    
    // Determine the next state based on current state and action type
    const nextState = getNextState(item.state, actionType)
    
    console.log('State transition:', { currentState: item.state, actionType, nextState })
    
    if (!nextState) {
      console.error('No valid next state found for current state:', item.state, 'action:', actionType)
      // Show error message to user
      alert(`Cannot perform ${actionType === 'confirm_transaction' ? 'Confirm' : 'Back'} action from current state: ${item.state}`)
      return
    }
    
    // Make API call to change transaction state
    const serviceUrl = SERVICE_MAPPING['sales'] || ''
    const url = `${serviceUrl}/sales/transactions/${item.id}/state/${nextState}`
    
    // console.log('Making API call to:', url)
    
    const response = await fetch(url, {
      method: 'POST',
      headers,
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to change transaction state: ${response.status} - ${errorText}`)
    }
    
    // Instead of navigating away, just reload the current schema and data
    await loadSchema()
  } catch (error) {
    console.error('Error changing transaction state:', error)
    // Show error message to user
    alert(`Error changing transaction state: ${error.message}`)
  }
}

// Determine next state based on current state and action type
function getNextState(currentState: string, actionType: string): string | null {
  // Define state transition mappings
  const forwardTransitions: Record<string, string> = {
    'draft': 'quote_pending_approval',
    'quote_pending_approval': 'quote_approved',
    'quote_approved': 'quote_sent',
    'quote_sent': 'quote_accepted',
    'quote_accepted': 'order_pending',
    'order_pending': 'order_confirmed',
    'order_confirmed': 'order_in_production',
    'order_in_production': 'order_ready_to_ship',
    'order_ready_to_ship': 'order_shipped',
    'order_partially_shipped': 'order_shipped',
    'order_shipped': 'order_delivered',
    'order_delivered': 'order_completed'
  }
  
  const backwardTransitions: Record<string, string> = {
    'quote_pending_approval': 'draft',
    'quote_approved': 'quote_pending_approval',
    'quote_sent': 'quote_approved',
    'quote_accepted': 'quote_sent',
    'order_pending': 'quote_accepted',
    'order_confirmed': 'order_pending',
    'order_in_production': 'order_confirmed',
    'order_ready_to_ship': 'order_in_production',
    'order_partially_shipped': 'order_ready_to_ship',
    'order_shipped': 'order_ready_to_ship',
    'order_delivered': 'order_shipped',
    'order_completed': 'order_delivered'
  }
  
  // console.log('getNextState called with:', { currentState, actionType })
  
  let nextState = null
  if (actionType === 'confirm_transaction') {
    nextState = forwardTransitions[currentState] || null
    console.log('Forward transition result:', nextState)
  } else if (actionType === 'back_transaction') {
    nextState = backwardTransitions[currentState] || null
    console.log('Backward transition result:', nextState)
  }
  
  return nextState
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
  // console.log('route changs')
  loadSchema()
})

// Also watch route name and params for more comprehensive updates
watch(() => route.name, () => {
  // console.log('route name changs')
  // loadSchema()
})

watch(() => route.params, () => {
  // console.log('route param changs')

  // loadSchema()
}, { deep: true })

// Initialize
onMounted(() => {
  // console.log('mounted..')
  loadSchema()
})
</script>
