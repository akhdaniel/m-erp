export type MenuItemType = 'link' | 'dropdown' | 'divider' | 'header'

export interface MenuItem {
  id: number
  code: string
  title: string
  description?: string
  url?: string
  external_url?: boolean
  icon?: string
  parent_id?: number
  order_index: number
  level: number
  is_active: boolean
  is_visible: boolean
  required_permission?: string
  required_role_level?: number
  css_class?: string
  badge_text?: string
  badge_class?: string
  target?: string
  metadata?: Record<string, any>
  metadata_info?: Record<string, any>  // API returns this field name
  item_type: MenuItemType
  created_at: string
  updated_at: string
  children?: MenuItem[]
}

export interface MenuTreeResponse {
  menus: MenuItem[]
  total_items: number
  user_permissions?: string[]
}