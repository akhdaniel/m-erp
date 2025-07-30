<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            {{ isEditMode ? 'Edit Partner' : 'Create Partner' }}
          </h1>
          <p class="mt-1 text-sm text-gray-500">
            {{ isEditMode ? 'Update partner information' : 'Add a new partner to the system' }}
          </p>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link
            to="/partners"
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
          <div v-if="partnerStore.error" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">
                  Error
                </h3>
                <div class="mt-2 text-sm text-red-700">
                  {{ partnerStore.error }}
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <!-- Partner Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">
                Partner Name *
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

            <!-- Partner Code -->
            <div>
              <label for="code" class="block text-sm font-medium text-gray-700">
                Partner Code
              </label>
              <div class="mt-1">
                <input
                  id="code"
                  v-model="form.code"
                  type="text"
                  class="input"
                  :class="{ 'border-red-300': errors.code }"
                />
              </div>
              <p v-if="errors.code" class="mt-2 text-sm text-red-600">
                {{ errors.code }}
              </p>
              <p class="mt-1 text-sm text-gray-500">
                Optional unique code for the partner
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

            <!-- Mobile -->
            <div>
              <label for="mobile" class="block text-sm font-medium text-gray-700">
                Mobile
              </label>
              <div class="mt-1">
                <input
                  id="mobile"
                  v-model="form.mobile"
                  type="tel"
                  class="input"
                  :class="{ 'border-red-300': errors.mobile }"
                />
              </div>
              <p v-if="errors.mobile" class="mt-2 text-sm text-red-600">
                {{ errors.mobile }}
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

            <!-- Tax ID -->
            <div>
              <label for="tax_id" class="block text-sm font-medium text-gray-700">
                Tax ID
              </label>
              <div class="mt-1">
                <input
                  id="tax_id"
                  v-model="form.tax_id"
                  type="text"
                  class="input"
                  :class="{ 'border-red-300': errors.tax_id }"
                />
              </div>
              <p v-if="errors.tax_id" class="mt-2 text-sm text-red-600">
                {{ errors.tax_id }}
              </p>
            </div>

            <!-- Industry -->
            <div>
              <label for="industry" class="block text-sm font-medium text-gray-700">
                Industry
              </label>
              <div class="mt-1">
                <input
                  id="industry"
                  v-model="form.industry"
                  type="text"
                  class="input"
                  :class="{ 'border-red-300': errors.industry }"
                />
              </div>
              <p v-if="errors.industry" class="mt-2 text-sm text-red-600">
                {{ errors.industry }}
              </p>
            </div>
          </div>

          <!-- Partner Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              Partner Type *
            </label>
            <div class="space-y-2">
              <div class="flex items-center">
                <input
                  id="is_customer"
                  v-model="form.is_customer"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="is_customer" class="ml-2 block text-sm text-gray-900">
                  Customer - This partner purchases goods/services from us
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="is_supplier"
                  v-model="form.is_supplier"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="is_supplier" class="ml-2 block text-sm text-gray-900">
                  Supplier - This partner provides goods/services to us
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="is_vendor"
                  v-model="form.is_vendor"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="is_vendor" class="ml-2 block text-sm text-gray-900">
                  Vendor - This partner is a service provider or contractor
                </label>
              </div>
              <div class="flex items-center">
                <input
                  id="is_company"
                  v-model="form.is_company"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label for="is_company" class="ml-2 block text-sm text-gray-900">
                  Company - This partner is a company (not an individual)
                </label>
              </div>
            </div>
            <p v-if="errors.partner_type" class="mt-2 text-sm text-red-600">
              {{ errors.partner_type }}
            </p>
          </div>

          <!-- Company Selection -->
          <div>
            <label for="company_id" class="block text-sm font-medium text-gray-700">
              Company *
            </label>
            <div class="mt-1">
              <select
                id="company_id"
                v-model="form.company_id"
                required
                class="input"
                :class="{ 'border-red-300': errors.company_id }"
              >
                <option value="">Select company</option>
                <option
                  v-for="company in companyOptions"
                  :key="company.value"
                  :value="company.value"
                >
                  {{ company.label }}
                </option>
              </select>
            </div>
            <p v-if="errors.company_id" class="mt-2 text-sm text-red-600">
              {{ errors.company_id }}
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
              Partner is active
            </label>
          </div>

          <!-- Submit button -->
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="partnerStore.isLoading"
              class="btn btn-primary"
            >
              <span v-if="partnerStore.isLoading" class="inline-flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isEditMode ? 'Updating...' : 'Creating...' }}
              </span>
              <span v-else>
                {{ isEditMode ? 'Update Partner' : 'Create Partner' }}
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
import { usePartnerStore } from '@/stores/partners'
import { useCompanyStore } from '@/stores/companies'
import type { PartnerCreate, PartnerUpdate } from '@/types'

