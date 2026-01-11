import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ordersAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useOrdersStore = defineStore('orders', () => {
  // State
  const orders = ref([])
  const currentOrder = ref(null)

  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
    page: 1,
    pageSize: 20
  })

  const isLoading = ref(false)
  const isCreatingOrder = ref(false)

  // Computed
  const pendingOrders = computed(() =>
    orders.value.filter(order => order.status === 'pending')
  )

  const paidOrders = computed(() =>
    orders.value.filter(order => order.status === 'paid')
  )

  const processingOrders = computed(() =>
    orders.value.filter(order => order.status === 'processing')
  )

  const shippedOrders = computed(() =>
    orders.value.filter(order => order.status === 'shipped')
  )

  const deliveredOrders = computed(() =>
    orders.value.filter(order => order.status === 'delivered')
  )

  const cancelledOrders = computed(() =>
    orders.value.filter(order => order.status === 'cancelled')
  )

  const hasNextPage = computed(() => !!pagination.value.next)
  const hasPreviousPage = computed(() => !!pagination.value.previous)

  // Actions
  const fetchOrders = async (params = {}) => {
    isLoading.value = true
    try {
      const response = await ordersAPI.getAll(params)
      orders.value = response.data.results || []

      pagination.value = {
        count: response.data.count || 0,
        next: response.data.next,
        previous: response.data.previous,
        page: params.page || 1,
        pageSize: params.page_size || 20
      }

      return response.data
    } catch (error) {
      console.error('Error fetching orders:', error)
      orders.value = []
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchOrderByNumber = async (orderNumber) => {
    isLoading.value = true
    try {
      const response = await ordersAPI.getByOrderNumber(orderNumber)
      currentOrder.value = response.data
      return response.data
    } catch (error) {
      console.error('Error fetching order:', error)
      currentOrder.value = null
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createOrder = async (orderData) => {
    isCreatingOrder.value = true
    try {
      const response = await ordersAPI.create(orderData)
      const order = response.data.order || response.data

      // Add to orders list
      orders.value.unshift(order)
      currentOrder.value = order

      toast.success('Order placed successfully')
      return order
    } catch (error) {
      console.error('Error creating order:', error)

      // Handle specific errors
      if (error.response?.data) {
        const errorData = error.response.data
        if (errorData.error) {
          toast.error(errorData.error)
        } else if (errorData.coupon_code) {
          toast.error(errorData.coupon_code[0] || 'Invalid coupon code')
        } else if (errorData.shipping_address_id) {
          toast.error('Please select a shipping address')
        } else {
          toast.error('Failed to create order')
        }
      } else {
        toast.error('Failed to create order')
      }

      throw error
    } finally {
      isCreatingOrder.value = false
    }
  }

  const cancelOrder = async (orderNumber) => {
    isLoading.value = true
    try {
      const response = await ordersAPI.cancel(orderNumber)
      const cancelledOrder = response.data.order || response.data

      // Update in orders list
      const index = orders.value.findIndex(o => o.order_number === orderNumber)
      if (index !== -1) {
        orders.value[index] = cancelledOrder
      }

      // Update current order if it's the same
      if (currentOrder.value?.order_number === orderNumber) {
        currentOrder.value = cancelledOrder
      }

      toast.success('Order cancelled successfully')
      return cancelledOrder
    } catch (error) {
      console.error('Error cancelling order:', error)
      if (error.response?.data?.error) {
        toast.error(error.response.data.error)
      } else {
        toast.error('Failed to cancel order')
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const clearOrders = () => {
    orders.value = []
  }

  const clearCurrentOrder = () => {
    currentOrder.value = null
  }

  const goToPage = async (page) => {
    return await fetchOrders({ page })
  }

  const nextPage = async () => {
    if (hasNextPage.value) {
      return await goToPage(pagination.value.page + 1)
    }
  }

  const previousPage = async () => {
    if (hasPreviousPage.value) {
      return await goToPage(pagination.value.page - 1)
    }
  }

  return {
    // State
    orders,
    currentOrder,
    pagination,
    isLoading,
    isCreatingOrder,

    // Computed
    pendingOrders,
    paidOrders,
    processingOrders,
    shippedOrders,
    deliveredOrders,
    cancelledOrders,
    hasNextPage,
    hasPreviousPage,

    // Actions
    fetchOrders,
    fetchOrderByNumber,
    createOrder,
    cancelOrder,
    clearOrders,
    clearCurrentOrder,
    goToPage,
    nextPage,
    previousPage
  }
})
