<template>
  <router-link
    v-if="category.slug"
    :to="{ name: 'CategoryPosts', params: { slug: category.slug } }"
    class="card hover:shadow-lg transition-all duration-300 group cursor-pointer"
  >
    <div class="card-body text-center py-6">
      <!-- Category Icon -->
      <div class="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-accent-200 transition-colors">
        <component
          :is="getCategoryIcon(category.name)"
          class="w-6 h-6 text-accent-600"
        />
      </div>

      <!-- Category Name -->
      <h3 class="text-lg font-semibold text-gray-900 mb-2 group-hover:text-accent-600 transition-colors">
        {{ category.name }}
      </h3>

      <!-- Description -->
      <p v-if="category.description" class="text-gray-600 text-sm mb-3 line-clamp-2">
        {{ category.description }}
      </p>

      <!-- Post Count -->
      <div class="flex items-center justify-center text-sm text-gray-500">
        <DocumentTextIcon class="w-4 h-4 mr-1" />
        <span>{{ category.posts_count }} {{ pluralize(category.posts_count, 'post', 'posts', 'posts') }}</span>
      </div>
    </div>
  </router-link>

  <!-- Fallback for categories without slug -->
  <div
    v-else
    class="card cursor-not-allowed opacity-50"
  >
    <div class="card-body text-center py-6">
      <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center mx-auto mb-4">
        <component
          :is="getCategoryIcon(category.name)"
          class="w-6 h-6 text-gray-400"
        />
      </div>

      <h3 class="text-lg font-semibold text-gray-600 mb-2">
        {{ category.name }}
      </h3>

      <p v-if="category.description" class="text-gray-500 text-sm mb-3 line-clamp-2">
        {{ category.description }}
      </p>

      <div class="flex items-center justify-center text-sm text-gray-400">
        <DocumentTextIcon class="w-4 h-4 mr-1" />
        <span>{{ category.posts_count }} {{ pluralize(category.posts_count, 'post', 'posts', 'posts') }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import {
  DocumentTextIcon,
  ComputerDesktopIcon,
  BeakerIcon,
  HeartIcon,
  BookOpenIcon,
  GlobeAltIcon,
  CameraIcon,
  MusicalNoteIcon,
  TrophyIcon,
  BriefcaseIcon,
  HomeIcon,
  ShoppingBagIcon,
  AcademicCapIcon,
  FilmIcon,
  TagIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'CategoryCard',
  components: {
    DocumentTextIcon,
    ComputerDesktopIcon,
    BeakerIcon,
    HeartIcon,
    BookOpenIcon,
    GlobeAltIcon,
    CameraIcon,
    MusicalNoteIcon,
    TrophyIcon,
    BriefcaseIcon,
    HomeIcon,
    ShoppingBagIcon,
    AcademicCapIcon,
    FilmIcon,
    TagIcon
  },
  props: {
    category: {
      type: Object,
      required: true,
      validator(category) {
        return category && typeof category === 'object' && category.name
      }
    }
  },
  setup() {
    const getCategoryIcon = (categoryName) => {
      if (!categoryName) return 'TagIcon'
      
      const name = categoryName.toLowerCase()
      
      if (name.includes('tech') || name.includes('технолог')) return 'ComputerDesktopIcon'
      if (name.includes('science') || name.includes('наука')) return 'BeakerIcon'
      if (name.includes('health') || name.includes('здоровье')) return 'HeartIcon'
      if (name.includes('education') || name.includes('образование')) return 'AcademicCapIcon'
      if (name.includes('travel') || name.includes('путешеств')) return 'GlobeAltIcon'
      if (name.includes('photo') || name.includes('фото')) return 'CameraIcon'
      if (name.includes('music') || name.includes('музыка')) return 'MusicalNoteIcon'
      if (name.includes('sport') || name.includes('спорт')) return 'TrophyIcon'
      if (name.includes('business') || name.includes('бизнес')) return 'BriefcaseIcon'
      if (name.includes('home') || name.includes('дом')) return 'HomeIcon'
      if (name.includes('shop') || name.includes('покупк')) return 'ShoppingBagIcon'
      if (name.includes('book') || name.includes('книг')) return 'BookOpenIcon'
      if (name.includes('movie') || name.includes('film') || name.includes('фильм') || name.includes('кино')) return 'FilmIcon'
      
      return 'TagIcon'
    }
    
    const pluralize = (count, one, few, many) => {
      if (typeof count !== 'number') return many
      
      const mod10 = count % 10
      const mod100 = count % 100
      
      if (mod100 >= 11 && mod100 <= 19) {
        return many
      }
      if (mod10 === 1) {
        return one
      }
      if (mod10 >= 2 && mod10 <= 4) {
        return few
      }
      return many
    }
    
    return {
      getCategoryIcon,
      pluralize
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>