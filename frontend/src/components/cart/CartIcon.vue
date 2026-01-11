<template>
  <router-link
    :to="{ name: 'cart' }"
    class="relative inline-flex items-center p-2 text-gray-700 hover:text-accent-600 transition-colors"
  >
    <ShoppingBagIcon class="w-6 h-6" />
    <span
      v-if="itemCount > 0"
      class="cart-badge"
    >
      {{ itemCount > 99 ? '99+' : itemCount }}
    </span>
  </router-link>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import { ShoppingBagIcon } from '@heroicons/vue/24/outline'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const cartStore = useCartStore()
const authStore = useAuthStore()

const itemCount = computed(() => {
  return cartStore.itemCount
})

const fetchCartIfNeeded = async () => {
  if (authStore.isAuthenticated) {
    try {
      await cartStore.fetchCart()
    } catch (error) {
      // Handle error silently
    }
  }
}

onMounted(async () => {
  if (authStore.isAuthenticated && !cartStore.cart) {
    await fetchCartIfNeeded()
  }
})

// Watch for authentication changes (login/logout)
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await fetchCartIfNeeded()
  } else {
    cartStore.resetCart()
  }
})
</script>
