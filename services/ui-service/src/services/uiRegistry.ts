import api from '@/services/api'

// Types for UI Registry
export interface UIComponent {
  id: string
  service: string
  type: string
  title: string
  description?: string
  path?: string
  config: Record<string, any>
  permissions: string[]
  order: number
  icon?: string
  parent_id?: string
  metadata: Record<string, any>
}

export interface DashboardWidget {
  id: string
  service: string
  title: string
  type: string
  size: string
  position?: { row: number; col: number }
  data_endpoint: string
  refresh_interval: number
  config: Record<string, any>
  permissions: string[]
}

export interface ListView {
  id: string
  service: string
  title: string
  entity: string
  columns: Array<{
    key: string
    label: string
    format?: string
    sortable?: boolean
  }>
  data_endpoint: string
  actions: Array<{
    id: string
    label: string
    icon?: string
    type?: string
  }>
  filters: Array<{
    key: string
    label: string
    type: string
    options?: any[]
  }>
  sorting: Record<string, any>
  pagination: boolean
  permissions: string[]
}

export interface FormView {
  id: string
  service: string
  title: string
  entity: string
  mode: string
  fields: Array<{
    key: string
    label: string
    type: string
    required?: boolean
    validation?: Record<string, any>
    conditional?: Record<string, any>
    [key: string]: any
  }>
  submit_endpoint: string
  data_endpoint?: string
  validation_rules: Record<string, any>
  layout: string
  permissions: string[]
}

export interface UIPackage {
  service: string
  components: UIComponent[]
  widgets: DashboardWidget[]
  lists: ListView[]
  forms: FormView[]
}

class UIRegistryService {
  // Get all UI components
  async getComponents(service?: string, type?: string): Promise<UIComponent[]> {
    const params = new URLSearchParams()
    if (service) params.append('service', service)
    if (type) params.append('type', type)
    
    const query = params.toString()
    return api.get<UIComponent[]>(`/v1/ui-registry/components${query ? '?' + query : ''}`)
  }

  // Get dashboard widgets
  async getDashboardWidgets(): Promise<DashboardWidget[]> {
    return api.get<DashboardWidget[]>('/v1/ui-registry/dashboard/widgets')
  }

  // Get list views
  async getListViews(): Promise<ListView[]> {
    return api.get<ListView[]>('/v1/ui-registry/lists')
  }

  // Get form views
  async getFormViews(): Promise<FormView[]> {
    return api.get<FormView[]>('/v1/ui-registry/forms')
  }

  // Get complete UI package for a service
  async getServiceUIPackage(service: string): Promise<UIPackage> {
    return api.get<UIPackage>(`/v1/ui-registry/services/${service}/ui-package`)
  }

  // Get specific component
  async getComponent(service: string, componentId: string): Promise<UIComponent> {
    return api.get<UIComponent>(`/v1/ui-registry/components/${service}/${componentId}`)
  }

  // Get specific list view
  async getListView(service: string, listId: string): Promise<ListView> {
    const lists = await this.getListViews()
    const list = lists.find(l => l.service === service && l.id === listId)
    if (!list) throw new Error(`List view not found: ${service}/${listId}`)
    return list
  }

  // Get specific form view
  async getFormView(service: string, formId: string): Promise<FormView> {
    const forms = await this.getFormViews()
    const form = forms.find(f => f.service === service && f.id === formId)
    if (!form) throw new Error(`Form view not found: ${service}/${formId}`)
    return form
  }

  // Fetch data for a widget
  async fetchWidgetData(widget: DashboardWidget): Promise<any> {
    try {
      return await api.get(widget.data_endpoint)
    } catch (error) {
      console.error(`Error fetching widget data for ${widget.id}:`, error)
      return null
    }
  }

  // Fetch data for a list
  async fetchListData(list: ListView, params?: Record<string, any>): Promise<any[]> {
    const queryParams = new URLSearchParams(params as any)
    const query = queryParams.toString()
    
    try {
      return await api.get<any[]>(`${list.data_endpoint}${query ? '?' + query : ''}`)
    } catch (error) {
      console.error(`Error fetching list data for ${list.id}:`, error)
      return []
    }
  }

  // Submit form data
  async submitForm(form: FormView, data: Record<string, any>): Promise<any> {
    const method = form.mode === 'edit' ? 'put' : 'post'
    const endpoint = form.mode === 'edit' && data.id 
      ? form.submit_endpoint.replace('{id}', data.id)
      : form.submit_endpoint
    
    return api[method](endpoint, data)
  }

  // Load form data for editing
  async loadFormData(form: FormView, id: string): Promise<any> {
    if (!form.data_endpoint) {
      throw new Error('No data endpoint configured for form')
    }
    
    const endpoint = form.data_endpoint.replace('{id}', id)
    return api.get(endpoint)
  }
}

export default new UIRegistryService()