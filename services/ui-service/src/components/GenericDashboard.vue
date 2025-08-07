<template>
  <div class="generic-dashboard">
    <!-- Dashboard Header -->
    <div class="mb-8" v-if="dashboard">
      <h1 class="text-3xl font-bold text-gray-900">{{ dashboard.title }}</h1>
      <p class="mt-2 text-gray-600" v-if="dashboard.description">
        {{ dashboard.description }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Widgets -->
    <div v-else class="dashboard-grid">
      <div
        v-for="widget in widgets"
        :key="widget.id"
        :class="getWidgetClass(widget)"
        class="widget-container"
      >
        <DashboardWidget
          :widget="widget"
          :data="widgetData[widget.id]"
          @refresh="refreshWidget(widget)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import uiRegistry from '@/services/uiRegistry'
import type { UIComponent, DashboardWidget as DashboardWidgetType } from '@/services/uiRegistry'
import DashboardWidget from './DashboardWidget.vue'

const route = useRoute()

// State
const loading = ref(true)
const error = ref<string | null>(null)
const dashboard = ref<UIComponent | null>(null)
const widgets = ref<DashboardWidgetType[]>([])
const widgetData = ref<Record<string, any>>({})

// Computed
const dashboardId = computed(() => route.params.dashboardId as string || 'main')
const service = computed(() => route.params.service as string || route.meta.service as string)

// Methods
const getWidgetClass = (widget: DashboardWidgetType) => {
  const sizeClasses = {
    small: 'col-span-1',
    medium: 'col-span-2',
    large: 'col-span-3',
    full: 'col-span-4'
  }
  return sizeClasses[widget.size] || sizeClasses.medium
}

const loadDashboard = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Load dashboard configuration
    if (service.value) {
      const components = await uiRegistry.getComponents(service.value, 'dashboard')
      dashboard.value = components.find(c => c.id === dashboardId.value) || components[0]
    }
    
    // Load widgets
    const allWidgets = await uiRegistry.getDashboardWidgets()
    widgets.value = allWidgets.filter(w => 
      !service.value || w.service === service.value
    )
    
    // Load widget data
    await loadWidgetData()
  } catch (err) {
    console.error('Error loading dashboard:', err)
    error.value = 'Failed to load dashboard configuration'
  } finally {
    loading.value = false
  }
}

const loadWidgetData = async () => {
  for (const widget of widgets.value) {
    try {
      const data = await uiRegistry.fetchWidgetData(widget)
      widgetData.value[widget.id] = data
    } catch (err) {
      console.error(`Error loading data for widget ${widget.id}:`, err)
      widgetData.value[widget.id] = null
    }
  }
}

const refreshWidget = async (widget: DashboardWidgetType) => {
  try {
    const data = await uiRegistry.fetchWidgetData(widget)
    widgetData.value[widget.id] = data
  } catch (err) {
    console.error(`Error refreshing widget ${widget.id}:`, err)
  }
}

// Setup auto-refresh for widgets
const setupAutoRefresh = () => {
  widgets.value.forEach(widget => {
    if (widget.refresh_interval > 0) {
      setInterval(() => {
        refreshWidget(widget)
      }, widget.refresh_interval * 1000)
    }
  })
}

// Lifecycle
onMounted(() => {
  loadDashboard()
})

// Watch for route changes
watch(() => route.params, () => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

@media (max-width: 1280px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.widget-container {
  min-height: 200px;
}
</style>