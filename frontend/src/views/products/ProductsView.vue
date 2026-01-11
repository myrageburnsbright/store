<template>
  <div class="container-content py-8">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Products</h1>
      <p class="text-gray-600">Browse our collection of products</p>
    </div>

    <!-- Filters and Sorting -->
    <div class="flex flex-col md:flex-row gap-4 mb-6">
      <!-- Search -->
      <div class="flex-1">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search products..."
          class="form-input w-full"
          @keyup.enter="handleSearch"
        />
      </div>

      <!-- Sort -->
      <div class="w-full md:w-64">
        <select
          v-model="sortBy"
          class="form-select w-full"
          @change="handleSort"
        >
          <option value="-created_at">Newest First</option>
          <option value="name">Name (A-Z)</option>
          <option value="-name">Name (Z-A)</option>
          <option value="base_price">Price: Low to High</option>
          <option value="-base_price">Price: High to Low</option>
          <option value="-sales_count">Most Popular</option>
        </select>
      </div>
    </div>

    <!-- Active Filters -->
    <div v-if="hasActiveFilters" class="flex flex-wrap gap-2 mb-6">
      <span class="text-sm text-gray-600">Active filters:</span>
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
      >
        Search: "{{ searchQuery }}"
        <XMarkIcon class="w-4 h-4" />
      </button>
      <button
        @click="clearAllFilters"
        class="text-sm text-accent-600 hover:text-accent-700 font-medium"
      >
        Clear all
      </button>
    </div>

    <!-- Results Count -->
    <div class="flex items-center justify-between mb-6">
      <p class="text-sm text-gray-600">
        {{ productsStore.pagination.count }} products found
      </p>
    </div>

    <!-- Products Grid -->
    <ProductGrid
      :products="productsStore.products"
      :loading="productsStore.isLoading"
      :has-filters="hasActiveFilters"
      @clear-filters="clearAllFilters"
    />

    <!-- Pagination -->
    <div v-if="productsStore.pagination.count > 0 && !productsStore.isLoading" class="mt-8">
      <PaginationComponent
        :current-page="productsStore.pagination.page"
        :total-pages="productsStore.totalPages"
        :has-next="productsStore.hasNextPage"
        :has-previous="productsStore.hasPreviousPage"
        @page-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useProductsStore } from '@/stores/products'
import ProductGrid from '@/components/products/ProductGrid.vue'
import PaginationComponent from '@/components/ui/PaginationComponent.vue'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()

const searchQuery = ref('')
const sortBy = ref('-created_at')

const hasActiveFilters = computed(() => {
  return searchQuery.value !== ''
})

onMounted(async () => {
  // Initialize from query params
  searchQuery.value = route.query.search || ''
  sortBy.value = route.query.ordering || '-created_at'

  // Fetch products
  await fetchProducts()
})

const fetchProducts = async () => {
  const params = {
    search: searchQuery.value || undefined,
    ordering: sortBy.value,
    page: route.query.page || 1
  }

  try {
    await productsStore.fetchProducts(params)
  } catch (error) {
    console.error('Failed to fetch products:', error)
  }
}

const handleSearch = () => {
  updateQueryParams({ search: searchQuery.value, page: 1 })
}

const handleSort = () => {
  updateQueryParams({ ordering: sortBy.value, page: 1 })
}

const handlePageChange = (page) => {
  updateQueryParams({ page })
}

const clearSearch = () => {
  searchQuery.value = ''
  updateQueryParams({ search: undefined, page: 1 })
}

const clearAllFilters = () => {
  searchQuery.value = ''
  sortBy.value = '-created_at'
  updateQueryParams({ search: undefined, ordering: '-created_at', page: 1 })
}

const updateQueryParams = (params) => {
  const query = { ...route.query, ...params }

  // Remove undefined values
  Object.keys(query).forEach(key => {
    if (query[key] === undefined || query[key] === '') {
      delete query[key]
    }
  })

  router.push({ query })
}

// Watch route changes
watch(() => route.query, async () => {
  if (route.name === 'products') {
    await fetchProducts()
  }
}, { deep: true })
</script>
