<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white shadow rounded-lg">
      <!-- Form Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold text-gray-900">
            Evaluate Supplier: {{ supplier?.name }}
          </h2>
          <div v-if="supplier?.performance_rating" class="flex items-center">
            <StarIcon v-for="n in 5" :key="n" class="h-5 w-5 flex-shrink-0" :class="n <= Math.round(supplier.performance_rating) ? 'text-yellow-400' : 'text-gray-300'" />
            <span class="ml-2 text-sm text-gray-500">{{ supplier.performance_rating.toFixed(1) }} / 5.0</span>
          </div>
        </div>
      </div>

      <!-- Form Content -->
      <form @submit.prevent="handleSubmit" class="divide-y divide-gray-200">
        <!-- Evaluation Criteria -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Evaluation Criteria</h3>
          <div class="space-y-6">
            <!-- Delivery Performance -->
            <div>
              <div class="flex justify-between">
                <label class="block text-sm font-medium text-gray-700">
                  Delivery Performance
                </label>
                <span class="text-sm text-gray-500">{{ evaluation.delivery_rating || 0 }} / 5</span>
              </div>
              <div class="mt-2 flex items-center">
                <StarIcon 
                  v-for="n in 5" 
                  :key="n" 
                  class="h-8 w-8 flex-shrink-0 cursor-pointer" 
                  :class="n <= (evaluation.delivery_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                  @click="setRating('delivery_rating', n)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">Rate the supplier's ability to deliver on time</p>
            </div>

            <!-- Product Quality -->
            <div>
              <div class="flex justify-between">
                <label class="block text-sm font-medium text-gray-700">
                  Product Quality
                </label>
                <span class="text-sm text-gray-500">{{ evaluation.quality_rating || 0 }} / 5</span>
              </div>
              <div class="mt-2 flex items-center">
                <StarIcon 
                  v-for="n in 5" 
                  :key="n" 
                  class="h-8 w-8 flex-shrink-0 cursor-pointer" 
                  :class="n <= (evaluation.quality_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                  @click="setRating('quality_rating', n)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">Rate the quality of products or services provided</p>
            </div>

            <!-- Price Competitiveness -->
            <div>
              <div class="flex justify-between">
                <label class="block text-sm font-medium text-gray-700">
                  Price Competitiveness
                </label>
                <span class="text-sm text-gray-500">{{ evaluation.price_rating || 0 }} / 5</span>
              </div>
              <div class="mt-2 flex items-center">
                <StarIcon 
                  v-for="n in 5" 
                  :key="n" 
                  class="h-8 w-8 flex-shrink-0 cursor-pointer" 
                  :class="n <= (evaluation.price_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                  @click="setRating('price_rating', n)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">Rate the competitiveness of the supplier's pricing</p>
            </div>

            <!-- Communication -->
            <div>
              <div class="flex justify-between">
                <label class="block text-sm font-medium text-gray-700">
                  Communication
                </label>
                <span class="text-sm text-gray-500">{{ evaluation.communication_rating || 0 }} / 5</span>
              </div>
              <div class="mt-2 flex items-center">
                <StarIcon 
                  v-for="n in 5" 
                  :key="n" 
                  class="h-8 w-8 flex-shrink-0 cursor-pointer" 
                  :class="n <= (evaluation.communication_rating || 0) ? 'text-yellow-400' : 'text-gray-300'"
                  @click="setRating('communication_rating', n)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">Rate the supplier's responsiveness and communication</p>
            </div>
          </div>
        </div>

        <!-- Comments Section -->
        <div class="px-6 py-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Additional Comments</h3>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Comments
            </label>
            <textarea
              v-model="evaluation.comments"
              rows="4"
              class="input"
              placeholder="Enter any additional comments about this supplier's performance..."
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
              type="submit"
              :disabled="isLoading || !isFormValid"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <span v-if="isLoading">Submitting...</span>
              <span v-else>Submit Evaluation</span>
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
import { 
  ExclamationCircleIcon,
  StarIcon
} from '@heroicons/vue/24/outline'

// Stores and router
const purchasingStore = usePurchasingStore()
const route = useRoute()
const router = useRouter()

// Local state
const isLoading = ref(false)
const error = ref(null)
const evaluation = ref({
  delivery_rating: 0,
  quality_rating: 0,
  price_rating: 0,
  communication_rating: 0,
  comments: ''
})

// Computed properties
const supplier = computed(() => purchasingStore.currentSupplier)

const isFormValid = computed(() => {
  return supplier.value && (
    evaluation.value.delivery_rating > 0 ||
    evaluation.value.quality_rating > 0 ||
    evaluation.value.price_rating > 0 ||
    evaluation.value.communication_rating > 0 ||
    evaluation.value.comments
  )
})

// Methods
const setRating = (field, value) => {
  evaluation.value[field] = value
}

const handleSubmit = async () => {
  if (!isFormValid.value) {
    error.value = 'Please provide at least one rating or comment.'
    return
  }

  try {
    isLoading.value = true
    error.value = null

    // Submit evaluation
    const result = await purchasingStore.evaluateSupplier(
      parseInt(route.params.id),
      evaluation.value
    )

    if (result) {
      // Show success message
      alert(`Supplier evaluation submitted successfully! New rating: ${result.new_rating.toFixed(1)}`)
      // Navigate back to suppliers list
      router.push({ name: 'purchasing-suppliers' })
    }
  } catch (err) {
    error.value = err.message || 'Failed to submit supplier evaluation'
    console.error('Error submitting supplier evaluation:', err)
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
    // Load supplier for evaluation
    if (route.params.id) {
      await purchasingStore.fetchSupplier(parseInt(route.params.id))
    }
  } catch (err) {
    error.value = 'Failed to load supplier data'
    console.error('Error loading supplier data:', err)
  }
})
</script>
</content>