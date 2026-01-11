import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { reviewsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useReviewsStore = defineStore('reviews', () => {
  // State
  const productReviews = ref({}) // Keyed by productSlug
  const isLoading = ref({}) // Keyed by productSlug
  const isSubmitting = ref(false)

  // Computed
  const getReviewsByProduct = (slug) => {
    return productReviews.value[slug] || []
  }

  const getLoadingState = (slug) => {
    return isLoading.value[slug] || false
  }

  // Actions
  const fetchReviews = async (productSlug) => {
    isLoading.value[productSlug] = true
    try {
      const response = await reviewsAPI.getByProduct(productSlug)
      productReviews.value[productSlug] = response.data.results || response.data || []
      return productReviews.value[productSlug]
    } catch (error) {
      console.error('Error fetching reviews:', error)
      productReviews.value[productSlug] = []
      throw error
    } finally {
      isLoading.value[productSlug] = false
    }
  }

  const createReview = async (productSlug, reviewData) => {
    isSubmitting.value = true
    try {
      const response = await reviewsAPI.create(productSlug, reviewData)
      const newReview = response.data

      // Add review to the product's reviews list
      if (!productReviews.value[productSlug]) {
        productReviews.value[productSlug] = []
      }
      productReviews.value[productSlug].unshift(newReview)

      toast.success('Review submitted successfully')
      return newReview
    } catch (error) {
      console.error('Error creating review:', error)

      if (error.response?.data) {
        const errorData = error.response.data
        if (errorData.detail) {
          toast.error(errorData.detail)
        } else if (errorData.rating) {
          toast.error(errorData.rating[0] || 'Invalid rating')
        } else if (errorData.comment) {
          toast.error(errorData.comment[0] || 'Invalid comment')
        } else {
          toast.error('Failed to submit review')
        }
      } else {
        toast.error('Failed to submit review')
      }

      throw error
    } finally {
      isSubmitting.value = false
    }
  }

  const updateReview = async (reviewId, reviewData) => {
    isSubmitting.value = true
    try {
      const response = await reviewsAPI.update(reviewId, reviewData)
      const updatedReview = response.data

      // Update the review in all product lists
      Object.keys(productReviews.value).forEach(slug => {
        const index = productReviews.value[slug].findIndex(r => r.id === reviewId)
        if (index !== -1) {
          productReviews.value[slug][index] = updatedReview
        }
      })

      toast.success('Review updated successfully')
      return updatedReview
    } catch (error) {
      console.error('Error updating review:', error)
      toast.error('Failed to update review')
      throw error
    } finally {
      isSubmitting.value = false
    }
  }

  const deleteReview = async (reviewId, productSlug = null) => {
    isSubmitting.value = true
    try {
      await reviewsAPI.delete(reviewId)

      // Remove from all product lists or specific product
      if (productSlug) {
        productReviews.value[productSlug] = productReviews.value[productSlug].filter(
          r => r.id !== reviewId
        )
      } else {
        Object.keys(productReviews.value).forEach(slug => {
          productReviews.value[slug] = productReviews.value[slug].filter(
            r => r.id !== reviewId
          )
        })
      }

      toast.success('Review deleted successfully')
    } catch (error) {
      console.error('Error deleting review:', error)
      toast.error('Failed to delete review')
      throw error
    } finally {
      isSubmitting.value = false
    }
  }

  const clearReviews = (productSlug = null) => {
    if (productSlug) {
      delete productReviews.value[productSlug]
    } else {
      productReviews.value = {}
    }
  }

  return {
    // State
    productReviews,
    isLoading,
    isSubmitting,

    // Computed
    getReviewsByProduct,
    getLoadingState,

    // Actions
    fetchReviews,
    createReview,
    updateReview,
    deleteReview,
    clearReviews
  }
})
