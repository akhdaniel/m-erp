<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            {{ isEditMode ? 'Edit Company' : 'Create Company' }}
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            {{ isEditMode ? 'Update company information' : 'Add a new company to the system' }}
          </p>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link
            to="/companies"
            class="btn btn-secondary mr-3"
          >
            Cancel
          </router-link>
        </div>
      </div>

      <!-- Form -->
      <div class="card">
        <form @submit.prevent="handleSubmit" class="card-body space-y-6">
          <!-- Error display -->
          <div v-if="companyStore.error" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                  Error
                </h3>
                <div class="mt-2 text-sm text-red-700">
                  {{ companyStore.error }}
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Company Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">
                Company Name *
              </label>
              <div class="mt-1">
                <input
                  id="name"
                  v-model="form.name"
                  type="text"
                  required
                  class="input"
                  :class="{ 'border-red-300': errors.name }"
                />
              </div>
              <p v-if="errors.name" class="mt-2 text-sm text-red-600">
                {{ errors.name }}
              </p>
            </div>

            <!-- Legal Name -->
            <div>
              <label for="legal_name" class="block text-sm font-medium text-gray-700">
                Legal Name *
              </label>
              <div class="mt-1">
                <input
                  id="legal_name"
                  v-model="form.legal_name"
                  type="text"
                  required
                  class="input"
                  :class="{ 'border-red-300': errors.legal_name }"
                />
              </div>
              <p v-if="errors.legal_name" class="mt-2 text-sm text-red-600">
                {{ errors.legal_name }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                Official legal name of the company
              </p>
            </div>

            <!-- Company Code -->
            <div>
              <label for="code" class="block text-sm font-medium text-gray-700">
                Company Code *
              </label>
              <div class="mt-1">
                <input
                  id="code"
                  v-model="form.code"
                  type="text"
                  required
                  :disabled="isEditMode"
                  class="input"
                  :class="{ 
                    'border-red-300': errors.code,
                    'bg-gray-50 cursor-not-allowed': isEditMode 
                  }"
                />
              </div>
              <p v-if="errors.code" class="mt-2 text-sm text-red-600">
                {{ errors.code }}
              </p>
              <p v-if="isEditMode" class="mt-2 text-sm text-gray-500">
                Company code cannot be changed after creation
              </p>
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">
                Email
              </label>
              <div class="mt-1">
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  class="input"
                  :class="{ 'border-red-300': errors.email }"
                />
              </div>
              <p v-if="errors.email" class="mt-2 text-sm text-red-600">
                {{ errors.email }}
              </p>
            </div>

            <!-- Phone -->
            <div>
              <label for="phone" class="block text-sm font-medium text-gray-700">
                Phone
              </label>
              <div class="mt-1">
                <input
                  id="phone"
                  v-model="form.phone"
                  type="tel"
                  class="input"
                  :class="{ 'border-red-300': errors.phone }"
                />
              </div>
              <p v-if="errors.phone" class="mt-2 text-sm text-red-600">
                {{ errors.phone }}
              </p>
            </div>

            <!-- Website -->
            <div>
              <label for="website" class="block text-sm font-medium text-gray-700">
                Website
              </label>
              <div class="mt-1">
                <input
                  id="website"
                  v-model="form.website"
                  type="url"
                  class="input"
                  :class="{ 'border-red-300': errors.website }"
                />
              </div>
              <p v-if="errors.website" class="mt-2 text-sm text-red-600">
                {{ errors.website }}
              </p>
            </div>

            <!-- Currency -->
            <div>
              <label for="currency" class="block text-sm font-medium text-gray-700">
                Currency *
              </label>
              <div class="mt-1">
                <select
                  id="currency"
                  v-model="form.currency"
                  required
                  class="input"
                  :class="{ 'border-red-300': errors.currency }"
                >
                  <option value="">Select currency</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="JPY">JPY - Japanese Yen</option>
                  <option value="CAD">CAD - Canadian Dollar</option>
                  <option value="AUD">AUD - Australian Dollar</option>
                </select>
              </div>
              <p v-if="errors.currency" class="mt-2 text-sm text-red-600">
                {{ errors.currency }}
              </p>
            </div>
          </div>

          <!-- Address -->
          <div>
            <label for="address" class="block text-sm font-medium text-gray-700">
              Address
            </label>
            <div class="mt-1">
              <textarea
                id="address"
                v-model="form.address"
                rows="3"
                class="input"
                :class="{ 'border-red-300': errors.address }"
              />
            </div>
            <p v-if="errors.address" class="mt-2 text-sm text-red-600">
              {{ errors.address }}
            </p>
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <input
              id="is_active"
              v-model="form.is_active"
              type="checkbox"
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-900">
              Company is active
            </label>
          </div>

          <!-- Submit button -->
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="companyStore.isLoading"
              class="btn btn-primary"
            >
              <span v-if="companyStore.isLoading" class="inline-flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isEditMode ? 'Updating...' : 'Creating...' }}
              </span>
              <span v-else>
                {{ isEditMode ? 'Update Company' : 'Create Company' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/AppLayout.vue'
import { useCompanyStore } from '@/stores/companies'
import type { CompanyCreate, CompanyUpdate } from '@/types'

const router = useRouter()
const route = useRoute()
const companyStore = useCompanyStore()

const companyId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id as string) : null
})

