import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import purchasingService, { 
  type PurchaseOrder, 
  type PurchaseOrderLineItem, 
  type Supplier,
  type PaginatedResponse 
} from '@/services/purchasing'
import type { Ref } from 'vue'

export const usePurchasingStore = defineStore('purchasing', () => {
  // State
  const purchaseOrders = ref<PurchaseOrder[]>([])
  const currentPurchaseOrder = ref<PurchaseOrder | null>(null)
  const suppliers = ref<Supplier[]>([])
  const currentSupplier = ref<Supplier | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0
  })

  // Getters
  const activeSuppliers = computed(() => 
    suppliers.value.filter(supplier => supplier.is_active)
  )

  const pendingApprovals = computed(() => 
    purchaseOrders.value.filter(po => po.approval_status === 'requires_approval')
  )

  // Approval related state
  const approvals = ref<any[]>([])
  const approvalStats = ref<any>({})
  const approvalWorkflows = ref<any[]>([])

  // Actions
  async function fetchPurchaseOrders(params?: {
    page?: number
    page_size?: number
    status?: string
    supplier_id?: number
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: PaginatedResponse<PurchaseOrder> = await purchasingService.getPurchaseOrders(params)
      
      purchaseOrders.value = response.data
      pagination.value = {
        total: response.total_count,
        page: response.page,
        pageSize: response.page_size,
        totalPages: response.total_pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch purchase orders'
      console.error('Failed to fetch purchase orders:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPurchaseOrder(id: number): Promise<PurchaseOrder | null> {
    try {
      isLoading.value = true
      error.value = null

      const order = await purchasingService.getPurchaseOrder(id)
      currentPurchaseOrder.value = order
      return order
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch purchase order'
      console.error('Failed to fetch purchase order:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createPurchaseOrder(data: PurchaseOrder): Promise<PurchaseOrder | null> {
    try {
      isLoading.value = true
      error.value = null

      const order = await purchasingService.createPurchaseOrder(data)
      
      // Add to the list if we have it loaded
      if (purchaseOrders.value.length > 0) {
        purchaseOrders.value.unshift(order)
        pagination.value.total += 1
      }
      
      currentPurchaseOrder.value = order
      return order
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create purchase order'
      console.error('Failed to create purchase order:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updatePurchaseOrder(id: number, data: PurchaseOrder): Promise<PurchaseOrder | null> {
    try {
      isLoading.value = true
      error.value = null

      const updatedOrder = await purchasingService.updatePurchaseOrder(id, data)
      
      // Update in the list if we have it
      const index = purchaseOrders.value.findIndex(po => po.id === id)
      if (index !== -1) {
        purchaseOrders.value[index] = updatedOrder
      }
      
      if (currentPurchaseOrder.value?.id === id) {
        currentPurchaseOrder.value = updatedOrder
      }
      
      return updatedOrder
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update purchase order'
      console.error('Failed to update purchase order:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deletePurchaseOrder(id: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await purchasingService.deletePurchaseOrder(id)
      
      // Remove from the list
      purchaseOrders.value = purchaseOrders.value.filter(po => po.id !== id)
      pagination.value.total -= 1
      
      if (currentPurchaseOrder.value?.id === id) {
        currentPurchaseOrder.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete purchase order'
      console.error('Failed to delete purchase order:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovals(params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: PaginatedResponse<any> = await purchasingService.getApprovals(params)
      
      approvals.value = response.data
      pagination.value = {
        total: response.total_count,
        page: response.page,
        pageSize: response.page_size,
        totalPages: response.total_pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch approvals'
      console.error('Failed to fetch approvals:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function approvePurchaseOrder(id: number, notes?: string): Promise<PurchaseOrder | null> {
    try {
      isLoading.value = true
      error.value = null

      const response = await purchasingService.approvePurchaseOrder(id, notes)
      const updatedOrder = response.purchase_order || response;
      
      // Update in the list if we have it
      const index = purchaseOrders.value.findIndex(po => po.id === id)
      if (index !== -1) {
        purchaseOrders.value[index] = updatedOrder
      }
      
      if (currentPurchaseOrder.value?.id === id) {
        currentPurchaseOrder.value = updatedOrder
      }
      
      // Also update in approvals list
      const approvalIndex = approvals.value.findIndex(a => a.id === id)
      if (approvalIndex !== -1) {
        approvals.value[approvalIndex] = { ...approvals.value[approvalIndex], status: 'approved' }
      }
      
      return updatedOrder
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to approve purchase order'
      console.error('Failed to approve purchase order:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function rejectPurchaseOrder(id: number, reason: string): Promise<PurchaseOrder | null> {
    try {
      isLoading.value = true
      error.value = null

      const response = await purchasingService.rejectPurchaseOrder(id, reason)
      const updatedOrder = response.purchase_order || response;
      
      // Update in the list if we have it
      const index = purchaseOrders.value.findIndex(po => po.id === id)
      if (index !== -1) {
        purchaseOrders.value[index] = updatedOrder
      }
      
      if (currentPurchaseOrder.value?.id === id) {
        currentPurchaseOrder.value = updatedOrder
      }
      
      // Also update in approvals list
      const approvalIndex = approvals.value.findIndex(a => a.id === id)
      if (approvalIndex !== -1) {
        approvals.value[approvalIndex] = { ...approvals.value[approvalIndex], status: 'rejected' }
      }
      
      return updatedOrder
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to reject purchase order'
      console.error('Failed to reject purchase order:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovalStats(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const stats = await purchasingService.getApprovalStats()
      approvalStats.value = stats
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch approval statistics'
      console.error('Failed to fetch approval statistics:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovalWorkflows(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const workflows = await purchasingService.getApprovalWorkflows()
      approvalWorkflows.value = workflows.workflows || []
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch approval workflows'
      console.error('Failed to fetch approval workflows:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSuppliers(params?: {
    page?: number
    page_size?: number
    status?: string
    category?: string
    min_rating?: number
  }): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response: PaginatedResponse<Supplier> = await purchasingService.getSuppliers(params)
      
      suppliers.value = response.data
      pagination.value = {
        total: response.total_count,
        page: response.page,
        pageSize: response.page_size,
        totalPages: response.total_pages
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch suppliers'
      console.error('Failed to fetch suppliers:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSupplier(id: number): Promise<Supplier | null> {
    try {
      isLoading.value = true
      error.value = null

      const supplier = await purchasingService.getSupplier(id)
      currentSupplier.value = supplier
      return supplier
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch supplier'
      console.error('Failed to fetch supplier:', err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function createSupplier(data: Partial<Supplier>): Promise<Supplier | null> {
    try {
      isLoading.value = true
      error.value = null

      const supplier = await purchasingService.createSupplier(data)
      
      // Add to the list if we have it loaded
      if (suppliers.value.length > 0) {
        suppliers.value.unshift(supplier)
        pagination.value.total += 1
      }
      
      currentSupplier.value = supplier
      return supplier
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create supplier'
      console.error('Failed to create supplier:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateSupplier(id: number, data: Partial<Supplier>): Promise<Supplier | null> {
    try {
      isLoading.value = true
      error.value = null

      const updatedSupplier = await purchasingService.updateSupplier(id, data)
      
      // Update in the list if we have it
      const index = suppliers.value.findIndex(s => s.id === id)
      if (index !== -1) {
        suppliers.value[index] = updatedSupplier
      }
      
      if (currentSupplier.value?.id === id) {
        currentSupplier.value = updatedSupplier
      }
      
      return updatedSupplier
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update supplier'
      console.error('Failed to update supplier:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteSupplier(id: number): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      await purchasingService.deleteSupplier(id)
      
      // Remove from the list
      suppliers.value = suppliers.value.filter(s => s.id !== id)
      pagination.value.total -= 1
      
      if (currentSupplier.value?.id === id) {
        currentSupplier.value = null
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete supplier'
      console.error('Failed to delete supplier:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function evaluateSupplier(id: number, evaluation: {
    delivery_rating?: number
    quality_rating?: number
    price_rating?: number
    communication_rating?: number
    comments?: string
  }): Promise<{ message: string; new_rating: number } | null> {
    try {
      isLoading.value = true
      error.value = null

      const result = await purchasingService.evaluateSupplier(id, evaluation)
      
      // Update the supplier in the list if we have it
      const index = suppliers.value.findIndex(s => s.id === id)
      if (index !== -1) {
        suppliers.value[index] = { ...suppliers.value[index], ...result }
      }
      
      if (currentSupplier.value?.id === id) {
        currentSupplier.value = { ...currentSupplier.value, ...result }
      }
      
      return result
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to evaluate supplier'
      console.error('Failed to evaluate supplier:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrentPurchaseOrder(): void {
    currentPurchaseOrder.value = null
  }

  function clearCurrentSupplier(): void {
    currentSupplier.value = null
  }

  function initializeNewPurchaseOrder(): void {
    currentPurchaseOrder.value = {
      supplier_id: 0,
      order_date: new Date().toISOString().split('T')[0],
      items: [],
      status: 'draft',
      approval_status: 'draft'
    }
  }

  return {
    // State
    purchaseOrders,
    currentPurchaseOrder,
    suppliers,
    currentSupplier,
    approvals,
    approvalStats,
    approvalWorkflows,
    isLoading,
    error,
    pagination,

    // Getters
    activeSuppliers,
    pendingApprovals,

    // Actions
    fetchPurchaseOrders,
    fetchPurchaseOrder,
    createPurchaseOrder,
    updatePurchaseOrder,
    deletePurchaseOrder,
    submitPurchaseOrderForApproval,
    fetchApprovals,
    approvePurchaseOrder,
    rejectPurchaseOrder,
    fetchApprovalStats,
    fetchApprovalWorkflows,
    fetchSuppliers,
    fetchSupplier,
    createSupplier,
    updateSupplier,
    deleteSupplier,
    evaluateSupplier,
    clearError,
    clearCurrentPurchaseOrder,
    clearCurrentSupplier,
    initializeNewPurchaseOrder
  }
})