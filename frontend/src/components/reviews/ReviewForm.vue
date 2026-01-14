<template>
  <div class="card">
    <div class="card-header">
      <h3 class="text-lg font-semibold text-gray-900">
        {{ existingReview ? 'Edit Your Review' : 'Write a Review' }}
      </h3>
    </div>

    <div class="card-body">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Rating Selector -->
        <div>
          <label class="form-label">
            Your Rating <span class="text-error-600">*</span>
          </label>
          <div class="flex gap-2 items-center">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              @click="rating = star"
              @mouseenter="hoverRating = star"
              @mouseleave="hoverRating = 0"
              class="focus:outline-none transition-transform hover:scale-110"
            >
              <StarIcon
                class="w-8 h-8"
                :class="
                  star <= (hoverRating || rating)
                    ? 'text-warning-500 fill-current'
                    : 'text-gray-300'
                "
              />
            </button>
            <span v-if="rating > 0" class="ml-2 text-sm text-gray-600">
              {{ ratingLabels[rating - 1] }}
            </span>
          </div>
          <p v-if="errors.rating" class="form-error">{{ errors.rating }}</p>
        </div>

        <!-- Comment Textarea -->
        <div>
          <label for="comment" class="form-label">
            Your Review <span class="text-error-600">*</span>
          </label>
          <textarea
            id="comment"
            v-model="comment"
            rows="5"
            class="form-input form-textarea"
            placeholder="Tell us about your experience with this product..."
            :disabled="isSubmitting"
          ></textarea>
          <p class="text-xs text-gray-500 mt-1">
            Minimum 10 characters ({{ comment.length }}/10)
          </p>
          <p v-if="errors.comment" class="form-error">{{ errors.comment }}</p>
        </div>

        <!-- Form Actions -->
        <div class="flex gap-3 pt-2">
          <button
            type="submit"
            :disabled="isSubmitting || !canSubmit"
            class="btn btn-primary flex-1"
          >
            <span v-if="isSubmitting" class="loading-spinner mr-2"></span>
            {{ isSubmitting ? 'Submitting...' : (existingReview ? 'Update Review' : 'Submit Review') }}
          </button>

          <button
            type="button"
            @click="$emit('cancel')"
            :disabled="isSubmitting"
            class="btn btn-outline"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useReviewsStore } from '@/stores/reviews'
import { StarIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  productSlug: {
    type: String,
    required: true
  },
  existingReview: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const reviewsStore = useReviewsStore()

const rating = ref(0)
const hoverRating = ref(0)
const comment = ref('')
const isSubmitting = ref(false)
const errors = ref({})

const ratingLabels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']

// Populate form if editing existing review
watch(
  () => props.existingReview,
  (newReview) => {
    if (newReview) {
      rating.value = newReview.rating
      comment.value = newReview.comment
    }
  },
  { immediate: true }
)

const canSubmit = computed(() => {
  return rating.value > 0 && comment.value.trim().length >= 10
})

const handleSubmit = async () => {
  // Clear previous errors
  errors.value = {}

  // Validation
  if (rating.value === 0) {
    errors.value.rating = 'Please select a rating'
    return
  }

  if (comment.value.trim().length < 10) {
    errors.value.comment = 'Review must be at least 10 characters'
    return
  }

  isSubmitting.value = true

  try {
    const reviewData = {
      rating: rating.value,
      comment: comment.value.trim()
    }

    if (props.existingReview) {
      await reviewsStore.updateReview(props.existingReview.id, reviewData)
    } else {
      await reviewsStore.createReview(props.productSlug, reviewData)
    }

    // Reset form
    rating.value = 0
    comment.value = ''

    emit('success')
  } catch (error) {
    // Handle specific field errors from backend
    if (error.response?.data) {
      errors.value = error.response.data
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
