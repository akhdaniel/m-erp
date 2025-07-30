import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import userService from '@/services/users'
import type { User, UserCreate, UserUpdate, PaginatedResponse } from '@/types'

export const useUserStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  })

  // Getters
  const activeUsers = computed(() => 
    users.value.filter(user => user.is_active)
  )

  const adminUsers = computed(() =>
    users.value.filter(user => user.is_superuser)
  )

  // Actions
  async function fetchUsers(params?: {
    page?: number
    size?: number
    search?: string
    is_active?: boolean
    company_id?: number
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: PaginatedResponse<User> = await userService.getUsers(params)
      
      users.value = response.items
      pagination.value = {
        total: response.total,
        page: response.page,
        size: response.size,
        pages: response.pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch users'
      console.error('Failed to fetch users:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser(id: number): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null

      const user = await userService.getUser(id)
      currentUser.value = user
      return user
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch user'
      console.error('Failed to fetch user:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createUser(data: UserCreate): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null

      const user = await userService.createUser(data)
      users.value.unshift(user)
      pagination.value.total += 1
      
      return user
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create user'
      console.error('Failed to create user:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateUser(id: number, data: UserUpdate): Promise<User | null> {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = await userService.updateUser(id, data)
      
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser
      }

      return updatedUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update user'
      console.error('Failed to update user:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteUser(id: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await userService.deleteUser(id)
      
      users.value = users.value.filter(u => u.id !== id)
      pagination.value.total -= 1
      
      if (currentUser.value?.id === id) {
        currentUser.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete user'
      console.error('Failed to delete user:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function toggleUserStatus(id: number, activate: boolean): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedUser = activate 
        ? await userService.activateUser(id)
        : await userService.deactivateUser(id)
      
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }
      
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || `Failed to ${activate ? 'activate' : 'deactivate'} user`
      console.error('Failed to toggle user status:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function resetUserPassword(id: number): Promise<string> {
    try {
      isLoading.value = true
      error.value = null

      const response = await userService.resetUserPassword(id)
      return response.temporary_password
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to reset user password'
      console.error('Failed to reset user password:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentUser(): void {
    currentUser.value = null
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    error,
    pagination,
    
    // Getters
    activeUsers,
    adminUsers,
    
    // Actions
    fetchUsers,
    fetchUser,
    createUser,
    updateUser,
    deleteUser,
    toggleUserStatus,
    resetUserPassword,
    clearError,
    clearCurrentUser
  }
})