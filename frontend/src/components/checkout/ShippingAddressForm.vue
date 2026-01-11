<template>
  <div class="card">
    <div class="card-header">
      <h3 class="text-lg font-semibold text-gray-900">
        {{ mode === 'edit' ? 'Edit Shipping Address' : 'Add Shipping Address' }}
      </h3>
    </div>

    <div class="card-body">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Full Name -->
        <div>
          <label for="full_name" class="form-label">
            Full Name <span class="text-error-600">*</span>
          </label>
          <input
            id="full_name"
            v-model="formData.full_name"
            type="text"
            class="form-input"
            placeholder="John Doe"
            required
          />
        </div>

        <!-- Phone -->
        <div>
          <label for="phone" class="form-label">
            Phone Number <span class="text-error-600">*</span>
          </label>
          <input
            id="phone"
            v-model="formData.phone"
            type="tel"
            class="form-input"
            placeholder="+1 (555) 123-4567"
            required
          />
        </div>

        <!-- Address Line 1 -->
        <div>
          <label for="address_line1" class="form-label">
            Address Line 1 <span class="text-error-600">*</span>
          </label>
          <input
            id="address_line1"
            v-model="formData.address_line1"
            type="text"
            class="form-input"
            placeholder="123 Main Street"
            required
          />
        </div>

        <!-- Address Line 2 -->
        <div>
          <label for="address_line2" class="form-label">
            Address Line 2 (Optional)
          </label>
          <input
            id="address_line2"
            v-model="formData.address_line2"
            type="text"
            class="form-input"
            placeholder="Apt 4B"
          />
        </div>

        <!-- City & State -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="city" class="form-label">
              City <span class="text-error-600">*</span>
            </label>
            <input
              id="city"
              v-model="formData.city"
              type="text"
              class="form-input"
              placeholder="New York"
              required
            />
          </div>

          <div>
            <label for="state" class="form-label">
              State/Province <span class="text-error-600">*</span>
            </label>
            <input
              id="state"
              v-model="formData.state"
              type="text"
              class="form-input"
              placeholder="NY"
              required
            />
          </div>
        </div>

        <!-- Postal Code & Country -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="postal_code" class="form-label">
              Postal Code <span class="text-error-600">*</span>
            </label>
            <input
              id="postal_code"
              v-model="formData.postal_code"
              type="text"
              class="form-input"
              placeholder="10001"
              required
            />
          </div>

          <div>
            <label for="country" class="form-label">
              Country <span class="text-error-600">*</span>
            </label>
            <input
              id="country"
              v-model="formData.country"
              type="text"
              class="form-input"
              placeholder="United States"
              required
            />
          </div>
        </div>

        <!-- Set as Default -->
        <div class="flex items-center">
          <input
            id="is_default"
            v-model="formData.is_default"
            type="checkbox"
            class="w-4 h-4 text-accent-600 border-gray-300 rounded focus:ring-accent-500"
          />
          <label for="is_default" class="ml-2 text-sm text-gray-700">
            Set as default shipping address
          </label>
        </div>

        <!-- Form Actions -->
        <div class="flex gap-3 pt-4">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="btn btn-primary flex-1"
          >
            <span v-if="isSubmitting" class="loading-spinner mr-2"></span>
            {{ isSubmitting ? 'Saving...' : (mode === 'edit' ? 'Update Address' : 'Save Address') }}
          </button>

          <button
            type="button"
            @click="handleCancel"
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
import { ref, watch } from 'vue'

const props = defineProps({
  address: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'create',
    validator: (value) => ['create', 'edit'].includes(value)
  }
})

const emit = defineEmits(['submit', 'cancel'])

const isSubmitting = ref(false)

const formData = ref({
  full_name: '',
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  is_default: false
})

// Populate form if editing existing address
watch(
  () => props.address,
  (newAddress) => {
    if (newAddress && props.mode === 'edit') {
      formData.value = {
        full_name: newAddress.full_name || '',
        phone: newAddress.phone || '',
        address_line1: newAddress.address_line1 || '',
        address_line2: newAddress.address_line2 || '',
        city: newAddress.city || '',
        state: newAddress.state || '',
        postal_code: newAddress.postal_code || '',
        country: newAddress.country || '',
        is_default: newAddress.is_default || false
      }
    }
  },
  { immediate: true }
)

const handleSubmit = async () => {
  isSubmitting.value = true
  try {
    emit('submit', formData.value)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>
