import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { wishlistAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useWishlistStore = defineStore('wishlist', () => {
  // State
  const wishlistItems = ref([])
  const isLoading = ref(false)

  // Computed
  const wishlistCount = computed(() => wishlistItems.value.length)

  const wishlistProductIds = computed(() =>
    wishlistItems.value.map(item => item.product.id)
  )

  // Actions
  const fetchWishlist = async () => {
    isLoading.value = true
    try {
      const response = await wishlistAPI.getAll()
      wishlistItems.value = response.data.results || response.data || []
      return wishlistItems.value
    } catch (error) {
      console.error('Error fetching wishlist:', error)
      wishlistItems.value = []
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const addToWishlist = async (productId) => {
    try {
      const response = await wishlistAPI.add({ product_id: productId })
      await fetchWishlist()
      toast.success('Added to wishlist')
      return response.data
    } catch (error) {
      console.error('Error adding to wishlist:', error)
      toast.error('Failed to add to wishlist')
      throw error
    }
  }

  const removeFromWishlist = async (productId) => {
    try {
      await wishlistAPI.remove(productId)
      wishlistItems.value = wishlistItems.value.filter(
        item => item.product.id !== productId
      )
      toast.success('Removed from wishlist')
    } catch (error) {
      console.error('Error removing from wishlist:', error)
      toast.error('Failed to remove from wishlist')
      throw error
    }
  }

  const isInWishlist = (productId) => {
    return wishlistProductIds.value.includes(productId)
  }

  const toggleWishlist = async (productId) => {
    if (isInWishlist(productId)) {
      await removeFromWishlist(productId)
    } else {
      await addToWishlist(productId)
    }
  }

  const resetWishlist = () => {
    wishlistItems.value = []
    isLoading.value = false
  }

  return {
    // State
    wishlistItems,
    isLoading,

    // Computed
    wishlistCount,
    wishlistProductIds,

    // Actions
    fetchWishlist,
    addToWishlist,
    removeFromWishlist,
    isInWishlist,
    toggleWishlist,
    resetWishlist
  }
})
