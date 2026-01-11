<template>
  <div class="card hover:shadow-md transition-shadow">
    <div class="card-body">
      <!-- Header -->
      <div class="flex justify-between items-start mb-4">
        <div>
          <h3 class="text-lg font-semibold text-gray-900">
            Order #{{ order.order_number }}
          </h3>
          <p class="text-sm text-gray-500 mt-1">
            {{ formatDate(order.created_at) }}
          </p>
        </div>

        <OrderStatusBadge :status="order.status" />
      </div>

      <!-- Order Items Summary -->
      <div class="mb-4">
        <div class="flex gap-2 mb-2">
          <div
            v-for="item in displayItems"
            :key="item.id"
            class="relative w-16 h-16 flex-shrink-0"
          >
            <img
              v-if="getProductImageUrl(item.product)"
              :src="getProductImageUrl(item.product)"
              :alt="item.product.name"
              class="w-full h-full object-cover rounded"
            />
            <div v-else class="w-full h-full bg-gray-200 rounded"></div>

            <!-- Quantity Badge -->
            <span
              class="absolute -top-1 -right-1 bg-gray-900 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center"
            >
              {{ item.quantity }}
            </span>
          </div>

          <!-- More Items Indicator -->
          <div
            v-if="order.items.length > maxDisplayItems"
            class="w-16 h-16 bg-gray-100 rounded flex items-center justify-center"
          >
            <span class="text-xs font-medium text-gray-600">
              +{{ order.items.length - maxDisplayItems }}
            </span>
          </div>
        </div>

        <p class="text-sm text-gray-600">
          {{ order.items.length }} {{ order.items.length === 1 ? 'item' : 'items' }}
        </p>
      </div>

      <!-- Shipping Address -->
      <div class="mb-4 p-3 bg-gray-50 rounded">
        <p class="text-xs font-medium text-gray-500 mb-1">Shipping To:</p>
        <p class="text-sm text-gray-900">{{ order.shipping_address.full_name }}</p>
        <p class="text-sm text-gray-600">
          {{ order.shipping_address.city }}, {{ order.shipping_address.state }}
        </p>
      </div>

      <!-- Total Amount -->
      <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
        <span class="text-gray-600">Total Amount:</span>
        <span class="text-xl font-bold text-gray-900">
          ${{ parseFloat(order.total).toFixed(2) }}
        </span>
      </div>

      <!-- Actions -->
      <div class="flex gap-3">
        <router-link
          :to="{ name: 'order-detail', params: { orderNumber: order.order_number } }"
          class="btn btn-primary flex-1"
        >
          View Details
        </router-link>

        <button
          v-if="canCancel"
          @click="$emit('cancel')"
          :disabled="isCancelling"
          class="btn btn-outline text-error-600 hover:bg-error-50"
        >
          {{ isCancelling ? 'Cancelling...' : 'Cancel Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getProductImageUrl } from '@/composables/useProductImage'
import OrderStatusBadge from './OrderStatusBadge.vue'

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

const maxDisplayItems = 3

const displayItems = computed(() => {
  return props.order.items.slice(0, maxDisplayItems)
})

const canCancel = computed(() => {
  return ['pending', 'paid'].includes(props.order.status)
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
</script>
