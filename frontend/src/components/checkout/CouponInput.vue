<template>
  <div class="card">
    <div class="card-body">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Discount Code</h3>

      <!-- Coupon Applied State -->
      <div v-if="hasCoupon" class="space-y-3">
        <div class="flex items-center justify-between p-3 bg-success-50 border border-success-200 rounded">
          <div class="flex items-center gap-2">
            <CheckCircleIcon class="w-5 h-5 text-success-600" />
            <div>
              <p class="text-sm font-medium text-success-900">
                Coupon Applied: {{ couponData.code }}
              </p>
              <p class="text-xs text-success-700">
                You saved ${{ parseFloat(couponDiscount).toFixed(2) }}
              </p>
            </div>
          </div>

          <button
            @click="handleRemoveCoupon"
            class="p-1 text-success-600 hover:text-success-700 transition-colors"
            title="Remove coupon"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Coupon Input Form -->
      <form v-else @submit.prevent="handleApplyCoupon" class="space-y-3">
        <div>
          <input
            v-model="couponCode"
            type="text"
            class="form-input"
            placeholder="Enter coupon code"
            :disabled="isValidating"
          />
        </div>

        <button
          type="submit"
          :disabled="!couponCode.trim() || isValidating"
          class="btn btn-primary w-full"
        >
          <span v-if="isValidating" class="loading-spinner mr-2"></span>
          {{ isValidating ? 'Validating...' : 'Apply Coupon' }}
        </button>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-3 p-3 bg-error-50 border border-error-200 rounded">
        <p class="text-sm text-error-700">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import { CheckCircleIcon, XMarkIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  orderAmount: {
    type: Number,
    required: true
  }
})

const checkoutStore = useCheckoutStore()

const couponCode = ref('')
const isValidating = ref(false)
const errorMessage = ref('')

const hasCoupon = computed(() => checkoutStore.hasCoupon)
const couponData = computed(() => checkoutStore.couponData)
const couponDiscount = computed(() => checkoutStore.couponDiscount)

// Watch for changes in checkout store's coupon code
watch(
  () => checkoutStore.couponCode,
  (newCode) => {
    if (!newCode) {
      couponCode.value = ''
    }
  }
)

const handleApplyCoupon = async () => {
  if (!couponCode.value.trim()) return

  errorMessage.value = ''
  isValidating.value = true

  try {
    await checkoutStore.validateCoupon(couponCode.value.trim(), props.orderAmount)
    couponCode.value = ''
  } catch (error) {
    // Error handling is done in the store with toast
    errorMessage.value = error.response?.data?.detail || 'Invalid coupon code'
  } finally {
    isValidating.value = false
  }
}

const handleRemoveCoupon = () => {
  checkoutStore.clearCoupon()
  couponCode.value = ''
  errorMessage.value = ''
}
</script>
