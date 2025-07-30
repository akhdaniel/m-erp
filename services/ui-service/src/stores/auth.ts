import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import authService from '@/services/auth'
import type { User, LoginCredentials, AuthToken } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>((() => {
    const stored = localStorage.getItem('auth_user')
    return stored ? JSON.parse(stored) : null
  })())
  const token = ref<string | null>(Cookies.get('auth_token') || null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_superuser || false)

  // Actions
  async function login(credentials: LoginCredentials): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await authService.login(credentials)
      
      // Handle the response format from the backend
      const authToken = response.access_token
      const userData = response.user
      
      // Store token in cookie and state
      token.value = authToken
      Cookies.set('auth_token', authToken, {
        expires: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes default
        secure: window.location.protocol === 'https:',
        sameSite: 'lax'
      })

      // Set user data directly from login response
      user.value = userData
      localStorage.setItem('auth_user', JSON.stringify(userData))
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (err) {
      console.warn('Logout request failed:', err)
    } finally {
      // Clear auth state regardless of API call success
      user.value = null
      token.value = null
      Cookies.remove('auth_token')
      localStorage.removeItem('auth_user')
    }
  }

  async function fetchCurrentUser(): Promise<void> {
    if (!token.value) return

    try {
      user.value = await authService.getCurrentUser()
      localStorage.setItem('auth_user', JSON.stringify(user.value))
    } catch (err: any) {
      console.error('Failed to fetch current user:', err)
      if (err.response?.status === 401) {
        await logout()
      }
    }
  }

  async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await authService.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Password change failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function initializeAuth(): Promise<void> {
    if (token.value && !user.value) {
      await fetchCurrentUser()
    }
  }

  function clearError(): void {
    error.value = null
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    logout,
    fetchCurrentUser,
    changePassword,
    initializeAuth,
    clearError
  }
})