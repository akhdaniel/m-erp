<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <div v-if="schema.breadcrumbs" class="flex" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-4 whitespace-nowrap">
          <li v-for="(crumb, index) in schema.breadcrumbs" :key="index" class="flex items-center">
            <router-link v-if="crumb.route" :to="crumb.route" class="text-gray-400 hover:text-gray-500">
              {{ crumb.label }}
            </router-link>
            <span v-else class="text-gray-500">{{ crumb.label }}</span>
            <svg v-if="index < schema.breadcrumbs.length - 1" class="flex-shrink-0 w-4 h-4 text-gray-300 ml-4" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
            </svg>
          </li>
        </ol>
      </div>
      <div class="mt-4">
        <h1 class="text-2xl font-semibold text-gray-900">
          {{ schema.title }}
        </h1>
        <p v-if="schema.description" class="mt-1 text-sm text-gray-600">
          {{ schema.description }}
        </p>
      </div>
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
    <div v-else-if="error" class="rounded-md bg-red-50 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error</h3>
          <div class="mt-2 text-sm ">
            <p class="text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Validation Errors -->
    <!-- <div v-if="validationErrors.length > 0" class="rounded-md bg-yellow-50 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">Please correct the following errors:</h3>
          <div class="mt-2 text-sm text-yellow-700">
            <ul class="list-disc list-inside">
              <li v-for="error in validationErrors" :key="error">{{ error }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div> -->

    <!-- View dwetial -->
    <!-- <form v-else @submit.prevent="handleSubmit" class="space-y-6"> -->
      <!-- Dynamic Sections -->
      <div v-for="section in schema.sections" :key="section.id" class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 v-if="section.title" class="text-lg font-medium leading-6 text-gray-900 mb-4">
            {{ section.title }}
          </h3>
          <p v-if="section.description" class="text-sm text-gray-600 mb-4">
            {{ section.description }}
          </p>
          
          <!-- Special handling for LineItemsManager component -->
          <LineItemsManager
            v-if="section.type === 'line_items' && section.component === 'LineItemsManager'"
            v-model="formData[section.key || 'items']"
            :title="section.config?.title"
            :entityType="section.config?.entityType"
            :taxRate="section.config?.taxRate"
            :productApiUrl="section.config?.productApiUrl"
            @totalsChanged="handleTotalsChanged"
          />
          
          <!-- Regular fields grid -->
          <div v-else :class="section.gridClass || 'grid grid-cols-1 gap-6 sm:grid-cols-2'">
            <div
              v-for="field in section.fields"
              :key="field.name"
              :class="field.colSpan ? `col-span-${field.colSpan}` : ''"
            >
              <!-- Text Input -->
              <div v-if="field.type === 'text' || field.type === 'email' || field.type === 'tel' || field.type === 'url'">
                <label :for="field.name" class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <input
                  :id="field.name"
                  v-model="formData[field.name]"
                  :type="field.type"
                  :required="field.required"
                  :disabled="field.disabled || (isEditMode && field.readOnlyOnEdit)"
                  :placeholder="field.placeholder"
                  :pattern="field.pattern"
                  :maxlength="field.maxLength"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  :class="{ 'bg-gray-100': field.disabled || (isEditMode && field.readOnlyOnEdit) }"
                >
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Number Input -->
              <div v-else-if="field.type === 'number'">
                <label :for="field.name" class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <div v-if="field.prefix || field.suffix" class="mt-1 relative rounded-md shadow-sm">
                  <div v-if="field.prefix" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">{{ field.prefix }}</span>
                  </div>
                  <input
                    :id="field.name"
                    v-model.number="formData[field.name]"
                    type="number"
                    :required="field.required"
                    :disabled="field.disabled"
                    :min="field.min"
                    :max="field.max"
                    :step="field.step"
                    :placeholder="field.placeholder"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    :class="{ 
                      'pl-7': field.prefix,
                      'pr-12': field.suffix,
                      'bg-gray-100': field.disabled
                    }"
                  >
                  <div v-if="field.suffix" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">{{ field.suffix }}</span>
                  </div>
                </div>
                <input
                  v-else
                  :id="field.name"
                  v-model.number="formData[field.name]"
                  type="number"
                  :required="field.required"
                  :disabled="field.disabled"
                  :min="field.min"
                  :max="field.max"
                  :step="field.step"
                  :placeholder="field.placeholder"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  :class="{ 'bg-gray-100': field.disabled }"
                >
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Autocomplete -->
              <div v-else-if="field.type === 'autocomplete'">
                <Autocomplete
                  v-model="formData[field.name]"
                  :field="field"
                  :modelValue="formData[field.name]"
                  :required="field.required"
                  :disabled="field.disabled"
                  :service-url="serviceUrl"
                />
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Select -->
              <div v-else-if="field.type === 'select'">
                <label :for="field.name" class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <select
                  :id="field.name"
                  v-model="formData[field.name]"
                  :required="field.required"
                  :disabled="field.disabled"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  :class="{ 'bg-gray-100': field.disabled }"
                >
                  <option v-if="!field.required" value="">{{ field.placeholder || 'Select...' }}</option>
                  <option
                    v-for="option in getFieldOptions(field)"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Textarea -->
              <div v-else-if="field.type === 'textarea'">
                <label :for="field.name" class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <textarea
                  :id="field.name"
                  v-model="formData[field.name]"
                  :required="field.required"
                  :disabled="field.disabled"
                  :rows="field.rows || 3"
                  :placeholder="field.placeholder"
                  :maxlength="field.maxLength"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm placeholder-gray-300"
                  :class="{ 'bg-gray-100': field.disabled }"
                ></textarea>
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Checkbox -->
              <div v-else-if="field.type === 'checkbox'">
                <div class="flex items-center">
                  <input
                    :id="field.name"
                    v-model="formData[field.name]"
                    type="checkbox"
                    :disabled="field.disabled"
                    class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  >
                  <label :for="field.name" class="ml-2 block text-sm text-gray-900">
                    {{ field.label }}
                  </label>
                </div>
                <p v-if="field.help" class="mt-1 text-sm text-gray-500 ml-6">{{ field.help }}</p>
              </div>

              <!-- Radio Group -->
              <div v-else-if="field.type === 'radio'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <div class="space-y-2">
                  <div v-for="option in getFieldOptions(field)" :key="option.value" class="flex items-center">
                    <input
                      :id="`${field.name}-${option.value}`"
                      v-model="formData[field.name]"
                      :value="option.value"
                      type="radio"
                      :required="field.required"
                      :disabled="field.disabled"
                      class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    >
                    <label :for="`${field.name}-${option.value}`" class="ml-2 block text-sm text-gray-900">
                      {{ option.label }}
                    </label>
                  </div>
                </div>
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Date/DateTime -->
              <div v-else-if="field.type === 'date' || field.type === 'datetime-local'">
                <label :for="field.name" class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                  <span v-if="field.required" class="text-red-500">*</span>
                </label>
                <input
                  :id="field.name"
                  v-model="formData[field.name]"
                  :type="field.type"
                  :required="field.required"
                  :disabled="field.disabled"
                  :min="field.min"
                  :max="field.max"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  :class="{ 'bg-gray-100': field.disabled }"
                >
                <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
              </div>

              <!-- Custom Component -->
              <component
                v-else-if="field.component"
                :is="field.component"
                v-model="formData[field.name]"
                :field="field"
                :disabled="field.disabled"
                :required="field.required"
                v-bind="field.props || {}"
              />

              <!-- Computed/Display Field -->
              <div v-else-if="field.type === 'display'">
                <label class="block text-sm font-medium text-gray-700">
                  {{ field.label }}
                </label>
                <div class="mt-1 text-sm text-gray-900 py-2">
                  {{ computeFieldValue(field) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end space-x-3">
        <button
          type="button"
          @click="handleCancel"
          class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          {{ schema.cancelLabel || 'Cancel' }}
        </button>
        
        <!-- Custom Actions -->
        <button
          v-for="action in schema.actions"
          :key="action.id"
          type="button"
          @click="executeAction(action)"
          :disabled="action.disabled || saving"
          :class="getActionClasses(action)"
          class="inline-flex justify-center py-2 px-4 text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2"
        >
          {{ action.label }}
        </button>
        
        <!-- <button
          type="submit"
          :disabled="saving || !isFormValid"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          <svg v-if="saving" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ saving ? 'Saving...' : (schema.submitLabel || (isEditMode ? 'Update' : 'Create')) }}
        </button> -->
      </div>
    <!-- </form> -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LineItemsManager from '@/components/LineItemsManager.vue'
