<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <nav v-if="schema.breadcrumbs" class="flex" aria-label="Breadcrumb">
        <ol class="flex items-center space-x-4">
          <li v-for="(crumb, index) in schema.breadcrumbs" :key="index">
            <router-link v-if="crumb.route" :to="crumb.route" class="text-gray-400 hover:text-gray-500">
              {{ crumb.label }}
            </router-link>
            <span v-else class="text-gray-500">{{ crumb.label }}</span>
            <svg v-if="index < schema.breadcrumbs.length - 1" class="flex-shrink-0 h-5 w-5 text-gray-300 ml-4" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
            </svg>
          </li>
        </ol>
      </nav>
      <div class="mt-4">
        <h1 class="text-2xl font-semibold text-gray-900">
          {{ schema.title || (isEditMode ? 'Edit' : 'Create') }}
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
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Validation Errors -->
    <div v-if="validationErrors.length > 0" class="rounded-md bg-yellow-50 p-4 mb-6">
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
    </div>

    <!-- Form -->
    <form v-else @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Dynamic Sections -->
      <div v-for="section in schema.sections" :key="section.id" class="bg-white shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <h3 v-if="section.title" class="text-lg font-medium leading-6 text-gray-900 mb-4">
            {{ section.title }}
          </h3>
          <p v-if="section.description" class="text-sm text-gray-600 mb-4">
            {{ section.description }}
          </p>
          
          <div :class="section.gridClass || 'grid grid-cols-1 gap-6 sm:grid-cols-2'">
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
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
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
        
        <button
          type="submit"
          :disabled="saving || !isFormValid"
          class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          <svg v-if="saving" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ saving ? 'Saving...' : (schema.submitLabel || (isEditMode ? 'Update' : 'Create')) }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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
  if (props.endpoint) return props.endpoint
  if (props.schema.endpoint) {
    const baseUrl = props.serviceUrl ? `${props.serviceUrl}${props.schema.endpoint}` : props.schema.endpoint
    return isEditMode.value ? `${baseUrl}/${recordId.value}` : baseUrl
  }
  return ''
})

const isFormValid = computed(() => {
  // Basic validation - can be extended
  return validationErrors.value.length === 0
})

// Initialize form
async function initializeForm() {
  // Set default values from schema
  props.schema.sections?.forEach((section: any) => {
    section.fields?.forEach((field: any) => {
      if (field.defaultValue !== undefined) {
        formData.value[field.name] = field.defaultValue
      } else if (field.type === 'checkbox') {
        formData.value[field.name] = false
      } else if (field.type === 'number') {
        formData.value[field.name] = null
      } else {
        formData.value[field.name] = ''
      }
    })
  })

  // Load options for select fields
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
    const response = await fetch(apiUrl.value)
    if (!response.ok) throw new Error('Failed to load record')
    
    const data = await response.json()
    
    // Map data to form
    Object.keys(data).forEach(key => {
      if (formData.value.hasOwnProperty(key)) {
        formData.value[key] = data[key]
      }
    })
    
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
    const url = props.serviceUrl 
      ? `${props.serviceUrl}${field.optionsEndpoint}`
      : field.optionsEndpoint
      
    const response = await fetch(url)
    if (!response.ok) throw new Error('Failed to load options')
    
    const data = await response.json()
    
    // Handle different response formats
    let options = []
    if (Array.isArray(data)) {
      options = data
    } else if (data.items) {
      options = data.items
    } else if (data.data) {
      options = data.data
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
    
    const response = await fetch(apiUrl.value, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to save')
    }
    
    const result = await response.json()
    
    // Navigate to success route or emit event
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

function executeAction(action: any) {
  emit('action', action, formData.value)
}

// Utility functions
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