const router = useRouter()
const route = useRoute()
const partnerStore = usePartnerStore()
const companyStore = useCompanyStore()

const partnerId = computed(() => {
  const id = route.params.id
  return id ? parseInt(id as string) : null
})

const isEditMode = computed(() => !!partnerId.value)

const form = reactive({
  name: '',
  code: '',
  email: '',
  phone: '',
  mobile: '',
  website: '',
  tax_id: '',
  industry: '',
  is_customer: true,
  is_supplier: false,
  is_vendor: false,
  is_company: false,
  is_active: true,
  company_id: null as number | null
})

const errors = ref<Record<string, string>>({})

// Company options for dropdown
const companyOptions = computed(() => 
  companyStore.companyOptions || []
)

async function loadPartner() {
  if (partnerId.value) {
    const partner = await partnerStore.fetchPartner(partnerId.value)
    if (partner) {
      Object.assign(form, {
        name: partner.name,
        code: partner.code || '',
        email: partner.email || '',
        phone: partner.phone || '',
        mobile: partner.mobile || '',
        website: partner.website || '',
        tax_id: partner.tax_id || '',
        industry: partner.industry || '',
        is_customer: partner.is_customer,
        is_supplier: partner.is_supplier,
        is_vendor: partner.is_vendor,
        is_company: partner.is_company,
        is_active: partner.is_active,
        company_id: partner.company_id
      })
    } else {
      router.push('/partners')
    }
  }
}

function validateForm(): boolean {
  errors.value = {}

  if (!form.name.trim()) {
    errors.value.name = 'Partner name is required'
  }

  if (form.code && !/^[A-Z0-9_-]+$/i.test(form.code)) {
    errors.value.code = 'Partner code can only contain letters, numbers, underscores, and hyphens'
  }

  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.value.email = 'Please enter a valid email address'
  }

  if (!form.company_id) {
    errors.value.company_id = 'Company is required'
  }

  if (!form.is_customer && !form.is_supplier && !form.is_vendor) {
    errors.value.partner_type = 'At least one partner type must be selected'
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
    if (isEditMode.value && partnerId.value) {
      const updateData: PartnerUpdate = {
        name: form.name,
        code: form.code || undefined,
        email: form.email || undefined,
        phone: form.phone || undefined,
        mobile: form.mobile || undefined,
        website: form.website || undefined,
        tax_id: form.tax_id || undefined,
        industry: form.industry || undefined,
        is_customer: form.is_customer,
        is_supplier: form.is_supplier,
        is_vendor: form.is_vendor,
        is_company: form.is_company,
        is_active: form.is_active
      }
      await partnerStore.updatePartner(partnerId.value, updateData)
    } else {
      const createData: PartnerCreate = {
        name: form.name,
        code: form.code || undefined,
        email: form.email || undefined,
        phone: form.phone || undefined,
        mobile: form.mobile || undefined,
        website: form.website || undefined,
        tax_id: form.tax_id || undefined,
        industry: form.industry || undefined,
        is_customer: form.is_customer,
        is_supplier: form.is_supplier,
        is_vendor: form.is_vendor,
        is_company: form.is_company,
        is_active: form.is_active,
        company_id: form.company_id!
      }
      await partnerStore.createPartner(createData)
    }

    router.push('/partners')
  } catch (error) {
    console.error('Failed to save partner:', error)
  }
}

onMounted(async () => {
  partnerStore.clearError()
  
  // Load companies for dropdown
  if (companyStore.companies.length === 0) {
    await companyStore.fetchCompanies()
  }
  
  // Load partner if editing
  await loadPartner()
})
</script>