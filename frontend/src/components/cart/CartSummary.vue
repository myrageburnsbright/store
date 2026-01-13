<template>
  <div class="card sticky top-4">
    <div class="card-header">
      <h3 class="text-xl font-bold text-gray-900">Cart Summary</h3>
    </div>

    <div class="card-body space-y-4">
      <!-- Items Count -->
      <div class="flex justify-between text-sm text-gray-600">
        <span>Items ({{ cart?.items?.length || 0 }} product{{ cart?.items?.length !== 1 ? 's' : '' }}):</span>
        <span>{{ itemCount }} item{{ itemCount !== 1 ? 's' : '' }}</span>
      </div>
      <div class="flex justify-between text-sm text-gray-600">
        <span>Subtotal</span>
        <span>${{ parseFloat(cart?.subtotal || 0).toFixed(2) }}</span>
      </div>

      <!-- Discounts -->
      <div v-if="cart?.total_discount > 0" class="flex justify-between text-sm text-success-600">
        <span>Total Discount</span>
        <span>-${{ parseFloat(cart.total_discount).toFixed(2) }}</span>
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200"></div>

      <!-- Coupon Input -->
      <div v-if="allowCoupon" class="space-y-2">
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
              <p class="text-xs text-success-700">-${{ parseFloat(appliedCoupon.discount_amount).toFixed(2) }} discount applied</p>
            </div>
          </div>
          <button
            @click="removeCoupon"
            class="text-success-700 hover:text-success-900 transition-colors"
            :disabled="isValidating"
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
            :disabled="isValidating"
            @keyup.enter="applyCoupon"
          />
          <button
            @click="applyCoupon"
            :disabled="!couponCode || isValidating"
            class="btn btn-sm btn-outline"
          >
            {{ isValidating ? 'Applying...' : 'Apply' }}
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

      <!-- Shipping Note -->
      <div class="text-xs text-gray-500">
        Shipping and taxes calculated at checkout
      </div>

      <!-- Divider -->
      <div class="border-t border-gray-200"></div>

      <!-- Total (without coupon) -->
      <div v-if="!appliedCoupon" class="flex justify-between text-xl font-bold text-gray-900">
        <span>Total</span>
        <span>${{ totalAmount }}</span>
      </div>

      <!-- Cart Total and Estimated Total (with coupon) -->
      <div v-else class="space-y-2">
        <div class="flex justify-between text-base text-gray-700">
          <span>Cart Total</span>
          <span>${{ totalAmount }}</span>
        </div>
        <div class="flex justify-between text-xl font-bold text-accent-600">
          <span>Estimated Total</span>
          <span>${{ estimatedTotal }}</span>
        </div>
        <p class="text-xs text-gray-500 pt-2">
          Estimated total includes coupon discount. Final amount will be confirmed at checkout.
        </p>
      </div>

      <!-- Checkout Button -->
      <router-link
        v-if="showCheckoutButton"
        :to="{ name: 'checkout' }"
        class="btn btn-primary btn-lg w-full"
      >
        Proceed to Checkout
      </router-link>

      <!-- Continue Shopping Link -->
      <router-link
        :to="{ name: 'products' }"
        class="block text-center text-[9px] text-accent-600 w-full hover:text-accent-1000 transition-colors btn btn-primary btn-sm"
      >
        Continue Shopping
      </router-link>

      <!-- Security Badge -->
      <div class="flex items-center justify-center gap-2 text-xs text-gray-500 pt-4 border-t border-gray-200">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>Secure Checkout</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { couponsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

const props = defineProps({
  cart: {
    type: Object,
    default: null
  },
  showCheckoutButton: {
    type: Boolean,
    default: true
  },
  allowCoupon: {
    type: Boolean,
    default: true
  },
  couponDiscount: {
    type: Number,
    default: 0
  },
  coupon: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['coupon-applied', 'coupon-removed'])

const couponCode = ref('')
const appliedCoupon = ref(props.coupon)
const isValidating = ref(false)
const couponError = ref('')

// Sync appliedCoupon with prop when it changes
watch(() => props.coupon, (newCoupon) => {
  appliedCoupon.value = newCoupon
})

const itemCount = computed(() => {
  if (!props.cart || !props.cart.items) return 0
  return props.cart.items.reduce((total, item) => total + item.quantity, 0)
})

// Use server-calculated total - don't calculate on client side
const totalAmount = computed(() => {
  // Always use the server's total directly
  // Coupon discounts should be applied on the server during order creation
  return parseFloat(props.cart?.total || 0).toFixed(2)
})

// Calculate estimated total for preview when coupon is applied
// This is ONLY for display purposes - server will calculate the actual total
const estimatedTotal = computed(() => {
  if (!appliedCoupon.value) {
    return totalAmount.value
  }
  const cartTotal = parseFloat(props.cart?.total || 0)
  const estimated = cartTotal - parseFloat(appliedCoupon.value.discount_amount)
  return Math.max(0, estimated).toFixed(2)
})

// Apply coupon
const applyCoupon = async () => {
  if (!couponCode.value || isValidating.value) return

  couponError.value = ''
  isValidating.value = true

  try {
    // Calculate order amount (cart total)
    const orderAmount = parseFloat(props.cart?.total || 0)

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

    // Emit event to parent
    emit('coupon-applied', appliedCoupon.value)
  } catch (error) {
    console.error('Coupon validation error:', error)
    if (error.response?.data?.error) {
      couponError.value = error.response.data.error
    } else {
      couponError.value = 'Invalid coupon code'
    }
    toast.error(couponError.value)
  } finally {
    isValidating.value = false
  }
}

// Remove coupon
const removeCoupon = () => {
  appliedCoupon.value = null
  couponCode.value = ''
  couponError.value = ''
  emit('coupon-removed')
  toast.info('Coupon removed')
}
</script>
