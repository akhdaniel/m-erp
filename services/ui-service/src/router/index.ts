import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresAuth: false, title: 'Login' }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Dashboard' }
  },
  {
    path: '/companies',
    name: 'Companies',
    component: () => import('@/views/companies/CompanyListView.vue'),
    meta: { requiresAuth: true, title: 'Companies' }
  },
  {
    path: '/companies/create',
    name: 'CreateCompany',
    component: () => import('@/views/companies/CompanyFormView.vue'),
    meta: { requiresAuth: true, title: 'Create Company' }
  },
  {
    path: '/companies/:id/edit',
    name: 'EditCompany',
    component: () => import('@/views/companies/CompanyFormView.vue'),
    meta: { requiresAuth: true, title: 'Edit Company' }
  },
  {
    path: '/partners',
    name: 'Partners',
    component: () => import('@/views/partners/PartnerListView.vue'),
    meta: { requiresAuth: true, title: 'Partners' }
  },
  {
    path: '/partners/create',
    name: 'CreatePartner',
    component: () => import('@/views/partners/PartnerFormView.vue'),
    meta: { requiresAuth: true, title: 'Create Partner' }
  },
  {
    path: '/partners/:id/edit',
    name: 'EditPartner',
    component: () => import('@/views/partners/PartnerFormView.vue'),
    meta: { requiresAuth: true, title: 'Edit Partner' }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/users/UserListView.vue'),
    meta: { requiresAuth: true, title: 'Users', requiresAdmin: true }
  },
  {
    path: '/users/create',
    name: 'CreateUser',
    component: () => import('@/views/users/UserFormView.vue'),
    meta: { requiresAuth: true, title: 'Create User', requiresAdmin: true }
  },
  {
    path: '/users/:id/edit',
    name: 'EditUser',
    component: () => import('@/views/users/UserFormView.vue'),
    meta: { requiresAuth: true, title: 'Edit User', requiresAdmin: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/profile/ProfileView.vue'),
    meta: { requiresAuth: true, title: 'My Profile' }
  },
  // Inventory Management Routes
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('@/views/inventory/InventoryDashboard.vue'),
    meta: { requiresAuth: true, title: 'Inventory Management' }
  },
  {
    path: '/inventory/products',
    name: 'ProductList',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Products - Inventory' }
  },
  {
    path: '/inventory/products/new',
    name: 'ProductCreate',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'New Product - Inventory' }
  },
  {
    path: '/inventory/products/:id/edit',
    name: 'ProductEdit',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Edit Product - Inventory' }
  },
  {
    path: '/inventory/categories',
    redirect: '/inventory'
  },
  {
    path: '/inventory/stock-movements',
    redirect: '/inventory'
  },
  {
    path: '/inventory/stock-levels',
    redirect: '/inventory'
  },
  {
    path: '/inventory/warehouses',
    redirect: '/inventory'
  },
  {
    path: '/inventory/receiving',
    redirect: '/inventory'
  },
  {
    path: '/inventory/suppliers',
    redirect: '/partners'
  },
  // Sales Management Routes
  {
    path: '/sales',
    redirect: '/sales/dashboard'
  },
  {
    path: '/sales/dashboard',
    name: 'SalesDashboard',
    component: () => import('@/views/sales/SalesDashboard.vue'),
    meta: { requiresAuth: true, title: 'Sales Dashboard' }
  },
  {
    path: '/sales/quotes',
    name: 'QuotesList',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Sales Quotes' }
  },
  {
    path: '/sales/quotes/new',
    name: 'QuoteCreate',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'New Quote' }
  },
  {
    path: '/sales/quotes/:id',
    name: 'QuoteView',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'View Quote' }
  },
  {
    path: '/sales/quotes/:id/edit',
    name: 'QuoteEdit',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Edit Quote' }
  },
  {
    path: '/sales/orders',
    name: 'OrdersList',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Sales Orders' }
  },
  {
    path: '/sales/orders/new',
    name: 'OrderCreate',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'New Order' }
  },
  {
    path: '/sales/orders/:id',
    name: 'OrderView',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'View Order' }
  },
  {
    path: '/sales/orders/:id/edit',
    name: 'OrderEdit',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Edit Order' }
  },
  {
    path: '/sales/pricing',
    name: 'PricingList',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Pricing Rules' }
  },
  {
    path: '/sales/pricing/new',
    name: 'PricingCreate',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'New Pricing Rule' }
  },
  {
    path: '/sales/pricing/:id/edit',
    name: 'PricingEdit',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Edit Pricing Rule' }
  },
  {
    path: '/sales/customers',
    name: 'CustomersList',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Customers' }
  },
  {
    path: '/sales/analytics',
    name: 'SalesAnalytics',
    component: () => import('@/views/DynamicView.vue'),
    meta: { requiresAuth: true, title: 'Sales Analytics' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { requiresAuth: false, title: 'Page Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - XERPIUM` : 'XERPIUM'
  
  // Initialize auth if we have a token but no user data
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initializeAuth()
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      // If token is invalid, clear it and redirect to login
      await authStore.logout()
      if (to.meta.requiresAuth) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check if route requires admin privileges
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
    return
  }
  
  // Redirect to dashboard if trying to access login while authenticated
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router