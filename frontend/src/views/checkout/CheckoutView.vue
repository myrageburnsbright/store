<template>
  <div class="container-content py-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-12 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading checkout...</p>
    </div>

    <!-- Empty Cart Redirect -->
    <div v-else-if="cartStore.isEmpty" class="card card-body text-center py-12">
      <h2 class="text-xl font-semibold text-gray-900 mb-2">Your cart is empty</h2>
      <p class="text-gray-600 mb-6">Add some products before checking out</p>
      <router-link :to="{ name: 'products' }" class="btn btn-primary mx-auto">
        Browse Products
      </router-link>
    </div>

    <!-- Checkout Content -->
    <div v-else class="grid grid-cols-1 gap-6" :class="currentStep < 3 ? 'lg:grid-cols-3' : ''">
      <!-- Main Checkout Form -->
      <div class="space-y-6" :class="currentStep < 3 ? 'lg:col-span-2' : ''">
        <!-- Step Indicator -->
        <div class="card">
          <div class="card-body">
            <div class="flex items-center justify-between">
              <div
                v-for="(step, index) in steps"
                :key="step.id"
                class="flex items-center"
                :class="{ 'flex-1': index < steps.length - 1 }"
              >
                <div class="flex items-center">
                  <!-- Step Circle -->
                  <div
                    :style="{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '3rem',
                      height: '3rem',
                      borderRadius: '50%',
                      fontWeight: '700',
                      fontSize: '1.125rem',
                      border: '2px solid',
                      backgroundColor: currentStep > step.id ? '#22c55e' : currentStep === step.id ? '#0284c7' : '#e5e7eb',
                      color: currentStep >= step.id ? '#ffffff' : '#374151',
                      borderColor: currentStep > step.id ? '#22c55e' : currentStep === step.id ? '#0284c7' : '#9ca3af'
                    }"
                  >
                    <!-- Show checkmark for completed steps -->
                    <svg v-if="currentStep > step.id" style="width: 1.5rem; height: 1.5rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                    </svg>
                    <!-- Show step number for current and future steps -->
                    <span v-else>{{ step.id }}</span>
                  </div>
                  <!-- Step Label -->
                  <span
                    :style="{
                      marginLeft: '0.75rem',
                      fontSize: '0.875rem',
                      fontWeight: currentStep >= step.id ? '600' : '500',
                      color: currentStep >= step.id ? '#0284c7' : '#6b7280'
                    }"
                    class="hidden sm:inline"
                  >
                    {{ step.label }}
                  </span>
                </div>

                <!-- Connector Line -->
                <div
                  v-if="index < steps.length - 1"
                  :style="{
                    flex: '1',
                    height: '2px',
                    marginLeft: '1rem',
                    marginRight: '1rem',
                    backgroundColor: currentStep > step.id ? '#22c55e' : '#d1d5db'
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 1: Shipping Address -->
        <div v-show="currentStep === 1">
          <ShippingAddressSelector
            :addresses="checkoutStore.shippingAddresses"
            :selected-id="checkoutStore.selectedAddressId"
            :is-loading="checkoutStore.isLoadingAddresses"
            @select="handleAddressSelect"
            @add="handleAddressAdded"
            @update="handleAddressUpdated"
            @delete="handleAddressDeleted"
          />

          <div class="mt-6 flex justify-end">
            <button
              @click="nextStep"
              :disabled="!checkoutStore.selectedAddressId"
              class="btn btn-primary btn-lg"
            >
              Continue to Review
            </button>
          </div>
        </div>

        <!-- Step 2: Review & Payment -->
        <div v-show="currentStep === 2">
          <!-- Payment Method Selection -->
          <div class="card mb-6">
            <div class="card-header">
              <h3 class="text-lg font-semibold text-gray-900">Payment Method</h3>
            </div>
            <div class="card-body space-y-3">
              <label
                v-for="method in paymentMethods"
                :key="method.value"
                class="flex items-center p-4 border rounded transition-all"
                :class="[
                  method.disabled
                    ? 'opacity-50 cursor-not-allowed bg-gray-50'
                    : 'cursor-pointer',
                  checkoutStore.paymentMethod === method.value && !method.disabled
                    ? 'border-accent-500 bg-accent-50'
                    : 'border-gray-300',
                  !method.disabled && checkoutStore.paymentMethod !== method.value
                    ? 'hover:border-gray-400'
                    : ''
                ]"
              >
                <input
                  type="radio"
                  :value="method.value"
                  v-model="selectedPaymentMethod"
                  :disabled="method.disabled"
                  class="w-4 h-4 text-accent-600 border-gray-300 focus:ring-accent-500 disabled:cursor-not-allowed"
                />
                <div class="ml-3 flex-1">
                  <p class="font-medium" :class="method.disabled ? 'text-gray-400' : 'text-gray-900'">
                    {{ method.label }}
                  </p>
                  <p class="text-sm" :class="method.disabled ? 'text-gray-400' : 'text-gray-600'">
                    {{ method.description }}
                  </p>
                </div>
                <component :is="method.icon" class="w-6 h-6" :class="method.disabled ? 'text-gray-300' : 'text-gray-400'" />
              </label>
            </div>
          </div>

          <!-- Customer Notes -->
          <div class="card mt-6">
            <div class="card-body">
              <label for="notes" class="form-label">Order Notes (Optional)</label>
              <textarea
                id="notes"
                v-model="customerNotes"
                rows="3"
                class="form-input form-textarea"
                placeholder="Any special instructions for your order..."
              ></textarea>
            </div>
          </div>

          <!-- Navigation -->
          <div class="mt-6 flex justify-between">
            <button @click="prevStep" class="btn btn-outline btn-lg">
              Back
            </button>
            <button @click="nextStep" class="btn btn-primary btn-lg">
              Continue to Review
            </button>
          </div>
        </div>

        <!-- Step 3: Order Review -->
        <div v-show="currentStep === 3">
          <OrderReview
            :cart="cartStore.cart"
            :shipping-address="checkoutStore.selectedAddress"
            :coupon="appliedCoupon"
            :coupon-discount="appliedCoupon?.discount_amount || 0"
            :is-processing="ordersStore.isCreatingOrder"
            @edit-address="currentStep = 1"
            @edit-coupon="currentStep = 2"
            @place-order="handlePlaceOrder"
          />

          <div class="mt-6">
            <button @click="prevStep" class="btn btn-outline btn-lg">
              Back
            </button>
          </div>
        </div>
      </div>

      <!-- Order Summary Sidebar (only show on steps 1 and 2, hide on review step 3) -->
      <div v-if="currentStep < 3">
        <CartSummary
          :cart="cartStore.cart"
          :show-checkout-button="false"
          :allow-coupon="true"
          :coupon="appliedCoupon"
          @coupon-applied="handleCouponApplied"
          @coupon-removed="handleCouponRemoved"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useCheckoutStore } from '@/stores/checkout'
