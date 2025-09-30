<template>
  <div class="max-w-4xl mx-auto p-6">
    <h1 class="text-2xl font-bold mb-6">DateTimePicker Test</h1>
    
    <div class="grid grid-cols-1 gap-6">
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-lg font-medium mb-4">Date Picker</h2>
        <DateTimePicker
          v-model="selectedDate"
          type="date"
          label="Select a date"
          placeholder="YYYY-MM-DD"
          help="Please select a date"
        />
        <p class="mt-2 text-sm text-gray-600">Selected date: {{ selectedDate }}</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-lg font-medium mb-4">DateTime Picker</h2>
        <DateTimePicker
          v-model="selectedDateTime"
          type="datetime-local"
          label="Select date and time"
          placeholder="YYYY-MM-DDTHH:mm"
          :min="minDateTime"
          :max="maxDateTime"
          help="Please select a date and time"
        />
        <p class="mt-2 text-sm text-gray-600">Selected datetime: {{ selectedDateTime }}</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-lg font-medium mb-4">Disabled Picker</h2>
        <DateTimePicker
          v-model="disabledDate"
          type="date"
          label="Disabled date picker"
          disabled
          placeholder="Cannot select"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DateTimePicker from '@/components/generic/DateTimePicker.vue'

const selectedDate = ref<string | null>(null)
const selectedDateTime = ref<string | null>(null)
const disabledDate = ref<string | null>('2025-01-01')

// Set min and max dates for datetime picker
const now = new Date()
const minDateTime = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7)
  .toISOString()
  .substring(0, 16)

const maxDateTime = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 7)
  .toISOString()
  .substring(0, 16)
</script>