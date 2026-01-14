import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { productsAPI, categoriesAPI, brandsAPI } from '@/services/api'
import { PAGINATION_CONFIG } from '@/config/pagination'

export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref([])
  const currentProduct = ref(null)
  const categories = ref([])
  const brands = ref([])
  const featuredProducts = ref([])

  const pagination = ref({
    count: 0,
    next: null,
    previous: null,
    page: 1,
    pageSize: PAGINATION_CONFIG.PAGE_SIZE
  })

  const filters = ref({
    search: '',
    category: '',
    brand: '',
    min_price: null,
    max_price: null,
    ordering: '-created_at' // Options: -price, price, -sales_count, name, -created_at
  })

  const isLoading = ref(false)
  const isLoadingProduct = ref(false)
  const isLoadingCategories = ref(false)
  const isLoadingBrands = ref(false)

  // Computed
  const hasNextPage = computed(() => !!pagination.value.next)
  const hasPreviousPage = computed(() => !!pagination.value.previous)
  const totalPages = computed(() =>
    Math.ceil(pagination.value.count / pagination.value.pageSize)
  )

  const inStockProducts = computed(() =>
    products.value.filter(p => p.stock_quantity > 0)
  )

  const lowStockProducts = computed(() =>
    products.value.filter(p => p.stock_quantity > 0 && p.stock_quantity < 10)
  )

  // Actions
  const fetchProducts = async (params = {}) => {
    isLoading.value = true
    try {
      const queryParams = { ...filters.value, ...params }

      // Remove empty values
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === null || queryParams[key] === '') {
          delete queryParams[key]
        }
      })

      const response = await productsAPI.getAll(queryParams)
      products.value = response.data.results || []

      pagination.value = {
        count: response.data.count || 0,
        next: response.data.next,
        previous: response.data.previous,
        page: parseInt(params.page) || 1,
        pageSize: PAGINATION_CONFIG.PAGE_SIZE
      }

      return response.data
    } catch (error) {
      console.error('Error fetching products:', error)
      products.value = []
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchProductBySlug = async (slug) => {
    isLoadingProduct.value = true
    try {
      // Check cache first
      const cached = products.value.find(p => p.slug === slug)
      if (cached) {
        currentProduct.value = cached
      }

      const response = await productsAPI.getBySlug(slug)
      currentProduct.value = response.data
      return response.data
    } catch (error) {
      console.error('Error fetching product:', error)
      currentProduct.value = null
      throw error
    } finally {
      isLoadingProduct.value = false
    }
  }

  const fetchCategories = async (params = {}) => {
    isLoadingCategories.value = true
    try {
      const response = await categoriesAPI.getAll(params)
      categories.value = response.data.results || response.data || []
      return categories.value
    } catch (error) {
      console.error('Error fetching categories:', error)
      categories.value = []
      throw error
    } finally {
      isLoadingCategories.value = false
    }
  }

  const fetchBrands = async (params = {}) => {
    isLoadingBrands.value = true
    try {
      const response = await brandsAPI.getAll(params)
      brands.value = response.data.results || response.data || []
      return brands.value
    } catch (error) {
      console.error('Error fetching brands:', error)
      brands.value = []
      throw error
    } finally {
      isLoadingBrands.value = false
    }
  }

  const fetchFeaturedProducts = async () => {
    try {
      const response = await productsAPI.getAll({
        is_featured: true,
        page_size: 8
      })
      featuredProducts.value = response.data.results || []
      return featuredProducts.value
    } catch (error) {
      console.error('Error fetching featured products:', error)
      featuredProducts.value = []
      throw error
    }
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      search: '',
      category: '',
      brand: '',
      min_price: null,
      max_price: null,
      ordering: '-created_at'
    }
  }

  const searchProducts = async (query) => {
    filters.value.search = query
    return await fetchProducts({ page: 1 })
  }

  const filterByCategory = async (categorySlug) => {
    filters.value.category = categorySlug
    return await fetchProducts({ page: 1 })
  }

  const filterByPriceRange = async (min, max) => {
    filters.value.min_price = min
    filters.value.max_price = max
    return await fetchProducts({ page: 1 })
  }

  const sortProducts = async (ordering) => {
    filters.value.ordering = ordering
    return await fetchProducts({ page: 1 })
  }

  const goToPage = async (page) => {
    return await fetchProducts({ page })
  }

  const nextPage = async () => {
    if (hasNextPage.value) {
      return await goToPage(pagination.value.page + 1)
    }
  }

  const previousPage = async () => {
    if (hasPreviousPage.value) {
      return await goToPage(pagination.value.page - 1)
    }
  }

  const clearProducts = () => {
    products.value = []
  }

  const clearCurrentProduct = () => {
    currentProduct.value = null
  }

  const getProductFromCache = (slug) => {
    return products.value.find(p => p.slug === slug)
  }

  const getCategoryById = (id) => {
    return categories.value.find(c => c.id === id)
  }

  const getBrandById = (id) => {
    return brands.value.find(b => b.id === id)
  }

  return {
    // State
    products,
    currentProduct,
    categories,
    brands,
    featuredProducts,
    pagination,
    filters,
    isLoading,
    isLoadingProduct,
    isLoadingCategories,
    isLoadingBrands,

    // Computed
    hasNextPage,
    hasPreviousPage,
    totalPages,
    inStockProducts,
    lowStockProducts,

    // Actions
    fetchProducts,
    fetchProductBySlug,
    fetchCategories,
    fetchBrands,
    fetchFeaturedProducts,
    setFilters,
    clearFilters,
    searchProducts,
    filterByCategory,
    filterByPriceRange,
    sortProducts,
    goToPage,
    nextPage,
    previousPage,
    clearProducts,
    clearCurrentProduct,
    getProductFromCache,
    getCategoryById,
    getBrandById
  }
})
