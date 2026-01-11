<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h3 class="text-lg font-semibold text-gray-900">Shipping Address</h3>
      <button
        @click="showAddForm = !showAddForm"
        class="btn btn-sm btn-outline"
      >
        <PlusIcon class="w-4 h-4 mr-1" />
        Add New Address
      </button>
    </div>

    <!-- Add New Address Form -->
    <div v-if="showAddForm" class="mb-4">
      <ShippingAddressForm
        mode="create"
        @submit="handleAddAddress"
        @cancel="showAddForm = false"
      />
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-8 text-center">
      <div class="loading-spinner mx-auto"></div>
      <p class="text-gray-600 mt-2">Loading addresses...</p>
    </div>

    <!-- No Addresses -->
    <div v-else-if="addresses.length === 0 && !showAddForm" class="card card-body text-center py-8">
      <p class="text-gray-600 mb-4">You don't have any saved shipping addresses</p>
      <button @click="showAddForm = true" class="btn btn-primary mx-auto">
        <PlusIcon class="w-5 h-5 mr-2" />
        Add Your First Address
      </button>
    </div>

    <!-- Address List -->
    <div v-else class="space-y-3">
      <div
        v-for="address in addresses"
        :key="address.id"
        class="card cursor-pointer transition-all"
        :class="{
          'ring-2 ring-accent-500 bg-accent-50': selectedId === address.id,
          'hover:shadow-md': selectedId !== address.id
        }"
        @click="selectAddress(address.id)"
      >
        <div class="card-body">
          <div class="flex items-start gap-3">
            <!-- Radio Button -->
            <div class="flex-shrink-0 mt-1">
              <input
                type="radio"
                :id="`address-${address.id}`"
                :value="address.id"
                :checked="selectedId === address.id"
                class="w-4 h-4 text-accent-600 border-gray-300 focus:ring-accent-500"
                @click.stop="selectAddress(address.id)"
              />
            </div>

            <!-- Address Details -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h4 class="font-semibold text-gray-900">{{ address.full_name }}</h4>
                <span v-if="address.is_default" class="badge badge-primary text-xs">
                  Default
                </span>
              </div>

              <p class="text-sm text-gray-600">{{ address.phone }}</p>

              <p class="text-sm text-gray-700 mt-2">
                {{ address.address_line1 }}
                <span v-if="address.address_line2">, {{ address.address_line2 }}</span>
              </p>

              <p class="text-sm text-gray-700">
                {{ address.city }}, {{ address.state }} {{ address.postal_code }}
              </p>

              <p class="text-sm text-gray-700">{{ address.country }}</p>
            </div>

            <!-- Action Buttons -->
            <div class="flex-shrink-0 flex gap-2">
              <button
                @click.stop="handleEdit(address)"
                class="p-2 text-gray-400 hover:text-accent-600 transition-colors"
                title="Edit address"
              >
                <PencilIcon class="w-4 h-4" />
              </button>

              <button
                v-if="!address.is_default"
                @click.stop="handleDelete(address.id)"
                class="p-2 text-gray-400 hover:text-error-600 transition-colors"
                title="Delete address"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Address Modal -->
    <div v-if="editingAddress" class="mt-4">
      <ShippingAddressForm
        mode="edit"
        :address="editingAddress"
        @submit="handleUpdateAddress"
        @cancel="editingAddress = null"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import ShippingAddressForm from './ShippingAddressForm.vue'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  addresses: {
    type: Array,
    required: true
  },
  selectedId: {
    type: Number,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'add', 'update', 'delete'])

const checkoutStore = useCheckoutStore()

const showAddForm = ref(false)
const editingAddress = ref(null)

const selectAddress = (addressId) => {
  emit('select', addressId)
}

const handleAddAddress = async (addressData) => {
  try {
    await checkoutStore.addShippingAddress(addressData)
    showAddForm.value = false
    emit('add')
  } catch (error) {
    console.error('Failed to add address:', error)
  }
}

const handleEdit = (address) => {
  editingAddress.value = { ...address }
  showAddForm.value = false
}

const handleUpdateAddress = async (addressData) => {
  try {
    await checkoutStore.updateShippingAddress(editingAddress.value.id, addressData)
    editingAddress.value = null
    emit('update')
  } catch (error) {
    console.error('Failed to update address:', error)
  }
}

const handleDelete = async (addressId) => {
  if (confirm('Are you sure you want to delete this address?')) {
    try {
      await checkoutStore.deleteShippingAddress(addressId)
      emit('delete')
    } catch (error) {
      console.error('Failed to delete address:', error)
    }
  }
}
</script>
