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
    return api.get<PaginatedResponse<User>>('/admin/users/', { params })
  }

  async getUser(id: number): Promise<User> {
    return api.get<User>(`/admin/users/${id}`)
  }

  async createUser(data: UserCreate): Promise<User> {
    return api.post<User>('/admin/users/', data)
  }

  async updateUser(id: number, data: UserUpdate): Promise<User> {
    return api.put<User>(`/admin/users/${id}`, data)
  }

  async deleteUser(id: number): Promise<void> {
    return api.delete<void>(`/admin/users/${id}`)
  }

  async activateUser(id: number): Promise<User> {
    return api.patch<User>(`/admin/users/${id}/activate`)
  }

  async deactivateUser(id: number): Promise<User> {
    return api.patch<User>(`/admin/users/${id}/deactivate`)
  }

  async resetUserPassword(id: number): Promise<{ temporary_password: string }> {
    return api.post<{ temporary_password: string }>(`/admin/users/${id}/reset-password`)
  }
}

export default new UserService()