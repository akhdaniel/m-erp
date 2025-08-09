<template>
  <AppLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="mb-6">
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-4">
            <li>
              <router-link to="/inventory/products" class="text-gray-400 hover:text-gray-500">
                Products
              </router-link>
            </li>
            <li class="flex items-center">
              <svg class="flex-shrink-0 h-5 w-5 text-gray-300" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
              </svg>
              <span class="ml-4 text-sm font-medium text-gray-500">
                {{ isEditMode ? 'Edit Product' : 'New Product' }}
              </span>
            </li>
          </ol>
        </nav>
        <div class="mt-4">
          <h1 class="text-2xl font-semibold text-gray-900">
            {{ isEditMode ? 'Edit Product' : 'Create New Product' }}
          </h1>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm text-gray-600">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-md bg-red-50 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="saveProduct" class="space-y-6">
        <!-- Basic Information -->
        <div class="bg-white shadow sm:rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Basic Information</h3>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div class="col-span-2">
                <label for="name" class="block text-sm font-medium text-gray-700">
                  Product Name <span class="text-red-500">*</span>
                </label>
                <input
                  id="name"
                  v-model="formData.name"
                  type="text"
                  required
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="Enter product name"
                >
              </div>

              <div>
                <label for="sku" class="block text-sm font-medium text-gray-700">
                  SKU <span class="text-red-500">*</span>
                </label>
                <input
                  id="sku"
                  v-model="formData.sku"
                  type="text"
                  required
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="e.g., PROD-001"
                >
              </div>

              <div>
                <label for="barcode" class="block text-sm font-medium text-gray-700">
                  Barcode
                </label>
                <input
                  id="barcode"
                  v-model="formData.barcode"
                  type="text"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="Optional barcode"
                >
              </div>

              <div>
                <label for="category" class="block text-sm font-medium text-gray-700">
                  Category
                </label>
                <select
                  id="category"
                  v-model="formData.category_id"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="">Select a category</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
              </div>

              <div>
                <label for="product_type" class="block text-sm font-medium text-gray-700">
                  Product Type
                </label>
                <select
                  id="product_type"
                  v-model="formData.product_type"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="physical">Physical Product</option>
                  <option value="service">Service</option>
                  <option value="digital">Digital Product</option>
                </select>
              </div>

              <div class="col-span-2">
                <label for="description" class="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  id="description"
                  v-model="formData.description"
                  rows="3"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="Enter product description"
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Pricing -->
        <div class="bg-white shadow sm:rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Pricing</h3>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div>
                <label for="list_price" class="block text-sm font-medium text-gray-700">
                  List Price
                </label>
                <div class="mt-1 relative rounded-md shadow-sm">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">$</span>
                  </div>
                  <input
                    id="list_price"
                    v-model.number="formData.list_price"
                    type="number"
                    step="0.01"
                    min="0"
                    class="mt-1 block w-full pl-7 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    placeholder="0.00"
                  >
                </div>
              </div>

              <div>
                <label for="cost_price" class="block text-sm font-medium text-gray-700">
                  Cost Price
                </label>
                <div class="mt-1 relative rounded-md shadow-sm">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">$</span>
                  </div>
                  <input
                    id="cost_price"
                    v-model.number="formData.cost_price"
                    type="number"
                    step="0.01"
                    min="0"
                    class="mt-1 block w-full pl-7 rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    placeholder="0.00"
                  >
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">
                  Margin
                </label>
                <div class="mt-1 text-sm text-gray-900 py-2">
                  {{ calculateMargin() }}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Inventory Settings -->
        <div class="bg-white shadow sm:rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium leading-6 text-gray-900 mb-4">Inventory Settings</h3>
            
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div>
                <label for="reorder_point" class="block text-sm font-medium text-gray-700">
                  Reorder Point
                </label>
                <input
                  id="reorder_point"
                  v-model.number="formData.reorder_point"
                  type="number"
                  min="0"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="0"
                >
              </div>

              <div>
                <label for="reorder_quantity" class="block text-sm font-medium text-gray-700">
                  Reorder Quantity
                </label>
                <input
                  id="reorder_quantity"
                  v-model.number="formData.reorder_quantity"
                  type="number"
                  min="0"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="0"
                >
              </div>

              <div>
                <label for="unit_of_measure" class="block text-sm font-medium text-gray-700">
                  Unit of Measure
                </label>
                <input
                  id="unit_of_measure"
                  v-model="formData.unit_of_measure"
                  type="text"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  placeholder="e.g., pcs, kg, m"
                >
              </div>
            </div>

            <div class="mt-6">
              <div class="flex items-center">
                <input
                  id="track_inventory"
                  v-model="formData.track_inventory"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                >
                <label for="track_inventory" class="ml-2 block text-sm text-gray-900">
                  Track inventory for this product
                </label>
              </div>
            </div>

            <div class="mt-4">
              <div class="flex items-center">
                <input
                  id="is_active"
                  v-model="formData.is_active"
                  type="checkbox"
                  class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                >
                <label for="is_active" class="ml-2 block text-sm text-gray-900">
                  Product is active
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="cancel"
            class="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <svg v-if="saving" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ saving ? 'Saving...' : (isEditMode ? 'Update Product' : 'Create Product') }}
          </button>
        </div>
      </form>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const router = useRouter()

