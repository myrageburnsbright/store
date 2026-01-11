import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { shippingAPI, couponsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useCheckoutStore = defineStore('checkout', () => {
  // State
  const shippingAddresses = ref([])
  const selectedAddressId = ref(null)
  const paymentMethod = ref('stripe')
  const couponCode = ref('')
  const couponDiscount = ref(0)
  const couponData = ref(null)
  const customerNotes = ref('')
  const isLoadingAddresses = ref(false)
  const isValidatingCoupon = ref(false)
  const isProcessingPayment = ref(false)

  // Computed
  const defaultAddress = computed(() =>
    shippingAddresses.value.find(addr => addr.is_default)
  )

  const hasAddresses = computed(() => shippingAddresses.value.length > 0)

  const selectedAddress = computed(() =>
    shippingAddresses.value.find(addr => addr.id === selectedAddressId.value)
  )

  const canProceed = computed(() => {
    return selectedAddressId.value && paymentMethod.value
  })

  const hasCoupon = computed(() => !!couponData.value)

  // Actions
  const fetchShippingAddresses = async () => {
    isLoadingAddresses.value = true
    try {
      const response = await shippingAPI.getAll()
      shippingAddresses.value = response.data.results || response.data || []

      // Auto-select default address
      if (defaultAddress.value && !selectedAddressId.value) {
        selectedAddressId.value = defaultAddress.value.id
      }

      return shippingAddresses.value
    } catch (error) {
      console.error('Error fetching shipping addresses:', error)
      shippingAddresses.value = []
      throw error
    } finally {
      isLoadingAddresses.value = false
    }
  }

  const addShippingAddress = async (addressData) => {
    try {
      const response = await shippingAPI.create(addressData)
      const newAddress = response.data

      shippingAddresses.value.push(newAddress)

      // If it's marked as default or it's the first address, select it
      if (newAddress.is_default || shippingAddresses.value.length === 1) {
        selectedAddressId.value = newAddress.id
      }

      toast.success('Address added successfully')
      return newAddress
    } catch (error) {
      console.error('Error adding shipping address:', error)
      toast.error('Failed to add address')
      throw error
    }
  }

  const updateShippingAddress = async (id, addressData) => {
    try {
      const response = await shippingAPI.update(id, addressData)
      const index = shippingAddresses.value.findIndex(addr => addr.id === id)
      if (index !== -1) {
        shippingAddresses.value[index] = response.data
      }
      toast.success('Address updated successfully')
      return response.data
    } catch (error) {
      console.error('Error updating shipping address:', error)
      toast.error('Failed to update address')
      throw error
    }
  }

  const deleteShippingAddress = async (id) => {
    try {
      await shippingAPI.delete(id)
      shippingAddresses.value = shippingAddresses.value.filter(addr => addr.id !== id)

      // If deleted address was selected, clear selection
      if (selectedAddressId.value === id) {
        selectedAddressId.value = null
      }

      toast.success('Address deleted successfully')
    } catch (error) {
      console.error('Error deleting shipping address:', error)
      toast.error('Failed to delete address')
      throw error
    }
  }

  const selectAddress = (addressId) => {
    selectedAddressId.value = addressId
  }

  const validateCoupon = async (code, orderAmount) => {
    if (!code) {
      clearCoupon()
      return
    }

    isValidatingCoupon.value = true
    try {
      const response = await couponsAPI.validate({
        code,
        order_amount: orderAmount
      })

      if (response.data.valid) {
        couponCode.value = code
        couponDiscount.value = parseFloat(response.data.discount_amount || 0)
        couponData.value = response.data.coupon
        toast.success(response.data.message || 'Coupon applied successfully')
        return response.data
      } else {
        clearCoupon()
        toast.error('Invalid coupon code')
        return null
      }
    } catch (error) {
      console.error('Error validating coupon:', error)
      clearCoupon()

      if (error.response?.data?.code) {
        toast.error(error.response.data.code[0] || 'Invalid coupon code')
      } else {
        toast.error('Failed to validate coupon')
      }

      throw error
    } finally {
      isValidatingCoupon.value = false
    }
  }

  const clearCoupon = () => {
    couponCode.value = ''
    couponDiscount.value = 0
    couponData.value = null
  }

  const setPaymentMethod = (method) => {
    paymentMethod.value = method
  }

  const setCustomerNotes = (notes) => {
    customerNotes.value = notes
  }

  const reset = () => {
    selectedAddressId.value = null
    paymentMethod.value = 'stripe'
    couponCode.value = ''
    couponDiscount.value = 0
    couponData.value = null
    customerNotes.value = ''
  }

  return {
    // State
    shippingAddresses,
    selectedAddressId,
    paymentMethod,
    couponCode,
    couponDiscount,
    couponData,
    customerNotes,
    isLoadingAddresses,
    isValidatingCoupon,
    isProcessingPayment,

    // Computed
    defaultAddress,
    hasAddresses,
    selectedAddress,
    canProceed,
    hasCoupon,

    // Actions
    fetchShippingAddresses,
    addShippingAddress,
    updateShippingAddress,
    deleteShippingAddress,
    selectAddress,
    validateCoupon,
    clearCoupon,
    setPaymentMethod,
    setCustomerNotes,
    reset
  }
})
