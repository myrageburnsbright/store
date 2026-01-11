/**
 * Валидатор для slug параметров
 * @param {Object} to - Объект маршрута назначения
 * @param {Object} from - Объект текущего маршрута
 * @param {Function} next - Функция для продолжения навигации
 */
export const validateSlug = (to, from, next) => {
    if (!to.params.slug || to.params.slug.trim() === '') {
      next({ name: 'NotFound' })
    } else {
      next()
    }
  }
  
  /**
   * Валидатор для ID параметров
   * @param {Object} to - Объект маршрута назначения
   * @param {Object} from - Объект текущего маршрута
   * @param {Function} next - Функция для продолжения навигации
   */
  export const validateId = (to, from, next) => {
    const id = parseInt(to.params.id)
    if (!id || isNaN(id) || id <= 0) {
      next({ name: 'NotFound' })
    } else {
      next()
    }
  }
  
  /**
   * Проверка прав доступа к редактированию поста
   * @param {Object} to - Объект маршрута назначения
   * @param {Object} from - Объект текущего маршрута
   * @param {Function} next - Функция для продолжения навигации
   */
  export const checkPostEditPermission = async (to, from, next) => {
    try {
      const { useAuthStore } = await import('@/stores/auth')
      const { usePostsStore } = await import('@/stores/posts')
      
      const authStore = useAuthStore()
      const postsStore = usePostsStore()
      
      if (!authStore.isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
      
      // Можно добавить проверку на владельца поста
      // const post = await postsStore.getPostBySlug(to.params.slug)
      // if (post.author_id !== authStore.user.id) {
      //   next({ name: 'NotFound' })
      //   return
      // }
      
      next()
    } catch (error) {
      next({ name: 'NotFound' })
    }
  }
  
  /**
   * Генерация мета-тегов для страницы
   * @param {string} title - Заголовок страницы
   * @param {string} description - Описание страницы
   * @param {string} keywords - Ключевые слова
   * @returns {Object} Объект с мета-данными
   */
  export const generatePageMeta = (title, description = '', keywords = '') => {
    return {
      title,
      meta: [
        {
          name: 'description',
          content: description
        },
        {
          name: 'keywords',
          content: keywords
        },
        {
          property: 'og:title',
          content: title
        },
        {
          property: 'og:description',
          content: description
        }
      ]
    }
  }
  
  /**
   * Middleware для логирования навигации
   * @param {Object} to - Объект маршрута назначения
   * @param {Object} from - Объект текущего маршрута
   * @param {Function} next - Функция для продолжения навигации
   */
  export const logNavigation = (to, from, next) => {
    // Navigation logging disabled
    next()
  }