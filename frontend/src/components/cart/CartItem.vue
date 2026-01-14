<template>
  <div class="card">
    <div class="card-body">
      <div class="flex gap-4">
        <!-- Product Image -->
        <div class="relative w-24 h-24 flex-shrink-0">
          <img
            v-if="productImage"
            :src="productImage"
            :alt="item.product.name"
            class="w-full h-full object-cover rounded"
          />
          <div v-else class="w-full h-full bg-gray-200 rounded flex items-center justify-center">
            <ShoppingBagIcon class="w-8 h-8 text-gray-400" />
          </div>
        </div>

        <!-- Product Info -->
        <div class="flex-1 min-w-0">
          <router-link
            :to="{ name: 'product-detail', params: { slug: item.product.slug } }"
            class="text-lg font-semibold text-gray-900 hover:text-accent-600 transition-colors line-clamp-2"
          >
            {{ item.product.name }}
          </router-link>

          <!-- Variant Info -->
          <p v-if="item.variant" class="text-sm text-gray-600 mt-1">
            Variant: {{ item.variant.name }}
          </p>

          <!-- Category -->
          <p class="text-sm text-gray-500 mt-1">
            {{ item.product.category_name || "Uncategorized" }}
          </p>

          <!-- Price Info -->
          <div class="mt-2">
            <span class="text-lg font-bold text-gray-900">
              ${{ parseFloat(item.original_price).toFixed(2) }}
            </span>
            <span v-if="item.discount_amount > 0" class="text-sm text-gray-500 ml-2">
              (Saved: ${{ parseFloat(item.discount_amount).toFixed(2) }})
            </span>
          </div>

          <!-- Stock Warning -->
          <p v-if="item.product.stock_quantity < 5 && item.product.stock_quantity > 0" class="text-sm text-warning-600 mt-1">
            Only {{ item.product.stock_quantity }} left in stock
          </p>
          <p v-else-if="item.product.stock_quantity === 0" class="text-sm text-error-600 mt-1">
            Out of stock
          </p>
        </div>

        <!-- Quantity & Actions -->
        <div class="flex flex-col items-end justify-between">
          <!-- Total Price -->
          <div class="text-xl font-bold text-gray-900">
            ${{ parseFloat(item.total_price).toFixed(2) }}
          </div>

          <!-- Quantity Selector -->
          <div class="quantity-selector">
            <button
              @click="decrementQuantity"
              :disabled="isUpdating || item.quantity <= 1"
              class="quantity-btn"
              aria-label="Decrease quantity"
            >
              <MinusIcon class="w-4 h-4" />
            </button>
            <input
              type="number"
              :value="item.quantity"
              @input="handleQuantityInput"
              :disabled="isUpdating"
              class="quantity-input no-arrows"
              min="1"
              :max="item.product.stock_quantity"
            />
            <button
              @click="incrementQuantity"
              :disabled="isUpdating || item.quantity >= item.product.stock_quantity"
              class="quantity-btn"
              aria-label="Increase quantity"
            >
              <PlusIcon class="w-4 h-4" />
            </button>
          </div>

          <!-- Remove Button -->
          <button
            @click="handleRemove"
            :disabled="isRemoving"
            class="btn btn-sm btn-outline text-error-600 hover:bg-error-50 mt-2"
          >
            <TrashIcon class="w-4 h-4 mr-1" />
            {{ isRemoving ? 'Removing...' : 'Remove' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useCartStore } from '@/stores/cart'
import { ShoppingBagIcon, MinusIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update', 'remove'])

const cartStore = useCartStore()
const isUpdating = ref(false)
const isRemoving = ref(false)

// Get product image - handle both list API (primary_image) and detail API (images array)
const productImage = computed(() => {
  const base = api.defaults.baseURL.replace(/\/$/, '')
  // From list API: primary_image is an object with {image: 'url'}
  if (props.item.product.primary_image && props.item.product.primary_image.image) {
    const imgPath = props.item.product.primary_image.image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  // From detail API: images is an array
  if (props.item.product.images && props.item.product.images.length > 0) {
    const imgPath = props.item.product.images[0].image
    if (imgPath.startsWith('http')) return imgPath
    return `${base}${imgPath.startsWith('/') ? '' : '/'}${imgPath}`
  }
  return null
})

const incrementQuantity = async () => {
  if (props.item.quantity >= props.item.product.stock_quantity) return
  await updateQuantity(props.item.quantity + 1)
}

const decrementQuantity = async () => {
  if (props.item.quantity <= 1) return
  await updateQuantity(props.item.quantity - 1)
}

const handleQuantityInput = async (event) => {
  const value = parseInt(event.target.value)
  if (isNaN(value) || value < 1) {
    event.target.value = props.item.quantity
    return
  }
  const maxQty = props.item.product.stock_quantity
  const newQty = Math.min(Math.max(1, value), maxQty)
  if (newQty !== props.item.quantity) {
    await updateQuantity(newQty)
  }
}

const updateQuantity = async (newQuantity) => {
  isUpdating.value = true
  try {
    await cartStore.updateQuantity(props.item.id, newQuantity)
    emit('update')
  } catch (error) {
    console.error("[CartItem] Error updating quantity:", error)
  } finally {
    isUpdating.value = false
  }
}

const handleRemove = async () => {
  isRemoving.value = true
  try {
    await cartStore.removeItem(props.item.id)
    emit('remove')
  } catch (error) {
    console.error("[CartItem] Error removing item:", error)
  } finally {
    isRemoving.value = false
  }
}
</script>
