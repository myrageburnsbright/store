<template>
  <div class="container-content py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">My Wishlist</h1>
      <span v-if="wishlistStore.wishlistCount > 0" class="text-gray-600">
        {{ wishlistStore.wishlistCount }} {{ wishlistStore.wishlistCount === 1 ? 'item' : 'items' }}
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="wishlistStore.isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading wishlist...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="wishlistStore.wishlistCount === 0" class="card card-body text-center py-12">
      <div class="mb-6">
        <HeartIcon class="w-20 h-20 mx-auto text-gray-300" />
      </div>
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Your wishlist is empty</h2>
      <p class="text-gray-600 mb-6">
        Save your favorite items to your wishlist and shop them later!
      </p>
      <router-link :to="{ name: 'products' }" class="btn btn-primary mx-auto">
        <ShoppingBagIcon class="w-5 h-5 mr-2" />
        Browse Products
      </router-link>
    </div>

    <!-- Wishlist Items -->
    <div v-else>
      <!-- Action Bar -->
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <p class="text-sm text-gray-600">
          {{ wishlistStore.wishlistCount }} {{ wishlistStore.wishlistCount === 1 ? 'product' : 'products' }} in your wishlist
        </p>

        <!-- Add All to Cart Button -->
        <button
          @click="handleAddAllToCart"
          :disabled="isAddingAll || !hasInStockItems"
          class="btn btn-outline"
        >
          <ShoppingCartIcon class="w-5 h-5 mr-2" />
          {{ isAddingAll ? 'Adding to Cart...' : 'Add All to Cart' }}
        </button>
      </div>

      <!-- Wishlist Grid -->
      <div class="space-y-4">
        <WishlistItem
          v-for="item in wishlistStore.wishlistItems"
          :key="item.id"
          :item="item"
        />
      </div>

      <!-- Recommendations -->
      <div v-if="wishlistStore.wishlistCount > 0" class="mt-12">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">You May Also Like</h2>
        </div>
        <p class="text-gray-600 text-center py-8">
          Browse our products to discover more items you'll love
        </p>
        <div class="text-center">
          <router-link :to="{ name: 'products' }" class="btn btn-primary">
            Continue Shopping
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWishlistStore } from '@/stores/wishlist'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'
import WishlistItem from '@/components/wishlist/WishlistItem.vue'
import { HeartIcon, ShoppingBagIcon, ShoppingCartIcon } from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'

const wishlistStore = useWishlistStore()
const cartStore = useCartStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const isAddingAll = ref(false)

const hasInStockItems = computed(() => {
  return wishlistStore.wishlistItems.some(item => item.product.stock_quantity > 0)
})

const handleAddAllToCart = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  isAddingAll.value = true
  let successCount = 0
  let failCount = 0

  try {
    // Add each in-stock item to cart
    for (const item of wishlistStore.wishlistItems) {
      if (item.product.stock_quantity > 0) {
        try {
          await cartStore.addToCart({
            product_id: item.product.id,
            quantity: 1
          })
          successCount++
        } catch (error) {
          failCount++
        }
      }
    }

    if (successCount > 0) {
      toast.success(`Added ${successCount} ${successCount === 1 ? 'item' : 'items'} to cart`)
    }

    if (failCount > 0) {
      toast.warning(`Could not add ${failCount} ${failCount === 1 ? 'item' : 'items'} to cart`)
    }
  } finally {
    isAddingAll.value = false
  }
}

onMounted(async () => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  // Fetch wishlist if not already loaded
  if (wishlistStore.wishlistItems.length === 0) {
    await wishlistStore.fetchWishlist()
  }
})
</script>
