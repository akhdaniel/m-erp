<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Inventory Management</h1>
      <p class="mt-2 text-gray-600">
        Monitor stock levels, track movements, and manage warehouse operations
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Key Metrics -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <!-- Total Products -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Total Products</dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900">
                      {{ stats.total_products.toLocaleString() }}
                    </div>
                    <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                      {{ stats.active_products }} active
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Stock Value -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Total Stock Value</dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900">
                      ${{ (stats.total_stock_value / 1000).toFixed(1) }}k
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Low Stock Alert -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Low Stock Items</dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-yellow-600">
                      {{ stats.low_stock_items }}
                    </div>
                    <div v-if="stats.out_of_stock_items > 0" class="ml-2 flex items-baseline text-sm font-semibold text-red-600">
                      {{ stats.out_of_stock_items }} out
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Warehouses -->
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Warehouses</dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900">
                      {{ stats.warehouses_count }}
                    </div>
                    <div class="ml-2 flex items-baseline text-sm font-semibold text-blue-600">
                      locations
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <!-- Recent Stock Movements -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Stock Movements
            </h3>
            <div class="flow-root">
              <ul class="-my-5 divide-y divide-gray-200">
                <li v-for="movement in recentMovements" :key="movement.id" class="py-4">
                  <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                      <span :class="getMovementIconClass(movement.movement_type)" class="h-8 w-8 rounded-full flex items-center justify-center">
                        <svg v-if="movement.movement_type === 'receipt'" class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
                        </svg>
                        <svg v-else-if="movement.movement_type === 'shipment'" class="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 13l-5 5m0 0l-5-5m5 5V6" />
                        </svg>
                        <svg v-else class="h-5 w-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4" />
                        </svg>
                      </span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">
                        {{ movement.product_name }}
                      </p>
                      <p class="text-sm text-gray-500">
                        {{ movement.warehouse_name }} • {{ formatMovementType(movement.movement_type) }}
                      </p>
                    </div>
                    <div class="text-right">
                      <div :class="movement.quantity > 0 ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                        {{ movement.quantity > 0 ? '+' : '' }}{{ movement.quantity }}
                      </div>
                      <div class="text-xs text-gray-500">
                        {{ formatTime(movement.created_at) }}
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
            <div class="mt-6">
              <a href="#" class="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                View all movements
              </a>
            </div>
          </div>
        </div>

        <!-- Low Stock Items -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              Low Stock Alerts
            </h3>
            <div class="flow-root">
              <ul class="-my-5 divide-y divide-gray-200">
                <li v-for="item in lowStockItems" :key="item.product_id" class="py-4">
                  <div class="flex items-center space-x-4">
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">
                        {{ item.product_name }}
                      </p>
                      <p class="text-sm text-gray-500">
                        {{ item.product_code }} • {{ item.warehouse_name }}
                      </p>
                    </div>
                    <div class="text-right">
                      <div class="text-sm">
                        <span :class="item.current_stock === 0 ? 'text-red-600 font-semibold' : 'text-yellow-600 font-medium'">
                          {{ item.current_stock }} units
                        </span>
                      </div>
                      <div class="text-xs text-gray-500">
                        Reorder: {{ item.reorder_point }}
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
            <div class="mt-6">
              <a href="#" class="w-full flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                View all low stock items
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-8">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <router-link
            to="/inventory/products"
            class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
          >
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <span class="absolute inset-0" aria-hidden="true"></span>
              <p class="text-sm font-medium text-gray-900">Add Product</p>
              <p class="text-sm text-gray-500 truncate">Create new product</p>
            </div>
          </router-link>

          <router-link
            to="/inventory/stock"
            class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
          >
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <span class="absolute inset-0" aria-hidden="true"></span>
              <p class="text-sm font-medium text-gray-900">Adjust Stock</p>
              <p class="text-sm text-gray-500 truncate">Update inventory levels</p>
            </div>
          </router-link>

          <router-link
            to="/inventory/receiving"
            class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
          >
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <span class="absolute inset-0" aria-hidden="true"></span>
              <p class="text-sm font-medium text-gray-900">Receive Items</p>
              <p class="text-sm text-gray-500 truncate">Process receipts</p>
            </div>
          </router-link>

          <router-link
            to="/inventory/reports"
            class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
          >
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v1a1 1 0 001 1h4a1 1 0 001-1v-1m3-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v7m3-2h6" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <span class="absolute inset-0" aria-hidden="true"></span>
              <p class="text-sm font-medium text-gray-900">View Reports</p>
              <p class="text-sm text-gray-500 truncate">Analytics & insights</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import inventoryService from '@/services/inventory'
import type { InventoryStats, RecentMovement, LowStockItem } from '@/services/inventory'

// State
const loading = ref(true)
const error = ref<string | null>(null)
const stats = ref<InventoryStats>({
  total_products: 0,
  active_products: 0,
  total_stock_value: 0,
  total_items_in_stock: 0,
  low_stock_items: 0,
  out_of_stock_items: 0,
  warehouses_count: 0,
  pending_receipts: 0,
  recent_movements: 0
})
const recentMovements = ref<RecentMovement[]>([])
const lowStockItems = ref<LowStockItem[]>([])

// Mock data for low stock items (until API is ready)
const mockLowStockItems: LowStockItem[] = [
  {
    product_id: 1,
    product_name: 'Widget Pro X1',
    product_code: 'WPX-001',
    current_stock: 5,
    reorder_point: 20,
    warehouse_name: 'Main Warehouse'
  },
  {
    product_id: 2,
    product_name: 'Gadget Plus',
    product_code: 'GP-002',
    current_stock: 0,
    reorder_point: 15,
    warehouse_name: 'Distribution Center'
  },
  {
    product_id: 3,
    product_name: 'Component A',
    product_code: 'CA-003',
    current_stock: 8,
    reorder_point: 25,
    warehouse_name: 'Main Warehouse'
  },
  {
    product_id: 4,
    product_name: 'Tool Kit Standard',
    product_code: 'TKS-004',
    current_stock: 3,
    reorder_point: 10,
    warehouse_name: 'Regional Hub'
  }
]

// Methods
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Fetch all dashboard data in parallel
    const [dashboardStats, movements] = await Promise.all([
      inventoryService.getDashboardStats(),
      inventoryService.getRecentMovements(5)
    ])
    
    stats.value = dashboardStats
    recentMovements.value = movements
    
    // Use mock data for low stock items for now
    lowStockItems.value = mockLowStockItems.slice(0, 4)
    
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
    error.value = 'Failed to load dashboard data. Please try again later.'
  } finally {
    loading.value = false
  }
}

const getMovementIconClass = (type: string) => {
  switch (type) {
    case 'receipt':
      return 'bg-green-100'
    case 'shipment':
      return 'bg-blue-100'
    case 'adjustment':
      return 'bg-gray-100'
    default:
      return 'bg-gray-100'
  }
}

const formatMovementType = (type: string) => {
  switch (type) {
    case 'receipt':
      return 'Received'
    case 'shipment':
      return 'Shipped'
    case 'adjustment':
      return 'Adjusted'
    default:
      return type
  }
}

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (hours < 1) {
    const minutes = Math.floor(diff / (1000 * 60))
    return `${minutes} min ago`
  } else if (hours < 24) {
    return `${hours} hr ago`
  } else {
    const days = Math.floor(hours / 24)
    return `${days} day${days > 1 ? 's' : ''} ago`
  }
}

// Lifecycle
onMounted(() => {
  fetchDashboardData()
})
</script>