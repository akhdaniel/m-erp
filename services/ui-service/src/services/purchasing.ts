import api from './api'

// Purchase Order interfaces
export interface PurchaseOrderLineItem {
  id?: number
  product_id: number
  item_name: string
  item_code: string
  description?: string
  quantity: number
  unit_price: number
  discount_percentage?: number
  total_amount?: number
}

export interface PurchaseOrder {
  id?: number
  po_number?: string
  supplier_id: number
  supplier_name?: string
  order_date: string
  expected_delivery?: string
  currency_code?: string
  payment_terms?: string
  shipping_address?: string
  billing_address?: string
  notes?: string
  status?: string
  approval_status?: string
  total_amount?: number
  items: PurchaseOrderLineItem[]
}

// Supplier interfaces
export interface Supplier {
  id: number
  code: string
  name: string
  category?: string
  contact_person?: string
  email?: string
  phone?: string
  website?: string
  address?: string
  city?: string
  state?: string
  country?: string
  postal_code?: string
  payment_terms?: string
  payment_terms_days?: number
  currency_code?: string
  credit_limit?: number
  is_active: boolean
  rating?: number
  performance_rating?: number
  total_orders?: number
  total_spend?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total_count: number
  page: number
  page_size: number
  total_pages: number
}

class PurchasingService {
  private baseUrl = `${import.meta.env.VITE_PURCHASING_API || '/api/v1'}/purchasing`

  // Purchase Order API methods
  async getPurchaseOrders(params?: {
    page?: number
    page_size?: number
    status?: string
    supplier_id?: number
  }): Promise<PaginatedResponse<PurchaseOrder>> {
    return api.get(`${this.baseUrl}/purchase-orders`, { params })
  }

  async getPurchaseOrder(id: number): Promise<PurchaseOrder> {
    return api.get(`${this.baseUrl}/purchase-orders/${id}`)
  }

  async createPurchaseOrder(data: PurchaseOrder): Promise<PurchaseOrder> {
    return api.post(`${this.baseUrl}/purchase-orders`, data)
  }

  async updatePurchaseOrder(id: number, data: PurchaseOrder): Promise<PurchaseOrder> {
    return api.put(`${this.baseUrl}/purchase-orders/${id}`, data)
  }

  async deletePurchaseOrder(id: number): Promise<void> {
    return api.delete(`${this.baseUrl}/purchase-orders/${id}`)
  }

  async submitPurchaseOrderForApproval(id: number): Promise<PurchaseOrder> {
    return api.post(`${this.baseUrl}/purchase-orders/${id}/submit-for-approval`)
  }

  // Supplier API methods
  async getSuppliers(params?: {
    page?: number
    page_size?: number
    status?: string
    category?: string
    min_rating?: number
  }): Promise<PaginatedResponse<Supplier>> {
    return api.get(`${this.baseUrl}/suppliers`, { params })
  }

  async getSupplier(id: number): Promise<Supplier> {
    return api.get(`${this.baseUrl}/suppliers/${id}`)
  }

  async createSupplier(data: Partial<Supplier>): Promise<Supplier> {
    return api.post(`${this.baseUrl}/suppliers`, data)
  }

  async updateSupplier(id: number, data: Partial<Supplier>): Promise<Supplier> {
    return api.put(`${this.baseUrl}/suppliers/${id}`, data)
  }

  async deleteSupplier(id: number): Promise<void> {
    return api.delete(`${this.baseUrl}/suppliers/${id}`)
  }

  async evaluateSupplier(id: number, evaluation: {
    delivery_rating?: number
    quality_rating?: number
    price_rating?: number
    communication_rating?: number
    comments?: string
  }): Promise<{ message: string; new_rating: number }> {
    return api.post(`${this.baseUrl}/suppliers/${id}/evaluate`, evaluation)
  }

  // Approval API methods
  async getPendingApprovals(): Promise<any> {
    return api.get(`${this.baseUrl}/approvals/pending`)
  }

  async getApprovals(params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<PaginatedResponse<any>> {
    return api.get(`${this.baseUrl}/approvals/pending`, { params })
  }

  async approvePurchaseOrder(id: number, notes?: string): Promise<PurchaseOrder> {
    return api.post(`${this.baseUrl}/purchase-orders/${id}/approve`, { approval_notes: notes })
  }

  async rejectPurchaseOrder(id: number, reason: string): Promise<PurchaseOrder> {
    return api.post(`${this.baseUrl}/purchase-orders/${id}/reject`, { rejection_reason: reason })
  }

  async getApprovalStats(): Promise<any> {
    return api.get(`${this.baseUrl}/approvals/stats`)
  }

  async getApprovalWorkflows(): Promise<any> {
    return api.get(`${this.baseUrl}/approvals/workflows`)
  }

  async getApprovalHistory(days?: number): Promise<any> {
    const params = days ? { days } : {}
    return api.get(`${this.baseUrl}/approvals/history`, { params })
  }

  // Dashboard API methods
  async getDashboardMetrics(): Promise<any> {
    return api.get(`${this.baseUrl}/dashboard/metrics`)
  }

  async getSpendingTrend(): Promise<any> {
    return api.get(`${this.baseUrl}/dashboard/charts/spending-trend`)
  }

  async getSupplierDistribution(): Promise<any> {
    return api.get(`${this.baseUrl}/dashboard/charts/supplier-distribution`)
  }

  async getRecentOrders(limit?: number): Promise<any> {
    return api.get(`${this.baseUrl}/dashboard/recent/orders`, { params: { limit } })
  }

  async getTopSuppliers(limit?: number): Promise<any> {
    return api.get(`${this.baseUrl}/dashboard/analytics/top-suppliers`, { params: { limit } })
  }
}

export default new PurchasingService()