import Autocomplete from '@/components/generic/Autocomplete.vue'

// Props
const props = defineProps<{
  schema: any  // Form schema from service
  id?: string | number  // Record ID for edit mode
  endpoint?: string  // Optional direct endpoint
  serviceUrl?: string  // Service base URL
}>()

const emit = defineEmits<{
  'submit': [data: any]
  'cancel': []
  'action': [action: any, data: any]
}>()

const route = useRoute()
const router = useRouter()

// State
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const validationErrors = ref<string[]>([])
const formData = ref<Record<string, any>>({})
const originalData = ref<Record<string, any>>({})
const fieldOptions = ref<Record<string, any[]>>({})

// Computed
const recordId = computed(() => props.id || route.params.id)
const isEditMode = computed(() => !!recordId.value && recordId.value !== 'new')

const apiUrl = computed(() => {
  if (props.endpoint) {
    return props.endpoint
  }
  if (props.schema.endpoint) {
    // If we have a serviceUrl, use it as the base
    if (props.serviceUrl) {
      // Check if the endpoint already starts with the serviceUrl to avoid duplication
      if (props.schema.endpoint.startsWith(props.serviceUrl)) {
        // Endpoint already includes the service URL, use it as-is
        return isEditMode.value ? `${props.schema.endpoint}/${recordId.value}` : props.schema.endpoint
      }
      
      // Combine serviceUrl and endpoint, being careful about slashes
      const base = props.serviceUrl.endsWith('/') ? props.serviceUrl.slice(0, -1) : props.serviceUrl
      let endpoint = props.schema.endpoint
      if (endpoint.startsWith('/')) {
        // If endpoint starts with /, remove it to avoid double slashes
        endpoint = endpoint.substring(1)
      }
      const fullEndpoint = endpoint ? `${base}/${endpoint}` : base
      return isEditMode.value ? `${fullEndpoint}/${recordId.value}` : fullEndpoint
    }
    // For API endpoints, use relative URLs that go through the Vite proxy
    // The proxy is configured to forward /api requests to http://kong:8000
    return isEditMode.value ? `${props.schema.endpoint}/${recordId.value}` : props.schema.endpoint
  }
  return ''
})

