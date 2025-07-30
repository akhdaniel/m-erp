import api from './api'
import type { Partner, PartnerCreate, PartnerUpdate, PartnerListResponse } from '@/types'

export class PartnerService {
  async getPartners(params?: {
    company_id?: number
    page?: number
    size?: number
    search?: string
    partner_type?: string
    is_active?: boolean
  }): Promise<PartnerListResponse> {
    return api.get<PartnerListResponse>('/v1/partners/', { params })
  }

  async getPartner(id: number): Promise<Partner> {
    return api.get<Partner>(`/v1/partners/${id}`)
  }

  async createPartner(data: PartnerCreate): Promise<Partner> {
    return api.post<Partner>('/v1/partners/', data)
  }

  async updatePartner(id: number, data: PartnerUpdate): Promise<Partner> {
    return api.put<Partner>(`/v1/partners/${id}`, data)
  }

  async deletePartner(id: number): Promise<void> {
    return api.delete<void>(`/v1/partners/${id}`)
  }

  async activatePartner(id: number): Promise<Partner> {
    return api.post<Partner>(`/v1/partners/${id}/activate`)
  }

  async deactivatePartner(id: number): Promise<Partner> {
    return api.post<Partner>(`/v1/partners/${id}/deactivate`)
  }
}

export default new PartnerService()