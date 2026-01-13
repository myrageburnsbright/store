<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

    <!-- Loading -->
    <div v-if="cartStore.isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading cart...</p>
    </div>

    <!-- Empty Cart -->
    <CartEmpty v-else-if="cartStore.isEmpty" />

    <!-- Cart with Items -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Cart Items -->
      <div class="lg:col-span-2 space-y-4">
        <CartItem
          v-for="item in cartStore.cartItems"
          :key="item.id"
          :item="item"
          @update="handleUpdate"
          @remove="handleRemove"
        />

        <!-- Clear Cart -->
        <div class="mt-6 flex justify-between items-center">
          <router-link
            :to="{ name: 'products' }"
            class="btn btn-primary btn-sm text-accent-600 hover:text-accent-700 font-medium"
          >
            ← Continue Shopping
          </router-link>
          <button
            @click="handleClearCart"
            :disabled="cartStore.isUpdating"
            class="text-red-600 hover:text-red-700 font-medium"
          >
            Clear Cart
          </button>
        </div>
      </div>

      <!-- Cart Summary -->
      <div>
        <CartSummary :cart="cartStore.cart" :show-checkout-button="true" :allow-coupon="false" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartEmpty from '@/components/cart/CartEmpty.vue'
import CartItem from '@/components/cart/CartItem.vue'
import CartSummary from '@/components/cart/CartSummary.vue'

const cartStore = useCartStore()

onMounted(async () => {
  if (!cartStore.cart) {
    await cartStore.fetchCart()
  }
})

const handleUpdate = () => {
  // Cart is automatically updated in the store
}

const handleRemove = () => {
  // Cart is automatically updated in the store
}

const handleClearCart = async () => {
  if (confirm('Are you sure you want to clear your cart?')) {
    await cartStore.clearCart()
  }
}
</script>
