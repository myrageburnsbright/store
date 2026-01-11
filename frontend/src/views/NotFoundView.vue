<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <!-- 404 illustration -->
      <div class="mb-8">
        <div class="mx-auto h-32 w-32 bg-accent-100 rounded-full flex items-center justify-center mb-6">
          <ExclamationTriangleIcon class="h-16 w-16 text-accent-600" />
        </div>
      </div>

      <!-- Title -->
      <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">
        Page Not Found
      </h2>

      <!-- Description -->
      <p class="text-gray-600 mb-8">
        Sorry, the requested page does not exist.
        It may have been moved or deleted.
      </p>

      <!-- Actions -->
      <div class="space-y-4">
        <router-link
          to="/"
          class="btn-primary w-full justify-center"
        >
          <HomeIcon class="w-5 h-5 mr-2" />
          Go Home
        </router-link>

        <button
          @click="goBack"
          class="btn-outline w-full justify-center"
        >
          <ArrowLeftIcon class="w-5 h-5 mr-2" />
          Go Back
        </button>
      </div>

      <!-- Useful links -->
      <div class="mt-8 pt-8 border-t border-gray-200">
        <p class="text-sm text-gray-500 mb-4">You might be interested in:</p>
        <div class="space-y-2">
          <router-link
            to="/posts"
            class="block text-accent-600 hover:text-accent-700 text-sm"
          >
            All Posts
          </router-link>
          <router-link
            to="/categories"
            class="block text-accent-600 hover:text-accent-700 text-sm"
          >
            Categories
          </router-link>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/posts/create"
            class="block text-accent-600 hover:text-accent-700 text-sm"
          >
            Create Post
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  ExclamationTriangleIcon,
  HomeIcon,
  ArrowLeftIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'NotFoundView',
  components: {
    ExclamationTriangleIcon,
    HomeIcon,
    ArrowLeftIcon
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    return {
      authStore,
      goBack
    }
  }
}
</script>
