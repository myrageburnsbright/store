<template>
  <div class="card">
    <div class="card-header">
      <h3 class="text-lg font-semibold text-gray-900">Order Summary</h3>
    </div>
    <div class="card-body space-y-4">
      <!-- Order Pricing -->
      <div class="space-y-3 text-sm">
        <div class="flex justify-between text-gray-600">
          <span>Subtotal</span>
          <span>${{ parseFloat(order.subtotal).toFixed(2) }}</span>
        </div>

        <div v-if="order.discount_amount > 0" class="flex justify-between text-success-600">
          <span>Product Discounts</span>
          <span>-${{ parseFloat(order.discount_amount).toFixed(2) }}</span>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200"></div>

        <!-- Coupon Input -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700">
            Have a coupon code?
          </label>

          <!-- Applied Coupon Display -->
          <div v-if="appliedCoupon" class="flex items-center justify-between p-3 bg-success-50 border border-success-200 rounded-lg">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p class="text-sm font-medium text-success-900">{{ appliedCoupon.code }}</p>
                <p class="text-xs text-success-700">-${{ parseFloat(appliedCoupon.discount_amount).toFixed(2) }} discount</p>
              </div>
            </div>
            <button
              @click="removeCoupon"
              class="text-success-700 hover:text-success-900 transition-colors"
              :disabled="isValidatingCoupon"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Coupon Input Form -->
          <div v-else class="flex gap-2">
            <input
              v-model="couponCode"
              type="text"
              placeholder="Enter coupon code"
              class="form-input flex-1 text-sm"
              :disabled="isValidatingCoupon"
              @keyup.enter="applyCoupon"
            />
            <button
              @click="applyCoupon"
              :disabled="!couponCode || isValidatingCoupon"
              class="btn btn-sm btn-outline"
            >
              {{ isValidatingCoupon ? 'Applying...' : 'Apply' }}
            </button>
          </div>

          <!-- Error Message -->
          <p v-if="couponError" class="text-xs text-error-600">
            {{ couponError }}
          </p>
        </div>

        <!-- Coupon Discount (if applied) -->
        <div v-if="appliedCoupon" class="flex justify-between text-sm font-medium text-success-600 bg-success-50 px-3 py-2 rounded">
          <span>Coupon Discount</span>
          <span>-${{ parseFloat(appliedCoupon.discount_amount).toFixed(2) }}</span>
        </div>

        <!-- Divider -->
        <div class="border-t border-gray-200"></div>

        <div class="flex justify-between text-gray-600">
          <span>Shipping</span>
          <span>${{ parseFloat(order.shipping_cost || 0).toFixed(2) }}</span>
        </div>

        <div class="flex justify-between text-gray-600">
          <span>Tax</span>
          <span>${{ parseFloat(order.tax_amount || 0).toFixed(2) }}</span>
        </div>

        <div class="border-t border-gray-200 pt-3 flex justify-between text-lg font-bold text-gray-900">
          <span>Total</span>
          <span>${{ calculatedTotal }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="space-y-3">
        <button
          @click="handleRetryPayment"
          :disabled="isProcessingPayment"
          class="btn btn-primary w-full"
        >
          {{ isProcessingPayment ? 'Processing Payment...' : 'Retry Payment' }}
        </button>

        <button
          @click="$emit('cancel')"
          :disabled="isCancelling"
          class="btn btn-outline w-full text-error-600 hover:bg-error-50"
        >
          {{ isCancelling ? 'Cancelling...' : 'Cancel Order' }}
        </button>

        <router-link
          :to="{ name: 'orders' }"
          class="btn btn-secondary w-full"
        >
          Back to Orders
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { couponsAPI, paymentsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  isCancelling: {
    type: Boolean,
    default: false
  }
})

defineEmits(['cancel'])

const couponCode = ref('')
const appliedCoupon = ref(null)
const isValidatingCoupon = ref(false)
const couponError = ref('')
const isProcessingPayment = ref(false)

// Calculate total with applied coupon
const calculatedTotal = computed(() => {
  if (!props.order) return '0.00'

  const subtotal = parseFloat(props.order.subtotal)
  const productDiscount = parseFloat(props.order.discount_amount || 0)
  const couponDiscount = appliedCoupon.value ? parseFloat(appliedCoupon.value.discount_amount) : 0
  const shipping = parseFloat(props.order.shipping_cost || 0)
  const tax = parseFloat(props.order.tax_amount || 0)

  const total = subtotal - productDiscount - couponDiscount + shipping + tax
  return Math.max(0, total).toFixed(2)
})

// Apply coupon
const applyCoupon = async () => {
  if (!couponCode.value || isValidatingCoupon.value) return

  couponError.value = ''
  isValidatingCoupon.value = true

  try {
    // Calculate order amount (subtotal - product discounts)
    const orderAmount = parseFloat(props.order.subtotal) - parseFloat(props.order.discount_amount || 0)

    const response = await couponsAPI.validate({
      code: couponCode.value.trim().toUpperCase(),
      order_amount: orderAmount
    })

    appliedCoupon.value = {
      code: response.data.coupon.code,
      discount_amount: response.data.discount_amount
    }

    toast.success(response.data.message || 'Coupon applied successfully!')
    couponCode.value = ''
  } catch (error) {
    console.error('Coupon validation error:', error)
    if (error.response?.data?.error) {
      couponError.value = error.response.data.error
    } else {
      couponError.value = 'Invalid coupon code'
    }
    toast.error(couponError.value)
  } finally {
    isValidatingCoupon.value = false
  }
}

// Remove coupon
const removeCoupon = () => {
  appliedCoupon.value = null
  couponCode.value = ''
  couponError.value = ''
  toast.info('Coupon removed')
}

// Handle payment retry
const handleRetryPayment = async () => {
  if (!props.order) return

  isProcessingPayment.value = true
  try {
    const frontendUrl = window.location.origin
    const paymentData = {
      frontend_url: frontendUrl
    }

    // Add coupon if applied
    if (appliedCoupon.value) {
      paymentData.coupon_code = appliedCoupon.value.code
    }

    const paymentResponse = await paymentsAPI.create(props.order.order_number, paymentData)

    // Redirect to Stripe checkout page
    window.location.href = paymentResponse.data.checkout_url
  } catch (error) {
    console.error('Failed to create payment session:', error)
    toast.error('Failed to initiate payment. Please try again.')
    isProcessingPayment.value = false
  }
}
</script>
