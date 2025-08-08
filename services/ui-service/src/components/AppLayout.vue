<template>
  <div class="h-screen flex flex-col bg-gray-50 overflow-hidden">
    <!-- Navigation - Fixed at top -->
    <nav class="relative bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <!-- Logo -->
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/dashboard" class="text-xl font-bold text-primary-600">
                XERPIUM
              </router-link>
            </div>
            
            <!-- Primary Navigation -->
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <!-- Always show Dashboard -->
              <router-link
                to="/dashboard"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                active-class="border-primary-500 text-gray-900"
              >
                Dashboard
              </router-link>
              
              <!-- Dynamic menus from API -->
              <template v-for="menu in topLevelMenus" :key="menu.id">
                <!-- Simple link menu -->
                <router-link
                  v-if="menu.item_type === 'link' && menu.url"
                  :to="menu.url"
                  class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors"
                  active-class="border-primary-500 text-gray-900"
                >
                  <span v-if="menu.icon" class="mr-1">
                    <i :class="menu.icon"></i>
                  </span>
                  {{ menu.title }}
                </router-link>
                
                <!-- Dropdown menu -->
                <Menu v-else-if="menu.item_type === 'dropdown' && menu.children && menu.children.length > 0" as="div" class="relative">
                  <MenuButton class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors inline-flex items-center">
                    <span v-if="menu.icon" class="mr-1">
                      <i :class="menu.icon"></i>
                    </span>
                    {{ menu.title }}
                    <ChevronDownIcon class="ml-1 h-4 w-4" />
                  </MenuButton>
                  
                  <transition
                    enter-active-class="transition ease-out duration-100"
                    enter-from-class="transform opacity-0 scale-95"
                    enter-to-class="transform opacity-100 scale-100"
                    leave-active-class="transition ease-in duration-75"
                    leave-from-class="transform opacity-100 scale-100"
                    leave-to-class="transform opacity-0 scale-95"
                  >
                    <MenuItems class="absolute left-0 z-10 mt-2 w-56 origin-top-left rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                      <MenuItem
                        v-for="child in menu.children"
                        :key="child.id"
                        v-slot="{ active }"
                      >
                        <router-link
                          v-if="child && child.url"
                          :to="child.url"
                          :class="[
                            active ? 'bg-gray-100' : '',
                            'block px-4 py-2 text-sm text-gray-700'
                          ]"
                        >
                          <span v-if="child.icon" class="mr-2">
                            <i :class="child.icon"></i>
                          </span>
                          {{ child.title }}
                        </router-link>
                      </MenuItem>
                    </MenuItems>
                  </transition>
                </Menu>
              </template>
            </div>
          </div>
          
          <!-- User menu -->
          <div class="hidden sm:ml-6 sm:flex sm:items-center">
            <Menu as="div" class="ml-3 relative">
              <div>
                <MenuButton class="bg-white rounded-full flex text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                  <span class="sr-only">Open user menu</span>
                  <div class="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                    <span class="text-sm font-medium text-primary-600">
                      {{ userInitials }}
                    </span>
                  </div>
                </MenuButton>
              </div>
              
              <transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <MenuItems class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <MenuItem v-slot="{ active }">
                    <router-link
                      to="/profile"
                      :class="[
                        active ? 'bg-gray-100' : '',
                        'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100'
                      ]"
                    >
                      My Profile
                    </router-link>
                  </MenuItem>
                  
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="handleLogout"
                      :class="[
                        active ? 'bg-gray-100' : '',
                        'block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100'
                      ]"
                    >
                      Sign out
                    </button>
                  </MenuItem>
                </MenuItems>
              </transition>
            </Menu>
          </div>
          
          <!-- Mobile menu button -->
          <div class="sm:hidden flex items-center">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
            >
              <span class="sr-only">Open main menu</span>
              <Bars3Icon v-if="!mobileMenuOpen" class="block h-6 w-6" />
              <XMarkIcon v-else class="block h-6 w-6" />
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile menu - Absolute positioned overlay -->
      <div v-show="mobileMenuOpen" class="sm:hidden absolute top-16 left-0 right-0 bg-white shadow-lg z-40 max-h-[calc(100vh-4rem)] overflow-y-auto">
        <div class="pt-2 pb-3 space-y-1">
          <!-- Always show Dashboard -->
          <router-link
            to="/dashboard"
            class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
            active-class="bg-primary-50 border-primary-500 text-primary-700"
            @click="mobileMenuOpen = false"
          >
            Dashboard
          </router-link>
          
          <!-- Dynamic menus from API -->
          <template v-for="menu in topLevelMenus" :key="menu.id">
            <!-- Simple link menu -->
            <router-link
              v-if="menu.item_type === 'link' && menu.url"
              :to="menu.url"
              class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 block pl-3 pr-4 py-2 border-l-4 text-base font-medium"
              active-class="bg-primary-50 border-primary-500 text-primary-700"
              @click="mobileMenuOpen = false"
            >
              <span v-if="menu.icon" class="mr-2">
                <i :class="menu.icon"></i>
              </span>
              {{ menu.title }}
            </router-link>
            
            <!-- Dropdown menu (expanded for mobile) -->
            <div v-else-if="menu.item_type === 'dropdown' && menu.children && menu.children.length > 0">
              <div class="border-transparent text-gray-700 font-semibold block pl-3 pr-4 py-2 border-l-4 text-base">
                <span v-if="menu.icon" class="mr-2">
                  <i :class="menu.icon"></i>
                </span>
                {{ menu.title }}
              </div>
              <div class="space-y-1">
                <template v-for="child in menu.children" :key="child.id">
                  <router-link
                    v-if="child && child.url"
                    :to="child.url"
                    class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 block pl-8 pr-4 py-2 border-l-4 text-base font-medium"
                    active-class="bg-primary-50 border-primary-500 text-primary-700"
                    @click="mobileMenuOpen = false"
                  >
                    <span v-if="child.icon" class="mr-2">
                      <i :class="child.icon"></i>
                    </span>
                    {{ child.title }}
                  </router-link>
                </template>
              </div>
            </div>
          </template>
        </div>
        
        <div class="pt-4 pb-3 border-t border-gray-200">
          <div class="flex items-center px-4">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                <span class="text-sm font-medium text-primary-600">
                  {{ userInitials }}
                </span>
              </div>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-800">
                {{ authStore.user?.first_name }} {{ authStore.user?.last_name }}
              </div>
              <div class="text-sm font-medium text-gray-500">
                {{ authStore.user?.email }}
              </div>
            </div>
          </div>
          
          <div class="mt-3 space-y-1">
            <router-link
              to="/profile"
              class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
              @click="mobileMenuOpen = false"
            >
              My Profile
            </router-link>
            
            <button
              @click="handleLogout"
              class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main content - Scrollable area -->
    <main class="flex-1 overflow-y-auto">
      <div class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <slot />
        </div>
      </div>
    </main>
    
    <!-- Notification Center - Fixed position -->
    <NotificationCenter />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import { Bars3Icon, XMarkIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import NotificationCenter from './NotificationCenter.vue'

const router = useRouter()
const authStore = useAuthStore()
const menuStore = useMenuStore()
const mobileMenuOpen = ref(false)

const userInitials = computed(() => {
  if (!authStore.user) return ''
  const first = authStore.user.first_name?.[0] || ''
  const last = authStore.user.last_name?.[0] || ''
  return (first + last).toUpperCase()
})

const topLevelMenus = computed(() => menuStore.topLevelMenus)

async function handleLogout() {
  try {
    await authStore.logout()
    menuStore.clearMenus()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// Fetch menus when component mounts
onMounted(async () => {
  console.log('AppLayout mounted, auth status:', authStore.isAuthenticated)
  if (authStore.isAuthenticated) {
    console.log('Fetching menus...')
    await menuStore.fetchMenus()
    console.log('Menus loaded:', menuStore.menus)
    console.log('Top level menus:', menuStore.topLevelMenus)
  }
})

// Watch for authentication changes
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    await menuStore.fetchMenus()
  } else {
    menuStore.clearMenus()
  }
})
</script>