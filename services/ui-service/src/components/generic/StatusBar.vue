<template>
  <div class="status-bar">
    <div class="status-bar-container">
      <div 
        v-for="(state, index) in workflowStates" 
        :key="state.value"
        :class="getStateClass(state)"
        @click="onStateClick(state)"
      >
        {{ state.label }}
        <div v-if="index < workflowStates.length - 1" class="arrow">›</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Define the props
const props = defineProps<{
  currentState: string
  stateTransitions?: {
    forwardTransitions?: Record<string, string>
    backwardTransitions?: Record<string, string>
  }
  onStateChange?: (state: string) => void
}>()

// Default state transitions based on the sales transaction workflow
const defaultForwardTransitions = {
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

const defaultBackwardTransitions = {
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

// Merge provided transitions with defaults
const forwardTransitions = {
  ...defaultForwardTransitions,
  ...(props.stateTransitions?.forwardTransitions || {})
}

const backwardTransitions = {
  ...defaultBackwardTransitions,
  ...(props.stateTransitions?.backwardTransitions || {})
}

// Define all states with labels
const stateLabels: Record<string, string> = {
  'draft': 'Draft',
  'quote_pending_approval': 'Pending Approval',
  'quote_approved': 'Approved',
  'quote_sent': 'Sent',
  'quote_accepted': 'Accepted',
  'order_pending': 'Order Pending',
  'order_confirmed': 'Confirmed',
  'order_in_production': 'In Production',
  'order_ready_to_ship': 'Ready to Ship',
  'order_partially_shipped': 'Partially Shipped',
  'order_shipped': 'Shipped',
  'order_delivered': 'Delivered',
  'order_completed': 'Completed'
}

// Build workflow states in order starting from draft
const workflowStates = computed(() => {
  const states: Array<{value: string, label: string}> = []
  let currentState = 'draft'
  
  // Add the first state
  states.push({ value: currentState, label: stateLabels[currentState] || currentState })
  
  // Follow the forward transitions to build the workflow
  while (forwardTransitions[currentState]) {
    currentState = forwardTransitions[currentState]
    states.push({ value: currentState, label: stateLabels[currentState] || currentState })
    
    // Prevent infinite loops
    if (states.length > 20) break
  }
  
  return states
})

// Get CSS class for a state
function getStateClass(state: {value: string, label: string}) {
  const classes = ['status-item']
  
  if (state.value === props.currentState) {
    classes.push('current')
  } else if (isStateReachable(state.value)) {
    classes.push('reachable')
  } else {
    classes.push('normal')
  }
  
  if (!isStateClickable(state)) {
    classes.push('disabled')
  }
  
  return classes.join(' ')
}

// Check if a state is reachable from the current state
function isStateReachable(stateValue: string): boolean {
  // Check if it's a forward state
  let currentState = props.currentState
  while (forwardTransitions[currentState]) {
    currentState = forwardTransitions[currentState]
    if (currentState === stateValue) return true
    // Prevent infinite loops
    if (Object.keys(forwardTransitions).indexOf(currentState) < 0) break
  }
  
  // Check if it's a backward state
  currentState = props.currentState
  while (backwardTransitions[currentState]) {
    currentState = backwardTransitions[currentState]
    if (currentState === stateValue) return true
    // Prevent infinite loops
    if (Object.keys(backwardTransitions).indexOf(currentState) < 0) break
  }
  
  return false
}

// Check if a state is clickable
function isStateClickable(state: {value: string, label: string}): boolean {
  // Current state is not clickable
  if (state.value === props.currentState) {
    return false
  }
  
  // Check if it's directly adjacent (next or previous)
  if (forwardTransitions[props.currentState] === state.value) {
    return true
  }
  
  if (backwardTransitions[props.currentState] === state.value) {
    return true
  }
  
  return false
}

// Handle state click
function onStateClick(state: {value: string, label: string}) {
  if (isStateClickable(state) && props.onStateChange) {
    props.onStateChange(state.value)
  }
}
</script>

<style scoped>
.status-bar {
  margin: 1rem 0;
  padding: 0.5rem 0;
}

.status-bar-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0;
}

.status-item {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid transparent;
}

.status-item:first-child {
  border-top-left-radius: 0.375rem;
  border-bottom-left-radius: 0.375rem;
}

.status-item:last-child {
  border-top-right-radius: 0.375rem;
  border-bottom-right-radius: 0.375rem;
}

.status-item.current {
  background-color: #3b82f6; /* blue-500 */
  color: white;
  border-color: #3b82f6;
}

.status-item.reachable {
  background-color: #dbeafe; /* blue-100 */
  color: #1d4ed8; /* blue-700 */
  border-color: #93c5fd; /* blue-300 */
}

.status-item.normal {
  background-color: #f3f4f6; /* gray-100 */
  color: #6b7280; /* gray-500 */
  border-color: #d1d5db; /* gray-300 */
}

.status-item:hover:not(.disabled):not(.current) {
  opacity: 0.8;
}

.status-item.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.status-item.current:hover {
  background-color: #2563eb; /* blue-600 */
}

.arrow {
  margin-left: 0.5rem;
  font-size: 0.875rem;
  opacity: 0.7;
}
</style>