import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(null)
  const refreshToken = ref(null)
  const isLoading = ref(false)
  const isInitialized = ref(false)

  // Computed properties
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userFullName = computed(() => {
    if (!user.value) return ''
    return user.value.full_name || `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username
  })
  const userInitials = computed(() => {
    if (!user.value) return ''
    const fullName = userFullName.value
    if (fullName) {
      const names = fullName.split(' ')
      return names.map(name => name.charAt(0).toUpperCase()).join('').slice(0, 2)
    }
    return user.value.username.charAt(0).toUpperCase()
  })

  // Actions
  const setTokens = (accessToken, refreshTokenValue) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue

    // Save tokens in cookies
    if (accessToken) {
      Cookies.set('access_token', accessToken, {
        expires: 1, // 1 day
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      })
    } else {
      Cookies.remove('access_token')
    }

    if (refreshTokenValue) {
      Cookies.set('refresh_token', refreshTokenValue, {
        expires: 7, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      })
    } else {
      Cookies.remove('refresh_token')
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    refreshToken.value = null
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
  }

  const initializeAuth = async () => {
    if (isInitialized.value) return

    try {
      const savedAccessToken = Cookies.get('access_token')
      const savedRefreshToken = Cookies.get('refresh_token')

      if (savedAccessToken && savedRefreshToken) {
        token.value = savedAccessToken
        refreshToken.value = savedRefreshToken

        // Try to get user data
        try {
          const response = await authAPI.getProfile()
          user.value = response.data
        } catch (error) {
          // If unable to get profile, clear tokens
          if (error.response?.status === 401) {
            // Try to refresh token
            try {
              await refreshAccessToken()
              const profileResponse = await authAPI.getProfile()
              user.value = profileResponse.data
            } catch (refreshError) {
              clearAuth()
            }
          } else {
            clearAuth()
          }
        }
      }
    } catch (error) {
      clearAuth()
    } finally {
      isInitialized.value = true
    }
  }

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)
      const { user: userData, access, refresh } = response.data
      
      setUser(userData)
      setTokens(access, refresh)
      
      return response.data
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    try {
      const response = await authAPI.register(userData)
      const { user: newUser, access, refresh } = response.data
      
      setUser(newUser)
      setTokens(access, refresh)
      
      return response.data
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true
    try {
      if (refreshToken.value) {
        await authAPI.logout({ refresh_token: refreshToken.value })
      }
    } catch (error) {
      // Ignore logout errors
    } finally {
      clearAuth()
      isLoading.value = false
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('Refresh token not available')
    }
    
    try {
      const response = await authAPI.refreshToken({ refresh: refreshToken.value })
      const { access } = response.data
      
      setTokens(access, refreshToken.value)
      return access
    } catch (error) {
      clearAuth()
      throw error
    }
  }

  const updateProfile = async (profileData) => {
    isLoading.value = true
    try {
      const response = await authAPI.updateProfile(profileData)
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const updateProfilePartial = async (profileData) => {
    isLoading.value = true
    try {
      const response = await authAPI.updateProfilePartial(profileData)
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    isLoading.value = true
    try {
      const response = await authAPI.changePassword(passwordData)
      return response.data
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const refreshUserProfile = async () => {
    if (!isAuthenticated.value) return

    try {
      const response = await authAPI.getProfile()
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }

  // Access rights checks
  const canEditPost = (post) => {
    return user.value && (user.value.id === post.author || user.value.is_staff)
  }

  const canEditComment = (comment) => {
    return user.value && (user.value.id === comment.author || user.value.is_staff)
  }

  const canModerate = () => {
    return user.value && (user.value.is_staff || user.value.is_superuser)
  }

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    isInitialized,

    // Computed properties
    isAuthenticated,
    userFullName,
    userInitials,

    // Actions
    initializeAuth,
    login,
    register,
    logout,
    refreshAccessToken,
    updateProfile,
    updateProfilePartial,
    changePassword,
    refreshUserProfile,

    // Permission checks
    canEditPost,
    canEditComment,
    canModerate,

    // Utilities
    setTokens,
    setUser,
    clearAuth
  }
})