import { useOrdersStore } from '@/stores/orders'
import { paymentsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import ShippingAddressSelector from '@/components/checkout/ShippingAddressSelector.vue'
import CouponInput from '@/components/checkout/CouponInput.vue'
import OrderReview from '@/components/checkout/OrderReview.vue'
import CartSummary from '@/components/cart/CartSummary.vue'
import {
  CreditCardIcon,
  BanknotesIcon,
  BuildingLibraryIcon
} from '@heroicons/vue/24/outline'

const toast = useToast()
const cartStore = useCartStore()
const checkoutStore = useCheckoutStore()
const ordersStore = useOrdersStore()
const router = useRouter()

const currentStep = ref(1)
const isLoading = ref(true)
const selectedPaymentMethod = ref('stripe')
const customerNotes = ref('')
const appliedCoupon = ref(null)

const steps = [
  { id: 1, label: 'Shipping' },
  { id: 2, label: 'Payment' },
  { id: 3, label: 'Review' }
]

const paymentMethods = [
  {
    value: 'stripe',
    label: 'Credit/Debit Card',
    description: 'Pay securely with Stripe',
    icon: CreditCardIcon,
    disabled: false
  },
  {
    value: 'paypal',
    label: 'PayPal',
    description: 'Coming soon',
    icon: BuildingLibraryIcon,
    disabled: true
  },
  {
    value: 'cash',
    label: 'Cash on Delivery',
    description: 'Coming soon',
    icon: BanknotesIcon,
    disabled: true
  }
]

// Watch payment method changes
watch(selectedPaymentMethod, (newMethod) => {
  checkoutStore.setPaymentMethod(newMethod)
})

// Watch customer notes changes
watch(customerNotes, (newNotes) => {
  checkoutStore.setCustomerNotes(newNotes)
})

const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const handleAddressSelect = (addressId) => {
  checkoutStore.selectAddress(addressId)
}

const handleAddressAdded = () => {
  // Address automatically selected by store if it's default or first
}

const handleAddressUpdated = () => {
  // Address list automatically updated by store
}

const handleAddressDeleted = () => {
  // Address automatically removed by store
}

// Coupon handlers
const handleCouponApplied = (coupon) => {
  appliedCoupon.value = coupon
  toast.success(`Coupon ${coupon.code} applied!`)
}

const handleCouponRemoved = () => {
  appliedCoupon.value = null
}

const handlePlaceOrder = async () => {
  try {
    const orderData = {
      shipping_address_id: checkoutStore.selectedAddressId,
      payment_method: checkoutStore.paymentMethod,
      customer_notes: checkoutStore.customerNotes || undefined
    }

    // Add coupon if applied
    if (appliedCoupon.value) {
      orderData.coupon_code = appliedCoupon.value.code
    }

    const order = await ordersStore.createOrder(orderData)

    // If payment method is Stripe, create payment session and redirect to Stripe
    if (checkoutStore.paymentMethod === 'stripe') {
      try {
        // Get frontend URL from window location
        const frontendUrl = window.location.origin

        const paymentData = {
          frontend_url: frontendUrl
        }

        // Add coupon if applied
        if (appliedCoupon.value) {
          paymentData.coupon_code = appliedCoupon.value.code
        }

        const paymentResponse = await paymentsAPI.create(order.order_number, paymentData)

        // Redirect to Stripe checkout page
        window.location.href = paymentResponse.data.checkout_url
      } catch (error) {
        console.error('Failed to create payment session:', error)
        toast.error('Failed to initiate payment. Please try again.')
      }
    } else {
      // For other payment methods (PayPal, Cash on Delivery)
      // Clear cart and redirect to success page
      await cartStore.fetchCart()
      checkoutStore.reset()

      router.push({
        name: 'checkout-success',
        query: { order_number: order.order_number }
      })
    }
  } catch (error) {
    console.error('Failed to create order:', error)
    // Error handling done in store with toast
  }
}

onMounted(async () => {
  isLoading.value = true
  try {
    // Load cart and shipping addresses in parallel
    await Promise.all([
      cartStore.cart ? Promise.resolve() : cartStore.fetchCart(),
      checkoutStore.fetchShippingAddresses()
    ])

    // Set initial payment method
    selectedPaymentMethod.value = checkoutStore.paymentMethod
    customerNotes.value = checkoutStore.customerNotes
  } catch (error) {
    console.error('Failed to load checkout data:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
