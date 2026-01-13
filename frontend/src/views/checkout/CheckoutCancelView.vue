<template>
  <div class="container-content py-12">
    <div class="max-w-2xl mx-auto text-center">
      <!-- Cancel Icon -->
      <div class="mb-6">
        <div class="w-20 h-20 mx-auto bg-yellow-100 rounded-full flex items-center justify-center">
          <XCircleIcon class="w-12 h-12 text-yellow-600" />
        </div>
      </div>

      <!-- Title -->
      <h1 class="text-3xl font-bold text-gray-900 mb-4">Payment Cancelled</h1>

      <!-- Message -->
      <p class="text-gray-600 mb-2">
        Your payment was cancelled and your order has not been completed.
      </p>
      <p class="text-gray-600 mb-8">
        Don't worry - no charges have been made to your account.
      </p>

      <!-- Order Details -->
      <div v-if="orderNumber" class="card card-body mb-8">
        <p class="text-sm text-gray-600 mb-2">Order Number</p>
        <p class="text-lg font-semibold text-gray-900">{{ orderNumber }}</p>
        <p class="text-sm text-gray-500 mt-2">Your order is saved and awaiting payment</p>
      </div>

      <!-- Actions -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          v-if="orderNumber"
          :to="{ name: 'orders' }"
          class="btn btn-outline btn-lg"
        >
          View My Orders
        </router-link>
        <router-link
          v-if="orderNumber"
          :to="{ name: 'order-detail', params: { orderNumber: orderNumber } }"
          class="btn btn-primary btn-lg"
        >
          Try Again
        </router-link>
        <router-link
          v-else
          :to="{ name: 'cart' }"
          class="btn btn-primary btn-lg"
        >
          Return to Cart
        </router-link>
      </div>

      <!-- Help Text -->
      <div class="mt-8 text-sm text-gray-500">
        <p>Need help? <router-link :to="{ name: 'home' }" class="text-accent-600 hover:text-accent-700">Contact Support</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { XCircleIcon } from '@heroicons/vue/24/outline'

const route = useRoute()

const orderNumber = ref(route.query.order_number || '')

onMounted(() => {
  // Check if order number exists
  if (!orderNumber.value) {
    console.warn('No order number provided in URL')
  }
})
</script>
