import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import partnerService from '@/services/partners'
import type { Partner, PartnerCreate, PartnerUpdate, PartnerListResponse } from '@/types'

export const usePartnerStore = defineStore('partners', () => {
  // State
  const partners = ref<Partner[]>([])
  const currentPartner = ref<Partner | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  })

  // Getters
  const activePartners = computed(() => 
    partners.value?.filter(partner => partner.is_active) || []
  )

  const customers = computed(() =>
    activePartners.value.filter(partner => partner.is_customer)
  )

  const suppliers = computed(() =>
    activePartners.value.filter(partner => partner.is_supplier)
  )

  const vendors = computed(() =>
    activePartners.value.filter(partner => partner.is_vendor)
  )

  const partnerOptions = computed(() =>
    activePartners.value.map(partner => ({
      value: partner.id,
      label: `${partner.name}${partner.code ? ` (${partner.code})` : ''}`
    }))
  )

  // Actions
  async function fetchPartners(params?: {
    company_id?: number
    page?: number
    size?: number
    search?: string
    partner_type?: string
    is_active?: boolean
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: PartnerListResponse = await partnerService.getPartners(params)
      
      partners.value = response.partners
      pagination.value = {
        total: response.total,
        page: response.page,
        size: response.per_page,
        pages: response.pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch partners'
      console.error('Failed to fetch partners:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPartner(id: number): Promise<Partner | null> {
    try {
      isLoading.value = true
      error.value = null

      const partner = await partnerService.getPartner(id)
      currentPartner.value = partner
      return partner
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch partner'
      console.error('Failed to fetch partner:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createPartner(data: PartnerCreate): Promise<Partner | null> {
    try {
      isLoading.value = true
      error.value = null

      const partner = await partnerService.createPartner(data)
      
      // Ensure partners array is initialized
      if (!partners.value) {
        partners.value = []
      }
      
      partners.value.unshift(partner)
      pagination.value.total += 1
      
      return partner
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create partner'
      console.error('Failed to create partner:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updatePartner(id: number, data: PartnerUpdate): Promise<Partner | null> {
    try {
      isLoading.value = true
      error.value = null

      const updatedPartner = await partnerService.updatePartner(id, data)
      
      // Ensure partners array is initialized
      if (partners.value) {
        const index = partners.value.findIndex(p => p.id === id)
        if (index !== -1) {
          partners.value[index] = updatedPartner
        }
      }
      
      if (currentPartner.value?.id === id) {
        currentPartner.value = updatedPartner
      }

      return updatedPartner
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update partner'
      console.error('Failed to update partner:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deletePartner(id: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await partnerService.deletePartner(id)
      
      // Ensure partners array is initialized
      if (partners.value) {
        partners.value = partners.value.filter(p => p.id !== id)
        pagination.value.total -= 1
      }
      
      if (currentPartner.value?.id === id) {
        currentPartner.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete partner'
      console.error('Failed to delete partner:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function togglePartnerStatus(id: number, activate: boolean): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedPartner = activate 
        ? await partnerService.activatePartner(id)
        : await partnerService.deactivatePartner(id)
      
      // Ensure partners array is initialized
      if (partners.value) {
        const index = partners.value.findIndex(p => p.id === id)
        if (index !== -1) {
          partners.value[index] = updatedPartner
        }
      }
      
      if (currentPartner.value?.id === id) {
        currentPartner.value = updatedPartner
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || `Failed to ${activate ? 'activate' : 'deactivate'} partner`
      console.error('Failed to toggle partner status:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentPartner(): void {
    currentPartner.value = null
  }

  return {
    // State
    partners,
    currentPartner,
    isLoading,
    error,
    pagination,
    
    // Getters
    activePartners,
    customers,
    suppliers,
    vendors,
    partnerOptions,
    
    // Actions
    fetchPartners,
    fetchPartner,
    createPartner,
    updatePartner,
    deletePartner,
    togglePartnerStatus,
    clearError,
    clearCurrentPartner
  }
})