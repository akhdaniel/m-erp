import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api'
import type { MenuItem, MenuTreeResponse } from '@/types/menu'

export const useMenuStore = defineStore('menu', () => {
  const menus = ref<MenuItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<Date | null>(null)

  // Computed properties
  const topLevelMenus = computed(() => 
    // The API returns a tree structure, so menus.value already contains only top-level items
    menus.value.filter(menu => menu.is_visible)
  )

  const hasMenus = computed(() => menus.value.length > 0)

  // Actions
  async function fetchMenus() {
    loading.value = true
    error.value = null

    try {
      const response = await api.get<MenuTreeResponse>('/api/v1/menus/tree')
      console.log('Menu API response:', response.data)
      menus.value = response.data.menus || []
      console.log('Stored menus:', menus.value)
      console.log('Menu count:', menus.value.length)
      lastFetch.value = new Date()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch menus'
      console.error('Menu fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  function getMenuById(id: number): MenuItem | undefined {
    return menus.value.find(menu => menu.id === id)
  }

  function getMenuByCode(code: string): MenuItem | undefined {
    return menus.value.find(menu => menu.code === code)
  }

  function getChildMenus(parentId: number): MenuItem[] {
    return menus.value.filter(menu => menu.parent_id === parentId && menu.is_visible)
  }

  function clearMenus() {
    menus.value = []
    lastFetch.value = null
    error.value = null
  }

  // Refresh menus if they haven't been fetched or are older than 5 minutes
  async function refreshMenusIfNeeded() {
    if (!lastFetch.value || Date.now() - lastFetch.value.getTime() > 5 * 60 * 1000) {
      await fetchMenus()
    }
  }

  return {
    // State
    menus,
    loading,
    error,
    lastFetch,
    
    // Computed
    topLevelMenus,
    hasMenus,
    
    // Actions
    fetchMenus,
    getMenuById,
    getMenuByCode,
    getChildMenus,
    clearMenus,
    refreshMenusIfNeeded
  }
})