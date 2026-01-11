<template>
  <button
    @click.stop="handleToggle"
    :disabled="isLoading"
    :class="buttonClass"
    :title="isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'"
    class="transition-all duration-200"
  >
    <HeartIcon
      :class="[
        iconClass,
        isInWishlist ? 'text-red-500 fill-current' : 'text-gray-600'
      ]"
    />
  </button>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWishlistStore } from '@/stores/wishlist'
import { useAuthStore } from '@/stores/auth'
import { HeartIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  productId: {
    type: Number,
    required: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  variant: {
    type: String,
    default: 'icon',
    validator: (value) => ['icon', 'button'].includes(value)
  }
})

const wishlistStore = useWishlistStore()
const authStore = useAuthStore()
const router = useRouter()

const isLoading = ref(false)

const isInWishlist = computed(() => {
  return wishlistStore.isInWishlist(props.productId)
})

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6'
}

const buttonSizeClasses = {
  sm: 'p-1.5',
  md: 'p-2',
  lg: 'p-3'
}

const iconClass = computed(() => sizeClasses[props.size])

const buttonClass = computed(() => {
  const baseClasses = 'rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-accent-500 disabled:opacity-50 disabled:cursor-not-allowed'

  if (props.variant === 'button') {
    return `btn btn-outline ${baseClasses}`
  }

  return `${buttonSizeClasses[props.size]} ${baseClasses}`
})

const handleToggle = async () => {
  // Check if user is authenticated
  if (!authStore.isAuthenticated) {
    router.push({
      name: 'login',
      query: { redirect: router.currentRoute.value.fullPath }
    })
    return
  }

  isLoading.value = true
  try {
    await wishlistStore.toggleWishlist(props.productId)
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
  } finally {
    isLoading.value = false
  }
}

// Fetch wishlist on mount if user is authenticated
onMounted(async () => {
  if (authStore.isAuthenticated && wishlistStore.wishlistItems.length === 0) {
    await wishlistStore.fetchWishlist()
  }
})
</script>
