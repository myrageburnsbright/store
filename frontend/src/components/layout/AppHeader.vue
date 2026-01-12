<template>
  <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
    <div class="container-content">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Navigation -->
        <div class="flex items-center space-x-8">
          <!-- Logo -->
          <router-link
            :to="{ name: 'home' }"
            class="flex items-center space-x-2 text-lg font-bold text-gray-900 hover:text-accent-600 transition-colors"
          >
            <div class="w-8 h-8 bg-accent-100 rounded-md flex items-center justify-center">
              <ShoppingBagIcon class="w-5 h-5 text-accent-600" />
            </div>
            <span>Store</span>
          </router-link>

          <!-- Main Navigation -->
          <nav class="hidden md:flex items-center space-x-6">
            <router-link
              :to="{ name: 'home' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'home' }"
            >
              Home
            </router-link>
            <router-link
              :to="{ name: 'products' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'products' || $route.name === 'product-detail' }"
            >
              Products
            </router-link>
            <router-link
              :to="{ name: 'categories' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'categories' || $route.name === 'category' }"
            >
              Categories
            </router-link>
          </nav>
        </div>

        <!-- Search Bar -->
        <div class="hidden lg:flex flex-1 max-w-lg mx-8">
          <div class="relative w-full">
            <div style="position: absolute; top: 0; bottom: 0; left: 0.75rem; display: flex; align-items: center; pointer-events: none;">
              <MagnifyingGlassIcon style="height: 1.25rem; width: 1.25rem; color: #9ca3af;" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search products..."
              style="padding-left: 2.5rem; padding-right: 2.5rem;"
              class="form-input"
              @keyup.enter="handleSearch"
            />
            <button
              v-if="searchQuery"
              @click="clearSearch"
              style="position: absolute; top: 0; bottom: 0; right: 0.75rem; display: flex; align-items: center;"
            >
              <XMarkIcon style="height: 1.25rem; width: 1.25rem; color: #9ca3af;" />
            </button>
          </div>
        </div>

        <!-- User Actions -->
        <div class="flex items-center space-x-4">
          <!-- Mobile Search Button -->
          <button
            @click="showMobileSearch = !showMobileSearch"
            class="lg:hidden p-2 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-50 transition-colors"
          >
            <MagnifyingGlassIcon class="w-5 h-5" />
          </button>

          <!-- Wishlist Icon -->
          <router-link
            v-if="authStore.isAuthenticated"
            :to="{ name: 'wishlist' }"
            class="relative p-2 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-50 transition-colors"
          >
            <HeartIcon class="w-6 h-6" />
            <span
              v-if="wishlistStore.wishlistCount > 0"
              class="cart-badge"
            >
              {{ wishlistStore.wishlistCount }}
            </span>
          </router-link>

          <!-- Cart Icon -->
          <CartIcon />

          <!-- User Menu -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button
              @click.stop="toggleUserMenu"
              class="flex items-center space-x-2 px-2.5 py-1.5 rounded-lg border-2 hover:border-accent-400 hover:bg-accent-50 transition-all focus:outline-none focus:ring-2 focus:ring-accent-500 focus:border-accent-500 h-10"
              :class="showUserMenu ? 'border-accent-500 bg-accent-50' : 'border-gray-200 bg-white'"
            >
              <div class="w-7 h-7 bg-gradient-to-br from-accent-500 to-accent-600 rounded-full flex items-center justify-center text-white text-xs font-semibold shadow-sm ring-2 ring-white">
                {{ authStore.userInitials }}
              </div>
              <span class="hidden sm:block text-sm font-medium text-gray-800">
                {{ authStore.userFullName }}
              </span>
              <ChevronDownIcon
                class="w-4 h-4 text-gray-600 transition-transform duration-200"
                :class="{ 'rotate-180': showUserMenu }"
              />
            </button>

            <!-- Dropdown Menu -->
            <transition name="dropdown">
              <div
                v-if="showUserMenu"
                v-click-outside="closeUserMenu"
                class="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50"
              >
                <!-- User Info -->
                <div class="px-4 py-3 border-b border-gray-100">
                  <p class="text-sm font-medium text-gray-900">{{ authStore.userFullName }}</p>
                  <p class="text-sm text-gray-500">{{ authStore.user?.email }}</p>
                </div>

                <!-- Menu Links -->
                <router-link
                  :to="{ name: 'profile' }"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-accent-600 transition-colors"
                  @click="closeUserMenu"
                >
                  <UserIcon class="w-4 h-4 mr-3" />
                  Profile
                </router-link>

                <router-link
                  :to="{ name: 'orders' }"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-accent-600 transition-colors"
                  @click="closeUserMenu"
                >
                  <ShoppingBagIcon class="w-4 h-4 mr-3" />
                  My Orders
                </router-link>

                <router-link
                  :to="{ name: 'wishlist' }"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-accent-600 transition-colors"
                  @click="closeUserMenu"
                >
                  <HeartIcon class="w-4 h-4 mr-3" />
                  Wishlist
                  <span v-if="wishlistStore.wishlistCount > 0" class="ml-auto badge badge-primary text-xs">
                    {{ wishlistStore.wishlistCount }}
                  </span>
                </router-link>

                <div class="border-t border-gray-100 my-1"></div>

                <router-link
                  :to="{ name: 'change-password' }"
                  class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-accent-600 transition-colors"
                  @click="closeUserMenu"
                >
                  <KeyIcon class="w-4 h-4 mr-3" />
                  Change Password
                </router-link>

                <button
                  @click="handleLogout"
                  class="flex items-center w-full px-4 py-2 text-sm text-error-600 hover:bg-error-50 hover:text-error-700 transition-colors"
                >
                  <ArrowRightOnRectangleIcon class="w-4 h-4 mr-3" />
                  Logout
                </button>
              </div>
            </transition>
          </div>

          <!-- Login/Register Buttons -->
          <div v-else class="flex items-center space-x-3">
            <router-link
              :to="{ name: 'login' }"
              class="btn btn-sm btn-outline"
            >
              Sign In
            </router-link>
            <router-link
              :to="{ name: 'register' }"
              class="btn btn-sm btn-primary"
            >
              Sign Up
            </router-link>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="md:hidden p-2 text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-50 transition-colors"
          >
            <Bars3Icon v-if="!showMobileMenu" class="w-6 h-6" />
            <XMarkIcon v-else class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Mobile Search -->
      <transition name="slide-down">
        <div v-if="showMobileSearch" class="lg:hidden py-4 border-t border-gray-200">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search products..."
              class="form-input pl-10"
              @keyup.enter="handleSearch"
            />
          </div>
        </div>
      </transition>

      <!-- Mobile Navigation -->
      <transition name="slide-down">
        <div v-if="showMobileMenu" class="md:hidden py-4 border-t border-gray-200">
          <nav class="flex flex-col space-y-2">
            <router-link
              :to="{ name: 'home' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'home' }"
              @click="showMobileMenu = false"
            >
              Home
            </router-link>
            <router-link
              :to="{ name: 'products' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'products' }"
              @click="showMobileMenu = false"
            >
              Products
            </router-link>
            <router-link
              :to="{ name: 'categories' }"
              class="nav-link"
              :class="{ 'active': $route.name === 'categories' }"
              @click="showMobileMenu = false"
            >
              Categories
            </router-link>

            <!-- Mobile User Links -->
            <div v-if="authStore.isAuthenticated" class="border-t border-gray-200 pt-2 mt-2">
              <router-link
                :to="{ name: 'profile' }"
                class="nav-link flex items-center"
                @click="showMobileMenu = false"
              >
                <UserIcon class="w-4 h-4 mr-2" />
                Profile
              </router-link>
              <router-link
                :to="{ name: 'orders' }"
                class="nav-link flex items-center"
                @click="showMobileMenu = false"
              >
                <ShoppingBagIcon class="w-4 h-4 mr-2" />
                My Orders
              </router-link>
              <router-link
                :to="{ name: 'wishlist' }"
                class="nav-link flex items-center"
                @click="showMobileMenu = false"
              >
                <HeartIcon class="w-4 h-4 mr-2" />
                Wishlist
              </router-link>
            </div>
          </nav>
        </div>
      </transition>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWishlistStore } from '@/stores/wishlist'
