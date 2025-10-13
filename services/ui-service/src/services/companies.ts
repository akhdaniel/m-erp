import api from './api'
import type { Company, CompanyCreate, CompanyUpdate, CompanyListResponse } from '@/types'

export class CompanyService {
  async getCompanies(params?: {
    page?: number
    size?: number
    search?: string
    is_active?: boolean
  }): Promise<CompanyListResponse> {
    return api.get<CompanyListResponse>('/api/v1/base/companies/', { params })
  }

  async getCompany(id: number): Promise<Company> {
    return api.get<Company>(`/api/v1/base/companies/${id}`)
  }

  async createCompany(data: CompanyCreate): Promise<Company> {
    return api.post<Company>('/api/v1/base/companies/', data)
  }

  async updateCompany(id: number, data: CompanyUpdate): Promise<Company> {
    return api.put<Company>(`/api/v1/base/companies/${id}`, data)
  }

  async deleteCompany(id: number): Promise<void> {
    return api.delete<void>(`/api/v1/base/companies/${id}`)
  }

  async activateCompany(id: number): Promise<Company> {
    return api.post<Company>(`/api/v1/base/companies/${id}/activate`)
  }

  async deactivateCompany(id: number): Promise<Company> {
    return api.post<Company>(`/api/v1/base/companies/${id}/deactivate`)
  }
}

export default new CompanyService()