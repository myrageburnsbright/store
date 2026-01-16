<template>
  <div class="container-narrow py-12">
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading order details...</p>
    </div>

    <!-- Success Content -->
    <div v-else-if="order" class="text-center">
      <!-- Success Icon -->
      <div class="mb-8">
        <div class="w-32 h-32 bg-success-50 rounded-full flex items-center justify-center mx-auto">
          <CheckCircleIcon class="w-24 h-24 text-success-500" />
        </div>
      </div>

      <!-- Success Message -->
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Order Placed Successfully!</h1>
      <p class="text-lg text-gray-600 mb-8">
        Thank you for your order. We'll send you a confirmation email shortly.
      </p>

      <!-- Order Details Card -->
      <div class="card text-left mb-8">
        <div class="card-header">
          <h2 class="text-xl font-semibold text-gray-900">Order Details</h2>
        </div>
        <div class="card-body space-y-4">
          <!-- Order Number -->
          <div class="flex justify-between items-center pb-4 border-b border-gray-200">
            <span class="text-gray-600">Order Number:</span>
            <span class="text-lg font-bold text-gray-900">#{{ order.order_number }}</span>
          </div>

          <!-- Order Date -->
          <div class="flex justify-between items-center pb-4 border-b border-gray-200">
            <span class="text-gray-600">Order Date:</span>
            <span class="font-medium text-gray-900">{{ formatDate(order.created_at) }}</span>
          </div>

          <!-- Status -->
          <div class="flex justify-between items-center pb-4 border-b border-gray-200">
            <span class="text-gray-600">Status:</span>
            <OrderStatusBadge :status="order.status" />
          </div>

          <!-- Payment Method -->
          <div class="flex justify-between items-center pb-4 border-b border-gray-200">
            <span class="text-gray-600">Payment Method:</span>
            <span class="font-medium text-gray-900 capitalize">{{ order.payment_method }}</span>
          </div>

          <!-- Pricing Breakdown -->
          <div class="space-y-2 pb-4 border-b border-gray-200">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Subtotal:</span>
              <span class="text-gray-900">${{ parseFloat(order.subtotal).toFixed(2) }}</span>
            </div>

            <div v-if="order.discount_amount > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Product Discounts:</span>
              <span class="text-success-600">-${{ parseFloat(order.discount_amount).toFixed(2) }}</span>
            </div>

            <div v-if="order.coupon_code && order.coupon_discount > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Coupon ({{ order.coupon_code }}):</span>
              <span class="text-success-600 font-medium">-${{ parseFloat(order.coupon_discount).toFixed(2) }}</span>
            </div>

            <div class="flex justify-between text-sm">
              <span class="text-gray-600">Shipping:</span>
              <span class="text-gray-900">${{ parseFloat(order.shipping_cost || 0).toFixed(2) }}</span>
            </div>

            <div v-if="order.tax_amount > 0" class="flex justify-between text-sm">
              <span class="text-gray-600">Tax:</span>
              <span class="text-gray-900">${{ parseFloat(order.tax_amount).toFixed(2) }}</span>
            </div>
          </div>

          <!-- Total Amount -->
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Total Amount:</span>
            <span class="text-2xl font-bold text-gray-900">
              ${{ parseFloat(order.total).toFixed(2) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Order Items Summary -->
      <div class="card text-left mb-8">
        <div class="card-header">
          <h3 class="text-lg font-semibold text-gray-900">
            Order Items ({{ order.items.length }})
          </h3>
        </div>
        <div class="card-body">
          <div class="space-y-3">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex gap-3 pb-3 border-b border-gray-200 last:border-0"
            >
              <!-- Product Image -->
              <div class="flex-shrink-0 w-16 h-16">
                <img
                  v-if="getProductImageUrl(item.product)"
                  :src="getProductImageUrl(item.product)"
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
                <p class="text-xs text-gray-600 mt-1">Qty: {{ item.quantity }}</p>
                <p class="text-xs text-gray-600 mt-1">Per unit:  <span>${{ item.unit_price }}</span></p>
       
              </div>

              <!-- Price -->
              <div class="flex-shrink-0 text-right">
                <p class="text-sm font-semibold text-gray-900">
                  ${{ parseFloat(item.total_price).toFixed(2) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Shipping Address -->
      <div class="card text-left mb-8">
        <div class="card-header">
          <h3 class="text-lg font-semibold text-gray-900">Shipping Address</h3>
        </div>
        <div class="card-body text-sm">
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

      <!-- What's Next -->
      <div class="card text-left mb-8">
        <div class="card-header">
          <h3 class="text-lg font-semibold text-gray-900">What's Next?</h3>
        </div>
        <div class="card-body">
          <ul class="space-y-3 text-sm text-gray-700">
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <span>You'll receive an order confirmation email with your order details</span>
            </li>
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <span>We'll notify you when your order ships</span>
            </li>
            <li class="flex items-start gap-3">
              <CheckCircleIcon class="w-5 h-5 text-success-600 flex-shrink-0 mt-0.5" />
              <span>You can track your order status in your orders page</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          :to="{ name: 'order-detail', params: { orderNumber: order.order_number } }"
          class="btn btn-primary"
        >
          <DocumentTextIcon class="w-5 h-5 mr-2" />
          View Order Details
        </router-link>

        <router-link :to="{ name: 'orders' }" class="btn btn-outline">
          <ShoppingBagIcon class="w-5 h-5 mr-2" />
          View All Orders
        </router-link>

        <router-link :to="{ name: 'products' }" class="btn w-full btn-secondary">
          Continue Shopping
        </router-link>
      </div>
    </div>

    <!-- Error State -->
    <div v-else class="card card-body text-center py-12">
      <div class="w-20 h-20 bg-error-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <XCircleIcon class="w-12 h-12 text-error-600" />
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Order Not Found</h2>
      <p class="text-gray-600 mb-6">
        We couldn't find the order you're looking for.
      </p>
      <div class="flex gap-4 justify-center">
        <router-link :to="{ name: 'orders' }" class="btn btn-primary">
          View Your Orders
        </router-link>
        <router-link :to="{ name: 'home' }" class="btn btn-outline">
          Go to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { getProductImageUrl } from '@/composables/useProductImage'
import OrderStatusBadge from '@/components/orders/OrderStatusBadge.vue'
import {
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  ShoppingBagIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const ordersStore = useOrdersStore()

const isLoading = ref(true)
const order = ref(null)

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

onMounted(async () => {
  const orderNumber = route.query.order_number

  if (!orderNumber) {
    isLoading.value = false
    return
  }

  try {
    order.value = await ordersStore.fetchOrderByNumber(orderNumber)
  } catch (error) {
    console.error("[CheckoutSuccessView] Error fetching order details:", error)
  } finally {
    isLoading.value = false
  }
})
</script>
