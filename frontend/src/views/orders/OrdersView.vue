<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Orders</h1>

    <!-- Filter Tabs -->
    <div class="mb-6 border-b border-gray-200">
      <nav class="flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="selectedTab = tab.value"
          class="whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm transition-colors"
          :class="
            selectedTab === tab.value
              ? 'border-accent-500 text-accent-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          "
        >
          {{ tab.label }}
          <span
            v-if="tab.count > 0"
            class="ml-2 py-0.5 px-2 rounded-full text-xs"
            :class="
              selectedTab === tab.value
                ? 'bg-accent-100 text-accent-600'
                : 'bg-gray-100 text-gray-600'
            "
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="ordersStore.isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading orders...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredOrders.length === 0" class="card card-body text-center py-12">
      <div class="mb-6">
        <ShoppingBagIcon class="w-20 h-20 mx-auto text-gray-300" />
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        {{ selectedTab === 'all' ? 'No orders yet' : `No ${selectedTab} orders` }}
      </h2>
      <p class="text-gray-600 mb-6">
        {{ selectedTab === 'all'
          ? "You haven't placed any orders yet. Start shopping to see your orders here!"
          : `You don't have any ${selectedTab} orders at the moment.`
        }}
      </p>
      <router-link :to="{ name: 'products' }" class="btn btn-primary mx-auto">
        <ShoppingBagIcon class="w-5 h-5 mr-2" />
        Start Shopping
      </router-link>
    </div>

    <!-- Orders List -->
    <div v-else class="space-y-4">
      <OrderCard
        v-for="order in filteredOrders"
        :key="order.id"
        :order="order"
        :is-cancelling="cancellingOrderId === order.id"
        @cancel="handleCancelOrder(order)"
      />

      <!-- Pagination -->
      <div v-if="ordersStore.pagination.count > ordersStore.pagination.pageSize" class="mt-8">
        <PaginationComponent
          :current-page="ordersStore.pagination.page"
          :total-pages="totalPages"
          :has-next="ordersStore.hasNextPage"
          :has-previous="ordersStore.hasPreviousPage"
          @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useOrdersStore } from '@/stores/orders'
import { useToast } from 'vue-toastification'
import OrderCard from '@/components/orders/OrderCard.vue'
import PaginationComponent from '@/components/ui/PaginationComponent.vue'
import { ShoppingBagIcon } from '@heroicons/vue/24/outline'

const ordersStore = useOrdersStore()
const toast = useToast()

const selectedTab = ref('all')
const cancellingOrderId = ref(null)

const tabs = computed(() => [
  {
    value: 'all',
    label: 'All Orders',
    count: ordersStore.orders.length
  },
  {
    value: 'pending',
    label: 'Pending',
    count: ordersStore.pendingOrders.length
  },
  {
    value: 'paid',
    label: 'Paid',
    count: ordersStore.paidOrders.length
  },
  {
    value: 'processing',
    label: 'Processing',
    count: ordersStore.processingOrders.length
  },
  {
    value: 'shipped',
    label: 'Shipped',
    count: ordersStore.shippedOrders.length
  },
  {
    value: 'delivered',
    label: 'Delivered',
    count: ordersStore.deliveredOrders.length
  },
  {
    value: 'cancelled',
    label: 'Cancelled',
    count: ordersStore.cancelledOrders.length
  }
])

const filteredOrders = computed(() => {
  switch (selectedTab.value) {
    case 'pending':
      return ordersStore.pendingOrders
    case 'paid':
      return ordersStore.paidOrders
    case 'processing':
      return ordersStore.processingOrders
    case 'shipped':
      return ordersStore.shippedOrders
    case 'delivered':
      return ordersStore.deliveredOrders
    case 'cancelled':
      return ordersStore.cancelledOrders
    default:
      return ordersStore.orders
  }
})

const totalPages = computed(() => {
  return Math.ceil(ordersStore.pagination.count / ordersStore.pagination.pageSize)
})

const handlePageChange = async (page) => {
  await ordersStore.goToPage(page)
}

const handleCancelOrder = async (order) => {
  if (!confirm(`Are you sure you want to cancel order #${order.order_number}?`)) {
    return
  }

  cancellingOrderId.value = order.id
  try {
    await ordersStore.cancelOrder(order.order_number)
  } catch (error) {
    console.error('Failed to cancel order:', error)
  } finally {
    cancellingOrderId.value = null
  }
}

// Fetch orders when tab changes
watch(selectedTab, async () => {
  // If filtering by status, we can filter client-side from existing data
  // No need to refetch unless implementing server-side filtering
})

onMounted(async () => {
  if (ordersStore.orders.length === 0) {
    await ordersStore.fetchOrders()
  }
})
</script>
