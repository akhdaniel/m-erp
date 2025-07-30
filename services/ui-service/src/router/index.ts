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
  document.title = to.meta.title ? `${to.meta.title} - M-ERP` : 'M-ERP'
  
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