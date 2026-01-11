<template>
  <div class="border-b border-gray-200 pb-6 last:border-0">
    <div class="flex gap-4">
      <!-- User Avatar -->
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-accent-100 flex items-center justify-center">
          <span class="text-sm font-semibold text-accent-700">
            {{ userInitials }}
          </span>
        </div>
      </div>

      <!-- Review Content -->
      <div class="flex-1 min-w-0">
        <!-- Header -->
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="font-semibold text-gray-900">{{ review.user.username }}</span>

          <!-- Star Rating -->
          <div class="star-rating">
            <StarIcon
              v-for="star in 5"
              :key="star"
              class="star"
              :class="star <= review.rating ? 'star-filled' : 'star-empty'"
            />
          </div>

          <span class="text-sm text-gray-500">
            {{ formatDate(review.created_at) }}
          </span>
        </div>

        <!-- Comment -->
        <p class="text-gray-700 text-sm leading-relaxed">
          {{ review.comment }}
        </p>

        <!-- Actions (if user owns this review) -->
        <div v-if="canEdit" class="flex gap-3 mt-3">
          <button
            @click="$emit('edit')"
            class="text-sm text-accent-600 hover:text-accent-700 font-medium"
          >
            Edit
          </button>
          <button
            @click="handleDelete"
            class="text-sm text-error-600 hover:text-error-700 font-medium"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { StarIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  review: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])

const authStore = useAuthStore()

const userInitials = computed(() => {
  const username = props.review.user.username
  return username
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const canEdit = computed(() => {
  return authStore.isAuthenticated && authStore.user?.id === props.review.user.id
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 1) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const handleDelete = () => {
  if (confirm('Are you sure you want to delete this review?')) {
    emit('delete')
  }
}
</script>
