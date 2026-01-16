<template>
  <div class="space-y-6">
    <!-- Order Header -->
    <div class="card">
      <div class="card-body">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 mb-2">
              Order #{{ order.order_number }}
            </h1>
            <p class="text-sm text-gray-600">
              Placed on {{ formatDate(order.created_at) }}
            </p>
          </div>

          <OrderStatusBadge :status="order.status" />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6" :class="showActions ? 'lg:grid-cols-3' : 'lg:grid-cols-1'">
      <!-- Main Content -->
      <div class="space-y-6" :class="showActions ? 'lg:col-span-2' : ''">
        <!-- Order Items -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Order Items</h3>
          </div>
          <div class="card-body">
            <div class="space-y-4">
              <div
                v-for="item in order.items"
                :key="item.id"
                class="flex gap-4 pb-4 border-b border-gray-200 last:border-0"
              >
                <!-- Product Image -->
                <router-link
                  :to="{ name: 'product-detail', params: { slug: item.product.slug } }"
                  class="flex-shrink-0"
                >
                  <img
                    v-if="getProductImage(item.product)"
                    :src="getProductImage(item.product)"
                    :alt="item.product.name"
                    class="w-20 h-20 object-cover rounded"
                  />
                  <div v-else class="w-20 h-20 bg-gray-200 rounded"></div>
                </router-link>

                <!-- Product Info -->
                <div class="flex-1 min-w-0">
                  <router-link
                    :to="{ name: 'product-detail', params: { slug: item.product.slug } }"
                    class="text-base font-semibold text-gray-900 hover:text-accent-600 line-clamp-2"
                  >
                    {{ item.product.name }}
                  </router-link>

                  <p v-if="item.variant" class="text-sm text-gray-600 mt-1">
                    Variant: {{ item.variant.name }}
                  </p>

                  <div class="flex gap-4 mt-2 text-sm text-gray-600">
                    <span>Qty: {{ item.quantity }}</span>
                    <span>×</span>
                    <span>${{ parseFloat(item.unit_price).toFixed(2) }}</span>
                  </div>

                  <p v-if="item.discount_amount > 0" class="text-sm text-success-600 mt-1">
                    Discount: -${{ parseFloat(item.discount_amount).toFixed(2) }}
                  </p>
                </div>

                <!-- Price -->
                <div class="flex-shrink-0 text-right">
                  <p class="text-lg font-semibold text-gray-900">
                    ${{ parseFloat(item.total_price).toFixed(2) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Shipping Address -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Shipping Address</h3>
          </div>
          <div class="card-body">
            <div class="text-sm">
              <p class="font-semibold text-gray-900">{{ order.shipping_address.full_name }}</p>
              <p class="text-gray-600 mt-1">{{ order.shipping_address.phone }}</p>
              <p class="text-gray-700 mt-2">
                {{ order.shipping_address.address_line1 }}
                <span v-if="order.shipping_address.address_line2">, {{ order.shipping_address.address_line2 }}</span>
              </p>
              <p class="text-gray-700">
                {{ order.shipping_address.city }}, {{ order.shipping_address.state }} {{ order.shipping_address.postal_code }}
              </p>
              <p class="text-gray-700">{{ order.shipping_address.country }}</p>
            </div>
          </div>
        </div>

        <!-- Payment Information -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Payment Information</h3>
          </div>
          <div class="card-body">
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Payment Method:</span>
                <span class="font-medium text-gray-900 capitalize">{{ order.payment_method }}</span>
              </div>

              <div v-if="order.payment_status" class="flex justify-between">
                <span class="text-gray-600">Payment Status:</span>
                <span class="font-medium" :class="paymentStatusClass">
                  {{ order.payment_status }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Timeline -->
        <div v-if="order.status_history && order.status_history.length > 0" class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Order Timeline</h3>
          </div>
          <div class="card-body">
            <div class="space-y-4">
              <div
                v-for="(history, index) in order.status_history"
                :key="history.id"
                class="flex gap-4"
              >
                <!-- Timeline Dot -->
                <div class="flex flex-col items-center">
                  <div
                    class="w-3 h-3 rounded-full"
                    :class="index === 0 ? 'bg-accent-600' : 'bg-gray-300'"
                  ></div>
                  <div
                    v-if="index !== order.status_history.length - 1"
                    class="w-0.5 flex-1 bg-gray-300 mt-1"
                  ></div>
                </div>

                <!-- Timeline Content -->
                <div class="flex-1 pb-4">
                  <OrderStatusBadge :status="history.status" />
                  <p class="text-sm text-gray-600 mt-1">
                    {{ formatDate(history.created_at) }}
                  </p>
                  <p v-if="history.notes" class="text-sm text-gray-700 mt-2">
                    {{ history.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div v-if="showActions" class="space-y-6">
        <!-- Order Summary -->
        <div class="card sticky top-4">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Order Summary</h3>
          </div>
          <div class="card-body">
            <div class="space-y-3 text-sm">
              <div class="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>${{ parseFloat(order.subtotal).toFixed(2) }}</span>
              </div>

              <div v-if="order.discount_amount > 0" class="flex justify-between text-success-600">
                <span>Product Discounts</span>
                <span>-${{ parseFloat(order.discount_amount).toFixed(2) }}</span>
              </div>

              <!-- Coupon Discount -->
              <div v-if="order.coupon_discount && order.coupon_discount > 0" class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <span class="text-success-700 font-medium">Coupon</span>
                  <span v-if="order.coupon_code" class="badge badge-success text-xs">{{ order.coupon_code }}</span>
                </div>
                <span class="text-success-700 font-medium">-${{ parseFloat(order.coupon_discount).toFixed(2) }}</span>
              </div>

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
                <span>${{ parseFloat(order.total).toFixed(2) }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div v-if="showActions" class="mt-6 space-y-3">
              <button
                v-if="canCancel"
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

        <!-- Customer Notes -->
        <div v-if="order.customer_notes" class="card">
          <div class="card-header">
            <h3 class="text-lg font-semibold text-gray-900">Order Notes</h3>
          </div>
          <div class="card-body">
            <p class="text-sm text-gray-700">{{ order.customer_notes }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import OrderStatusBadge from './OrderStatusBadge.vue'

const props = defineProps({
  order: {
    type: Object,
    required: true
  },
  isCancelling: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

defineEmits(['cancel'])

const canCancel = computed(() => {
  return ['pending', 'paid'].includes(props.order.status)
})

const paymentStatusClass = computed(() => {
  const status = props.order.payment_status?.toLowerCase()
  if (status === 'paid' || status === 'completed') return 'text-success-600'
  if (status === 'pending') return 'text-warning-600'
  if (status === 'failed') return 'text-error-600'
  return 'text-gray-900'
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get product image - handle both list API (primary_image) and detail API (images array)
const getProductImage = (product) => {
  // From list API: primary_image is an object with {image: 'url'}
  if (product.primary_image && product.primary_image.image) {
    return product.primary_image.image
  }
  // From detail API: images is an array
  if (product.images && product.images.length > 0) {
    return product.images[0].image
  }
  return null
}
</script>
