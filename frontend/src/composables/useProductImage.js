import { computed } from 'vue'
import api from '@/services/api'

/**
 * Unified product image handler
 * Works with both list API (primary_image) and detail API (images array)
 *
 * @param {Object|Ref} product - Product object or ref containing product data
 * @returns {ComputedRef<string|null>} Full image URL or null
 */
export function useProductImage(product) {
  return computed(() => {
    const productValue = product.value || product

    if (!productValue) return null

    const base = api.defaults.baseURL.replace(/\/$/, '')

    // From list API: primary_image is an object with {image: 'url'}
    if (productValue.primary_image && productValue.primary_image.image) {
      const imgPath = productValue.primary_image.image
      if (imgPath.startsWith('http')) return imgPath
      return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
    }

    // From detail API: images is an array
    if (productValue.images && productValue.images.length > 0) {
      const imgPath = productValue.images[0].image
      if (imgPath.startsWith('http')) return imgPath
      return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
    }

    return null
  })
}

/**
 * Get product image URL directly (non-reactive)
 * Use this in template methods or when you don't need reactivity
 *
 * @param {Object} product - Product object
 * @returns {string|null} Full image URL or null
 */
export function getProductImageUrl(product) {
  if (!product) return null

  const base = api.defaults.baseURL.replace(/\/$/, '')

  // From list API: primary_image is an object with {image: 'url'}
  if (product.primary_image && product.primary_image.image) {
    const imgPath = product.primary_image.image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }

  // From detail API: images is an array
  if (product.images && product.images.length > 0) {
    const imgPath = product.images[0].image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }

  return null
}
