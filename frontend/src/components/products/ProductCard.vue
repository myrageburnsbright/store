<template>
  <div class="card group cursor-pointer" @click="navigateToProduct">
    <!-- Product Image -->
    <div class="relative aspect-[4/3] overflow-hidden">
      <img
        v-if="productImage"
        :src="productImage"
        :alt="product.name"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div
        v-else
        class="w-full h-full bg-gray-200 flex items-center justify-center"
      >
        <span class="text-gray-400">No image</span>
      </div>

      <!-- Stock Badge -->
      <div class="absolute top-2 left-2">
        <span
          v-if="product.stock_quantity <= 0"
          class="stock-badge stock-out"
        >
          Out of Stock
        </span>
        <span
          v-else-if="product.stock_quantity < 10"
          class="stock-badge stock-low"
        >
          Low Stock
        </span>
      </div>

      <!-- Discount Badge (top-left) -->
      <div
        v-if="product.discount_percentage > 0"
        class="absolute top-2 left-2 z-10"
      >
        <span class="badge badge-xl text-base badge-error opacity-75 border border-red-150">
          -{{ product.discount_percentage }}%
        </span>
      </div>

      <!-- Wishlist Button (top-right) -->
      <button
        class="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md opacity-0 group-hover:opacity-100 transition-opacity z-10"
        @click.stop="toggleWishlist"
        :disabled="isTogglingWishlist"
      >
        <HeartIcon
          class="w-5 h-5"
          :class="isInWishlist ? 'text-red-500 fill-current' : 'text-gray-600'"
        />
      </button>
    </div>

    <!-- Product Info -->
    <div class="card-body">
      <!-- Category -->
      <div v-if="product.category" class="mb-2">
        <span class="badge badge-gray text-xs">
          {{ product.category.name }}
        </span>
      </div>

      <!-- Product Name -->
      <h3 class="text-lg font-semibold text-gray-900 line-clamp-2 mb-2">
        {{ product.name }}
      </h3>

      <!-- Rating -->
      <div v-if="product.average_rating" class="flex items-center gap-2 mb-2">
        <div class="star-rating">
          <StarIcon
            v-for="star in 5"
            :key="star"
            class="star"
            :class="star <= product.average_rating ? 'star-filled' : 'star-empty'"
          />
        </div>
        <span class="text-sm text-gray-600">
          ({{ product.reviews_count || 0 }})
        </span>
      </div>

      <!-- Price -->
      <div class="flex items-center gap-2 mb-3">
        <span class="text-xl font-bold text-gray-900">
          ${{ finalPrice }}
        </span>
        <span v-if="product.discount_percentage > 0" class="text-sm text-gray-500 line-through">
          ${{ product.base_price }}
        </span>
      </div>

      <!-- Add to Cart Button -->
      <button
        class="btn btn-primary w-full"
        @click.stop="handleAddToCart"
        :disabled="product.stock_quantity <= 0 || isAddingToCart"
      >
        <ShoppingCartIcon class="w-5 h-5" />
        <span v-if="product.stock_quantity <= 0">Out of Stock</span>
        <span v-else-if="isAddingToCart">Adding...</span>
        <span v-else>Add to Cart</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { HeartIcon, ShoppingCartIcon, StarIcon } from '@heroicons/vue/24/outline'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()

const isAddingToCart = ref(false)
const isTogglingWishlist = ref(false)

// Get product image - handle both list API (primary_image) and detail API (images array)
const productImage = computed(() => {
  // From list API: primary_image is an object with {image: 'url'}
  if (props.product.primary_image && props.product.primary_image.image) {
    return props.product.primary_image.image
  }
  // From detail API: images is an array
  if (props.product.images && props.product.images.length > 0) {
    return props.product.images[0].image
  }
  return null
})

// Use server-calculated price instead of calculating on frontend
const finalPrice = computed(() => {
  return Number(props.product.price || props.product.base_price).toFixed(2)
})

const isInWishlist = computed(() => {
  return wishlistStore.isInWishlist(props.product.id)
})

const navigateToProduct = () => {
  router.push({
    name: 'product-detail',
    params: { slug: props.product.slug }
  })
}

const handleAddToCart = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  isAddingToCart.value = true
  try {
    await cartStore.addToCart({
      product_id: props.product.id,
      quantity: 1
    })
  } catch (error) {
    // Error handled by store
  } finally {
    isAddingToCart.value = false
  }
}

const toggleWishlist = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }

  isTogglingWishlist.value = true
  try {
    await wishlistStore.toggleWishlist(props.product.id)
  } catch (error) {
    // Error handled by store
  } finally {
    isTogglingWishlist.value = false
  }
}
</script>
