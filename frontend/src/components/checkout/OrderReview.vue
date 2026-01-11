<template>
  <div class="card">
    <div class="card-header">
      <h3 class="text-xl font-semibold text-gray-900">Order Review</h3>
    </div>

    <div class="card-body space-y-6">
      <!-- Order Items -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 mb-3">
          Order Items ({{ cart?.items?.length || 0 }})
        </h4>

        <div class="space-y-3">
          <div
            v-for="item in cart?.items || []"
            :key="item.id"
            class="flex gap-3 pb-3 border-b border-gray-200 last:border-0"
          >
            <!-- Product Image -->
            <div class="flex-shrink-0 w-16 h-16">
              <img
                v-if="getProductImage(item.product)"
                :src="getProductImage(item.product)"
                :alt="item.product.name"
                class="w-full h-full object-cover rounded"
              />
              <div v-else class="w-full h-full bg-gray-200 rounded"></div>
            </div>

            <!-- Product Info -->
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 line-clamp-2">
                {{ item.product.name }}
              </p>
              <p v-if="item.variant" class="text-xs text-gray-500 mt-1">
                {{ item.variant.name }}
              </p>
              <p class="text-xs text-gray-600 mt-1">Qty: {{ item.quantity }}</p>
            </div>

            <!-- Price -->
            <div class="flex-shrink-0 text-right">
              <p class="text-sm font-semibold text-gray-900">
                ${{ parseFloat(item.total_price).toFixed(2) }}
              </p>
              <p v-if="item.discount_amount > 0" class="text-xs text-success-600">
                Saved ${{ parseFloat(item.discount_amount).toFixed(2) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Shipping Address -->
      <div>
        <div class="flex justify-between items-center mb-3">
          <h4 class="text-sm font-semibold text-gray-900">Shipping Address</h4>
          <button
            @click="$emit('edit-address')"
            class="text-xs text-accent-600 hover:text-accent-700 font-medium"
          >
            Edit
          </button>
        </div>

        <div v-if="shippingAddress" class="p-3 bg-gray-50 rounded text-sm">
          <p class="font-medium text-gray-900">{{ shippingAddress.full_name }}</p>
          <p class="text-gray-600">{{ shippingAddress.phone }}</p>
          <p class="text-gray-700 mt-2">
            {{ shippingAddress.address_line1 }}
            <span v-if="shippingAddress.address_line2">, {{ shippingAddress.address_line2 }}</span>
          </p>
          <p class="text-gray-700">
            {{ shippingAddress.city }}, {{ shippingAddress.state }} {{ shippingAddress.postal_code }}
          </p>
          <p class="text-gray-700">{{ shippingAddress.country }}</p>
        </div>
        <div v-else class="p-3 bg-error-50 border border-error-200 rounded text-sm">
          <p class="text-error-700">No shipping address selected</p>
        </div>
      </div>

      <!-- Applied Coupon -->
      <div v-if="coupon">
        <div class="flex justify-between items-center mb-3">
          <h4 class="text-sm font-semibold text-gray-900">Discount Code</h4>
          <button
            @click="$emit('edit-coupon')"
            class="text-xs text-accent-600 hover:text-accent-700 font-medium"
          >
            Change
          </button>
        </div>

        <div class="p-3 bg-success-50 border border-success-200 rounded text-sm">
          <div class="flex justify-between items-center">
            <span class="font-medium text-success-900">{{ coupon.code }}</span>
            <span class="text-success-700">
              -${{ parseFloat(couponDiscount).toFixed(2) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="border-t border-gray-200 pt-4">
        <h4 class="text-sm font-semibold text-gray-900 mb-3">Order Summary</h4>

        <div class="space-y-2 text-sm">
          <div class="flex justify-between text-gray-600">
            <span>Subtotal</span>
            <span>${{ parseFloat(cart?.subtotal || 0).toFixed(2) }}</span>
          </div>

          <div v-if="cart?.total_discount > 0" class="flex justify-between text-success-600">
            <span>Product Discounts</span>
            <span>-${{ parseFloat(cart.total_discount).toFixed(2) }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="flex justify-between text-success-600">
            <span>Coupon Discount</span>
            <span>-${{ parseFloat(couponDiscount).toFixed(2) }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="border-t border-gray-200 pt-2 flex justify-between text-base text-gray-700">
            <span>Cart Total</span>
            <span>${{ totalAmount }}</span>
          </div>

          <div v-if="couponDiscount > 0" class="flex justify-between text-lg font-bold text-accent-600">
            <span>Estimated Final Total</span>
            <span>${{ estimatedTotal }}</span>
          </div>

          <div v-if="!couponDiscount || couponDiscount <= 0" class="border-t border-gray-200 pt-2 flex justify-between text-lg font-bold text-gray-900">
            <span>Total</span>
            <span>${{ totalAmount }}</span>
          </div>
        </div>

        <!-- Coupon Disclaimer -->
        <div v-if="couponDiscount > 0" class="mt-3 p-3 bg-accent-50 border border-accent-200 rounded text-xs text-accent-800">
          <p>
            <strong>Note:</strong> The estimated final total includes your coupon discount.
            The exact amount (including shipping and tax) will be calculated and confirmed when placing your order.
          </p>
        </div>
      </div>

      <!-- Place Order Button -->
      <button
        @click="$emit('place-order')"
        :disabled="!canPlaceOrder || isProcessing"
        class="btn btn-primary btn-lg w-full"
      >
        <span v-if="isProcessing" class="loading-spinner mr-2"></span>
        {{ isProcessing ? 'Processing...' : 'Place Order' }}
      </button>

      <p class="text-xs text-gray-500 text-center">
        By placing your order, you agree to our Terms of Service and Privacy Policy
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import api from '@/services/api'

const props = defineProps({
  cart: {
    type: Object,
    required: true
  },
  shippingAddress: {
    type: Object,
    default: null
  },
  coupon: {
    type: Object,
    default: null
  },
  couponDiscount: {
    type: Number,
    default: 0
  },
  isProcessing: {
    type: Boolean,
    default: false
  }
})

defineEmits(['edit-address', 'edit-coupon', 'place-order'])

const canPlaceOrder = computed(() => {
  return props.shippingAddress && props.cart?.items?.length > 0
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

// Get product image - handle both list API (primary_image) and detail API (images array)
const getProductImage = (product) => {
  const base = api.defaults.baseURL.replace(/\/$/, '')
  // From list API: primary_image is an object with {image: 'url'}
  if (product.primary_image && product.primary_image.image) {
    const imgPath = product.primary_image.image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  // From detail API: images is an array
  if (product.images && product.images.length > 0) {
    const imgPath = product.images[0].image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  return null
}
</script>
