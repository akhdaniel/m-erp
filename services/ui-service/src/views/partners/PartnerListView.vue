<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Partners
          </h1>
          <div class="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div class="mt-2 flex items-center text-sm text-gray-500">
              <UsersIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {{ partnerStore.pagination.total }} partners
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link
            to="/partners/create"
            class="btn btn-primary inline-flex items-center"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add Partner
          </router-link>
        </div>
      </div>

      <!-- Filters and search -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-4">
            <div>
              <label for="search" class="block text-sm font-medium text-gray-700">
                Search
              </label>
              <div class="mt-1">
                <input
                  id="search"
                  v-model="filters.search"
                  type="text"
                  placeholder="Search partners..."
                  class="input"
                  @input="debouncedSearch"
                />
              </div>
            </div>
            
            <div>
              <label for="partner-type" class="block text-sm font-medium text-gray-700">
                Type
              </label>
              <div class="mt-1">
                <select
                  id="partner-type"
                  v-model="filters.partner_type"
                  class="input"
                  @change="handleFilterChange"
                >
                  <option value="">All Types</option>
                  <option value="customer">Customers</option>
                  <option value="supplier">Suppliers</option>
                  <option value="vendor">Vendors</option>
                  <option value="both">Both Customer & Supplier</option>
                </select>
              </div>
            </div>
            
            <div>
              <label for="status" class="block text-sm font-medium text-gray-700">
                Status
              </label>
              <div class="mt-1">
                <select
                  id="status"
                  v-model="filters.is_active"
                  class="input"
                  @change="handleFilterChange"
                >
                  <option value="">All</option>
                  <option :value="true">Active</option>
                  <option :value="false">Inactive</option>
                </select>
              </div>
            </div>
            
            <div>
              <label for="page-size" class="block text-sm font-medium text-gray-700">
                Items per page
              </label>
              <div class="mt-1">
                <select
                  id="page-size"
                  v-model="filters.size"
                  class="input"
                  @change="handleFilterChange"
                >
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="partnerStore.isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500">Loading partners...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="partnerStore.error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Error loading partners
            </h3>
            <div class="mt-2 text-sm text-red-700">
              {{ partnerStore.error }}
            </div>
            <div class="mt-4">
              <button
                @click="loadPartners"
                class="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Partners table -->
      <div v-else class="card">
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Partner
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Industry
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th scope="col" class="relative px-6 py-3">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="partner in (partnerStore.partners || [])" :key="partner.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ partner.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ partner.code || 'No code' }}
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex flex-wrap gap-1">
                    <span v-if="partner.is_customer" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      Customer
                    </span>
                    <span v-if="partner.is_supplier" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Supplier
                    </span>
                    <span v-if="partner.is_vendor" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                      Vendor
                    </span>
                    <span v-if="partner.is_company" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      Company
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    {{ partner.email || '-' }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ partner.phone || partner.mobile || '-' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ partner.industry || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    partner.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]">
                    {{ partner.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(partner.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <router-link
                    :to="`/partners/${partner.id}/edit`"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    Edit
                  </router-link>
                  <button
                    @click="togglePartnerStatus(partner)"
                    :class="[
                      partner.is_active 
                        ? 'text-red-600 hover:text-red-900' 
                        : 'text-green-600 hover:text-green-900'
                    ]"
                  >
                    {{ partner.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button
                    @click="deletePartner(partner)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Empty state -->
          <div v-if="!partnerStore.partners || partnerStore.partners.length === 0" class="text-center py-12">
            <UsersIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No partners found</h3>
            <p class="mt-1 text-sm text-gray-500">
              Get started by creating a new partner.
            </p>
            <div class="mt-6">
              <router-link to="/partners/create" class="btn btn-primary">
                <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
                Add Partner
              </router-link>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="partnerStore.pagination.pages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="changePage(partnerStore.pagination.page - 1)"
              :disabled="partnerStore.pagination.page <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="changePage(partnerStore.pagination.page + 1)"
              :disabled="partnerStore.pagination.page >= partnerStore.pagination.pages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing
                <span class="font-medium">{{ (partnerStore.pagination.page - 1) * partnerStore.pagination.size + 1 }}</span>
                to
                <span class="font-medium">{{ Math.min(partnerStore.pagination.page * partnerStore.pagination.size, partnerStore.pagination.total) }}</span>
                of
                <span class="font-medium">{{ partnerStore.pagination.total }}</span>
                results
              </p>
            </div>
            
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="changePage(partnerStore.pagination.page - 1)"
                  :disabled="partnerStore.pagination.page <= 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeftIcon class="h-5 w-5" />
                </button>
                
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="changePage(page)"
                  :class="[
                    page === partnerStore.pagination.page
                      ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                  ]"
                >
                  {{ page }}
                </button>
                
                <button
                  @click="changePage(partnerStore.pagination.page + 1)"
                  :disabled="partnerStore.pagination.page >= partnerStore.pagination.pages"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRightIcon class="h-5 w-5" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  UsersIcon,
  PlusIcon,
  ExclamationTriangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/AppLayout.vue'
import { usePartnerStore } from '@/stores/partners'
import type { Partner } from '@/types'

const partnerStore = usePartnerStore()

// Reactive filters
const filters = ref({
  search: '',
  partner_type: '',
  is_active: '',
  size: 10,
  page: 1
})

// Computed pagination
const visiblePages = computed(() => {
  const current = partnerStore.pagination.page
  const total = partnerStore.pagination.pages
  const delta = 2 // Show 2 pages before and after current page
  
  const range = []
  const rangeWithDots = []
  
  for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
    range.push(i)
  }
  
  if (current - delta > 2) {
    rangeWithDots.push(1, '...')
  } else {
    rangeWithDots.push(1)
  }
  
  rangeWithDots.push(...range)
  
  if (current + delta < total - 1) {
    rangeWithDots.push('...', total)
  } else {
    rangeWithDots.push(total)
  }
  
  return rangeWithDots.filter((page, index, array) => page !== array[index - 1])
})

// Debounced search
let searchTimeout: NodeJS.Timeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadPartners()
  }, 300)
}

// Event handlers
const handleFilterChange = () => {
  filters.value.page = 1
  loadPartners()
}

const changePage = (page: number) => {
  if (page >= 1 && page <= partnerStore.pagination.pages) {
    filters.value.page = page
    loadPartners()
  }
}

const loadPartners = async () => {
  const params = {
    page: filters.value.page,
    size: filters.value.size,
    search: filters.value.search || undefined,
    partner_type: filters.value.partner_type || undefined,
    is_active: filters.value.is_active !== '' ? filters.value.is_active : undefined
  }
  await partnerStore.fetchPartners(params)
}

const togglePartnerStatus = async (partner: Partner) => {
  if (confirm(`Are you sure you want to ${partner.is_active ? 'deactivate' : 'activate'} ${partner.name}?`)) {
    try {
      await partnerStore.togglePartnerStatus(partner.id, !partner.is_active)
    } catch (error) {
      console.error('Failed to toggle partner status:', error)
    }
  }
}

const deletePartner = async (partner: Partner) => {
  if (confirm(`Are you sure you want to delete ${partner.name}? This action cannot be undone.`)) {
    try {
      await partnerStore.deletePartner(partner.id)
    } catch (error) {
      console.error('Failed to delete partner:', error)
    }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Load partners on mount
onMounted(() => {
  partnerStore.clearError()
  loadPartners()
})
</script>