const isFormValid = computed(() => {
  // Basic validation - can be extended
  return validationErrors.value.length === 0
})

// Initialize form
async function initializeForm() {
  let selectionFieldExist = false
  // Set default values from schema
  props.schema.sections?.forEach((section: any) => {
    section.fields?.forEach((field: any) => {
      if (field.defaultValue !== undefined) {
        formData.value[field.name] = field.defaultValue
      } else if (field.type === 'checkbox') {
        formData.value[field.name] = false
      } else if (field.type === 'number') {
        formData.value[field.name] = null
      }
      else if (field.type === 'select') {
        selectionFieldExist=true
      } else {
        formData.value[field.name] = ''
      }
    })
  })

  // Load options for select fields
  if (selectionFieldExist)
    await loadFieldOptions()

  // Load existing data if editing
  if (isEditMode.value) {
    await loadRecord()
  }
}

// Load record for editing
async function loadRecord() {
  if (!apiUrl.value) {
    error.value = 'No endpoint configured'
    return
  }

  loading.value = true
  error.value = ''
  
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
    
    const response = await fetch(apiUrl.value, { headers })
    if (!response.ok) throw new Error('Failed to load record')
    
    const data = await response.json()
    
    // Map data to form
    Object.keys(data).forEach(key => {
      if (formData.value.hasOwnProperty(key)) {
        // Check if there's a field definition for this key
        let fieldDef = null
        props.schema.sections?.forEach((section: any) => {
          const field = section.fields?.find((f: any) => f.name === key)
          if (field) fieldDef = field
        })
        
        // Handle different field types
        if (fieldDef) {
          if (fieldDef.type === 'date' && data[key]) {
            // Convert ISO date to YYYY-MM-DD format for date input
            formData.value[key] = data[key].split('T')[0]
          } else if (fieldDef.type === 'datetime-local' && data[key]) {
            // Convert ISO datetime to datetime-local format
            formData.value[key] = data[key].substring(0, 16) // YYYY-MM-DDTHH:mm
          } else if (fieldDef.type === 'component' && fieldDef.component === 'LineItemsManager') {
            // Handle line items - check both 'line_items' and 'items' fields
            formData.value[key] = data.line_items || data.items || []
          } else {
            formData.value[key] = data[key]
          }
        } else {
          formData.value[key] = data[key]
        }
      }
    })
    
    // Also check for line_items if the form has that field but API returns items
    if (formData.value.hasOwnProperty('line_items') && !data.line_items && data.items) {
      formData.value.line_items = data.items
    }
    
    // Map API field names to form field names
    if (formData.value.hasOwnProperty('quote_date') && data.valid_from) {
      formData.value.quote_date = data.valid_from.split('T')[0]
    }
    
    originalData.value = { ...formData.value }
  } catch (err: any) {
    error.value = err.message || 'Failed to load record'
    console.error('Error loading record:', err)
  } finally {
    loading.value = false
  }
}

