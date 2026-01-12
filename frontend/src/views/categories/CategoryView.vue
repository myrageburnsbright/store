<template>
  <div class="container-content py-8">
    <!-- Breadcrumb -->
    <BreadcrumbsNav v-if="category" :breadcrumbs="breadcrumbs" />

    <!-- Loading State -->
    <div v-if="isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading category...</p>
    </div>

    <!-- Category Not Found -->
    <div v-else-if="!category" class="card card-body text-center py-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">Category Not Found</h2>
      <p class="text-gray-600 mb-6">
        The category you're looking for doesn't exist.
      </p>
      <router-link :to="{ name: 'categories' }" class="btn btn-primary mx-auto">
        Browse All Categories
      </router-link>
    </div>

    <!-- Category Content -->
    <div v-else>
      <!-- Category Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ category.name }}</h1>
        <p v-if="category.description" class="text-gray-600 max-w-3xl">
          {{ category.description }}
        </p>
      </div>

      <!-- Subcategories Section (if has children) -->
      <div v-if="category.children && category.children.length > 0" class="mb-12">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Shop by Subcategory</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <router-link
            v-for="subCategory in category.children"
            :key="subCategory.id"
            :to="{ name: 'category', params: { slug: subCategory.slug } }"
            class="card card-body p-4 group hover:shadow-md transition-all cursor-pointer"
          >
            <!-- Subcategory Image -->
            <div v-if="subCategory.image" class="aspect-square mb-3 overflow-hidden rounded">
              <img
                :src="subCategory.image"
                :alt="subCategory.name"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>

            <!-- Subcategory Icon -->
            <div
              v-else
              class="aspect-square mb-3 bg-gradient-to-br from-accent-50 to-accent-100 rounded flex items-center justify-center"
            >
              <span class="text-3xl">{{ getCategoryIcon(subCategory.slug) }}</span>
            </div>

            <!-- Subcategory Name -->
            <h3 class="text-sm font-semibold text-gray-900 group-hover:text-accent-600 transition-colors line-clamp-2 text-center">
              {{ subCategory.name }}
            </h3>

            <!-- Product Count -->
            <p class="text-xs text-gray-500 mt-2 text-center">
              {{ subCategory.products_count || 0 }} products
            </p>
          </router-link>
        </div>

        <!-- Divider -->
        <hr class="mt-10 mb-8 border-gray-200" />
      </div>

      <!-- Products Section -->
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Filters Sidebar (optional - could add later) -->

        <!-- Products Grid -->
        <div class="flex-1">
          <!-- Section Header -->
          <h2 v-if="category.children && category.children.length > 0" class="text-xl font-semibold text-gray-900 mb-6">
            All {{ category.name }} Products
          </h2>

          <!-- Sort & Filter Bar -->
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
            <p class="text-sm text-gray-600">
              {{ productsStore.pagination.count }} {{ productsStore.pagination.count === 1 ? 'product' : 'products' }} found
            </p>

            <!-- Sort Dropdown -->
            <select
              v-model="sortBy"
              @change="handleSortChange"
              class="form-input form-select w-full sm:w-auto"
            >
              <option value="-created_at">Newest First</option>
              <option value="created_at">Oldest First</option>
              <option value="name">Name (A-Z)</option>
              <option value="-name">Name (Z-A)</option>
              <option value="base_price">Price (Low to High)</option>
              <option value="-base_price">Price (High to Low)</option>
              <option value="-sales_count">Most Popular</option>
            </select>
          </div>

          <!-- Products Grid Component -->
          <ProductGrid
            :products="productsStore.products"
            :loading="productsStore.isLoading"
          />

          <!-- Pagination -->
          <div v-if="productsStore.pagination.count > productsStore.pagination.pageSize" class="mt-8">
            <PaginationComponent
              :current-page="productsStore.pagination.page"
              :total-pages="totalPages"
              :has-next="productsStore.hasNextPage"
              :has-previous="productsStore.hasPreviousPage"
              @page-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useBreadcrumbs } from '@/composables/useBreadcrumbs'
import { categoriesAPI } from '@/services/api'
import ProductGrid from '@/components/products/ProductGrid.vue'
import PaginationComponent from '@/components/ui/PaginationComponent.vue'
import BreadcrumbsNav from '@/components/ui/BreadcrumbsNav.vue'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()

const isLoading = ref(true)
const category = ref(null)
const sortBy = ref(route.query.ordering || '-created_at')

const breadcrumbs = useBreadcrumbs(category)

const totalPages = computed(() => {
  return Math.ceil(productsStore.pagination.count / productsStore.pagination.pageSize)
})

// Category icon mapping (same as CategoriesView)
const categoryIcons = {
  base: '🏪',
  electronics: '💻',
  clothing: '👕',
  fashion: '👕',
  'home-garden': '🏡',
  home: '🏡',
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

const loadCategoryAndProducts = async () => {
  isLoading.value = true
  try {
    // Fetch category details with parent/children relationships
    // Use the detail API endpoint instead of list to get full parent chain
    const response = await categoriesAPI.getBySlug(route.params.slug)
    category.value = response.data

    if (!category.value) {
      isLoading.value = false
      return
    }

    // Fetch products for this category
    // Backend expects 'category__slug' parameter
    await productsStore.fetchProducts({
      category__slug: route.params.slug,
      ordering: sortBy.value,
      page: route.query.page || 1
    })
  } catch (error) {
    console.error('Failed to load category:', error)
    category.value = null
  } finally {
    isLoading.value = false
  }
}

const handleSortChange = () => {
  const query = { ...route.query, ordering: sortBy.value, page: 1 }
  router.push({ query })
}

const handlePageChange = (page) => {
  const query = { ...route.query, page }
  router.push({ query })
}

// Watch for route changes
watch(() => route.params.slug, () => {
  loadCategoryAndProducts()
})

watch(() => route.query, () => {
  loadCategoryAndProducts()
}, { deep: true })

onMounted(() => {
  loadCategoryAndProducts()
})
</script>
