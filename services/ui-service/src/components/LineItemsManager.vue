<template>
  <div class="space-y-4">
    <!-- Header with Add Button -->
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-medium text-gray-900">
        {{ title || 'Line Items' }}
      </h3>
      <button
        type="button"
        @click="showAddModal = true"
        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <PlusIcon class="-ml-0.5 mr-2 h-4 w-4" />
        Add Item
      </button>
    </div>

    <!-- Line Items Table -->
    <div v-if="items.length > 0" class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
              Product
            </th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              SKU
            </th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              Quantity
            </th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              Unit Price
            </th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              Discount %
            </th>
            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
              Total
            </th>
            <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="(item, index) in items" :key="item.id || index">
            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
              {{ item.item_name || item.product_name || item.name }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
              {{ item.item_code || item.product_sku || item.sku }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
              {{ item.quantity }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
              {{ formatCurrency(item.unit_price) }}
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
              {{ item.discount_percentage || 0 }}%
            </td>
            <td class="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">
              {{ formatCurrency(calculateLineTotal(item)) }}
            </td>
            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
              <button
                type="button"
                @click="editItem(index)"
                class="text-primary-600 hover:text-primary-900 mr-2"
              >
                Edit
              </button>
              <button
                type="button"
                @click="removeItem(index)"
                class="text-red-600 hover:text-red-900"
              >
                Remove
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No items added</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by adding a product to this {{ entityType }}.</p>
      <div class="mt-6">
        <button
          type="button"
          @click="showAddModal = true"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <PlusIcon class="-ml-1 mr-1 h-5 w-5" />
          Add First Item
        </button>
      </div>
    </div>

    <!-- Totals Section -->
    <div v-if="items.length > 0" class="bg-white rounded-lg p-4">
      <div class="space-y-2">
        <div class="flex justify-between text-sm">
          <span>Subtotal:</span>
          <span class="font-medium">{{ formatCurrency(subtotal) }}</span>
        </div>
        <div v-if="totalDiscount > 0" class="flex justify-between text-sm">
          <span class="text-gray-600">Discount:</span>
          <span class="font-medium text-red-600">-{{ formatCurrency(totalDiscount) }}</span>
        </div>
        <div v-if="taxAmount > 0" class="flex justify-between text-sm">
          <span class="text-gray-600">Tax ({{ taxRate }}%):</span>
          <span class="font-medium">{{ formatCurrency(taxAmount) }}</span>
        </div>
        <div class="flex justify-between text-base font-semibold pt-2 border-t border-gray-200">
          <span>Total:</span>
          <span>{{ formatCurrency(total) }}</span>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <TransitionRoot as="template" :show="showAddModal">
      <Dialog as="div" class="relative z-50" @close="closeModal">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mt-3 text-center sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-lg font-semibold leading-6 text-gray-900">
                      {{ editingIndex !== null ? 'Edit Item' : 'Add Item' }}
                    </DialogTitle>
                    <div class="mt-4 space-y-4">
                      <!-- Product Selection -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Product</label>
                        <div class="mt-1 relative">
                          <input
                            v-model="productSearch"
                            @input="searchProducts"
                            @focus="showProductDropdown = true"
                            type="text"
                            class="block w-full rounded-md xerp_input focus:ring-primary-500 sm:text-sm"
                            placeholder="Search for a product..."
                          />
                          <!-- Product Dropdown -->
                          <div v-if="showProductDropdown && searchResults.length > 0" class="absolute z-10 mt-1 w-full rounded-md bg-white shadow-lg">
                            <ul class="max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                              <li
                                v-for="product in searchResults"
                                :key="product.id"
                                @click="selectProduct(product)"
                                class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-50"
                              >
                                <div>
                                  <span class="font-medium">{{ product.name }}</span>
                                  <span class="text-gray-500 ml-2">{{ product.sku }}</span>
                                </div>
                                <span class="text-sm text-gray-500">
                                  {{ formatCurrency(product.price) }} / {{ product.unit }}
                                </span>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>

                      <!-- Quantity -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Quantity</label>
                        <input
                          v-model.number="currentItem.quantity"
                          type="number"
                          min="1"
                          step="1"
                          class="mt-1 block w-full rounded-md xerp_input focus:ring-primary-500 sm:text-sm"
                        />
                      </div>

                      <!-- Unit Price -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Unit Price</label>
                        <input
                          v-model.number="currentItem.unit_price"
                          type="number"
                          min="0"
                          step="0.01"
                          class="mt-1 block w-full rounded-md xerp_input focus:ring-primary-500 sm:text-sm"
                        />
                      </div>

                      <!-- Discount -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Discount %</label>
                        <input
                          v-model.number="currentItem.discount_percentage"
                          type="number"
                          min="0"
                          max="100"
                          step="0.01"
                          class="mt-1 block w-full rounded-md xerp_input focus:ring-primary-500 sm:text-sm"
                        />
                      </div>

                      <!-- Line Total Preview -->
                      <div class="bg-gray-50 p-3 rounded-md">
                        <div class="flex justify-between text-sm">
                          <span>Line Total:</span>
                          <span class="font-medium">{{ formatCurrency(calculateLineTotal(currentItem)) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    @click="saveItem"
                    :disabled="!currentItem.product_id || !currentItem.quantity"
                    class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 disabled:opacity-50 disabled:cursor-not-allowed sm:col-start-2"
                  >
                    {{ editingIndex !== null ? 'Update' : 'Add' }}
                  </button>
                  <button
                    type="button"
                    @click="closeModal"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  >
                    Cancel
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { PlusIcon } from '@heroicons/vue/24/outline'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: 'Line Items'
  },
  entityType: {
    type: String,
    default: 'document'
  },
  taxRate: {
    type: Number,
    default: 0
  },
  productApiUrl: {
    type: String,
    default: import.meta.env.VITE_SALES_API || '/api/v1/products'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'totalsChanged'])

// Local state
const items = ref(props.modelValue || [])
const showAddModal = ref(false)
const editingIndex = ref(null)
const currentItem = ref({
  product_id: null,
  product_name: '',
  product_sku: '',
  quantity: 1,
  unit_price: 0,
  discount_percentage: 0
})

// Initialize items with modelValue if provided
console.log('LineItemsManager mounted with modelValue:', props.modelValue)
if (props.modelValue && Array.isArray(props.modelValue) && props.modelValue.length > 0) {
  items.value = [...props.modelValue]
  console.log('Initialized items with modelValue:', items.value)
} else if (props.modelValue) {
  console.log('modelValue is not an array or is empty:', props.modelValue)
}

// Product search
const productSearch = ref('')
const searchResults = ref([])
const showProductDropdown = ref(false)
const searchTimeout = ref(null)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  console.log('LineItemsManager modelValue changed:', newValue)
  if (newValue && Array.isArray(newValue)) {
    items.value = [...newValue]
    console.log('Updated items with new value:', items.value)
  } else {
    items.value = []
    console.log('Set items to empty array')
  }
}, { deep: true })

// Computed values
const subtotal = computed(() => {
  return items.value.reduce((sum, item) => {
    const lineTotal = item.quantity * item.unit_price
    return sum + lineTotal
  }, 0)
})

const totalDiscount = computed(() => {
  return items.value.reduce((sum, item) => {
    const lineTotal = item.quantity * item.unit_price
    const discount = lineTotal * (item.discount_percentage || 0) / 100
    return sum + discount
  }, 0)
})

const taxAmount = computed(() => {
  const taxableAmount = subtotal.value - totalDiscount.value
  return taxableAmount * props.taxRate / 100
})

const total = computed(() => {
  return subtotal.value - totalDiscount.value + taxAmount.value
})

// Methods
const searchProducts = async () => {
  clearTimeout(searchTimeout.value)
  
  if (productSearch.value.length < 2) {
    searchResults.value = []
    return
  }

  searchTimeout.value = setTimeout(async () => {
    try {
      const response = await fetch(`${props.productApiUrl}/autocomplete?q=${encodeURIComponent(productSearch.value)}`)
      if (response.ok) {
        searchResults.value = await response.json()
      }
    } catch (error) {
      console.error('Error searching products:', error)
      searchResults.value = []
    }
  }, 300)
}

const selectProduct = (product) => {
  currentItem.value.product_id = product.id
  currentItem.value.product_name = product.name
  currentItem.value.product_sku = product.sku
  currentItem.value.unit_price = product.price || 0
  productSearch.value = product.display || product.name
  showProductDropdown.value = false
}

const calculateLineTotal = (item) => {
  const lineTotal = item.quantity * item.unit_price
  const discount = lineTotal * (item.discount_percentage || 0) / 100
  return lineTotal - discount
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0)
}

