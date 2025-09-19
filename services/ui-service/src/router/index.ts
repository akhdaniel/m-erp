import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import type { RouteRecordRaw } from 'vue-router'
import type { MenuItem } from '@/types/menu'

const staticRoutes: RouteRecordRaw[] = [
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

// Function to generate dynamic routes from menu items
function generateDynamicRoutes(menus: MenuItem[]): RouteRecordRaw[] {
  const dynamicRoutes: RouteRecordRaw[] = []
  
  function processMenu(menu: MenuItem) {
    // Skip hidden menus
    if (!menu.is_visible) return
    
    // Generate route for this menu if it has a URL
    if (menu.url && menu.item_type === 'link') {
      // For inventory, sales, purchasing, and other dynamic modules, use DynamicView
      /*
      if (menu.url.startsWith('/inventory') || 
          menu.url.startsWith('/base') || 
          menu.url.startsWith('/sales') || 
          menu.url.startsWith('/purchasing') ||
          menu.url.startsWith('/settings')) {
        dynamicRoutes.push({
          path: menu.url,
          name: menu.code || `dynamic-${menu.id}`,
          component: () => import('@/views/DynamicView.vue'),
          meta: { 
            requiresAuth: true, 
            title: menu.title,
            requiredPermission: menu.required_permission
          }
        })
        
        // Add "edit" route if this is a list view
        if (menu.url.includes('/products')   || 
            menu.url.includes('/base')     || 
            menu.url.includes('/orders')     || 
            menu.url.includes('/suppliers')  ||
            menu.url.includes('/quotations') ||
            menu.url.includes('/transactions') ||
            menu.url.includes('/pricing')    ||
            menu.url.includes('/warehouses') ||
            menu.url.includes('/categories') ||
            menu.url.includes('/customers')  ||
            menu.url.includes('/receiving')  ||
            menu.url.includes('/stock')) {
          dynamicRoutes.push({
            path: `${menu.url}/:id/edit`,
            name: `${menu.code || `dynamic-${menu.id}`}-edit`,
            component: () => import('@/views/DynamicView.vue'),
            meta: { 
              requiresAuth: true, 
              title: `Edit ${menu.title}`,
              requiredPermission: menu.required_permission
            }
          })
          
          // Add "create" route if this is a list view
          dynamicRoutes.push({
            path: `${menu.url}/new`,
            name: `${menu.code || `dynamic-${menu.id}`}-create`,
            component: () => import('@/views/DynamicView.vue'),
            meta: { 
              requiresAuth: true, 
              title: `New ${menu.title.replace(' List', '').replace('s', '')}`,
              requiredPermission: menu.required_permission
            }
          })
        }
      }
        */
      // For dashboard views, use DynamicDashboard
      /*
      else if (menu.url.includes('/dashboard')) {
        dynamicRoutes.push({
          path: menu.url,
          name: menu.code || `dynamic-dashboard-${menu.id}`,
          component: () => import('@/views/DynamicDashboard.vue'),
          meta: { 
            requiresAuth: true, 
            title: menu.title,
            requiredPermission: menu.required_permission
          }
        })
      }
      */
     if (menu.url.includes('/dashboard')) {
        dynamicRoutes.push({
          path: menu.url,
          name: menu.code || `dynamic-dashboard-${menu.id}`,
          component: () => import('@/views/DynamicDashboard.vue'),
          meta: { 
            requiresAuth: true, 
            title: menu.title,
            requiredPermission: menu.required_permission
          }
        })
      }
      else{
         dynamicRoutes.push({
          path: menu.url,
          name: menu.code || `dynamic-${menu.id}`,
          component: () => import('@/views/DynamicView.vue'),
          meta: { 
            requiresAuth: true, 
            title: menu.title,
            requiredPermission: menu.required_permission
          }
        })
        dynamicRoutes.push({
            path: `${menu.url}/:id/edit`,
            name: `${menu.code || `dynamic-${menu.id}`}-edit`,
            component: () => import('@/views/DynamicView.vue'),
            meta: { 
              requiresAuth: true, 
              title: `Edit ${menu.title}`,
              requiredPermission: menu.required_permission
            }
          })
        
        // Add "create" route if this is a list view
        dynamicRoutes.push({
          path: `${menu.url}/new`,
          name: `${menu.code || `dynamic-${menu.id}`}-create`,
          component: () => import('@/views/DynamicView.vue'),
          meta: { 
            requiresAuth: true, 
            title: `New ${menu.title.replace(' List', '').replace('s', '')}`,
            requiredPermission: menu.required_permission
          }
        })
      }
    }
    
    // Process child menus recursively
    //console.log('Process child menus recursively......')
    if (menu.children && menu.children.length > 0) {
      menu.children.forEach(processMenu)
    }

    // console.log('dynamicRoutes=====', dynamicRoutes)
  }
  
  //console.log('Process all top-level menus...', menus)
  menus.forEach(processMenu)
  
  console.log('dynamicRoutes====', dynamicRoutes)
  return dynamicRoutes
}

// Initialize routes with static routes
let routes: RouteRecordRaw[] = [...staticRoutes]

// Create router with initial static routes
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Track if dynamic routes have been added
let dynamicRoutesAdded = false

// Function to add dynamic routes from menu data
async function addDynamicRoutes() {
  if (dynamicRoutesAdded) {
    console.log('Dynamic routes already added, skipping')
    return
  }
  
  const authStore = useAuthStore()
  const menuStore = useMenuStore()
  
  // console.log('Adding dynamic routes, auth status:', authStore.isAuthenticated)
  // console.log('Menu store has menus:', menuStore.hasMenus)
  
  // Only add dynamic routes if user is authenticated
  if (authStore.isAuthenticated) {
    try {
      // Fetch menus if not already loaded
      if (!menuStore.hasMenus) {
        // console.log('Fetching menus...')
        await menuStore.fetchMenus()
      }
      
      // console.log('Menus loaded:', menuStore.menus)
      
      // Generate and add dynamic routes
      const dynamicRoutes = generateDynamicRoutes(menuStore.menus)
      // console.log('Generated routes:', dynamicRoutes.map(r => ({path: r.path, name: r.name})))
      
      dynamicRoutes.forEach(route => {
        // console.log('Adding route to router:', route.path)
        router.addRoute(route)
      })
      
      dynamicRoutesAdded = true
      // console.log(`Added ${dynamicRoutes.length} dynamic routes`)
      
      // Log all current routes for debugging
      // console.log('Current router routes:', router.getRoutes().map(r => r.path))
    } catch (error) {
      console.error('Failed to add dynamic routes:', error)
    }
  } else {
    console.log('User not authenticated, skipping dynamic routes')
  }
}

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // console.log('Navigation guard - to:', to.path, 'from:', from.path)
  // console.log('Auth status:', authStore.isAuthenticated, 'Token:', !!authStore.token)
  
  // Check if this is a route that should have a dynamic route
  if (to.path.startsWith('/inventory') || to.path.startsWith('/sales') || to.path.startsWith('/purchasing')) {
    // console.log('This is a dynamic route path:', to.path)
    // Check if dynamic routes have been added
    // console.log('Dynamic routes added:', dynamicRoutesAdded)
    if (dynamicRoutesAdded) {
      // Check if the route exists
      const route = router.resolve(to.path)
      // console.log('Resolved route:', route.name, route.path)
    }
  }
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - XERPIUM` : 'XERPIUM'
  // console.log('Setting page title:', document.title)
  
  // Initialize auth if we have a token but no user data
  if (authStore.token && !authStore.user) {
    // console.log('Initializing auth...')
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
  
  // Ensure user data is fresh for routes that require permissions
  if (to.meta.requiredPermission && authStore.token) {
    try {
      // Refresh user data to ensure permissions are up to date
      await authStore.fetchCurrentUser()
      // console.log('Refreshed user data for permission check')
      // console.log('User now has permissions:', authStore.user?.permissions)
    } catch (error) {
      console.error('Failed to refresh user data:', error)
      // Continue with existing user data
    }
  }
  
  // Add dynamic routes if not already added and user is authenticated
  if (authStore.isAuthenticated && !dynamicRoutesAdded) {
    // console.log('Adding dynamic routes...')
    await addDynamicRoutes()
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // console.log('Route requires auth, redirecting to login')
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check if route requires admin privileges
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // console.log('Route requires admin, redirecting to dashboard')
    next({ name: 'Dashboard' })
    return
  }
  
  // Check if route requires specific permission
  if (to.meta.requiredPermission && !authStore.hasPermission(to.meta.requiredPermission)) {
    // console.log('Route requires permission, redirecting to dashboard')
    // console.log('Required permission:', to.meta.requiredPermission)
    // console.log('User permissions:', authStore.user?.permissions)
    // console.log('Has permission:', authStore.hasPermission(to.meta.requiredPermission))
    next({ name: 'Dashboard' })
    return
  }
  
  // Redirect to dashboard if trying to access login while authenticated
  if (to.name === 'Login' && authStore.isAuthenticated) {
    // console.log('Already authenticated, redirecting to dashboard')
    next({ name: 'Dashboard' })
    return
  }
  
  // console.log('Allowing navigation to:', to.path)
  next()
})

export default router