// Load options for select fields
async function loadFieldOptions() {
  const promises = []
  
  props.schema.sections?.forEach((section: any) => {
    section.fields?.forEach((field: any) => {
      if (field.optionsEndpoint) {
        promises.push(loadOptions(field))
      } else if (field.options) {
        fieldOptions.value[field.name] = field.options
      }
    })
  })
  
  await Promise.all(promises)
}

async function loadOptions(field: any) {
  try {

    console.log('loadOptions=====', field.optionsEndpoint)
    // Check if the optionsEndpoint is already a full URL
    let url = field.optionsEndpoint
    if (!field.optionsEndpoint.startsWith('http://') && !field.optionsEndpoint.startsWith('https://')) {
      // For API endpoints, use relative URLs that go through the Vite proxy
      url = field.optionsEndpoint
    }
    
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
    
    const response = await fetch(url, { headers })
    if (!response.ok) throw new Error('Failed to load options')
    
    const data = await response.json()
    
    // Handle different response formats
    let options = []
    if (field.optionsDataPath) {
      // Use specified data path if provided
      options = getNestedValue(data, field.optionsDataPath) || []
    } else if (Array.isArray(data)) {
      options = data
    } else if (data.items) {
      options = data.items
    } else if (data.data) {
      options = data.data
    } else if (data.partners) {
      // Handle partners response format
      options = data.partners
    }
    
    // Map to label/value format
    fieldOptions.value[field.name] = options.map((item: any) => ({
      label: item[field.optionLabelField || 'label'] || item.name || item.title || item.id,
      value: item[field.optionValueField || 'value'] || item.id
    }))
  } catch (err) {
    console.error(`Error loading options for ${field.name}:`, err)
    fieldOptions.value[field.name] = []
  }
}

