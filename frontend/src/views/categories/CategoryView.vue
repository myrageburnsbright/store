<template>
  <div class="container-content py-8">
    <!-- Breadcrumb -->
    <nav class="mb-6 text-sm">
      <ol class="flex items-center space-x-2 text-gray-600">
        <li>
          <router-link :to="{ name: 'home' }" class="hover:text-accent-600">
            Home
          </router-link>
        </li>
        <li>
          <ChevronRightIcon class="w-4 h-4" />
        </li>
        <li>
          <router-link :to="{ name: 'categories' }" class="hover:text-accent-600">
            Categories
          </router-link>
        </li>
        <li v-if="category">
          <ChevronRightIcon class="w-4 h-4" />
        </li>
        <li v-if="category" class="text-gray-900 font-medium">
          {{ category.name }}
        </li>
      </ol>
    </nav>

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

      <!-- Products Section -->
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Filters Sidebar (optional - could add later) -->

        <!-- Products Grid -->
        <div class="flex-1">
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
import ProductGrid from '@/components/products/ProductGrid.vue'
import PaginationComponent from '@/components/ui/PaginationComponent.vue'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()

const isLoading = ref(true)
const category = ref(null)
const sortBy = ref(route.query.ordering || '-created_at')

const totalPages = computed(() => {
  return Math.ceil(productsStore.pagination.count / productsStore.pagination.pageSize)
})

const loadCategoryAndProducts = async () => {
  isLoading.value = true
  try {
    // Fetch category details
    const categories = await productsStore.fetchCategories()
    category.value = categories.find(cat => cat.slug === route.params.slug)

    if (!category.value) {
      isLoading.value = false
      return
    }

    // Fetch products for this category
    await productsStore.fetchProducts({
      category: route.params.slug,
      ordering: sortBy.value,
      page: route.query.page || 1
    })
  } catch (error) {
    console.error('Failed to load category:', error)
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
