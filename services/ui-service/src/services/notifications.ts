/**
 * Real-time notification service using Server-Sent Events and Redis pub/sub
 */
import { ref, reactive } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'info' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  priority: number
  expires_at?: string
}

export interface NotificationStore {
  notifications: Notification[]
  connected: boolean
  eventSource: EventSource | null
}

// Global notification store
export const notificationStore = reactive<NotificationStore>({
  notifications: [],
  connected: false,
  eventSource: null
})

class NotificationService {
  private baseUrl = 'http://localhost:8007'  // Notification service URL
  private eventSource: EventSource | null = null
  private maxNotifications = 50
  
  /**
   * Connect to real-time notification stream
   */
  connect(userId?: number): void {
    if (this.eventSource) {
      this.disconnect()
    }
    
    // Construct URL with user ID if provided
    const url = userId 
      ? `${this.baseUrl}/notifications/stream?user_id=${userId}`
      : `${this.baseUrl}/notifications/stream`
    
    console.log('🔌 Connecting to notification stream:', url)
    
    this.eventSource = new EventSource(url)
    notificationStore.eventSource = this.eventSource
    
    this.eventSource.onopen = () => {
      console.log('✅ Notification stream connected')
      notificationStore.connected = true
    }
    
    this.eventSource.onmessage = (event) => {
      try {
        const notification: Notification = JSON.parse(event.data)
        this.addNotification(notification)
      } catch (error) {
        console.error('Failed to parse notification:', error)
      }
    }
    
    this.eventSource.onerror = (error) => {
      console.error('❌ Notification stream error:', error)
      notificationStore.connected = false
      
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        if (this.eventSource?.readyState === EventSource.CLOSED) {
          console.log('🔄 Attempting to reconnect notification stream...')
          this.connect(userId)
        }
      }, 5000)
    }
  }
  
  /**
   * Disconnect from notification stream
   */
  disconnect(): void {
    if (this.eventSource) {
      console.log('🔌 Disconnecting from notification stream')
      this.eventSource.close()
      this.eventSource = null
      notificationStore.eventSource = null
      notificationStore.connected = false
    }
  }
  
  /**
   * Add a notification to the store
   */
  addNotification(notification: Notification): void {
    console.log('📢 New notification:', notification.title)
    
    // Add to the beginning of the array
    notificationStore.notifications.unshift(notification)
    
    // Limit the number of notifications
    if (notificationStore.notifications.length > this.maxNotifications) {
      notificationStore.notifications = notificationStore.notifications.slice(0, this.maxNotifications)
    }
    
    // Show browser notification if permission granted
    this.showBrowserNotification(notification)
    
    // Auto-remove notification if it has an expiry
    if (notification.expires_at) {
      const expiryTime = new Date(notification.expires_at).getTime()
      const currentTime = new Date().getTime()
      const timeToExpiry = expiryTime - currentTime
      
      if (timeToExpiry > 0) {
        setTimeout(() => {
          this.removeNotification(notification.id)
        }, timeToExpiry)
      }
    } else {
      // Auto-remove after 30 seconds for high priority, 10 seconds for others
      const autoRemoveTime = notification.priority >= 3 ? 30000 : 10000
      setTimeout(() => {
        this.removeNotification(notification.id)
      }, autoRemoveTime)
    }
  }
  
  /**
   * Remove a notification from the store
   */
  removeNotification(notificationId: string): void {
    const index = notificationStore.notifications.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      notificationStore.notifications.splice(index, 1)
    }
  }
  
  /**
   * Clear all notifications
   */
  clearAll(): void {
    notificationStore.notifications = []
  }
  
  /**
   * Show browser notification if permission granted
   */
  private showBrowserNotification(notification: Notification): void {
    if ('Notification' in window && Notification.permission === 'granted') {
      const browserNotification = new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: notification.id,
        requireInteraction: notification.priority >= 3
      })
      
      // Auto-close after 5 seconds unless high priority
      if (notification.priority < 3) {
        setTimeout(() => {
          browserNotification.close()
        }, 5000)
      }
    }
  }
  
  /**
   * Request browser notification permission
   */
  async requestNotificationPermission(): Promise<NotificationPermission> {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      console.log('🔔 Notification permission:', permission)
      return permission
    }
    return 'denied'
  }
  
  /**
   * Add a local notification (for testing or fallback)
   */
  addLocalNotification(
    type: Notification['type'],
    title: string,
    message: string,
    priority: number = 1
  ): void {
    const notification: Notification = {
      id: `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      title,
      message,
      timestamp: new Date().toISOString(),
      priority
    }
    
    this.addNotification(notification)
  }
  
  /**
   * Get notification icon class based on type
   */
  getNotificationIcon(type: Notification['type']): string {
    const iconMap = {
      success: '✅',
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌'
    }
    return iconMap[type] || 'ℹ️'
  }
  
  /**
   * Get notification color class based on type
   */
  getNotificationColorClass(type: Notification['type']): string {
    const colorMap = {
      success: 'text-green-600 bg-green-50 border-green-200',
      info: 'text-blue-600 bg-blue-50 border-blue-200',
      warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      error: 'text-red-600 bg-red-50 border-red-200'
    }
    return colorMap[type] || colorMap.info
  }
}

// Export singleton instance
export const notificationService = new NotificationService()

// Auto-connect when imported (will be overridden when user logs in)
if (typeof window !== 'undefined') {
  // Request notification permission on first load
  notificationService.requestNotificationPermission()
}