<template>
  <span
    class="badge"
    :class="badgeClass"
  >
    {{ statusLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) =>
      ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'].includes(value)
  }
})

const statusLabels = {
  pending: 'Pending Payment',
  paid: 'Paid',
  processing: 'Processing',
  shipped: 'Shipped',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
  refunded: 'Refunded'
}

const badgeClasses = {
  pending: 'badge-gray',
  paid: 'badge-success',
  processing: 'badge-primary',
  shipped: 'badge-primary',
  delivered: 'badge-success',
  cancelled: 'badge-error',
  refunded: 'bg-orange-100 text-orange-800'
}

const statusLabel = computed(() => statusLabels[props.status] || props.status)
const badgeClass = computed(() => badgeClasses[props.status] || 'badge-gray')
</script>
