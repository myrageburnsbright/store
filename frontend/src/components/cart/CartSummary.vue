<template>
  <div class="card sticky top-4">
    <div class="card-header">
      <h3 class="text-xl font-bold text-gray-900">Cart Summary</h3>
    </div>

    <div class="card-body space-y-4">
      <!-- Items Count -->
      <div class="flex justify-between text-sm text-gray-600">
        <span>Items ({{ itemCount }})</span>
        <span>${{ parseFloat(cart?.subtotal || 0).toFixed(2) }}</span>
      </div>

      <!-- Discounts -->
      <div v-if="cart?.total_discount > 0" class="flex justify-between text-sm text-success-600">
        <span>Total Discount</span>
        <span>-${{ parseFloat(cart.total_discount).toFixed(2) }}</span>
      </div>

      <!-- Coupon Discount (if applied) -->
      <div v-if="couponDiscount > 0" class="flex justify-between text-sm text-success-600">
        <span>Coupon Discount</span>
        <span>-${{ parseFloat(couponDiscount).toFixed(2) }}</span>
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
      <div v-if="!couponDiscount || couponDiscount <= 0" class="flex justify-between text-xl font-bold text-gray-900">
        <span>Total</span>
        <span>${{ totalAmount }}</span>
      </div>

      <!-- Cart Total and Estimated Total (with coupon) -->
      <div v-if="couponDiscount > 0" class="space-y-2">
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
        class="block text-center text-sm text-accent-600 w-full hover:text-accent-700 transition-colors btn btn-primary btn-lg"
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
import { computed } from 'vue'

const props = defineProps({
  cart: {
    type: Object,
    default: null
  },
  showCheckoutButton: {
    type: Boolean,
    default: true
  },
  couponDiscount: {
    type: Number,
    default: 0
  }
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
  if (!props.couponDiscount || props.couponDiscount <= 0) {
    return totalAmount.value
  }
  const cartTotal = parseFloat(props.cart?.total || 0)
  const estimated = cartTotal - parseFloat(props.couponDiscount)
  return Math.max(0, estimated).toFixed(2)
})
</script>
