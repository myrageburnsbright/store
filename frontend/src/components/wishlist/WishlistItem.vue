<template>
  <div class="card">
    <div class="card-body">
      <div class="flex gap-4">
        <!-- Product Image -->
        <router-link
          :to="{ name: 'product-detail', params: { slug: item.product.slug } }"
          class="flex-shrink-0"
        >
          <div class="relative w-24 h-24">
            <img
              v-if="productImage"
              :src="productImage"
              :alt="item.product.name"
              class="w-full h-full object-cover rounded"
            />
            <div v-else class="w-full h-full bg-gray-200 rounded flex items-center justify-center">
              <ShoppingBagIcon class="w-8 h-8 text-gray-400" />
            </div>

            <!-- Out of Stock Overlay -->
            <div
              v-if="item.product.stock_quantity === 0"
              class="absolute inset-0 bg-black bg-opacity-50 rounded flex items-center justify-center"
            >
              <span class="text-white text-xs font-semibold">Out of Stock</span>
            </div>
          </div>
        </router-link>

        <!-- Product Info -->
        <div class="flex-1 min-w-0">
          <router-link
            :to="{ name: 'product-detail', params: { slug: item.product.slug } }"
            class="text-lg font-semibold text-gray-900 hover:text-accent-600 transition-colors line-clamp-2"
          >
            {{ item.product.name }}
          </router-link>

          <!-- Category & Brand -->
          <p class="text-sm text-gray-600 mt-1">
            {{ item.product.category_name || 'Uncategorized' }}
            <span v-if="item.product.brand"> • {{ item.product.brand.name }}</span>
          </p>

          <!-- Rating -->
          <div class="flex items-center gap-2 mt-2">
            <div class="star-rating">
              <StarIcon
                v-for="star in 5"
                :key="star"
                class="star"
                :class="star <= item.product.average_rating ? 'star-filled' : 'star-empty'"
              />
            </div>
            <span class="text-sm text-gray-600">
              ({{ item.product.reviews_count || 0 }})
            </span>
          </div>

          <!-- Stock Status -->
          <div class="mt-2">
            <span
              v-if="item.product.stock_quantity > 0 && item.product.stock_quantity < 5"
              class="stock-badge stock-low"
            >
              Only {{ item.product.stock_quantity }} left
            </span>
            <span
              v-else-if="item.product.stock_quantity === 0"
              class="stock-badge stock-out"
            >
              Out of Stock
            </span>
            <span
              v-else
              class="stock-badge stock-in"
            >
              In Stock
            </span>
          </div>
        </div>

        <!-- Price & Actions -->
        <div class="flex flex-col items-end justify-between">
          <!-- Price -->
          <div class="text-right">
            <p class="price text-xl">
              ${{ finalPrice }}
            </p>
            <p v-if="hasDiscount" class="price-old text-sm">
              ${{ parseFloat(item.product.base_price).toFixed(2) }}
            </p>
            <p v-if="hasDiscount" class="price-discount text-xs">
              Save {{ item.product.discount_percentage }}%
            </p>
          </div>

          <!-- Actions -->
          <div class="flex flex-col gap-2 w-full">
            <button
              @click="handleAddToCart"
              :disabled="item.product.stock_quantity === 0 || isAddingToCart"
              class="btn btn-primary btn-sm w-full"
            >
              <ShoppingCartIcon class="w-4 h-4 mr-1" />
              {{ isAddingToCart ? 'Adding...' : 'Add to Cart' }}
            </button>

            <button
              @click="handleRemove"
              :disabled="isRemoving"
              class="btn btn-outline btn-sm w-full text-error-600 hover:bg-error-50"
            >
              <TrashIcon class="w-4 h-4 mr-1" />
              {{ isRemoving ? 'Removing...' : 'Remove' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useAuthStore } from '@/stores/auth'
import { useProductImage } from '@/composables/useProductImage'
import { StarIcon } from '@heroicons/vue/24/solid'
import { ShoppingBagIcon, ShoppingCartIcon, TrashIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()
const router = useRouter()

const isAddingToCart = ref(false)
const isRemoving = ref(false)

// Get product image - handle both list API (primary_image) and detail API (images array)
const productImage = computed(() => {
  const base = api.defaults.baseURL.replace(/\/$/, '')
  // From list API: primary_image is an object with {image: 'url'}
  if (props.item.product.primary_image && props.item.product.primary_image.image) {
    const imgPath = props.item.product.primary_image.image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  // From detail API: images is an array
  if (props.item.product.images && props.item.product.images.length > 0) {
    const imgPath = props.item.product.images[0].image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  return null
})
const hasDiscount = computed(() => {
  return props.item.product.discount_percentage > 0
})

const finalPrice = computed(() => {
  return Number(props.item.product.price || props.item.product.base_price).toFixed(2)
})

const handleAddToCart = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  isAddingToCart.value = true
  try {
    await cartStore.addToCart({
      product_id: props.item.product.id,
      quantity: 1
    })

    // Optionally remove from wishlist after adding to cart
    // await wishlistStore.removeFromWishlist(props.item.product.id)
  } catch (error) {
    console.error("[WishlistItem] Error adding to cart:", error)
  } finally {
    isAddingToCart.value = false
  }
}

const handleRemove = async () => {
  isRemoving.value = true
  try {
    await wishlistStore.removeFromWishlist(props.item.product.id)
  } catch (error) {
    console.error("[WishlistItem] Error removing from wishlist:", error)
  } finally {
    isRemoving.value = false
  }
}
</script>
