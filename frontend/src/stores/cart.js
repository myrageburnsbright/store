import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { cartAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useCartStore = defineStore('cart', () => {
  // State
  const cart = ref(null)
  const isLoading = ref(false)
  const isUpdating = ref(false)

  // Computed
  const cartItems = computed(() => cart.value?.items || [])

  const itemCount = computed(() => {
    return cartItems.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const subtotal = computed(() => {
    return cart.value?.subtotal || '0.00'
  })

  const totalDiscount = computed(() => {
    return cart.value?.total_discount || '0.00'
  })

  const total = computed(() => {
    return cart.value?.total || '0.00'
  })

  const isEmpty = computed(() => {
    return !cart.value || cartItems.value.length === 0
  })

  // Actions
  const fetchCart = async () => {
    isLoading.value = true
    try {
      const response = await cartAPI.getCart()
      cart.value = response.data
      return cart.value
    } catch (error) {
      console.error('Error fetching cart:', error)
      cart.value = null
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const addToCart = async ({ product_id, variant_id = null, quantity = 1 }) => {
    isUpdating.value = true
    try {
      const response = await cartAPI.addItem({
        product_id,
        variant_id,
        quantity
      })
      cart.value = response.data
      toast.success('Product added to cart')
      return cart.value
    } catch (error) {
      if (error.response?.status === 400) {
        toast.error(error.response.data?.error || 'Unable to add product to cart')
      } else {
        toast.error('Failed to add product to cart')
      }
      throw error
    } finally {
      isUpdating.value = false
    }
  }

  const updateQuantity = async (itemId, quantity) => {
    isUpdating.value = true
    try {
      const response = await cartAPI.updateItem(itemId, { quantity })
      cart.value = response.data
      toast.success('Cart updated')
      return cart.value
    } catch (error) {
      console.error('Error updating cart item:', error)
      if (error.response?.status === 400) {
        toast.error(error.response.data?.error || 'Insufficient stock')
      } else {
        toast.error('Failed to update cart')
      }
      throw error
    } finally {
      isUpdating.value = false
    }
  }

  const removeItem = async (itemId) => {
    isUpdating.value = true
    try {
      const response = await cartAPI.removeItem(itemId)
      cart.value = response.data
      toast.success('Item removed from cart')
      return cart.value
    } catch (error) {
      console.error('Error removing cart item:', error)
      toast.error('Failed to remove item')
      throw error
    } finally {
      isUpdating.value = false
    }
  }

  const clearCart = async () => {
    isUpdating.value = true
    try {
      const response = await cartAPI.clear()
      cart.value = response.data
      toast.success('Cart cleared')
      return cart.value
    } catch (error) {
      console.error('Error clearing cart:', error)
      toast.error('Failed to clear cart')
      throw error
    } finally {
      isUpdating.value = false
    }
  }

  const refreshCart = async () => {
    return await fetchCart()
  }

  const getItemByProduct = (productId, variantId = null) => {
    return cartItems.value.find(item =>
      item.product.id === productId &&
      (variantId ? item.variant?.id === variantId : !item.variant)
    )
  }

  const isProductInCart = (productId, variantId = null) => {
    return !!getItemByProduct(productId, variantId)
  }

  const resetCart = () => {
    cart.value = null
    isLoading.value = false
    isUpdating.value = false
  }

  return {
    // State
    cart,
    isLoading,
    isUpdating,

    // Computed
    cartItems,
    itemCount,
    subtotal,
    totalDiscount,
    total,
    isEmpty,

    // Actions
    fetchCart,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    refreshCart,
    getItemByProduct,
    isProductInCart,
    resetCart
  }
})
