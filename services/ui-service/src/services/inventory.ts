import api from '@/services/api'

// Types for inventory data
export interface Product {
  id: number
  code: string
  name: string
  description?: string
  category_id?: number
  list_price: number
  cost_price: number
  quantity_on_hand: number
  quantity_available: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface StockLevel {
  product_id: number
  product_name: string
  product_code: string
  warehouse_id: number
  warehouse_name: string
  quantity_on_hand: number
  quantity_reserved: number
  quantity_available: number
  quantity_incoming: number
  reorder_point?: number
  reorder_quantity?: number
}

export interface Warehouse {
  id: number
  code: string
  name: string
  description?: string
  address?: string
  city?: string
  state?: string
  country?: string
  is_active: boolean
  capacity_units?: number
  used_units?: number
  available_units?: number
}

export interface InventoryStats {
  total_products: number
  active_products: number
  total_stock_value: number
  total_items_in_stock: number
  low_stock_items: number
  out_of_stock_items: number
  warehouses_count: number
  pending_receipts: number
  recent_movements: number
}

export interface RecentMovement {
  id: number
  product_name: string
  movement_type: string
  quantity: number
  warehouse_name: string
  created_at: string
}

export interface LowStockItem {
  product_id: number
  product_name: string
  product_code: string
  current_stock: number
  reorder_point: number
  warehouse_name: string
}

class InventoryService {
  // Products
  async getProducts(params?: { 
    search?: string
    category_id?: number
    is_active?: boolean
    limit?: number
    offset?: number 
  }) {
    const queryParams = new URLSearchParams()
    if (params?.search) queryParams.append('search', params.search)
    if (params?.category_id) queryParams.append('category_id', params.category_id.toString())
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    
    const query = queryParams.toString()
    return api.get<Product[]>(`/v1/products${query ? '?' + query : ''}`)
  }

  async getProduct(id: number) {
    return api.get<Product>(`/v1/products/${id}`)
  }

  async getProductStats() {
    return api.get<{ 
      total: number
      active: number
      inactive: number
      categories: number 
    }>('/v1/products/stats')
  }

  // Stock
  async getStockLevels(params?: {
    warehouse_id?: number
    product_id?: number
    low_stock?: boolean
    limit?: number
    offset?: number
  }) {
    const queryParams = new URLSearchParams()
    if (params?.warehouse_id) queryParams.append('warehouse_id', params.warehouse_id.toString())
    if (params?.product_id) queryParams.append('product_id', params.product_id.toString())
    if (params?.low_stock) queryParams.append('low_stock', 'true')
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    
    const query = queryParams.toString()
    return api.get<StockLevel[]>(`/v1/stock${query ? '?' + query : ''}`)
  }

  async getStockStats() {
    return api.get<{
      total_value: number
      total_items: number
      low_stock_count: number
      out_of_stock_count: number
      warehouses: number
    }>('/v1/stock/stats')
  }

  async getLowStockItems(limit: number = 10) {
    return api.get<LowStockItem[]>(`/v1/stock/low?limit=${limit}`)
  }

  // Warehouses
  async getWarehouses(params?: {
    is_active?: boolean
    limit?: number
    offset?: number
  }) {
    const queryParams = new URLSearchParams()
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    if (params?.offset) queryParams.append('offset', params.offset.toString())
    
    const query = queryParams.toString()
    return api.get<Warehouse[]>(`/v1/warehouses${query ? '?' + query : ''}`)
  }

  async getWarehouse(id: number) {
    return api.get<Warehouse>(`/v1/warehouses/${id}`)
  }

  async getWarehouseStats() {
    return api.get<{
      total: number
      active: number
      total_capacity: number
      total_used: number
      utilization_percentage: number
    }>('/v1/warehouses/stats')
  }

  // Dashboard
  async getDashboardStats(): Promise<InventoryStats> {
    // In a real implementation, this would be a single optimized endpoint
    // For now, we'll simulate it with mock data or multiple calls
    try {
      // Try to get real data from the inventory service
      const [productStats, stockStats, warehouseStats] = await Promise.all([
        this.getProductStats().catch(() => ({ total: 0, active: 0, inactive: 0, categories: 0 })),
        this.getStockStats().catch(() => ({ 
          total_value: 0, 
          total_items: 0, 
          low_stock_count: 0, 
          out_of_stock_count: 0,
          warehouses: 0 
        })),
        this.getWarehouseStats().catch(() => ({ 
          total: 0, 
          active: 0, 
          total_capacity: 0, 
          total_used: 0,
          utilization_percentage: 0 
        }))
      ])

      return {
        total_products: productStats.total,
        active_products: productStats.active,
        total_stock_value: stockStats.total_value,
        total_items_in_stock: stockStats.total_items,
        low_stock_items: stockStats.low_stock_count,
        out_of_stock_items: stockStats.out_of_stock_count,
        warehouses_count: warehouseStats.total,
        pending_receipts: 0, // Would come from receiving endpoint
        recent_movements: 0  // Would come from movements endpoint
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
      // Return mock data for development
      return {
        total_products: 1248,
        active_products: 1156,
        total_stock_value: 2458750.00,
        total_items_in_stock: 45678,
        low_stock_items: 23,
        out_of_stock_items: 5,
        warehouses_count: 3,
        pending_receipts: 7,
        recent_movements: 156
      }
    }
  }

  async getRecentMovements(limit: number = 10): Promise<RecentMovement[]> {
    try {
      return await api.get<RecentMovement[]>(`/v1/stock/movements/recent?limit=${limit}`)
    } catch (error) {
      console.error('Error fetching recent movements:', error)
      // Return mock data for development
      return [
        {
          id: 1,
          product_name: 'Widget Pro X1',
          movement_type: 'receipt',
          quantity: 100,
          warehouse_name: 'Main Warehouse',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          product_name: 'Gadget Plus',
          movement_type: 'shipment',
          quantity: -25,
          warehouse_name: 'Distribution Center',
          created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 3,
          product_name: 'Component A',
          movement_type: 'adjustment',
          quantity: 10,
          warehouse_name: 'Main Warehouse',
          created_at: new Date(Date.now() - 7200000).toISOString()
        }
      ]
    }
  }
}

export default new InventoryService()