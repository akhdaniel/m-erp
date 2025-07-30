import api from './api'
import type { User, LoginCredentials, AuthToken } from '@/types'

export class AuthService {
  async login(credentials: LoginCredentials): Promise<AuthToken> {
    return api.post<AuthToken>('/auth/login', {
      email: credentials.username,
      password: credentials.password
    })
  }

  async getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  }

  async logout(): Promise<void> {
    return api.post<void>('/auth/logout')
  }

  async register(userData: {
    username: string
    email: string
    password: string
    first_name: string
    last_name: string
    company_id: number
  }): Promise<User> {
    return api.post<User>('/auth/register', userData)
  }

  async refreshToken(): Promise<AuthToken> {
    return api.post<AuthToken>('/auth/refresh')
  }

  async changePassword(data: {
    current_password: string
    new_password: string
  }): Promise<void> {
    return api.post<void>('/auth/change-password', data)
  }

  async resetPassword(email: string): Promise<void> {
    return api.post<void>('/auth/reset-password', { email })
  }
}

export default new AuthService()