// State
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const categories = ref<any[]>([])

// Form data
const formData = ref({
  name: '',
  sku: '',
  barcode: '',
  description: '',
  category_id: '',
  product_type: 'physical',
  list_price: null as number | null,
  cost_price: null as number | null,
  reorder_point: null as number | null,
  reorder_quantity: null as number | null,
  unit_of_measure: '',
  track_inventory: true,
  is_active: true,
  company_id: 1
})

// Computed
const productId = computed(() => route.params.id as string)
const isEditMode = computed(() => productId.value && productId.value !== 'new')

// API base URL
const INVENTORY_API = 'http://localhost:8005/api/v1'

// Load product for editing
async function loadProduct() {
  if (!isEditMode.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${INVENTORY_API}/products/${productId.value}`)
    if (!response.ok) throw new Error('Failed to load product')
    
    const product = await response.json()
    
    // Map the product data to form
    formData.value = {
      name: product.name || '',
      sku: product.sku || '',
      barcode: product.barcode || '',
      description: product.description || '',
      category_id: product.category_id || '',
      product_type: product.product_type || 'physical',
      list_price: product.list_price,
      cost_price: product.cost_price,
      reorder_point: product.reorder_point,
      reorder_quantity: product.reorder_quantity,
      unit_of_measure: product.unit_of_measure || '',
      track_inventory: product.track_inventory !== false,
      is_active: product.is_active !== false,
      company_id: product.company_id || 1
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load product'
    console.error('Error loading product:', err)
  } finally {
    loading.value = false
  }
}

// Fetch categories
async function fetchCategories() {
  try {
    const response = await fetch(`${INVENTORY_API}/products/categories`)
    if (!response.ok) throw new Error('Failed to fetch categories')
    
    const data = await response.json()
    categories.value = data.items || []
  } catch (err) {
    console.error('Error fetching categories:', err)
  }
}

// Save product
async function saveProduct() {
  saving.value = true
  error.value = ''
  
  try {
    const url = isEditMode.value
      ? `${INVENTORY_API}/products/${productId.value}`
      : `${INVENTORY_API}/products`
    
    const method = isEditMode.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to save product')
    }
    
    // Success - navigate back to list
    router.push('/inventory/products')
  } catch (err: any) {
    error.value = err.message || 'Failed to save product'
    console.error('Error saving product:', err)
  } finally {
    saving.value = false
  }
}

// Calculate margin
function calculateMargin(): string {
  const list = formData.value.list_price
  const cost = formData.value.cost_price
  
  if (!list || !cost || cost === 0) return '0.00'
  
  const margin = ((list - cost) / list) * 100
  return margin.toFixed(2)
}

// Cancel
function cancel() {
  router.push('/inventory/products')
}

// Initialize
onMounted(() => {
  fetchCategories()
  if (isEditMode.value) {
    loadProduct()
  }
})
</script>