<template>
  <div class="autocomplete-wrapper">
    <label :for="field.name" class="block text-sm font-medium text-gray-700">
      {{ field.label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="mt-1 relative">
      <input
        :id="field.name"
        ref="inputRef"
        v-model="searchTerm"
        :placeholder="field.placeholder || 'Start typing to search...'"
        :disabled="disabled"
        :required="required"
        type="text"
        class="input"
        :class="{ 'bg-gray-100': disabled }"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="handleInput"
        @keydown.down="handleArrowDown"
        @keydown.up="handleArrowUp"
        @keydown.enter="handleEnter"
        @keydown.escape="handleEscape"
      >
      <div 
        v-if="isLoading" 
        class="absolute inset-y-0 right-0 flex items-center pr-3"
      >
        <svg class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    </div>
    
    <!-- Dropdown -->
    <div 
      v-if="showDropdown && filteredOptions.length > 0" 
      class="absolute z-10 mt-1 w-full rounded-md bg-white shadow-lg"
      :style="{ 
        minWidth: dropdownMinWidth + 'px',
        maxHeight: '200px',
        overflowY: 'auto'
      }"
    >
      <ul 
        ref="dropdownRef"
        class="max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm"
        role="listbox"
      >
        <li
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          class="relative py-2 pl-3 pr-9 cursor-default select-none"
          :class="[
            index === highlightedIndex ? 'text-white bg-primary-600' : 'text-gray-900',
            'relative cursor-default select-none py-2 pl-3 pr-9'
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center">
            <span class="block truncate" :class="{ 'font-semibold': index === highlightedIndex }">
              {{ option.label }}
            </span>
          </div>
          <span
            v-if="selectedValue === option.value"
            class="absolute inset-y-0 right-0 flex items-center pr-4"
            :class="index === highlightedIndex ? 'text-white' : 'text-primary-600'"
          >
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </span>
        </li>
      </ul>
    </div>
    
    <!-- Hidden input to store the actual value -->
    <input 
      type="hidden" 
      :name="field.name" 
      :value="selectedValue"
    >
    
    <p v-if="field.help" class="mt-1 text-sm text-gray-500">{{ field.help }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'

// Props
const props = defineProps<{
  modelValue: any
  field: any
  disabled?: boolean
  required?: boolean
  serviceUrl?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

// Refs
const inputRef = ref<HTMLInputElement | null>(null)
const dropdownRef = ref<HTMLDivElement | null>(null)
const searchTerm = ref('')
const selectedValue = ref<any>(null)
const selectedLabel = ref<string>('')
const options = ref<Array<{ label: string; value: any }>>([])
const isLoading = ref(false)
const showDropdown = ref(false)
const highlightedIndex = ref(-1)
const dropdownMinWidth = ref(0)

// Computed
const filteredOptions = computed(() => {
  if (!searchTerm.value) return options.value
  
  return options.value.filter(option => 
    option.label.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

// Methods
async function loadOptions() {
  console.log('autocomplete loadOptions', props.field.optionsEndpoint)
  if (!props.field.optionsEndpoint) return
  
  isLoading.value = true
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
    
    // Construct the full URL using serviceUrl if provided
    let url = props.field.optionsEndpoint
    if (props.serviceUrl && !url.startsWith('http')) {
      // Remove trailing slash from serviceUrl if present
      const baseUrl = props.serviceUrl.endsWith('/') ? props.serviceUrl.slice(0, -1) : props.serviceUrl
      // Add leading slash to optionsEndpoint if not present
      const endpoint = url.startsWith('/') ? url : `/${url}`
      url = `${baseUrl}${endpoint}`
    }
    
    const response = await fetch(url, { headers })
    if (!response.ok) throw new Error('Failed to load options')
    
    const data = await response.json()
    
    // Handle different response formats
    let resultOptions = []
    if (props.field.optionsDataPath) {
      // Use specified data path if provided
      resultOptions = getNestedValue(data, props.field.optionsDataPath) || []
    } else if (Array.isArray(data)) {
      resultOptions = data
    } else if (data.items) {
      resultOptions = data.items
    } else if (data.data) {
      resultOptions = data.data
    } else if (data.partners) {
      // Handle partners response format
      resultOptions = data.partners
    }
    
    // Map to label/value format
    options.value = resultOptions.map((item: any) => ({
      label: item[props.field.optionLabelField || 'label'] || item.name || item.title || item.id,
      value: item[props.field.optionValueField || 'value'] || item.id
    }))
  } catch (err) {
    console.error(`Error loading options for ${props.field.name}:`, err)
    options.value = []
  } finally {
    isLoading.value = false
  }
}

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((curr, prop) => curr?.[prop], obj)
}

function handleFocus() {
  if (props.disabled) return
  showDropdown.value = true
  highlightedIndex.value = -1
  dropdownMinWidth.value = inputRef.value?.offsetWidth || 0
  if (options.value.length === 0) {
    loadOptions()
  }
}

function handleBlur(e: FocusEvent) {
  // Delay hiding dropdown to allow for clicks on options
  setTimeout(() => {
    showDropdown.value = false
    highlightedIndex.value = -1
    
    // If no option is selected, clear the search term
    if (!selectedValue.value) {
      searchTerm.value = ''
    } else {
      // Set the search term to the selected label
      searchTerm.value = selectedLabel.value
    }
  }, 200)
}

function handleInput() {
  showDropdown.value = true
  highlightedIndex.value = -1
  selectedValue.value = null
  selectedLabel.value = ''
  emit('update:modelValue', null)
}

function handleArrowDown(e: KeyboardEvent) {
  e.preventDefault()
  if (!showDropdown.value) {
    showDropdown.value = true
    return
  }
  
  if (highlightedIndex.value < filteredOptions.value.length - 1) {
    highlightedIndex.value++
    scrollToHighlighted()
  }
}

function handleArrowUp(e: KeyboardEvent) {
  e.preventDefault()
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
    scrollToHighlighted()
  }
}

function handleEnter(e: KeyboardEvent) {
  e.preventDefault()
  if (showDropdown.value && highlightedIndex.value >= 0) {
    selectOption(filteredOptions.value[highlightedIndex.value])
  } else if (filteredOptions.value.length > 0) {
    // If no option is highlighted, select the first one
    selectOption(filteredOptions.value[0])
  }
}

function handleEscape() {
  showDropdown.value = false
  highlightedIndex.value = -1
}

function scrollToHighlighted() {
  nextTick(() => {
    if (dropdownRef.value && highlightedIndex.value >= 0) {
      const dropdownItems = dropdownRef.value.querySelectorAll('li')
      if (dropdownItems[highlightedIndex.value]) {
        dropdownItems[highlightedIndex.value].scrollIntoView({ block: 'nearest' })
      }
    }
  })
}

function selectOption(option: { label: string; value: any }) {
  selectedValue.value = option.value
  selectedLabel.value = option.label
  searchTerm.value = option.label
  showDropdown.value = false
  highlightedIndex.value = -1
  emit('update:modelValue', option.value)
  
  // Focus back to input
  setTimeout(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  }, 0)
}

// Watch for modelValue changes
watch(() => props.modelValue, (newValue) => {
  selectedValue.value = newValue
  if (newValue && options.value.length > 0) {
    const selectedOption = options.value.find(option => option.value === newValue)
    if (selectedOption) {
      selectedLabel.value = selectedOption.label
      searchTerm.value = selectedOption.label
    }
  } else if (newValue) {
    // Check if we have a display name stored in the parent form data
    // This is a special case where the parent form stores the display name
    // in a field with the pattern _{field_name}_display
    const displayNameField = `_${props.field.name}_display`
    const parentFormData = (props.field as any).parentFormData
    if (parentFormData && parentFormData[displayNameField]) {
      selectedLabel.value = parentFormData[displayNameField]
      searchTerm.value = parentFormData[displayNameField]
    }
  } else if (!newValue) {
    selectedLabel.value = ''
    searchTerm.value = ''
  }
}, { immediate: true })

// Initialize
onMounted(() => {
  dropdownMinWidth.value = inputRef.value?.offsetWidth || 0
})
</script>

<style scoped>
.autocomplete-wrapper {
  position: relative;
}
</style>