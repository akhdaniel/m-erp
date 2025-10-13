<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold text-gray-900">Purchase Orders</h1>
        <p class="mt-1 text-sm text-gray-500">Manage and track all purchase orders</p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <router-link
          :to="{ name: 'purchasing-orders-create' }"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
          New Purchase Order
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            class="input"
          >
            <option value="">All Statuses</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="pending">Pending</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <!-- Supplier Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
          <select
            v-model="filters.supplier_id"
            class="input"
          >
            <option value="">All Suppliers</option>
            <option
              v-for="supplier in activeSuppliers"
              :key="supplier.id"
              :value="supplier.id"
            >
              {{ supplier.name }}
            </option>
          </select>
        </div>

        <!-- Date Range Filters -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">From Date</label>
          <input
            v-model="filters.from_date"
            type="date"
            class="input"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">To Date</label>
          <input
            v-model="filters.to_date"
            type="date"
            class="input"
          />
        </div>
      </div>

      <div class="mt-4 flex justify-end">
        <button
          @click="resetFilters"
          class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Reset Filters
        </button>
      </div>
    </div>

    <!-- Purchase Orders Table -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                PO Number
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Supplier
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Order Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Approval
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in purchaseOrders" :key="order.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ order.po_number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ order.supplier_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(order.order_date) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatCurrency(order.total_amount) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass(order.status)">
                  {{ order.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getApprovalBadgeClass(order.approval_status)">
                  {{ order.approval_status ? order.approval_status.replace('_', ' ') : 'N/A' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <router-link
                  :to="{ name: 'purchasing-orders-view', params: { id: order.id } }"
                  class="text-primary-600 hover:text-primary-900 mr-3"
                >
                  View
                </router-link>
                <router-link
                  v-if="order.status === 'draft'"
                  :to="{ name: 'purchasing-orders-edit', params: { id: order.id } }"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Edit
                </router-link>
                <button
                  v-else
                  @click="viewOrder(order.id)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Details
                </button>
              </td>
            </tr>
            <tr v-if="purchaseOrders.length === 0">
              <td colspan="7" class="px-6 py-12 text-center">
                <div class="text-sm text-gray-500">
                  <DocumentSearchIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No purchase orders</h3>
                  <p class="mt-1 text-sm text-gray-500">Get started by creating a new purchase order.</p>
                  <div class="mt-6">
                    <router-link
                      :to="{ name: 'purchasing-orders-create' }"
                      class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
                      New Purchase Order
                    </router-link>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="purchaseOrders.length > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="prevPage"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
              to
              <span class="font-medium">{{ Math.min(currentPage * pageSize, total) }}</span>
              of
              <span class="font-medium">{{ total }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                <span class="sr-only">Previous</span>
                <ChevronLeftIcon class="h-5 w-5" />
              </button>
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  page === currentPage
                    ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                ]"
              >
                {{ page }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
              >
                <span class="sr-only">Next</span>
                <ChevronRightIcon class="h-5 w-5" />
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-6 bg-red-50 border border-red-200 rounded-md p-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading purchase orders</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePurchasingStore } from '@/stores/purchasing'
import {
  PlusIcon,
  DocumentSearchIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const filters = ref({
  status: '',
  supplier_id: '',
  from_date: '',
  to_date: ''
})

// Computed properties
const purchaseOrders = computed(() => purchasingStore.purchaseOrders)
const activeSuppliers = computed(() => purchasingStore.activeSuppliers)
const isLoading = computed(() => purchasingStore.isLoading)
const error = computed(() => purchasingStore.error)
const total = computed(() => purchasingStore.pagination.total)
const currentPage = computed(() => purchasingStore.pagination.page)
const pageSize = computed(() => purchasingStore.pagination.pageSize)
const totalPages = computed(() => purchasingStore.pagination.totalPages)

const visiblePages = computed(() => {
  const pages = []
  const delta = 2
  const left = currentPage.value - delta
  const right = currentPage.value + delta + 1
  
  for (let i = 1; i <= totalPages.value; i++) {
    if (i === 1 || i === totalPages.value || (i >= left && i < right)) {
      pages.push(i)
    }
  }
  
  return pages
})

// Methods
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (amount) => {
  if (!amount) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    draft: 'bg-gray-100 text-gray-800',
    approved: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const getApprovalBadgeClass = (status) => {
  const statusClasses = {
    draft: 'bg-gray-100 text-gray-800',
    requires_approval: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const loadPurchaseOrders = async (page = 1) => {
  try {
    const params = {
      page,
      page_size: pageSize.value,
      ...filters.value
    }
    
    // Remove empty filter values
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    await purchasingStore.fetchPurchaseOrders(params)
  } catch (err) {
    console.error('Error loading purchase orders:', err)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    supplier_id: '',
    from_date: '',
    to_date: ''
  }
  loadPurchaseOrders()
}

const viewOrder = (orderId) => {
  router.push({ name: 'purchasing-orders-view', params: { id: orderId } })
}

const prevPage = () => {
  if (currentPage.value > 1) {
    loadPurchaseOrders(currentPage.value - 1)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    loadPurchaseOrders(currentPage.value + 1)
  }
}

const goToPage = (page) => {
  if (page !== currentPage.value) {
    loadPurchaseOrders(page)
  }
}

// Watch for filter changes
watch(filters, () => {
  loadPurchaseOrders()
}, { deep: true })

// Lifecycle hooks
onMounted(async () => {
  // Load suppliers first
  if (purchasingStore.suppliers.length === 0) {
    await purchasingStore.fetchSuppliers()
  }
  
  // Load purchase orders
  loadPurchaseOrders()
})
</script>