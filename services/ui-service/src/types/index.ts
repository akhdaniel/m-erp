// User types
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_superuser: boolean
  company_id: number
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  first_name: string
  last_name: string
  company_id: number
  is_active?: boolean
  is_superuser?: boolean
}

export interface UserUpdate {
  email?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  is_superuser?: boolean
}

// Company types
export interface Company {
  id: number
  name: string
  legal_name: string
  code: string
  email?: string
  phone?: string
  website?: string
  tax_id?: string
  street?: string
  street2?: string
  city?: string
  state?: string
  zip?: string
  country?: string
  currency: string
  timezone?: string
  logo_url?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CompanyCreate {
  name: string
  legal_name: string
  code: string
  email?: string
  phone?: string
  website?: string
  tax_id?: string
  street?: string
  street2?: string
  city?: string
  state?: string
  zip?: string
  country?: string
  currency: string
  timezone?: string
  logo_url?: string
  is_active?: boolean
}

export interface CompanyUpdate {
  name?: string
  legal_name?: string
  email?: string
  phone?: string
  website?: string
  tax_id?: string
  street?: string
  street2?: string
  city?: string
  state?: string
  zip?: string
  country?: string
  currency?: string
  timezone?: string
  logo_url?: string
  is_active?: boolean
}

// Partner types
export interface Partner {
  id: number
  name: string
  code?: string
  partner_type: string
  email?: string
  phone?: string
  mobile?: string
  website?: string
  tax_id?: string
  industry?: string
  parent_partner_id?: number
  is_company: boolean
  is_customer: boolean
  is_supplier: boolean
  is_vendor: boolean
  is_active: boolean
  company_id: number
  created_at: string
  updated_at: string
}

export interface PartnerCreate {
  name: string
  code?: string
  partner_type?: string
  email?: string
  phone?: string
  mobile?: string
  website?: string
  tax_id?: string
  industry?: string
  parent_partner_id?: number
  is_company?: boolean
  is_customer?: boolean
  is_supplier?: boolean
  is_vendor?: boolean
  is_active?: boolean
  company_id: number
}

export interface PartnerUpdate {
  name?: string
  code?: string
  partner_type?: string
  email?: string
  phone?: string
  mobile?: string
  website?: string
  tax_id?: string
  industry?: string
  parent_partner_id?: number
  is_company?: boolean
  is_customer?: boolean
  is_supplier?: boolean
  is_vendor?: boolean
  is_active?: boolean
}

// Partner-specific paginated response to match backend
export interface PartnerListResponse {
  partners: Partner[]
  total: number
  page: number
  per_page: number
  pages: number
}

// Auth types
export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  refresh_token: string
  user: User
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Company-specific paginated response to match backend
export interface CompanyListResponse {
  companies: Company[]
  total: number
  page: number
  per_page: number
  pages: number
}

// Permission types
export interface Permission {
  id: number
  code: string
  name: string
  description?: string
  category: string
  action: string
  is_active: boolean
}

export interface Role {
  id: number
  name: string
  description?: string
  level: number
  is_active: boolean
  permissions: Permission[]
}

// Menu types
export interface MenuItem {
  id: number
  name: string
  path?: string
  icon?: string
  parent_id?: number
  sequence: number
  is_active: boolean
  is_visible: boolean
  required_permission?: string
  required_role_level?: number
  children?: MenuItem[]
}