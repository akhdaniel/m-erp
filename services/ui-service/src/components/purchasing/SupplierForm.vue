<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white shadow rounded-lg">
      <!-- Form Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ isEditMode ? 'Edit Supplier' : 'New Supplier' }}
          </h2>
          <div v-if="supplier?.status" class="flex items-center space-x-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass(supplier.status)">
              {{ supplier.status }}
            </span>
          </div>
        </div>
      </div>

      <!-- Form Content -->
      <form @submit.prevent="handleSubmit" class="divide-y divide-gray-200">
        <!-- Basic Information Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Supplier Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Supplier Code <span class="text-red-500">*</span>
              </label>
              <input
                v-model="supplier.code"
                type="text"
                required
                :disabled="isEditMode"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="e.g., SUP001"
              />
            </div>

            <!-- Supplier Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Supplier Name <span class="text-red-500">*</span>
              </label>
              <input
                v-model="supplier.name"
                type="text"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="Enter supplier company name"
              />
            </div>

            <!-- Category -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                v-model="supplier.category"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              >
                <option value="general">General</option>
                <option value="preferred">Preferred</option>
                <option value="strategic">Strategic</option>
              </select>
            </div>

            <!-- Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                v-model="supplier.is_active"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              >
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Contact Information Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Contact Information</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Contact Person -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Contact Person
              </label>
              <input
                v-model="supplier.contact_person"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="Primary contact name"
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                v-model="supplier.email"
                type="email"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="supplier@example.com"
              />
            </div>

            <!-- Phone -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                v-model="supplier.phone"
                type="tel"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="+1-555-0100"
              />
            </div>

            <!-- Website -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Website
              </label>
              <input
                v-model="supplier.website"
                type="url"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="https://www.supplier.com"
              />
            </div>
          </div>
        </div>

        <!-- Address Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Address</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Street Address -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Street Address
              </label>
              <input
                v-model="supplier.address"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="123 Main Street"
              />
            </div>

            <!-- City -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                v-model="supplier.city"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="New York"
              />
            </div>

            <!-- State/Province -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                State/Province
              </label>
              <input
                v-model="supplier.state"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="NY"
              />
            </div>

            <!-- Postal Code -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Postal Code
              </label>
              <input
                v-model="supplier.postal_code"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="10001"
              />
            </div>

            <!-- Country -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <input
                v-model="supplier.country"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="USA"
                value="USA"
              />
            </div>
          </div>
        </div>

        <!-- Business Terms Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Business Terms</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Payment Terms (Days) -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms (Days)
              </label>
              <input
                v-model.number="supplier.payment_terms_days"
                type="number"
                min="0"
                max="365"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="30"
              />
            </div>

            <!-- Currency -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Currency
              </label>
              <select
                v-model="supplier.currency_code"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              >
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
              </select>
            </div>

            <!-- Tax ID -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Tax ID
              </label>
              <input
                v-model="supplier.tax_id"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="Tax identification number"
              />
            </div>

            <!-- Initial Rating -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Initial Rating
              </label>
              <input
                v-model.number="supplier.rating"
                type="number"
                min="1"
                max="5"
                step="0.5"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="3.0"
              />
            </div>
          </div>
        </div>

        <!-- Form Actions -->
        <div class="px-6 py-4 bg-gray-50 flex justify-between">
          <div>
            <button
              type="button"
              @click="handleCancel"
              class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
          </div>
          <div class="flex space-x-3">
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="isLoading">Saving...</span>
              <span v-else>Save Supplier</span>
            </button>
          </div>
        </div>
      </form>

      <!-- Error Message -->
      <div v-if="error" class="px-6 py-4 bg-red-50 border-t border-red-200">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePurchasingStore } from '@/stores/purchasing'
import { ExclamationCircleIcon } from '@heroicons/vue/24/outline'

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const isLoading = ref(false)
const error = ref(null)

// Computed properties
const supplier = computed(() => purchasingStore.currentSupplier || {})
const isEditMode = computed(() => !!route.params.id)

const isFormValid = computed(() => {
  return supplier.value.code && supplier.value.name
})

// Methods
const getStatusBadgeClass = (status) => {
  const statusClasses = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    suspended: 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields.'
    return
  }

  try {
    isLoading.value = true
    error.value = null

    let result
    if (isEditMode.value) {
      // Update existing supplier
      result = await purchasingStore.updateSupplier(
        parseInt(route.params.id),
        supplier.value
      )
    } else {
      // Create new supplier
      result = await purchasingStore.createSupplier(supplier.value)
    }

    if (result) {
      // Show success message and navigate back to suppliers list
      alert(`Supplier ${isEditMode.value ? 'updated' : 'created'} successfully!`)
      router.push({ name: 'purchasing-suppliers' })
    }
  } catch (err) {
    error.value = err.message || 'Failed to save supplier'
    console.error('Error saving supplier:', err)
  } finally {
    isLoading.value = false
  }
}

const handleCancel = () => {
  router.push({ name: 'purchasing-suppliers' })
}

// Lifecycle hooks
onMounted(async () => {
  try {
    // Load supplier if editing
    if (isEditMode.value) {
      await purchasingStore.fetchSupplier(parseInt(route.params.id))
    } else {
      // Initialize new supplier
      purchasingStore.clearCurrentSupplier()
      // Set default values
      purchasingStore.currentSupplier = {
        code: '',
        name: '',
        category: 'general',
        is_active: true,
        payment_terms_days: 30,
        currency_code: 'USD',
        rating: 3.0,
        country: 'USA'
      }
    }
  } catch (err) {
    error.value = 'Failed to load data'
    console.error('Error loading data:', err)
  }
})
</script>
</content>