import { useToast } from 'vue-toastification'
import CartIcon from '@/components/cart/CartIcon.vue'
import {
  ShoppingBagIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  HeartIcon,
  UserIcon,
  KeyIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  Bars3Icon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const toast = useToast()

const searchQuery = ref('')
const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const showMobileSearch = ref(false)

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      name: 'products',
      query: { search: searchQuery.value.trim() }
    })
    showMobileSearch.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    closeUserMenu()
    toast.success('Successfully logged out')
    router.push({ name: 'home' })
  } catch (error) {
    toast.error('Failed to logout')
  }
}

const fetchWishlistIfNeeded = async () => {
  if (authStore.isAuthenticated) {
    try {
      await wishlistStore.fetchWishlist()
    } catch (error) {
      // Handle error silently
    }
  }
}

// Load wishlist on mount if user is authenticated
onMounted(async () => {
  if (authStore.isAuthenticated && wishlistStore.wishlistItems.length === 0) {
    await fetchWishlistIfNeeded()
  }
})

// Watch for authentication changes (login/logout)
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await fetchWishlistIfNeeded()
  } else {
    wishlistStore.resetWishlist()
  }
})

// Click outside directive
const vClickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
  transform-origin: top right;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.dropdown-enter-to,
.dropdown-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

/* Slide down animation */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 300px;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-10px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 300px;
  transform: translateY(0);
}

/* Rotate animation */
.rotate-180 {
  transform: rotate(180deg);
}
</style>
