<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Purchase Approvals</h1>
      <p class="mt-1 text-sm text-gray-500">Manage and track purchase order approvals</p>
    </div>

    <!-- Filters -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filters.status"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        <!-- Amount Range Filters -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Min Amount</label>
          <input
            v-model="filters.amount_min"
            type="number"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="0"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Max Amount</label>
          <input
            v-model="filters.amount_max"
            type="number"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            placeholder="10000"
          />
        </div>

        <!-- Date Range Filters -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
          <select
            v-model="filters.date_range"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          >
            <option value="">All Dates</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
          </select>
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

    <!-- Approvals Table -->
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
                Amount
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Requested By
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Request Date
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="approval in approvals" :key="approval.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ approval.po_number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ approval.supplier_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatCurrency(approval.total_amount) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ approval.requested_by }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDate(approval.order_date) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass('pending')">
                  pending
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="approveOrder(approval.id)"
                  class="text-green-600 hover:text-green-900 mr-3"
                >
                  Approve
                </button>
                <button
                  @click="rejectOrder(approval.id)"
                  class="text-red-600 hover:text-red-900 mr-3"
                >
                  Reject
                </button>
                <router-link
                  :to="`/purchasing/orders/${approval.id}`"
                  class="text-primary-600 hover:text-primary-900"
                >
                  View
                </router-link>
              </td>
            </tr>
            <tr v-if="approvals.length === 0">
              <td colspan="7" class="px-6 py-12 text-center">
                <div class="text-sm text-gray-500">
                  <DocumentSearchIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No approvals</h3>
                  <p class="mt-1 text-sm text-gray-500">There are no purchase orders requiring approval at this time.</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="approvals.length > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
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
          <h3 class="text-sm font-medium text-red-800">Error loading approvals</h3>
          <div class="mt-2 text-sm text-red-700">
            <p>{{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePurchasingStore } from '@/stores/purchasing'
import {
  DocumentSearchIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

// Define the approval interface
interface Approval {
  id: number
  po_number: string
  po_id?: number
  supplier_name: string
  total_amount: number
  currency_code: string
  order_date: string
  approval_level: string
  requested_by: string
  urgency: string
  status?: string
  [key: string]: any
}

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const filters = ref({
  status: '',
  amount_min: '',
  amount_max: '',
  date_range: ''
})

// Computed properties
const approvals = computed<Approval[]>(() => purchasingStore.approvals)
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
const formatCurrency = (amount) => {
  if (!amount) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const loadApprovals = async (page = 1) => {
  try {
    const params: any = {
      page: page,
      page_size: pageSize.value
    }
    
    // Add filters if they exist
    if (filters.value.status) {
      params.status = filters.value.status
    }
    
    if (filters.value.amount_min) {
      params.amount_min = parseFloat(filters.value.amount_min)
    }
    
    if (filters.value.amount_max) {
      params.amount_max = parseFloat(filters.value.amount_max)
    }
    
    if (filters.value.date_range) {
      params.date_range = filters.value.date_range
    }
    
    await purchasingStore.fetchApprovals(params)
  } catch (err) {
    console.error('Error loading approvals:', err)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    amount_min: '',
    amount_max: '',
    date_range: ''
  }
  loadApprovals()
}

const approveOrder = async (orderId) => {
  if (confirm('Are you sure you want to approve this purchase order?')) {
    try {
      const notes = prompt('Add any approval notes (optional):') || undefined
      await purchasingStore.approvePurchaseOrder(orderId, notes)
      // Reload the approvals list
      await loadApprovals(currentPage.value)
    } catch (err) {
      console.error('Error approving order:', err)
      // Show error to user
      alert('Failed to approve order: ' + (err.response?.data?.detail || err.message || 'Unknown error'))
    }
  }
}

const rejectOrder = async (orderId) => {
  const reason = prompt('Please provide a reason for rejection:')
  if (reason) {
    try {
      await purchasingStore.rejectPurchaseOrder(orderId, reason)
      // Reload the approvals list
      await loadApprovals(currentPage.value)
    } catch (err) {
      console.error('Error rejecting order:', err)
      // Show error to user
      alert('Failed to reject order: ' + (err.response?.data?.detail || err.message || 'Unknown error'))
    }
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    loadApprovals(currentPage.value - 1)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    loadApprovals(currentPage.value + 1)
  }
}

const goToPage = (page) => {
  if (page !== currentPage.value) {
    loadApprovals(page)
  }
}

// Watch for filter changes
watch(filters, () => {
  loadApprovals()
}, { deep: true })

// Lifecycle hooks
onMounted(async () => {
  loadApprovals()
})
</script>
</content>