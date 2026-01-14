<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">Shop by Category</h1>
    <p class="text-gray-600 mb-8">Browse our wide selection of products by category</p>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading categories...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="rootCategories.length === 0" class="card card-body text-center py-12">
      <p class="text-gray-600">No categories available at the moment</p>
    </div>

    <!-- Hierarchical Categories -->
    <div v-else class="space-y-10">
      <!-- Root Category Section -->
      <div
        v-for="rootCategory in rootCategories"
        :key="rootCategory.id"
        class="category-section"
      >
        <!-- Root Category Header -->
        <div class="mb-6">
          <router-link
            :to="{ name: 'category', params: { slug: rootCategory.slug } }"
            class="inline-flex items-center gap-3 group"
          >
            <!-- Icon/Image -->
            <div v-if="rootCategory.image" class="w-16 h-16 rounded-lg overflow-hidden">
              <img
                :src="rootCategory.image"
                :alt="rootCategory.name"
                class="w-full h-full object-cover"
              />
            </div>
            <div
              v-else
              class="w-16 h-16 bg-gradient-to-br from-accent-100 to-accent-200 rounded-lg flex items-center justify-center"
            >
              <span class="text-3xl">{{ getCategoryIcon(rootCategory.slug) }}</span>
            </div>

            <!-- Name & Arrow -->
            <div class="flex-1">
              <h2 class="text-2xl font-bold text-gray-900 group-hover:text-accent-600 transition-colors">
                {{ rootCategory.name }}
              </h2>
              <p v-if="rootCategory.description" class="text-sm text-gray-600 mt-1">
                {{ rootCategory.description }}
              </p>
            </div>

            <ChevronRightIcon class="w-6 h-6 text-accent-600 group-hover:translate-x-1 transition-transform" />
          </router-link>
        </div>

        <!-- Subcategories (Level 2) -->
        <div
          v-if="rootCategory.children && rootCategory.children.length > 0"
          class="space-y-6 pl-4"
        >
          <div
            v-for="subCategory in rootCategory.children"
            :key="subCategory.id"
            class="subcategory-section"
          >
            <!-- Level 2 Category Header -->
            <div class="mb-4">
              <router-link
                :to="{ name: 'category', params: { slug: subCategory.slug } }"
                class="inline-flex items-center gap-2 group"
              >
                <!-- Subcategory Icon (smaller) -->
                <div v-if="subCategory.image" class="w-10 h-10 rounded overflow-hidden">
                  <img
                    :src="subCategory.image"
                    :alt="subCategory.name"
                    class="w-full h-full object-cover"
                  />
                </div>
                <div
                  v-else
                  class="w-10 h-10 bg-gradient-to-br from-gray-100 to-gray-200 rounded flex items-center justify-center"
                >
                  <span class="text-xl">{{ getCategoryIcon(subCategory.slug) }}</span>
                </div>

                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-accent-600 transition-colors">
                  {{ subCategory.name }}
                </h3>

                <span class="text-xs text-gray-500">
                  ({{ subCategory.products_count || 0 }} products)
                </span>

                <ChevronRightIcon class="w-4 h-4 text-accent-600 group-hover:translate-x-1 transition-transform" />
              </router-link>
            </div>

            <!-- Level 3 Categories Grid (if exists) -->
            <div
              v-if="getCategoryChildren(subCategory.id).length > 0"
              class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 pl-4"
            >
              <router-link
                v-for="childCategory in getCategoryChildren(subCategory.id)"
                :key="childCategory.id"
                :to="{ name: 'category', params: { slug: childCategory.slug } }"
                class="card card-body p-3 group hover:shadow-md transition-all cursor-pointer border border-gray-200"
              >
                <!-- Child Category Icon -->
                <div v-if="childCategory.image" class="aspect-square mb-2 overflow-hidden rounded">
                  <img
                    :src="childCategory.image"
                    :alt="childCategory.name"
                    class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <div
                  v-else
                  class="aspect-square mb-2 bg-gradient-to-br from-gray-50 to-gray-100 rounded flex items-center justify-center"
                >
                  <span class="text-2xl">{{ getCategoryIcon(childCategory.slug) }}</span>
                </div>

                <!-- Child Category Name -->
                <h4 class="text-xs font-medium text-gray-900 group-hover:text-accent-600 transition-colors line-clamp-2">
                  {{ childCategory.name }}
                </h4>

                <!-- Product Count -->
                <p class="text-xs text-gray-500 mt-1">
                  {{ childCategory.products_count || 0 }} products
                </p>
              </router-link>
            </div>

            <!-- No Children - Show as Single Card -->
            <div v-else class="pl-4">
              <router-link
                :to="{ name: 'category', params: { slug: subCategory.slug } }"
                class="inline-block text-sm text-accent-600 hover:text-accent-700 hover:underline"
              >
                View all {{ subCategory.name }} products →
              </router-link>
            </div>
          </div>
        </div>

        <!-- "View All" Button for Root Category -->
        <div v-else class="pl-4">
          <router-link
            :to="{ name: 'category', params: { slug: rootCategory.slug } }"
            class="btn btn-outline"
          >
            View all {{ rootCategory.name }} products
            <ChevronRightIcon class="w-4 h-4 ml-2" />
          </router-link>
        </div>

        <!-- Divider (not after last category) -->
        <hr v-if="rootCategory !== rootCategories[rootCategories.length - 1]" class="mt-10 border-gray-200" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { categoriesAPI } from '@/services/api'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

const isLoading = ref(true)
const allCategories = ref([])

// Get only root categories (no parent)
// parent can be null (root) or a number (child category ID)
const rootCategories = computed(() => {
  return allCategories.value.filter(cat => cat.parent === null || cat.parent === undefined)
})

// Map category slugs to emoji icons (fallback if no image)
const categoryIcons = {
  base: '🏪',
  electronics: '💻',
  clothing: '👕',
  fashion: '👕',
  'home-garden': '🏡',
  'home': '🏡',
  sports: '⚽',
  books: '📚',
  toys: '🧸',
  beauty: '💄',
  food: '🍔',
  automotive: '🚗',
  health: '🏥',
  smartphones: '📱',
  laptops: '💻',
  tablets: '📱',
  accessories: '🎧',
  'mens-clothing': '👔',
  'womens-clothing': '👗',
  shoes: '👟',
  furniture: '🛋️',
  decor: '🖼️',
  jewlery: '💎',
  necklace: '📿',
  ring: '💍',
  headphones: '🎧',
  cameras: '📷',
  default: '🛍️'
}

const getCategoryIcon = (slug) => {
  return categoryIcons[slug] || categoryIcons.default
}

// Get children of a specific category by ID
const getCategoryChildren = (parentId) => {
  return allCategories.value.filter(cat => cat.parent === parentId)
}

onMounted(async () => {
  isLoading.value = true
  try {
    // Fetch all categories - backend will return them with children
    const response = await categoriesAPI.getAll()
    allCategories.value = response.data.results || response.data || []
  } catch (error) {
    console.error("[CategoriesView] Error fetching categories:", error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.category-section {
  scroll-margin-top: 100px; /* For smooth scroll to anchors */
}
</style>