const editItem = (index) => {
  editingIndex.value = index
  const item = items.value[index]
  currentItem.value = {
    product_id: item.product_id,
    product_name: item.item_name || item.product_name,
    product_sku: item.item_code || item.product_sku,
    quantity: item.quantity,
    unit_price: item.unit_price,
    discount_percentage: item.discount_percentage || 0
  }
  productSearch.value = currentItem.value.product_name
  showAddModal.value = true
}

const removeItem = (index) => {
  items.value.splice(index, 1)
  updateParent()
}

const saveItem = () => {
  if (!currentItem.value.product_id || !currentItem.value.quantity) {
    return
  }

  // Format the item for the API
  const formattedItem = {
    product_id: currentItem.value.product_id,
    item_name: currentItem.value.product_name,
    item_code: currentItem.value.product_sku,
    quantity: currentItem.value.quantity,
    unit_price: currentItem.value.unit_price,
    discount_percentage: currentItem.value.discount_percentage || 0,
    description: `${currentItem.value.product_sku} - ${currentItem.value.product_name}`
  }

  if (editingIndex.value !== null) {
    items.value[editingIndex.value] = formattedItem
  } else {
    items.value.push(formattedItem)
  }

  updateParent()
  closeModal()
}

const closeModal = () => {
  showAddModal.value = false
  editingIndex.value = null
  currentItem.value = {
    product_id: null,
    product_name: '',
    product_sku: '',
    quantity: 1,
    unit_price: 0,
    discount_percentage: 0
  }
  productSearch.value = ''
  searchResults.value = []
  showProductDropdown.value = false
}

const updateParent = () => {
  emit('update:modelValue', items.value)
  emit('totalsChanged', {
    subtotal: subtotal.value,
    discount: totalDiscount.value,
    tax: taxAmount.value,
    total: total.value
  })
}

// Close dropdown on click outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showProductDropdown.value = false
  }
}

// Add event listener on mount
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>