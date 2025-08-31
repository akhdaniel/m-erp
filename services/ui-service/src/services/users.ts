import api from './api'
import type { User, UserCreate, UserUpdate, PaginatedResponse } from '@/types'

export class UserService {
  async getUsers(params?: {
    page?: number
    size?: number
    search?: string
    is_active?: boolean
    company_id?: number
  }): Promise<PaginatedResponse<User>> {
    return api.get<PaginatedResponse<User>>('/api/admin/users/', { params })
  }

  async getUser(id: number): Promise<User> {
    return api.get<User>(`/api/admin/users/${id}`)
  }

  async createUser(data: UserCreate): Promise<User> {
    return api.post<User>('/api/admin/users/', data)
  }

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    return api.put<User>(`/api/admin/users/${id}`, data)
  }

  async deleteUser(id: number): Promise<void> {
    return api.delete<void>(`/api/admin/users/${id}`)
  }

  async activateUser(id: number): Promise<User> {
    return api.patch<User>(`/api/admin/users/${id}/activate`)
  }

  async deactivateUser(id: number): Promise<User> {
    return api.patch<User>(`/api/admin/users/${id}/deactivate`)
  }

  async resetUserPassword(id: number): Promise<{ temporary_password: string }> {
    return api.post<{ temporary_password: string }>(`/api/admin/users/${id}/reset-password`)
  }
}

export default new UserService()