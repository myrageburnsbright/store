<template>
  <div class="container-content py-8">
    <!-- Loading State -->
    <div v-if="ordersStore.isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading order details...</p>
    </div>

    <!-- Order Not Found -->
    <div v-else-if="!order" class="card card-body text-center py-12">
      <div class="w-20 h-20 bg-error-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <XCircleIcon class="w-12 h-12 text-error-600" />
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Order Not Found</h2>
      <p class="text-gray-600 mb-6">
        The order you're looking for doesn't exist or you don't have permission to view it.
      </p>
      <div class="flex gap-4 justify-center">
        <router-link :to="{ name: 'orders' }" class="btn btn-primary">
          View All Orders
        </router-link>
        <router-link :to="{ name: 'home' }" class="btn btn-outline">
          Go to Home
        </router-link>
      </div>
    </div>

    <!-- Order Detail -->
    <div v-else>
      <!-- Breadcrumb -->
      <nav class="mb-6 text-sm">
        <ol class="flex items-center space-x-2 text-gray-600">
          <li>
            <router-link :to="{ name: 'orders' }" class="hover:text-accent-600">
              My Orders
            </router-link>
          </li>
          <li>
            <ChevronRightIcon class="w-4 h-4" />
          </li>
          <li class="text-gray-900 font-medium">Order #{{ order.order_number }}</li>
        </ol>
      </nav>

      <!-- Order Detail Component -->
      <OrderDetail
        :order="order"
        :is-cancelling="isCancelling"
        @cancel="handleCancelOrder"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import OrderDetail from '@/components/orders/OrderDetail.vue'
import { XCircleIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const ordersStore = useOrdersStore()

const isCancelling = ref(false)

const order = computed(() => ordersStore.currentOrder)

const handleCancelOrder = async () => {
  if (!order.value) return

  if (!confirm(`Are you sure you want to cancel order #${order.value.order_number}?`)) {
    return
  }

  isCancelling.value = true
  try {
    await ordersStore.cancelOrder(order.value.order_number)
    // Order is automatically updated in the store
  } catch (error) {
    console.error('Failed to cancel order:', error)
  } finally {
    isCancelling.value = false
  }
}

onMounted(async () => {
  const orderNumber = route.params.orderNumber

  if (!orderNumber) {
    router.push({ name: 'orders' })
    return
  }

  try {
    await ordersStore.fetchOrderByNumber(orderNumber)
  } catch (error) {
    console.error('Failed to load order:', error)
  }
})
</script>