const isEditMode = computed(() => !!companyId.value)

const form = reactive({
  name: '',
  legal_name: '',
  code: '',
  email: '',
  phone: '',
  website: '',
  address: '',
  currency: 'USD',
  is_active: true
})

const errors = ref<Record<string, string>>({})

async function loadCompany() {
  if (companyId.value) {
    const company = await companyStore.fetchCompany(companyId.value)
    if (company) {
      Object.assign(form, {
        name: company.name,
        legal_name: company.legal_name,
        code: company.code,
        email: company.email || '',
        phone: company.phone || '',
        website: company.website || '',
        address: company.street || '',
        currency: company.currency,
        is_active: company.is_active
      })
    } else {
      router.push('/companies')
    }
  }
}

function validateForm(): boolean {
  errors.value = {}

  if (!form.name.trim()) {
    errors.value.name = 'Company name is required'
  }

  if (!form.legal_name.trim()) {
    errors.value.legal_name = 'Legal name is required'
  }

  if (!form.code.trim()) {
    errors.value.code = 'Company code is required'
  } else if (!/^[A-Z0-9_-]+$/i.test(form.code)) {
    errors.value.code = 'Company code can only contain letters, numbers, underscores, and hyphens'
  }

  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = 'Please enter a valid email address'
  }

  if (!form.currency) {
    errors.value.currency = 'Currency is required'
  }

  if (form.website && !form.website.startsWith('http')) {
    form.website = 'https://' + form.website
  }

  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) {
    return
  }

  try {
    if (isEditMode.value && companyId.value) {
      const updateData: CompanyUpdate = {
        name: form.name,
        legal_name: form.legal_name,
        email: form.email || undefined,
        phone: form.phone || undefined,
        website: form.website || undefined,
        street: form.address || undefined,
        currency: form.currency,
        is_active: form.is_active
      }
      await companyStore.updateCompany(companyId.value, updateData)
    } else {
      const createData: CompanyCreate = {
        name: form.name,
        legal_name: form.legal_name,
        code: form.code.toUpperCase(),
        email: form.email || undefined,
        phone: form.phone || undefined,
        website: form.website || undefined,
        street: form.address || undefined,
        currency: form.currency,
        is_active: form.is_active
      }
      await companyStore.createCompany(createData)
    }

    router.push('/companies')
  } catch (error) {
    console.error('Failed to save company:', error)
  }
}

onMounted(() => {
  companyStore.clearError()
  loadCompany()
})
</script>