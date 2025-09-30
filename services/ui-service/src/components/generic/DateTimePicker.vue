<template>
  <div class="datetime-picker" ref="pickerContainer">
    <label :for="id" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="mt-1 relative rounded-md shadow-sm">
      <input
        :id="id"
        ref="inputRef"
        v-model="displayValue"
        :type="inputType"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :min="min"
        :max="max"
        class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
        :class="{ 'bg-gray-100': disabled }"
        @focus="handleFocus"
        @blur="handleBlur"
        @change="handleChange"
        @click="openCalendar"
      >
      
      <div class="absolute inset-y-0 right-0 flex items-center pr-3" v-if="!disabled">
        <button
          type="button"
          class="text-gray-400 hover:text-gray-500 focus:outline-none"
          @click="toggleCalendar"
          @keydown.enter="toggleCalendar"
          @keydown.space="toggleCalendar"
          tabindex="-1"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Calendar Popup -->
    <div 
      v-if="showCalendar" 
      class="absolute z-10 mt-1 bg-white shadow-lg rounded-md p-4 border border-gray-200"
      :class="calendarPosition"
    >
      <div class="calendar-header flex justify-between items-center mb-2">
        <button @click="prevMonth" class="p-1 rounded hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
        <div class="font-medium">
          {{ formatMonthYear(currentMonth, currentYear) }}
        </div>
        <button @click="nextMonth" class="p-1 rounded hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <div class="calendar-grid grid grid-cols-7 gap-1 mb-2">
        <div v-for="day in weekdays" :key="day" class="text-center text-xs font-medium text-gray-500 py-1">
          {{ day }}
        </div>
      </div>
      
      <div class="calendar-grid grid grid-cols-7 gap-1">
        <div
          v-for="day in calendarDays"
          :key="day.date.toString()"
          class="text-center text-sm p-1 rounded cursor-pointer hover:bg-gray-100"
          :class="{
            'text-gray-900': !day.isCurrentMonth,
            'text-gray-400': !day.isCurrentMonth,
            'bg-primary-100': day.isToday && !day.isSelected,
            'bg-primary-600 text-white': day.isSelected,
            'cursor-not-allowed opacity-50': day.isDisabled
          }"
          @click="selectDate(day)"
        >
          {{ !isNaN(day.date.getDate()) ? day.date.getDate() : '' }}
        </div>
      </div>
      
      <!-- Time Picker for datetime-local -->
      <div v-if="type === 'datetime-local'" class="time-picker mt-3 pt-3 border-t border-gray-200">
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-700">Time:</span>
          <input
            type="number"
            v-model="selectedHour"
            min="0"
            max="23"
            class="w-16 rounded border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            @change="updateDateTime"
          >
          <span>:</span>
          <input
            type="number"
            v-model="selectedMinute"
            min="0"
            max="59"
            class="w-16 rounded border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
            @change="updateDateTime"
          >
        </div>
      </div>
      
      <div class="calendar-footer mt-3 pt-3 border-t border-gray-200 flex justify-between">
        <button 
          @click="setToday" 
          class="text-sm text-primary-600 hover:text-primary-800"
        >
          Today
        </button>
        <button 
          @click="clearDate" 
          class="text-sm text-gray-600 hover:text-gray-800"
        >
          Clear
        </button>
      </div>
    </div>
    
    <p v-if="help" class="mt-1 text-sm text-gray-500">{{ help }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

// Props
const props = defineProps<{
  modelValue: string | null | undefined
  type: 'date' | 'datetime-local'
  label?: string
  required?: boolean
  disabled?: boolean
  placeholder?: string
  min?: string
  max?: string
  help?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
}>()

// Refs
const inputRef = ref<HTMLInputElement | null>(null)
const pickerContainer = ref<HTMLDivElement | null>(null)
const displayValue = ref<string>('')
const showCalendar = ref(false)
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const selectedHour = ref(0)
const selectedMinute = ref(0)
const calendarPosition = ref('')

// Constants
const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']

// Computed
const id = computed(() => `datetime-picker-${Math.random().toString(36).substr(2, 9)}`)
const inputType = computed(() => props.type)

// Calendar days
const calendarDays = computed(() => {
  // Check if currentMonth and currentYear are valid
  if (isNaN(currentMonth.value) || isNaN(currentYear.value)) {
    const now = new Date()
    currentMonth.value = now.getMonth()
    currentYear.value = now.getFullYear()
  }
  
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const today = new Date()
  let selected = props.modelValue ? new Date(props.modelValue) : null
  
  // Check if selected date is valid
  if (selected && isNaN(selected.getTime())) {
    selected = null
  }
  
  // Previous month days
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  const firstDayOfWeek = firstDay.getDay()
  
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(currentYear.value, currentMonth.value - 1, prevMonthLastDay - i)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: date.toDateString() === today.toDateString(),
      isSelected: selected ? date.toDateString() === selected.toDateString() : false,
      isDisabled: isDateDisabled(date)
    })
  }
  
  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    days.push({
      date,
      isCurrentMonth: true,
      isToday: date.toDateString() === today.toDateString(),
      isSelected: selected ? date.toDateString() === selected.toDateString() : false,
      isDisabled: isDateDisabled(date)
    })
  }
  
  // Next month days
  const remainingDays = 42 - days.length // 6 rows x 7 days
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(currentYear.value, currentMonth.value + 1, i)
    days.push({
      date,
      isCurrentMonth: false,
      isToday: date.toDateString() === today.toDateString(),
      isSelected: selected ? date.toDateString() === selected.toDateString() : false,
      isDisabled: isDateDisabled(date)
    })
  }
  
  return days
})