// Form submission
async function handleSubmit() {
  if (!validate()) return
  
  if (props.schema.customSubmit) {
    emit('submit', formData.value)
    return
  }
  
  if (!apiUrl.value) {
    error.value = 'No endpoint configured'
    return
  }
  
  saving.value = true
  error.value = ''
  
  try {
    const method = isEditMode.value ? 'PUT' : 'POST'
    
    // Prepare submission data - handle line_items special case and clean up empty values
    const submitData = { ...formData.value }
    
    // Clean up form data - convert empty strings to null for optional fields
    Object.keys(submitData).forEach(key => {
      // Handle parent_category_id - convert empty string to null
      if (key === 'parent_category_id' && submitData[key] === '') {
        submitData[key] = null
      }
      // Handle color field - convert empty string to null
      else if (key === 'color' && submitData[key] === '') {
        submitData[key] = null
      }
      // Handle other fields that should be null instead of empty string
      else if (submitData[key] === '') {
        // Check if this field is not required - if so, we can set it to null
        let isRequired = false
        props.schema.sections?.forEach((section: any) => {
          const field = section.fields?.find((f: any) => f.name === key)
          if (field && field.required) {
            isRequired = true
          }
        })
        // Only set to null if not required
        if (!isRequired) {
          submitData[key] = null
        }
      }
    })
    
    // If we have line_items, we may need to rename it to items for the API
    if (submitData.line_items && !submitData.items) {
      submitData.items = submitData.line_items
      delete submitData.line_items
    }
    
    console.log('handleSubmit-----', apiUrl.value)
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
    
    const response = await fetch(apiUrl.value, {
      method,
      headers,
      body: JSON.stringify(submitData)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      let errorMessage = 'Failed to save'
      
      // Handle detailed validation errors
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          // Pydantic validation errors
          const errorMessages = errorData.detail.map((err: any) => {
            // Extract field name from location path
            const fieldPath = err.loc?.slice(1).join('.') || 'field'
            return `${fieldPath}: ${err.msg}`
          })
          errorMessage = errorMessages.join(', ')
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        }
      }
      
      throw new Error(errorMessage)
    }
    
    const result = await response.json()
    
    // Navigate to success route or emit event
    console.log('submitted go back to', props.schema.successRoute)
    if (props.schema.successRoute) {
      router.push(props.schema.successRoute)
    } else {
      emit('submit', result)
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to save'
    console.error('Error saving:', err)
  } finally {
    saving.value = false
  }
}

// Validation
function validate(): boolean {
  validationErrors.value = []
  
  props.schema.sections?.forEach((section: any) => {
    section.fields?.forEach((field: any) => {
      // Required validation
      if (field.required && !formData.value[field.name]) {
        validationErrors.value.push(`${field.label} is required`)
      }
      
      // Custom validation
      if (field.validate) {
        const error = field.validate(formData.value[field.name], formData.value)
        if (error) {
          validationErrors.value.push(error)
        }
      }
    })
  })
  
  return validationErrors.value.length === 0
}

// Actions
function handleCancel() {
  if (props.schema.cancelRoute) {
    router.push(props.schema.cancelRoute)
  } else {
    emit('cancel')
  }
}

// Handle line items totals change
function handleTotalsChanged(totals: any) {
  // Update form data with calculated totals
  formData.value.subtotal = totals.subtotal
  formData.value.discount = totals.discount
  formData.value.tax = totals.tax
  formData.value.total = totals.total
}

function executeAction(action: any) {
  emit('action', action, formData.value)
}

// Utility functions
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((curr, prop) => curr?.[prop], obj)
}

function getFieldOptions(field: any): any[] {
  return fieldOptions.value[field.name] || field.options || []
}

function computeFieldValue(field: any): string {
  if (field.compute) {
    return field.compute(formData.value)
  }
  return formData.value[field.name] || ''
}

function getActionClasses(action: any): string {
  const baseClasses = action.variant === 'primary'
    ? 'border-transparent text-white bg-primary-600 hover:bg-primary-700'
    : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
  return `${baseClasses} ${action.class || ''}`
}

// Watch for schema changes
watch(() => props.schema, () => {
  initializeForm()
}, { deep: true })

// Initialize
onMounted(() => {
  initializeForm()
})

// Expose methods for parent components
defineExpose({
  validate,
  submit: handleSubmit,
  reset: initializeForm
})
</script>
