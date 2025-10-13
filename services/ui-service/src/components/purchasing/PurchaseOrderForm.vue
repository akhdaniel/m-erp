<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white shadow rounded-lg">
      <!-- Form Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            {{ isEditMode ? 'Edit Purchase Order' : 'New Purchase Order' }}
          </h2>
          <div class="flex items-center space-x-2">
            <span v-if="purchaseOrder?.status" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getStatusBadgeClass(purchaseOrder.status)">
              {{ purchaseOrder.status }}
            </span>
            <span v-if="purchaseOrder?.approval_status" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize" :class="getApprovalBadgeClass(purchaseOrder.approval_status)">
              {{ purchaseOrder.approval_status.replace('_', ' ') }}
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
            <!-- Supplier Selection -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Supplier <span class="text-red-500">*</span>
              </label>
              <select
                v-model="purchaseOrder.supplier_id"
                required
                :disabled="isEditMode"
                class="input"
              >
                <option value="">Select a supplier</option>
                <option
                  v-for="supplier in activeSuppliers"
                  :key="supplier.id"
                  :value="supplier.id"
                >
                  {{ supplier.name }} ({{ supplier.code }})
                </option>
              </select>
              <p v-if="!isEditMode" class="mt-1 text-xs text-gray-500">
                Select a supplier to load their default payment terms and currency
              </p>
            </div>

            <!-- Order Date -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Order Date <span class="text-red-500">*</span>
              </label>
              <input
                v-model="purchaseOrder.order_date"
                type="date"
                required
                class="input"
              />
            </div>

            <!-- Expected Delivery -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Expected Delivery
              </label>
              <input
                v-model="purchaseOrder.expected_delivery"
                type="date"
                class="input"
              />
            </div>

            <!-- Currency -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Currency
              </label>
              <select
                v-model="purchaseOrder.currency_code"
                class="input"
              >
                <option value="USD">USD - US Dollar</option>
                <option value="EUR">EUR - Euro</option>
                <option value="GBP">GBP - British Pound</option>
              </select>
            </div>

            <!-- Payment Terms -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms
              </label>
              <select
                v-model="purchaseOrder.payment_terms"
                class="input"
              >
                <option value="Net 30">Net 30</option>
                <option value="Net 60">Net 60</option>
                <option value="COD">COD - Cash on Delivery</option>
                <option value="Prepaid">Prepaid</option>
              </select>
            </div>

            <!-- PO Number (Read-only in edit mode) -->
            <div v-if="isEditMode && purchaseOrder.po_number">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                PO Number
              </label>
              <input
                v-model="purchaseOrder.po_number"
                type="text"
                disabled
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-50 sm:text-sm"
              />
            </div>
          </div>
        </div>

        <!-- Line Items Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Line Items</h3>
          <LineItemsManager
            v-model="purchaseOrder.items"
            title="Purchase Order Items"
            entity-type="purchase order"
            :product-api-url="productApiUrl"
            :tax-rate="10"
            @totals-changed="handleTotalsChanged"
          />
        </div>

        <!-- Addresses Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Addresses</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Shipping Address -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Shipping Address
              </label>
              <textarea
                v-model="purchaseOrder.shipping_address"
                rows="3"
                class="input"
                placeholder="Enter shipping address"
              ></textarea>
            </div>

            <!-- Billing Address -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Billing Address
              </label>
              <textarea
                v-model="purchaseOrder.billing_address"
                rows="3"
                class="input"
                placeholder="Enter billing address"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Notes Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Information</h3>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              v-model="purchaseOrder.notes"
              rows="4"
              class="input"
              placeholder="Enter any additional notes or instructions for this purchase order"
            ></textarea>
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
              v-if="!isEditMode || purchaseOrder.status === 'draft'"
              type="button"
              @click="handleSaveDraft"
              :disabled="isLoading"
              class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="isLoading && saveAction === 'draft'">Saving...</span>
              <span v-else>Save as Draft</span>
            </button>
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="isLoading && saveAction === 'submit'">Submitting...</span>
              <span v-else-if="isEditMode && purchaseOrder.status !== 'draft'">Update Purchase Order</span>
              <span v-else>Submit for Approval</span>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePurchasingStore } from '@/stores/purchasing'
