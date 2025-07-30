<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Companies
          </h1>
          <div class="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div class="mt-2 flex items-center text-sm text-gray-500">
              <BuildingOfficeIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {{ companyStore.pagination.total }} companies
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link
            to="/companies/create"
            class="btn btn-primary inline-flex items-center"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add Company
          </router-link>
        </div>
      </div>

      <!-- Filters and search -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <div>
              <label for="search" class="block text-sm font-medium text-gray-700">
                Search
              </label>
              <div class="mt-1">
                <input
                  id="search"
                  v-model="filters.search"
                  type="text"
                  placeholder="Search companies..."
                  class="input"
                  @input="debouncedSearch"
                />
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
      <div v-if="companyStore.isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500">Loading companies...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="companyStore.error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
              Error loading companies
            </h3>
            <div class="mt-2 text-sm text-red-700">
              {{ companyStore.error }}
            </div>
            <div class="mt-4">
              <button
                @click="loadCompanies"
                class="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Companies table -->
      <div v-else class="card">
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Currency
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
              <tr v-for="company in (companyStore.companies || [])" :key="company.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ company.name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ company.code }}
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    {{ company.email || '-' }}
                  </div>
                  <div class="text-sm text-gray-500">
                    {{ company.phone || '-' }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ company.currency }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    company.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]">
                    {{ company.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(company.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <router-link
                    :to="`/companies/${company.id}/edit`"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    Edit
                  </router-link>
                  <button
                    @click="toggleCompanyStatus(company)"
                    :class="[
                      company.is_active 
                        ? 'text-red-600 hover:text-red-900' 
                        : 'text-green-600 hover:text-green-900'
                    ]"
                  >
                    {{ company.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button
                    @click="deleteCompany(company)"
                    class="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Empty state -->
          <div v-if="!companyStore.companies || companyStore.companies.length === 0" class="text-center py-12">
            <BuildingOfficeIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No companies found</h3>
            <p class="mt-1 text-sm text-gray-500">
              Get started by creating a new company.
            </p>
            <div class="mt-6">
              <router-link to="/companies/create" class="btn btn-primary">
                <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
                Add Company
              </router-link>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="companyStore.pagination.pages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="changePage(companyStore.pagination.page - 1)"
              :disabled="companyStore.pagination.page <= 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="changePage(companyStore.pagination.page + 1)"
              :disabled="companyStore.pagination.page >= companyStore.pagination.pages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing
                <span class="font-medium">{{ (companyStore.pagination.page - 1) * companyStore.pagination.size + 1 }}</span>
                to
                <span class="font-medium">{{ Math.min(companyStore.pagination.page * companyStore.pagination.size, companyStore.pagination.total) }}</span>
                of
                <span class="font-medium">{{ companyStore.pagination.total }}</span>
                results
              </p>
            </div>
            
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="changePage(companyStore.pagination.page - 1)"
                  :disabled="companyStore.pagination.page <= 1"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeftIcon class="h-5 w-5" />
                </button>
                
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="changePage(page)"
                  :class="[
                    page === companyStore.pagination.page
                      ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50',
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium'
                  ]"
                >
                  {{ page }}
                </button>
                
                <button
                  @click="changePage(companyStore.pagination.page + 1)"
                  :disabled="companyStore.pagination.page >= companyStore.pagination.pages"
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
  BuildingOfficeIcon,
  PlusIcon,
  ExclamationTriangleIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/AppLayout.vue'
import { useCompanyStore } from '@/stores/companies'
import type { Company } from '@/types'

const companyStore = useCompanyStore()

const filters = ref({
  search: '',
  is_active: '',
  size: 10,
  page: 1
})

let searchTimeout: ReturnType<typeof setTimeout>

const visiblePages = computed(() => {
  const current = companyStore.pagination.page
  const total = companyStore.pagination.pages
  const delta = 2
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

  return rangeWithDots.filter((page, index, array) => array.indexOf(page) === index && page !== 1 || index === 0)
})

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadCompanies()
  }, 500)
}

function handleFilterChange() {
  filters.value.page = 1
  loadCompanies()
}

async function loadCompanies() {
  const params: any = {
    page: filters.value.page,
    size: filters.value.size
  }
  
  if (filters.value.search) {
    params.search = filters.value.search
  }
  
  if (filters.value.is_active !== '') {
    params.is_active = filters.value.is_active
  }
  
  await companyStore.fetchCompanies(params)
}

function changePage(page: number) {
  if (page >= 1 && page <= companyStore.pagination.pages) {
    filters.value.page = page
    loadCompanies()
  }
}

async function toggleCompanyStatus(company: Company) {
  if (confirm(`Are you sure you want to ${company.is_active ? 'deactivate' : 'activate'} ${company.name}?`)) {
    try {
      await companyStore.toggleCompanyStatus(company.id, !company.is_active)
    } catch (error) {
      alert('Failed to update company status')
    }
  }
}

async function deleteCompany(company: Company) {
  if (confirm(`Are you sure you want to delete ${company.name}? This action cannot be undone.`)) {
    try {
      await companyStore.deleteCompany(company.id)
    } catch (error) {
      alert('Failed to delete company')
    }
  }
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadCompanies()
})
</script>