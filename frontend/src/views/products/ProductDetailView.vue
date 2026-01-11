<template>
  <div class="container-content py-8">
    <!-- Loading State -->
    <div v-if="productsStore.isLoadingProduct" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading product...</p>
    </div>

    <!-- Product Detail -->
    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Product Images -->
      <div>
        <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
          <img
            v-if="product.images && product.images.length > 0"
            :src="currentImage"
            :alt="product.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
            No image available
          </div>
        </div>

        <!-- Image Thumbnails -->
        <div v-if="product.images && product.images.length > 1" class="grid grid-cols-4 gap-2">
          <button
            v-for="(image, index) in product.images"
            :key="image.id"
            @click="currentImageIndex = index"
            class="aspect-square bg-gray-100 rounded overflow-hidden border-2 transition-colors"
            :class="currentImageIndex === index ? 'border-accent-600' : 'border-transparent'"
          >
            <img :src="image.image" :alt="`${product.name} ${index + 1}`" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Product Info -->
      <div>
        <!-- Category -->
        <div v-if="product.category" class="mb-2">
          <router-link
            :to="{ name: 'category', params: { slug: product.category.slug } }"
            class="badge badge-gray text-sm hover:bg-gray-200"
          >
            {{ product.category.name }}
          </router-link>
        </div>

        <!-- Product Name -->
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ product.name }}</h1>

        <!-- Rating -->
        <div v-if="product.average_rating" class="flex items-center gap-2 mb-4">
          <div class="star-rating">
            <StarIcon
              v-for="star in 5"
              :key="star"
              class="star"
              :class="star <= product.average_rating ? 'star-filled' : 'star-empty'"
            />
          </div>
          <span class="text-sm text-gray-600">
            {{ product.average_rating }} ({{ product.reviews_count || 0 }} reviews)
          </span>
        </div>

        <!-- Price -->
        <div class="flex items-baseline gap-3 mb-6">
          <span class="text-4xl font-bold text-gray-900">
            ${{ finalPrice }}
          </span>
          <span v-if="product.discount_percentage > 0" class="text-xl text-gray-500 line-through">
            ${{ product.base_price }}
          </span>
          <span v-if="product.discount_percentage > 0" class="badge badge-error">
            -{{ product.discount_percentage }}%
          </span>
        </div>

        <!-- Stock Status -->
        <div class="mb-6">
          <span v-if="product.stock_quantity <= 0" class="stock-badge stock-out">
            Out of Stock
          </span>
          <span v-else-if="product.stock_quantity < 10" class="stock-badge stock-low">
            Only {{ product.stock_quantity }} left in stock
          </span>
          <span v-else class="stock-badge stock-in">
            In Stock
          </span>
        </div>

        <!-- Quantity Selector -->
        <div class="mb-6">
          <label class="form-label mb-2">Quantity</label>
          <div class="quantity-selector">
            <button
              @click="decrementQuantity"
              :disabled="quantity <= 1"
              class="quantity-btn"
            >
              -
            </button>
            <input
              v-model.number="quantity"
              type="number"
              min="1"
              :max="product.stock_quantity"
              class="quantity-input"
            />
            <button
              @click="incrementQuantity"
              :disabled="quantity >= product.stock_quantity"
              class="quantity-btn"
            >
              +
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 mb-6">
          <button
            @click="handleAddToCart"
            :disabled="product.stock_quantity <= 0 || isAddingToCart"
            class="btn btn-primary flex-1"
          >
            <ShoppingCartIcon class="w-5 h-5" />
            <span v-if="isAddingToCart">Adding...</span>
            <span v-else>Add to Cart</span>
          </button>

          <button
            @click="toggleWishlist"
            :disabled="isTogglingWishlist"
            class="btn btn-outline"
          >
            <HeartIcon
              class="w-5 h-5"
              :class="isInWishlist ? 'fill-current text-red-500' : ''"
            />
          </button>
        </div>

        <!-- Description -->
        <div class="border-t pt-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Description</h3>
          <div class="text-gray-600 prose max-w-none" v-html="product.description"></div>
        </div>

        <!-- Brand -->
        <div v-if="product.brand" class="border-t pt-6 mt-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Brand</h3>
          <router-link
            :to="{ name: 'brand', params: { slug: product.brand.slug } }"
            class="text-accent-600 hover:text-accent-700"
          >
            {{ product.brand.name }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Product Not Found -->
    <div v-else class="py-12 text-center">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Product not found</h2>
      <p class="text-gray-600 mb-4">The product you're looking for doesn't exist or has been removed.</p>
      <router-link :to="{ name: 'products' }" class="btn btn-primary">
        Browse Products
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShoppingCartIcon, HeartIcon, StarIcon } from '@heroicons/vue/24/outline'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()

const quantity = ref(1)
const currentImageIndex = ref(0)
const isAddingToCart = ref(false)
const isTogglingWishlist = ref(false)

const product = computed(() => productsStore.currentProduct)

const currentImage = computed(() => {
  if (product.value?.images && product.value.images.length > 0) {
    return product.value.images[currentImageIndex.value].image
  }
  return null
})

const finalPrice = computed(() => {
  return product.value ? Number(product.value.price || product.value.base_price).toFixed(2) : '0.00'
})

const isInWishlist = computed(() => {
  return product.value ? wishlistStore.isInWishlist(product.value.id) : false
})

onMounted(async () => {
  const slug = route.params.slug
  try {
    await productsStore.fetchProductBySlug(slug)
    if (authStore.isAuthenticated && wishlistStore.wishlistItems.length === 0) {
      await wishlistStore.fetchWishlist()
    }
  } catch (error) {
    console.error('Failed to fetch product:', error)
  }
})

const incrementQuantity = () => {
  if (quantity.value < product.value.stock_quantity) {
    quantity.value++
  }
}

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

const handleAddToCart = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  isAddingToCart.value = true
  try {
    await cartStore.addToCart({
      product_id: product.value.id,
      quantity: quantity.value
    })
    quantity.value = 1
  } catch (error) {
    console.error('Failed to add to cart:', error)
  } finally {
    isAddingToCart.value = false
  }
}

const toggleWishlist = async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  isTogglingWishlist.value = true
  try {
    await wishlistStore.toggleWishlist(product.value.id)
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
  } finally {
    isTogglingWishlist.value = false
  }
}
</script>
