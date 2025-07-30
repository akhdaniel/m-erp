import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import companyService from '@/services/companies'
import type { Company, CompanyCreate, CompanyUpdate, CompanyListResponse } from '@/types'

export const useCompanyStore = defineStore('companies', () => {
  // State
  const companies = ref<Company[]>([])
  const currentCompany = ref<Company | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    size: 10,
    pages: 0
  })

  // Getters
  const activeCompanies = computed(() => 
    companies.value.filter(company => company.is_active)
  )

  const companyOptions = computed(() =>
    activeCompanies.value.map(company => ({
      value: company.id,
      label: `${company.name} (${company.code})`
    }))
  )

  // Actions
  async function fetchCompanies(params?: {
    page?: number
    size?: number
    search?: string
    is_active?: boolean
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: CompanyListResponse = await companyService.getCompanies(params)
      
      companies.value = response.companies
      pagination.value = {
        total: response.total,
        page: response.page,
        size: response.per_page,
        pages: response.pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch companies'
      console.error('Failed to fetch companies:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCompany(id: number): Promise<Company | null> {
    try {
      isLoading.value = true
      error.value = null

      const company = await companyService.getCompany(id)
      currentCompany.value = company
      return company
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch company'
      console.error('Failed to fetch company:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createCompany(data: CompanyCreate): Promise<Company | null> {
    try {
      isLoading.value = true
      error.value = null

      const company = await companyService.createCompany(data)
      
      // Ensure companies array is initialized
      if (!companies.value) {
        companies.value = []
      }
      
      companies.value.unshift(company)
      pagination.value.total += 1
      
      return company
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create company'
      console.error('Failed to create company:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateCompany(id: number, data: CompanyUpdate): Promise<Company | null> {
    try {
      isLoading.value = true
      error.value = null

      const updatedCompany = await companyService.updateCompany(id, data)
      
      // Ensure companies array is initialized
      if (companies.value) {
        const index = companies.value.findIndex(c => c.id === id)
        if (index !== -1) {
          companies.value[index] = updatedCompany
        }
      }
      
      if (currentCompany.value?.id === id) {
        currentCompany.value = updatedCompany
      }

      return updatedCompany
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update company'
      console.error('Failed to update company:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteCompany(id: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await companyService.deleteCompany(id)
      
      // Ensure companies array is initialized
      if (companies.value) {
        companies.value = companies.value.filter(c => c.id !== id)
        pagination.value.total -= 1
      }
      
      if (currentCompany.value?.id === id) {
        currentCompany.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete company'
      console.error('Failed to delete company:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function toggleCompanyStatus(id: number, activate: boolean): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const updatedCompany = activate 
        ? await companyService.activateCompany(id)
        : await companyService.deactivateCompany(id)
      
      // Ensure companies array is initialized
      if (companies.value) {
        const index = companies.value.findIndex(c => c.id === id)
        if (index !== -1) {
          companies.value[index] = updatedCompany
        }
      }
      
      if (currentCompany.value?.id === id) {
        currentCompany.value = updatedCompany
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || `Failed to ${activate ? 'activate' : 'deactivate'} company`
      console.error('Failed to toggle company status:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentCompany(): void {
    currentCompany.value = null
  }

  return {
    // State
    companies,
    currentCompany,
    isLoading,
    error,
    pagination,
    
    // Getters
    activeCompanies,
    companyOptions,
    
    // Actions
    fetchCompanies,
    fetchCompany,
    createCompany,
    updateCompany,
    deleteCompany,
    toggleCompanyStatus,
    clearError,
    clearCurrentCompany
  }
})