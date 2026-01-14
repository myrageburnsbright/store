import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Base API configuration
const API_BASE_URL = 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add authorization token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // If sending FormData, remove Content-Type to let browser set it automatically with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)


// Response interceptor - error handling and token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    // Don't retry if this is already a retry, or if it's the refresh token endpoint itself
    const isRefreshTokenRequest = originalRequest.url?.includes('/auth/token/refresh')

    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshTokenRequest) {
      originalRequest._retry = true

      // Attempt to refresh token
      if (authStore.refreshToken) {
        try {
          await authStore.refreshAccessToken()
          originalRequest.headers.Authorization = `Bearer ${authStore.token}`
          return api(originalRequest)
        } catch (refreshError) {
          authStore.logout()
          router.push({ name: 'login' })
          toast.error('Session expired. Please sign in again.')
          return Promise.reject(refreshError)
        }
      } else {
        authStore.logout()
        router.push({ name: 'login' })
        toast.error('Authorization required.')
      }
    }

    // If refresh token request fails with 401, immediately logout
    if (error.response?.status === 401 && isRefreshTokenRequest) {
      authStore.logout()
      router.push({ name: 'login' })
      toast.error('Session expired. Please sign in again.')
      return Promise.reject(error)
    }

    // Handle other errors
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          if (data.detail) {
            toast.error(data.detail)
          } else if (typeof data === 'object') {
            // Show first validation error
            const firstError = Object.values(data)[0]
            if (Array.isArray(firstError)) {
              toast.error(firstError[0])
            }
          }
          break
        case 403:
          toast.error('You do not have permission to perform this action.')
          break
        case 404:
          toast.error('The requested resource was not found.')
          break
        case 429:
          toast.error('Too many requests. Please try again later.')
          break
        case 500:
          toast.error('Internal server error. Please try again later.')
          break
        default:
          toast.error('An unexpected error occurred.')
      }
    } else if (error.request) {
      toast.error('Unable to connect to the server.')
    } else {
      toast.error('An error occurred while sending the request.')
    }
    
    return Promise.reject(error)
  }
)

// API методы
export const authAPI = {
  register: (data) => api.post('/api/v1/auth/register/', data),
  login: (data) => api.post('/api/v1/auth/login/', data),
  logout: (data) => api.post('/api/v1/auth/logout/', data),
  refreshToken: (data) => api.post('/api/v1/auth/token/refresh/', data),
  getProfile: () => api.get('/api/v1/auth/profile/'),
  updateProfile: (data) => api.put('/api/v1/auth/profile/', data),
  updateProfilePartial: (data) => api.patch('/api/v1/auth/profile/', data),
  changePassword: (data) => api.put('/api/v1/auth/change-password/', data)
}

// E-Commerce API Endpoints

// Products & Catalog
export const productsAPI = {
  getAll: (params) => api.get('/products/', { params }),
  getBySlug: (slug) => api.get(`/products/${slug}/`),
  getRelated: (slug) => api.get(`/products/${slug}/related/`),
  create: (data) => api.post('/products/', apiUtils.createFormData(data)),
  update: (slug, data) => api.put(`/products/${slug}/`, apiUtils.createFormData(data)),
  delete: (slug) => api.delete(`/products/${slug}/`)
}

export const categoriesAPI = {
  getAll: (params) => api.get('/categories/', { params }),
  getBySlug: (slug) => api.get(`/categories/${slug}/`),
  getProducts: (slug, params) => api.get(`/categories/${slug}/products/`, { params })
}

export const brandsAPI = {
  getAll: (params) => api.get('/brands/', { params }),
  getBySlug: (slug) => api.get(`/brands/${slug}/`)
}

// Shopping Cart
export const cartAPI = {
  getCart: () => api.get('/cart/'),
  addItem: (data) => api.post('/cart/add/', data),
  updateItem: (itemId, data) => api.patch(`/cart/items/${itemId}/update/`, data),
  removeItem: (itemId) => api.delete(`/cart/items/${itemId}/remove/`),
  clear: () => api.delete('/cart/clear/')
}

// Orders & Checkout
export const ordersAPI = {
  getAll: (params) => api.get('/payment/orders/', { params }),
  getByOrderNumber: (orderNumber) => api.get(`/payment/orders/${orderNumber}/`),
  create: (data) => api.post('/payment/orders/create/', data),
  cancel: (orderNumber) => api.post(`/payment/orders/${orderNumber}/cancel/`)
}

export const shippingAPI = {
  getAll: () => api.get('/payment/shipping-addresses/'),
  create: (data) => api.post('/payment/shipping-addresses/create/', data),
  update: (id, data) => api.patch(`/payment/shipping-addresses/${id}/update/`, data),
  delete: (id) => api.delete(`/payment/shipping-addresses/${id}/delete/`),
  setDefault: (id) => api.post(`/payment/shipping-addresses/${id}/set-default/`)
}

export const paymentsAPI = {
  create: (orderNumber, data = {}) => api.post(`/payment/payments/${orderNumber}/create/`, data),
  getDetails: (id) => api.get(`/payment/payments/${id}/`)
}

// Coupons
export const couponsAPI = {
  validate: (data) => api.post('/payment/coupons/validate/', data)
}

// Wishlist
export const wishlistAPI = {
  getAll: () => api.get('/wishlist/'),
  add: (data) => api.post('/wishlist/add/', data),
  remove: (productId) => api.delete(`/wishlist/remove/${productId}/`)
}

// Reviews
export const reviewsAPI = {
  getByProduct: (productSlug) => api.get(`/products/${productSlug}/reviews/`),
  create: (productSlug, data) => api.post(`/products/${productSlug}/reviews/create/`, data),
  update: (id, data) => api.put(`/reviews/${id}/`, data),
  delete: (id) => api.delete(`/reviews/${id}/`)
}

// Tags
export const tagsAPI = {
  getAll: () => api.get('/tags/')
}

// File upload utilities
export const uploadAPI = {
  uploadImage: (file, onProgress) => {
    const formData = new FormData()
    formData.append('image', file)
    
    return api.post('/api/v1/upload/image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(percentCompleted)
        }
      }
    })
  }
}

// Data handling utilities
export const apiUtils = {
  // Create FormData for file uploads
  createFormData: (data) => {
    const formData = new FormData()
    
    Object.keys(data).forEach(key => {
      const value = data[key]
      if (value !== null && value !== undefined) {
        if (value instanceof File) {
          formData.append(key, value)
        } else if (typeof value === 'object') {
          formData.append(key, JSON.stringify(value))
        } else {
          formData.append(key, value)
        }
      }
    })
    
    return formData
  },

  // Build query parameters
  buildQueryParams: (params) => {
    const searchParams = new URLSearchParams()
    
    Object.keys(params).forEach(key => {
      const value = params[key]
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(item => searchParams.append(key, item))
        } else {
          searchParams.append(key, value)
        }
      }
    })
    
    return searchParams.toString()
  },

  // Safely extract data from response
  extractData: (response, defaultValue = null) => {
    return response?.data || defaultValue
  },

  // Safely extract pagination
  extractPagination: (response) => {
    const data = response?.data
    return {
      count: data?.count || 0,
      next: data?.next || null,
      previous: data?.previous || null,
      results: data?.results || []
    }
  }
}

export default api