import LineItemsManager from '@/components/LineItemsManager.vue'
import { ExclamationCircleIcon } from '@heroicons/vue/24/outline'

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const isLoading = ref(false)
const error = ref(null)
const saveAction = ref('') // 'draft' or 'submit'
const productApiUrl = ref(import.meta.env.VITE_INVENTORY_API || 'http://localhost:8005/api/v1')

// Computed properties
const purchaseOrder = computed(() => purchasingStore.currentPurchaseOrder || {})
const activeSuppliers = computed(() => purchasingStore.activeSuppliers)
const isEditMode = computed(() => !!route.params.id)

const isFormValid = computed(() => {
  return purchaseOrder.value.supplier_id && 
         purchaseOrder.value.order_date && 
         purchaseOrder.value.items && 
         purchaseOrder.value.items.length > 0
})

// Methods
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

const handleTotalsChanged = (totals) => {
  // Update the purchase order total based on line items
  if (purchaseOrder.value) {
    purchaseOrder.value.total_amount = totals.total
  }
}

const handleSaveDraft = async () => {
  saveAction.value = 'draft'
  await handleSubmit(true)
}

const handleSubmit = async (saveAsDraft = false) => {
  if (!isFormValid.value) {
    error.value = 'Please fill in all required fields and add at least one line item.'
    return
  }

  try {
    isLoading.value = true
    error.value = null

    let result
    if (isEditMode.value) {
      // Update existing purchase order
      result = await purchasingStore.updatePurchaseOrder(
        parseInt(route.params.id),
        purchaseOrder.value
      )
    } else {
      // Create new purchase order
      result = await purchasingStore.createPurchaseOrder(purchaseOrder.value)
    }

    if (result) {
      if (saveAsDraft) {
        // Show success message and stay on page
        alert('Purchase order saved as draft successfully!')
        // Reload the purchase order to get updated data
        if (result.id) {
          await purchasingStore.fetchPurchaseOrder(result.id)
        }
      } else {
        // Submit for approval or update
        if (!isEditMode.value) {
          // Submit new PO for approval
          await purchasingStore.submitPurchaseOrderForApproval(result.id)
          alert('Purchase order submitted for approval successfully!')
        }
        // Navigate back to purchase orders list
        router.push({ name: 'purchasing-orders' })
      }
    }
  } catch (err) {
    error.value = err.message || 'Failed to save purchase order'
    console.error('Error saving purchase order:', err)
  } finally {
    isLoading.value = false
    saveAction.value = ''
  }
}

const handleCancel = () => {
  router.push({ name: 'purchasing-orders' })
}

// Watch for supplier changes to set default values
watch(() => purchaseOrder.value.supplier_id, (newSupplierId) => {
  if (newSupplierId && !isEditMode.value) {
    const supplier = activeSuppliers.value.find(s => s.id === newSupplierId)
    if (supplier) {
      if (!purchaseOrder.value.currency_code) {
        purchaseOrder.value.currency_code = supplier.currency_code || 'USD'
      }
      if (!purchaseOrder.value.payment_terms) {
        purchaseOrder.value.payment_terms = supplier.payment_terms || 'Net 30'
      }
    }
  }
})

// Lifecycle hooks
onMounted(async () => {
  try {
    // Load suppliers
    if (purchasingStore.suppliers.length === 0) {
      await purchasingStore.fetchSuppliers()
    }

    // Load purchase order if editing
    if (isEditMode.value) {
      await purchasingStore.fetchPurchaseOrder(parseInt(route.params.id))
    } else {
      // Initialize new purchase order
      purchasingStore.initializeNewPurchaseOrder()
    }
  } catch (err) {
    error.value = 'Failed to load data'
    console.error('Error loading data:', err)
  }
})
</script>