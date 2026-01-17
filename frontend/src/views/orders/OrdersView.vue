<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">My Orders</h1>

    <!-- Filter Tabs -->
    <div class="mb-6 border-b border-gray-100">
      <nav class="flex-wrap space" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="selectedTab = tab.value"
          class="whitespace-nowrap pb-2 px-3 border-b-2 font-medium text-sm transition-colors"
          :class="
            selectedTab === tab.value
              ? 'border-black text-black'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          "
        >
          {{ tab.label }}
          <span
            v-if="tab.count > 0"
            class="mr-2 py-0.5 px-2 rounded-full text-xs"
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
      <div class="mt-8">
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
    count: ordersStore.statusCounts.all
  },
  {
    value: 'pending',
    label: 'Pending',
    count: ordersStore.statusCounts.pending
  },
  {
    value: 'paid',
    label: 'Paid',
    count: ordersStore.statusCounts.paid
  },
  {
    value: 'processing',
    label: 'Processing',
    count: ordersStore.statusCounts.processing
  },
  {
    value: 'shipped',
    label: 'Shipped',
    count: ordersStore.statusCounts.shipped
  },
  {
    value: 'delivered',
    label: 'Delivered',
    count: ordersStore.statusCounts.delivered
  },
  {
    value: 'cancelled',
    label: 'Cancelled',
    count: ordersStore.statusCounts.cancelled
  }
])

// Now uses server-side filtered data
const filteredOrders = computed(() => {
  return ordersStore.orders
})

const totalPages = computed(() => {
  return Math.ceil(ordersStore.pagination.count / ordersStore.pagination.pageSize)
})

const handlePageChange = async (page) => {
  const params = { page }
  if (selectedTab.value !== 'all') {
    params.status = selectedTab.value
  }
  await ordersStore.fetchOrders(params)
}

const handleCancelOrder = async (order) => {
  if (!confirm(`Are you sure you want to cancel order #${order.order_number}?`)) {
    return
  }

  cancellingOrderId.value = order.id
  try {
    await ordersStore.cancelOrder(order.order_number)
    // Refetch current page after cancellation
    await fetchOrders()
  } catch (error) {
    console.error("[OrdersView] Error canceling order:", error)
  } finally {
    cancellingOrderId.value = null
  }
}

// Fetch orders with current status filter
const fetchOrders = async () => {
  const params = {}
  if (selectedTab.value !== 'all') {
    params.status = selectedTab.value
  }
  await ordersStore.fetchOrders(params)
}

// Fetch all status counts on initial load
const fetchAllStatusCounts = async () => {
  const statuses = ['all', 'pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled']

  // Fetch counts for all statuses in parallel
  await Promise.all(
    statuses.map(async (status) => {
      const params = status === 'all' ? {} : { status, page: 1 }
      await ordersStore.fetchOrders(params)
    })
  )

  // After fetching all counts, load the current tab's full data
  await fetchOrders()
}

// Fetch orders when tab changes
watch(selectedTab, async () => {
  await fetchOrders()
})

onMounted(async () => {
  await fetchAllStatusCounts()
})
</script>
