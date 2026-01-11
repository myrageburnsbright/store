<template>
  <div class="flex flex-col items-center justify-center py-16 px-4">
    <!-- Empty Cart Icon -->
    <div class="relative mb-6">
      <ShoppingCartIcon class="w-24 h-24 text-gray-300" />
      <div class="absolute -top-2 -right-2 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
        <span class="text-gray-500 font-bold">0</span>
      </div>
    </div>

    <!-- Title -->
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>

    <!-- Description -->
    <p class="text-gray-600 text-center mb-8 max-w-md">
      Looks like you haven't added anything to your cart yet. Browse our products and find something you like!
    </p>

    <!-- CTA Buttons -->
    <div class="flex flex-col sm:flex-row gap-4">
      <router-link :to="{ name: 'products' }" class="btn btn-primary btn-lg">
        <ShoppingBagIcon class="w-5 h-5 mr-2" />
        Start Shopping
      </router-link>

      <router-link
        v-if="isAuthenticated"
        :to="{ name: 'wishlist' }"
        class="btn btn-outline btn-lg"
      >
        <HeartIcon class="w-5 h-5 mr-2" />
        View Wishlist
      </router-link>
    </div>

    <!-- Popular Categories (Optional) -->
    <div class="mt-12 w-full max-w-3xl">
      <h3 class="text-lg font-semibold text-gray-900 mb-4 text-center">
        Popular Categories
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <router-link
          v-for="category in popularCategories"
          :key="category.slug"
          :to="{ name: 'category', params: { slug: category.slug } }"
          class="card card-body text-center hover:shadow-md transition-shadow"
        >
          <span class="text-3xl mb-2">{{ category.icon }}</span>
          <span class="text-sm font-medium text-gray-900">{{ category.name }}</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ShoppingCartIcon, ShoppingBagIcon, HeartIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

// Mock popular categories - in real app, fetch from store
const popularCategories = [
  { name: 'Electronics', slug: 'electronics', icon: '💻' },
  { name: 'Fashion', slug: 'fashion', icon: '👕' },
  { name: 'Home & Garden', slug: 'home-garden', icon: '🏡' },
  { name: 'Sports', slug: 'sports', icon: '⚽' }
]
</script>