// Watch for modelValue changes
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    displayValue.value = newValue
    const date = new Date(newValue)
    currentMonth.value = date.getMonth()
    currentYear.value = date.getFullYear()
    selectedHour.value = date.getHours()
    selectedMinute.value = date.getMinutes()
  } else {
    displayValue.value = ''
    const now = new Date()
    currentMonth.value = now.getMonth()
    currentYear.value = now.getFullYear()
    selectedHour.value = 0
    selectedMinute.value = 0
  }
}, { immediate: true })

// Handle focus
function handleFocus() {
  // Nothing special for now
}

// Handle blur
function handleBlur() {
  // Close calendar when clicking outside
  setTimeout(() => {
    if (showCalendar.value && !isClickInsideCalendar()) {
      showCalendar.value = false
    }
  }, 100)
}

// Handle change
function handleChange() {
  emit('update:modelValue', displayValue.value || null)
}

// Open calendar immediately
function openCalendar() {
  if (props.disabled) return
  
  // Always ensure we have valid month/year
  if (!props.modelValue) {
    const now = new Date()
    currentMonth.value = now.getMonth()
    currentYear.value = now.getFullYear()
  } else {
    const date = new Date(props.modelValue)
    // Check if date is valid
    if (isNaN(date.getTime())) {
      // If invalid, default to current date
      const now = new Date()
      currentMonth.value = now.getMonth()
      currentYear.value = now.getFullYear()
    } else {
      currentMonth.value = date.getMonth()
      currentYear.value = date.getFullYear()
    }
  }
  
  showCalendar.value = true
  setPosition()
  
  // Initialize time values if datetime
  if (props.type === 'datetime-local' && props.modelValue) {
    const date = new Date(props.modelValue)
    if (!isNaN(date.getTime())) {
      selectedHour.value = date.getHours()
      selectedMinute.value = date.getMinutes()
    }
  }
}

// Toggle calendar
function toggleCalendar() {
  if (props.disabled) return
  showCalendar.value = !showCalendar.value
  if (showCalendar.value) {
    setPosition()
    // Initialize time values if datetime
    if (props.type === 'datetime-local' && props.modelValue) {
      const date = new Date(props.modelValue)
      selectedHour.value = date.getHours()
      selectedMinute.value = date.getMinutes()
    }
  }
}

// Set calendar position
function setPosition() {
  if (pickerContainer.value) {
    const rect = pickerContainer.value.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    
    // Check if calendar would go off right edge
    if (rect.left + 300 > viewportWidth) {
      calendarPosition.value = 'right-0'
    } else {
      calendarPosition.value = 'left-0'
    }
  }
}

// Check if click is inside calendar
function isClickInsideCalendar() {
  return document.activeElement?.closest('.datetime-picker') === pickerContainer.value
}

// Format month and year
function formatMonthYear(month: number, year: number): string {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]
  return `${months[month]} ${year}`
}

// Navigation
function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// Date selection
function selectDate(day: any) {
  if (day.isDisabled) return
  
  const date = new Date(day.date)
  
  if (props.type === 'date') {
    // Format as YYYY-MM-DD
    const formatted = formatDate(date)
    displayValue.value = formatted
    emit('update:modelValue', formatted)
    showCalendar.value = false
  } else {
    // For datetime, update date but keep time picker open
    date.setHours(selectedHour.value, selectedMinute.value)
    const formatted = formatDateTime(date)
    displayValue.value = formatted
    emit('update:modelValue', formatted)
  }
}

// Update datetime when time changes
function updateDateTime() {
  if (props.modelValue) {
    const date = new Date(props.modelValue)
    date.setHours(selectedHour.value, selectedMinute.value)
    const formatted = formatDateTime(date)
    displayValue.value = formatted
    emit('update:modelValue', formatted)
  }
}

// Set to today
function setToday() {
  const now = new Date()
  currentMonth.value = now.getMonth()
  currentYear.value = now.getFullYear()
  
  if (props.type === 'date') {
    const formatted = formatDate(now)
    displayValue.value = formatted
    emit('update:modelValue', formatted)
    showCalendar.value = false
  } else {
    selectedHour.value = now.getHours()
    selectedMinute.value = now.getMinutes()
    const formatted = formatDateTime(now)
    displayValue.value = formatted
    emit('update:modelValue', formatted)
  }
}

// Clear date
function clearDate() {
  displayValue.value = ''
  emit('update:modelValue', null)
  showCalendar.value = false
}

// Format date as YYYY-MM-DD
function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Format datetime as YYYY-MM-DDTHH:mm
function formatDateTime(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// Check if date is disabled
function isDateDisabled(date: Date): boolean {
  if (props.min) {
    const minDate = new Date(props.min)
    if (date < minDate) return true
  }
  if (props.max) {
    const maxDate = new Date(props.max)
    if (date > maxDate) return true
  }
  return false
}

// Click outside handler
function handleClickOutside(event: MouseEvent) {
  if (showCalendar.value && pickerContainer.value && !pickerContainer.value.contains(event.target as Node)) {
    showCalendar.value = false
  }
}

// Keydown handler
function handleKeydown(event: KeyboardEvent) {
  if (showCalendar.value && event.key === 'Escape') {
    showCalendar.value = false
    inputRef.value?.focus()
  }
}

// Initialize
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
  
  if (props.modelValue) {
    displayValue.value = props.modelValue
    const date = new Date(props.modelValue)
    currentMonth.value = date.getMonth()
    currentYear.value = date.getFullYear()
    selectedHour.value = date.getHours()
    selectedMinute.value = date.getMinutes()
  } else {
    const now = new Date()
    currentMonth.value = now.getMonth()
    currentYear.value = now.getFullYear()
  }
})

// Cleanup
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.datetime-picker {
  width: 100%;
}

.calendar-grid {
  grid-template-columns: repeat(7, minmax(0, 1fr));
}
</style>