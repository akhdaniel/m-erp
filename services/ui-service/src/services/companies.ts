import api from './api'
import type { Company, CompanyCreate, CompanyUpdate, CompanyListResponse } from '@/types'

export class CompanyService {
  async getCompanies(params?: {
    page?: number
    size?: number
    search?: string
    is_active?: boolean
  }): Promise<CompanyListResponse> {
    return api.get<CompanyListResponse>('/v1/companies/', { params })
  }

  async getCompany(id: number): Promise<Company> {
    return api.get<Company>(`/v1/companies/${id}`)
  }

  async createCompany(data: CompanyCreate): Promise<Company> {
    return api.post<Company>('/v1/companies/', data)
  }

  async updateCompany(id: number, data: CompanyUpdate): Promise<Company> {
    return api.put<Company>(`/v1/companies/${id}`, data)
  }

  async deleteCompany(id: number): Promise<void> {
    return api.delete<void>(`/v1/companies/${id}`)
  }

  async activateCompany(id: number): Promise<Company> {
    return api.post<Company>(`/v1/companies/${id}/activate`)
  }

  async deactivateCompany(id: number): Promise<Company> {
    return api.post<Company>(`/v1/companies/${id}/deactivate`)
  }
}

export default new CompanyService()