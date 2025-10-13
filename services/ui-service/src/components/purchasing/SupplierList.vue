<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold text-gray-900">Suppliers</h1>
        <p class="mt-1 text-sm text-gray-500">Manage and track all suppliers</p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <router-link
          :to="{ name: 'purchasing-suppliers-create' }"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
          New Supplier
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
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            v-model="filters.category"
            class="input"
          >
            <option value="">All Categories</option>
            <option value="general">General</option>
            <option value="preferred">Preferred</option>
            <option value="strategic">Strategic</option>
          </select>
        </div>

        <!-- Rating Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Min Rating</label>
          <select
            v-model="filters.min_rating"
            class="input"
          >
            <option value="">Any Rating</option>
            <option value="1">1 Star</option>
            <option value="2">2 Stars</option>
            <option value="3">3 Stars</option>
            <option value="4">4 Stars</option>
            <option value="5">5 Stars</option>
          </select>
        </div>

        <!-- Search Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Supplier name"
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

    <!-- Suppliers Table -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Supplier
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rating
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Orders
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Spend
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
            <tr v-for="supplier in suppliers" :key="supplier.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ supplier.name }}</div>
                <div class="text-sm text-gray-500">{{ supplier.code }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ supplier.category }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <StarIcon v-for="n in 5" :key="n" class="h-4 w-4 flex-shrink-0" :class="n <= Math.round(supplier.performance_rating || 0) ? 'text-yellow-400' : 'text-gray-300'" />
                  <span class="ml-1 text-sm text-gray-500">{{ (supplier.performance_rating || 0).toFixed(1) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ supplier.total_orders || 0 }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatCurrency(supplier.total_spend || 0) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass(supplier.status)">
                  {{ supplier.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <router-link
                  :to="{ name: 'purchasing-suppliers-view', params: { id: supplier.id } }"
                  class="text-primary-600 hover:text-primary-900 mr-3"
                >
                  View
                </router-link>
                <router-link
                  :to="{ name: 'purchasing-suppliers-edit', params: { id: supplier.id } }"
                  class="text-primary-600 hover:text-primary-900 mr-3"
                >
                  Edit
                </router-link>
                <button
                  v-if="supplier.status === 'active'"
                  @click="evaluateSupplier(supplier.id)"
                  class="text-primary-600 hover:text-primary-900"
                >
                  Evaluate
                </button>
              </td>
            </tr>
            <tr v-if="suppliers.length === 0">
              <td colspan="7" class="px-6 py-12 text-center">
                <div class="text-sm text-gray-500">
                  <DocumentSearchIcon class="mx-auto h-12 w-12 text-gray-400" />
                  <h3 class="mt-2 text-sm font-medium text-gray-900">No suppliers</h3>
                  <p class="mt-1 text-sm text-gray-500">Get started by creating a new supplier.</p>
                  <div class="mt-6">
                    <router-link
                      :to="{ name: 'purchasing-suppliers-create' }"
                      class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
                      New Supplier
                    </router-link>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="suppliers.length > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
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
          <h3 class="text-sm font-medium text-red-800">Error loading suppliers</h3>
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
  ExclamationCircleIcon,
  StarIcon
} from '@heroicons/vue/24/outline'

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const filters = ref({
  status: '',
  category: '',
  min_rating: '',
  search: ''
})

// Computed properties
const suppliers = computed(() => purchasingStore.suppliers)
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

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    suspended: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const loadSuppliers = async (page = 1) => {
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
    
    await purchasingStore.fetchSuppliers(params)
  } catch (err) {
    console.error('Error loading suppliers:', err)
  }
}

const resetFilters = () => {
  filters.value = {
    status: '',
    category: '',
    min_rating: '',
    search: ''
  }
  loadSuppliers()
}

const evaluateSupplier = (supplierId) => {
  router.push({ name: 'purchasing-suppliers-evaluate', params: { id: supplierId } })
}

const prevPage = () => {
  if (currentPage.value > 1) {
    loadSuppliers(currentPage.value - 1)
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    loadSuppliers(currentPage.value + 1)
  }
}

const goToPage = (page) => {
  if (page !== currentPage.value) {
    loadSuppliers(page)
  }
}

// Watch for filter changes
watch(filters, () => {
  loadSuppliers()
}, { deep: true })

// Lifecycle hooks
onMounted(async () => {
  loadSuppliers()
})
</script>
</content>