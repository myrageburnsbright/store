<template>
  <div class="min-h-screen bg-white">
    <!-- Hero Section -->
    <section style="background: linear-gradient(to right, #2563eb, #1d4ed8);" class="text-white">
      <div class="container-content py-20 text-center">
        <h1 class="text-4xl md:text-5xl font-bold mb-6">
          Welcome to Our Store
        </h1>
        <p class="text-xl mb-8 max-w-2xl mx-auto" style="opacity: 0.95;">
          Discover amazing products at great prices. Shop with confidence and enjoy fast shipping on all orders.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link :to="{ name: 'products' }" class="btn btn-lg bg-white hover:bg-gray-100" style="color: #2563eb;">
            Shop Now
          </router-link>
          <router-link :to="{ name: 'categories' }" class="btn btn-lg btn-outline border-white text-white  hover:bg-white" style="border-color: white; color: #2563eb;">
            Browse Categories
          </router-link>
        </div>
      </div>
    </section>

    <!-- Featured Products -->
    <section class="py-12 bg-white">
      <div class="container-content">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-900">Featured Products</h2>
          <router-link :to="{ name: 'products' }" class="text-accent-600 hover:text-accent-700 font-medium">
            View All →
          </router-link>
        </div>

        <div v-if="productsStore.isLoading" class="py-12 text-center">
          <div class="loading-spinner mx-auto"></div>
          <p class="text-gray-600 mt-4">Loading products...</p>
        </div>

        <ProductGrid
          v-else
          :products="featuredProducts"
          :loading="false"
        />
      </div>
    </section>

    <!-- Categories Section -->
    <section class="py-12 bg-gray-50">
      <div class="container-content">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-900">Shop by Category</h2>
          <router-link :to="{ name: 'categories' }" class="text-accent-600 hover:text-accent-700 font-medium">
            View All →
          </router-link>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <router-link
            v-for="category in displayCategories"
            :key="category.id"
            :to="{ name: 'category', params: { slug: category.slug } }"
            class="card card-body text-center hover:shadow-lg transition-all group"
          >
            <div class="aspect-square mb-3 bg-gradient-to-br from-accent-100 to-accent-200 rounded-lg flex items-center justify-center">
              <span class="text-4xl">{{ getCategoryIcon(category.slug) }}</span>
            </div>
            <h3 class="text-sm font-semibold text-gray-900 group-hover:text-accent-600 transition-colors">
              {{ category.name }}
            </h3>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Popular Products -->
    <section class="py-12 bg-white">
      <div class="container-content">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-900">Popular Products</h2>
          <router-link :to="{ name: 'products', query: { ordering: '-sales_count' } }" class="text-accent-600 hover:text-accent-700 font-medium">
            View All →
          </router-link>
        </div>

        <ProductGrid
          :products="popularProducts"
          :loading="productsStore.isLoading"
        />
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-12 bg-gray-50">
      <div class="container-content">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TruckIcon class="w-8 h-8 text-accent-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Free Shipping</h3>
            <p class="text-gray-600 text-sm">On orders over $50</p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShieldCheckIcon class="w-8 h-8 text-accent-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Secure Payment</h3>
            <p class="text-gray-600 text-sm">100% secure transactions</p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ArrowPathIcon class="w-8 h-8 text-accent-600" />
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Easy Returns</h3>
            <p class="text-gray-600 text-sm">30-day return policy</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter CTA -->
    <section v-if="!authStore.isAuthenticated" class="py-12 bg-accent-600 text-white">
      <div class="container-content text-center">
        <h2 class="text-3xl font-bold mb-3">Join Our Community</h2>
        <p class="text-accent-100 mb-8 max-w-2xl mx-auto">
          Create an account to track your orders, save your wishlist, and get exclusive deals.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link :to="{ name: 'register' }" class="btn btn-lg bg-white text-accent-600 hover:bg-gray-100">
            Create Account
          </router-link>
          <router-link :to="{ name: 'login' }" class="btn btn-lg btn-outline border-white text-white hover:bg-white hover:text-accent-600">
            Sign In
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProductsStore } from '@/stores/products'
import ProductGrid from '@/components/products/ProductGrid.vue'
import { TruckIcon, ShieldCheckIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const productsStore = useProductsStore()

const featuredProducts = computed(() => productsStore.products.slice(0, 8))
const popularProducts = computed(() => {
  return [...productsStore.products]
    .sort((a, b) => (b.sales_count || 0) - (a.sales_count || 0))
    .slice(0, 8)
})

const displayCategories = computed(() => productsStore.categories.slice(0, 6))

const categoryIcons = {
  electronics: '💻',
  fashion: '👕',
  'home-garden': '🏡',
  sports: '⚽',
  books: '📚',
  toys: '🧸',
  beauty: '💄',
  food: '🍔',
  automotive: '🚗',
  health: '🏥',
  default: '🛍️'
}

const getCategoryIcon = (slug) => {
  return categoryIcons[slug] || categoryIcons.default
}

onMounted(async () => {
  await Promise.all([
    productsStore.fetchProducts({ page_size: 16 }),
    productsStore.fetchCategories()
  ])
})
</script>
