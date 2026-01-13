import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy loading components
const Home = () => import('@/views/HomeView.vue')
const NotFound = () => import('@/views/NotFoundView.vue')

// Auth views
const Login = () => import('@/views/auth/LoginView.vue')
const Register = () => import('@/views/auth/RegisterView.vue')
const Profile = () => import('@/views/auth/ProfileView.vue')
const ChangePassword = () => import('@/views/auth/ChangePasswordView.vue')

// Product views
const ProductsView = () => import('@/views/products/ProductsView.vue')
const ProductDetailView = () => import('@/views/products/ProductDetailView.vue')

// Cart views
const CartView = () => import('@/views/cart/CartView.vue')

// Checkout views
const CheckoutView = () => import('@/views/checkout/CheckoutView.vue')
const CheckoutSuccessView = () => import('@/views/checkout/CheckoutSuccessView.vue')

// Order views
const OrdersView = () => import('@/views/orders/OrdersView.vue')
const OrderDetailView = () => import('@/views/orders/OrderDetailView.vue')

// Wishlist view
const WishlistView = () => import('@/views/wishlist/WishlistView.vue')

// Category views
const CategoriesView = () => import('@/views/categories/CategoriesView.vue')
const CategoryView = () => import('@/views/categories/CategoryView.vue')

const routes = [
  // Home
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { title: 'Home' }
  },

  // Auth Routes
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { title: 'Login', requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { title: 'Register', requiresGuest: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile,
    meta: { title: 'Profile', requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'change-password',
    component: ChangePassword,
    meta: { title: 'Change Password', requiresAuth: true }
  },

  // Product Routes
  {
    path: '/products',
    name: 'products',
    component: ProductsView,
    meta: { title: 'Products' }
  },
  {
    path: '/products/:slug',
    name: 'product-detail',
    component: ProductDetailView,
    meta: { title: 'Product Detail' }
  },

  // Category Routes
  {
    path: '/categories',
    name: 'categories',
    component: CategoriesView,
    meta: { title: 'Categories' }
  },
  {
    path: '/categories/:slug',
    name: 'category',
    component: CategoryView,
    meta: { title: 'Category' }
  },

  // Brand Routes
  {
    path: '/brands/:slug',
    name: 'brand',
    component: CategoryView, // Reuse CategoryView for now
    meta: { title: 'Brand' }
  },

  // Shopping Cart
  {
    path: '/cart',
    name: 'cart',
    component: CartView,
    meta: { title: 'Shopping Cart' }
  },

  // Checkout
  {
    path: '/checkout',
    name: 'checkout',
    component: CheckoutView,
    meta: { title: 'Checkout', requiresAuth: true }
  },
  {
    path: '/checkout/success',
    name: 'checkout-success',
    component: CheckoutSuccessView,
    meta: { title: 'Order Success', requiresAuth: true }
  },
  {
    path: '/checkout/cancel',
    name: 'checkout-cancel',
    component: () => import('../views/checkout/CheckoutCancelView.vue'),
    meta: { title: 'Payment Cancelled', requiresAuth: true }
  },

  // Orders
  {
    path: '/orders',
    name: 'orders',
    component: OrdersView,
    meta: { title: 'My Orders', requiresAuth: true }
  },
  {
    path: '/orders/:orderNumber',
    name: 'order-detail',
    component: OrderDetailView,
    meta: { title: 'Order Details', requiresAuth: true }
  },

  // Wishlist
  {
    path: '/wishlist',
    name: 'wishlist',
    component: WishlistView,
    meta: { title: 'My Wishlist', requiresAuth: true }
  },

  // 404 - Must be last
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound,
    meta: { title: '404 Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Initialize auth on first navigation
  if (!authStore.isInitialized) {
    try {
      await authStore.initializeAuth()
    } catch (error) {
      console.error('Auth initialization error:', error)
    }
  }

  // Update page title
  document.title = to.meta.title
    ? `${to.meta.title} | E-Commerce Store`
    : 'E-Commerce Store'

  // Check auth requirements
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // Check guest requirements
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router
