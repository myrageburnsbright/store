<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Shop by Category</h1>
    <p class="text-gray-600 mb-8">Browse our wide selection of products by category</p>

    <!-- Loading State -->
    <div v-if="productsStore.isLoadingCategories" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading categories...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="categories.length === 0" class="card card-body text-center py-12">
      <p class="text-gray-600">No categories available at the moment</p>
    </div>

    <!-- Categories Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <router-link
        v-for="category in categories"
        :key="category.id"
        :to="{ name: 'category', params: { slug: category.slug } }"
        class="card card-body group hover:shadow-lg transition-all cursor-pointer"
      >
        <!-- Category Image (if available) -->
        <div v-if="category.image" class="aspect-square mb-4 overflow-hidden rounded-lg">
          <img
            :src="category.image"
            :alt="category.name"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>

        <!-- Category Icon Placeholder (if no image) -->
        <div
          v-else
          class="aspect-square mb-4 bg-gradient-to-br from-accent-100 to-accent-200 rounded-lg flex items-center justify-center"
        >
          <span class="text-5xl">{{ getCategoryIcon(category.slug) }}</span>
        </div>

        <!-- Category Info -->
        <h3 class="text-lg font-semibold text-gray-900 group-hover:text-accent-600 transition-colors">
          {{ category.name }}
        </h3>

        <p v-if="category.description" class="text-sm text-gray-600 mt-2 line-clamp-2">
          {{ category.description }}
        </p>

        <!-- Product Count -->
        <p class="text-sm text-gray-500 mt-3">
          {{ category.product_count || 0 }} {{ (category.product_count || 0) === 1 ? 'product' : 'products' }}
        </p>

        <!-- View Category Arrow -->
        <div class="mt-4 flex items-center text-accent-600 font-medium text-sm">
          <span>View Category</span>
          <ChevronRightIcon class="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

const productsStore = useProductsStore()

const categories = computed(() => productsStore.categories)

// Map category slugs to emoji icons (fallback if no image)
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
  if (productsStore.categories.length === 0) {
    await productsStore.fetchCategories()
  }
})
</script>