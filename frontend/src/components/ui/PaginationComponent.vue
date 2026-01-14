<!-- PaginationComponent.vue -->
<template>
  <nav class="flex items-center justify-between border-t border-gray-200 px-4 py-3 sm:px-6" aria-label="Pagination">
    <div class="hidden sm:block">
      <p class="text-sm text-gray-700">
        Page
        <span class="font-medium">{{ currentPage }}</span>
        of
        <span class="font-medium">{{ totalPages }}</span>
      </p>
    </div>
    <div class="flex flex-1 justify-between sm:justify-end">
      <button
        @click="$emit('page-change', currentPage - 1)"
        :disabled="!hasPrevious"
        class="btn-outline btn-sm mr-3"
        :class="{ 'opacity-50 cursor-not-allowed': !hasPrevious }"
      >
        Previous
      </button>

      <!-- Page Numbers -->
      <div class="hidden sm:flex items-center space-x-2">
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="$emit('page-change', page)"
          :class="[
            'px-4 py-2 text-sm font-bold rounded-lg transition-all min-w-[40px]',
            page === currentPage
              ? 'bg-blue-600 text-white shadow-lg cursor-default'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300 border border-gray-400'
          ]"
          :disabled="page === currentPage"
        >
          {{ page }}
        </button>
      </div>

      <button
        @click="$emit('page-change', currentPage + 1)"
        :disabled="!hasNext"
        class="btn-outline btn-sm ml-3"
        :class="{ 'opacity-50 cursor-not-allowed': !hasNext }"
      >
        Next
      </button>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'PaginationComponent',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    },
    hasNext: {
      type: Boolean,
      default: false
    },
    hasPrevious: {
      type: Boolean,
      default: false
    }
  },
  emits: ['page-change'],
  setup(props) {
    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, props.currentPage - 2)
      const end = Math.min(props.totalPages, props.currentPage + 2)

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    })

    return {
      visiblePages
    }
  }
}
</script>
