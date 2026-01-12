<template>
  <nav aria-label="Breadcrumb" class="breadcrumb-nav">
    <ol class="breadcrumb-list">
      <li
        v-for="(crumb, index) in breadcrumbs"
        :key="index"
        class="breadcrumb-item"
        :class="{ 'active': crumb.isActive }"
      >
        <!-- Home icon for first item -->
        <HomeIcon v-if="index === 0" class="breadcrumb-home-icon" />

        <!-- Link for non-active items -->
        <router-link
          v-if="!crumb.isActive"
          :to="crumb.path"
          class="breadcrumb-link"
        >
          {{ crumb.name }}
        </router-link>

        <!-- Text for active (current) item -->
        <span v-else class="breadcrumb-current">
          {{ crumb.name }}
        </span>

        <!-- Separator (not after last item) -->
        <ChevronRightIcon
          v-if="index < breadcrumbs.length - 1"
          class="breadcrumb-separator"
        />
      </li>
    </ol>
  </nav>
</template>

<script setup>
import { onMounted } from 'vue'
import { HomeIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { generateBreadcrumbStructuredData } from '@/composables/useBreadcrumbs'

const props = defineProps({
  breadcrumbs: {
    type: Array,
    required: true,
    default: () => []
  },
  /**
   * Include JSON-LD structured data for SEO
   */
  includeStructuredData: {
    type: Boolean,
    default: true
  }
})

// Add structured data to page head for SEO
onMounted(() => {
  if (!props.includeStructuredData || props.breadcrumbs.length === 0) return

  const structuredData = generateBreadcrumbStructuredData(props.breadcrumbs)

  // Create script tag with JSON-LD
  const script = document.createElement('script')
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(structuredData)
  script.id = 'breadcrumb-structured-data'

  // Remove existing breadcrumb structured data if present
  const existing = document.getElementById('breadcrumb-structured-data')
  if (existing) {
    existing.remove()
  }

  // Add to document head
  document.head.appendChild(script)
})
</script>

<style scoped>
.breadcrumb-nav {
  padding: 0.75rem 0;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.breadcrumb-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.breadcrumb-item.active {
  color: #111827;
  font-weight: 500;
}

.breadcrumb-home-icon {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
  flex-shrink: 0;
}

.breadcrumb-link {
  color: #0284c7;
  text-decoration: none;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #0369a1;
  text-decoration: underline;
}

.breadcrumb-current {
  color: #111827;
  font-weight: 500;
}

.breadcrumb-separator {
  width: 1rem;
  height: 1rem;
  color: #9ca3af;
  flex-shrink: 0;
}

/* Mobile: Collapse breadcrumbs if too long */
@media (max-width: 640px) {
  .breadcrumb-list {
    font-size: 0.813rem;
  }

  .breadcrumb-item {
    max-width: 150px;
  }

  .breadcrumb-link,
  .breadcrumb-current {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
