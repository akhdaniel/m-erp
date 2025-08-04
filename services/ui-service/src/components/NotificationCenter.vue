<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <!-- Connection Status -->
    <div 
      v-if="showConnectionStatus"
      class="flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-300"
      :class="connectionStatusClass"
    >
      <div class="flex items-center space-x-2">
        <div 
          class="w-2 h-2 rounded-full"
          :class="store.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'"
        ></div>
        <span>{{ store.connected ? 'Live Updates Connected' : 'Reconnecting...' }}</span>
      </div>
    </div>

    <!-- Notifications -->
    <TransitionGroup
      name="notification"
      tag="div"
      class="space-y-2"
    >
      <div
        v-for="notification in visibleNotifications"
        :key="notification.id"
        class="notification-card"
        :class="[
          'max-w-sm p-4 rounded-lg border shadow-lg transition-all duration-300 cursor-pointer',
          notificationService.getNotificationColorClass(notification.type)
        ]"
        @click="removeNotification(notification.id)"
      >
        <div class="flex items-start space-x-3">
          <div class="text-lg">
            {{ notificationService.getNotificationIcon(notification.type) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <h4 class="text-sm font-semibold truncate">
                {{ notification.title }}
              </h4>
              <button
                @click.stop="removeNotification(notification.id)"
                class="ml-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            <p class="text-sm opacity-90">{{ notification.message }}</p>
            <div class="flex items-center justify-between mt-2 text-xs opacity-70">
              <span>{{ formatTime(notification.timestamp) }}</span>
              <span v-if="notification.priority >= 3" class="font-semibold">
                High Priority
              </span>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Show All / Clear All Button -->
    <div
      v-if="store.notifications.length > maxVisible"
      class="text-center"
    >
      <button
        @click="showAll = !showAll"
        class="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
      >
        {{ showAll ? 'Show Less' : `Show All (${store.notifications.length})` }}
      </button>
    </div>

    <!-- Clear All Button -->
    <div
      v-if="store.notifications.length > 0"
      class="text-center"
    >
      <button
        @click="clearAll"
        class="px-3 py-1 text-xs text-red-600 hover:text-red-700 underline"
      >
        Clear All
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { notificationService, notificationStore } from '@/services/notifications'

// Component state
const showAll = ref(false)
const maxVisible = ref(5)
const showConnectionStatus = ref(true)

// Reactive store reference
const store = notificationStore

// Computed properties
const visibleNotifications = computed(() => {
  if (showAll.value) {
    return store.notifications
  }
  return store.notifications.slice(0, maxVisible.value)
})

const connectionStatusClass = computed(() => {
  return store.connected
    ? 'bg-green-50 text-green-700 border border-green-200'
    : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
})

// Methods
const removeNotification = (id: string) => {
  notificationService.removeNotification(id)
}

const clearAll = () => {
  notificationService.clearAll()
  showAll.value = false
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) { // Less than 1 minute
    return 'Just now'
  } else if (diff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(diff / 60000)
    return `${minutes}m ago`
  } else if (diff < 86400000) { // Less than 1 day
    const hours = Math.floor(diff / 3600000)
    return `${hours}h ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Hide connection status after 10 seconds
onMounted(() => {
  setTimeout(() => {
    showConnectionStatus.value = false
  }, 10000)
})
</script>

<style scoped>
/* Notification animations */
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.notification-move {
  transition: transform 0.3s ease;
}

.notification-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
}

.notification-card:hover {
  transform: translateY(-2px);
  shadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
}
</style>