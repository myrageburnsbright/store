<template>
  <div class="space-y-6">
    <!-- Reviews Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Customer Reviews</h2>
        <div v-if="reviews.length > 0" class="flex items-center gap-3 mt-2">
          <!-- Average Rating -->
          <div class="star-rating">
            <StarIcon
              v-for="star in 5"
              :key="star"
              class="star"
              :class="star <= Math.round(averageRating) ? 'star-filled' : 'star-empty'"
            />
          </div>
          <span class="text-lg font-semibold text-gray-900">
            {{ averageRating.toFixed(1) }}
          </span>
          <span class="text-gray-600">
            ({{ reviews.length }} {{ reviews.length === 1 ? 'review' : 'reviews' }})
          </span>
        </div>
      </div>

      <!-- Write Review Button -->
      <button
        v-if="canWriteReview"
        @click="showForm = !showForm"
        class="btn btn-primary"
      >
        <PencilIcon class="w-5 h-5 mr-2" />
        {{ hasUserReview ? 'Edit Your Review' : 'Write a Review' }}
      </button>

      <router-link
        v-else-if="!isAuthenticated"
        :to="{ name: 'login', query: { redirect: $route.fullPath } }"
        class="btn btn-primary"
      >
        Sign In to Review
      </router-link>
    </div>

    <!-- Review Form -->
    <div v-if="showForm">
      <ReviewForm
        :product-slug="productSlug"
        :existing-review="userReview"
        @success="handleReviewSuccess"
        @cancel="showForm = false"
      />
    </div>

    <!-- Rating Distribution -->
    <div v-if="reviews.length > 0" class="card">
      <div class="card-body">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Rating Distribution</h3>
        <div class="space-y-2">
          <div
            v-for="star in [5, 4, 3, 2, 1]"
            :key="star"
            class="flex items-center gap-3"
          >
            <span class="text-sm font-medium text-gray-700 w-12">
              {{ star }} star{{ star !== 1 ? 's' : '' }}
            </span>

            <!-- Progress Bar -->
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-warning-500 transition-all duration-300"
                :style="{ width: `${getRatingPercentage(star)}%` }"
              ></div>
            </div>

            <span class="text-sm text-gray-600 w-12 text-right">
              {{ getRatingCount(star) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-8 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading reviews...</p>
    </div>

    <!-- No Reviews -->
    <div v-else-if="reviews.length === 0" class="card card-body text-center py-12">
      <p class="text-gray-600 mb-4">No reviews yet. Be the first to review this product!</p>
      <button
        v-if="isAuthenticated"
        @click="showForm = true"
        class="btn btn-primary mx-auto"
      >
        Write the First Review
      </button>
    </div>

    <!-- Reviews List -->
    <div v-else class="space-y-6">
      <!-- Sort Options -->
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-900">
          All Reviews ({{ reviews.length }})
        </h3>
        <select
          v-model="sortBy"
          class="form-input form-select w-auto text-sm"
        >
          <option value="recent">Most Recent</option>
          <option value="highest">Highest Rating</option>
          <option value="lowest">Lowest Rating</option>
        </select>
      </div>

      <!-- Reviews -->
      <div class="card">
        <div class="card-body space-y-6">
          <ReviewItem
            v-for="review in sortedReviews"
            :key="review.id"
            :review="review"
            @edit="handleEditReview(review)"
            @delete="handleDeleteReview(review.id)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useReviewsStore } from '@/stores/reviews'
import { useAuthStore } from '@/stores/auth'
import ReviewItem from './ReviewItem.vue'
import ReviewForm from './ReviewForm.vue'
import { StarIcon, PencilIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  productSlug: {
    type: String,
    required: true
  }
})

const reviewsStore = useReviewsStore()
const authStore = useAuthStore()

const showForm = ref(false)
const sortBy = ref('recent')

const isLoading = computed(() => reviewsStore.getLoadingState(props.productSlug))
const reviews = computed(() => reviewsStore.getReviewsByProduct(props.productSlug))
const isAuthenticated = computed(() => authStore.isAuthenticated)

const averageRating = computed(() => {
  if (reviews.value.length === 0) return 0
  const sum = reviews.value.reduce((acc, review) => acc + review.rating, 0)
  return sum / reviews.value.length
})

const userReview = computed(() => {
  if (!isAuthenticated.value) return null
  return reviews.value.find(review => review.user.id === authStore.user?.id)
})

const hasUserReview = computed(() => !!userReview.value)

const canWriteReview = computed(() => {
  return isAuthenticated.value
})

const sortedReviews = computed(() => {
  const sorted = [...reviews.value]

  switch (sortBy.value) {
    case 'highest':
      return sorted.sort((a, b) => b.rating - a.rating)
    case 'lowest':
      return sorted.sort((a, b) => a.rating - b.rating)
    case 'recent':
    default:
      return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
})

const getRatingCount = (rating) => {
  return reviews.value.filter(review => review.rating === rating).length
}

const getRatingPercentage = (rating) => {
  if (reviews.value.length === 0) return 0
  return (getRatingCount(rating) / reviews.value.length) * 100
}

const handleReviewSuccess = () => {
  showForm.value = false
  // Reviews are automatically refreshed in the store
}

const handleEditReview = (review) => {
  showForm.value = true
}

const handleDeleteReview = async (reviewId) => {
  try {
    await reviewsStore.deleteReview(reviewId, props.productSlug)
  } catch (error) {
    console.error("[ReviewsSection] Error deleting review:", error)
  }
}

onMounted(async () => {
  await reviewsStore.fetchReviews(props.productSlug)
})
</script>
