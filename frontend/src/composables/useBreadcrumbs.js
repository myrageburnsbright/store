import { computed } from 'vue'

/**
 * Build breadcrumb trail from category hierarchy
 * @param {Object} category - Category object with parent relationships
 * @returns {Array} Breadcrumb items [{name, path, isActive}]
 */
export function useBreadcrumbs(category) {
  return computed(() => {
    const breadcrumbs = [
      {
        name: 'Home',
        path: '/',
        isActive: false
      }
    ]

    if (!category || !category.value) return breadcrumbs

    const cat = category.value || category

    // Build chain by traversing up parent hierarchy
    const chain = []
    let current = cat

    while (current) {
      chain.unshift({
        name: current.name,
        path: `/categories/${current.slug}`,
        slug: current.slug
      })
      current = current.parent
    }

    // Add all categories from chain
    chain.forEach((item, index) => {
      breadcrumbs.push({
        name: item.name,
        path: item.path,
        slug: item.slug,
        isActive: index === chain.length - 1 // Last item is active
      })
    })

    return breadcrumbs
  })
}

/**
 * Build breadcrumbs for product page
 * @param {Object} product - Product object with category
 * @param {String} productName - Product name for last breadcrumb
 * @returns {Array} Breadcrumb items
 */
export function useProductBreadcrumbs(product, productName) {
  return computed(() => {
    const breadcrumbs = [
      {
        name: 'Home',
        path: '/',
        isActive: false
      }
    ]

    if (!product || !product.value) return breadcrumbs

    const prod = product.value || product

    // Add category chain if category has parent data
    if (prod.category) {
      const chain = []
      let current = prod.category

      while (current) {
        chain.unshift({
          name: current.name,
          path: `/categories/${current.slug}`,
          slug: current.slug
        })
        current = current.parent
      }

      chain.forEach(item => {
        breadcrumbs.push({
          name: item.name,
          path: item.path,
          slug: item.slug,
          isActive: false
        })
      })
    }

    // Add product as last item
    const name = productName?.value || productName || prod.name
    breadcrumbs.push({
      name,
      path: `/products/${prod.slug}`,
      slug: prod.slug,
      isActive: true // Current page
    })

    return breadcrumbs
  })
}

/**
 * Generate structured data (JSON-LD) for breadcrumbs - for SEO
 * @param {Array} breadcrumbs - Breadcrumb items
 * @param {String} baseUrl - Base URL of the site
 * @returns {Object} JSON-LD structured data
 */
export function generateBreadcrumbStructuredData(breadcrumbs, baseUrl = window.location.origin) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: crumb.path.startsWith('http') ? crumb.path : `${baseUrl}${crumb.path}`
    }))
  }
}
