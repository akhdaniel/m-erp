<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="mt-2 text-sm text-gray-700">
          Welcome back, {{ authStore.user?.first_name }}! Here's an overview of your XERPIUM system.
        </p>
      </div>

      <!-- Stats cards -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <BuildingOfficeIcon class="h-8 w-8 text-primary-600" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    Total Companies
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ stats.companies }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <UsersIcon class="h-8 w-8 text-green-600" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    Active Users
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    {{ stats.users }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-body">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ServerIcon class="h-8 w-8 text-blue-600" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">
                    System Status
                  </dt>
                  <dd class="text-lg font-medium text-gray-900">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Healthy
                    </span>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Quick Actions
          </h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">
            Common tasks to get you started.
          </p>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <router-link
              to="/companies/create"
              class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <div class="flex-shrink-0">
                <PlusIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="flex-1 min-w-0">
                <span class="absolute inset-0" aria-hidden="true" />
                <p class="text-sm font-medium text-gray-900">
                  Create Company
                </p>
                <p class="text-sm text-gray-500 truncate">
                  Add a new company to the system
                </p>
              </div>
            </router-link>

            <router-link
              v-if="authStore.isAdmin"
              to="/users/create"
              class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <div class="flex-shrink-0">
                <UserPlusIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="flex-1 min-w-0">
                <span class="absolute inset-0" aria-hidden="true" />
                <p class="text-sm font-medium text-gray-900">
                  Create User
                </p>
                <p class="text-sm text-gray-500 truncate">
                  Add a new user account
                </p>
              </div>
            </router-link>

            <router-link
              to="/profile"
              class="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <div class="flex-shrink-0">
                <UserIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="flex-1 min-w-0">
                <span class="absolute inset-0" aria-hidden="true" />
                <p class="text-sm font-medium text-gray-900">
                  My Profile
                </p>
                <p class="text-sm text-gray-500 truncate">
                  Update your account settings
                </p>
              </div>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Recent activity (placeholder) -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Recent Activity
          </h3>
        </div>
        <div class="card-body">
          <p class="text-sm text-gray-500">
            Recent activity tracking will be available once the audit logging system is implemented.
          </p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  BuildingOfficeIcon,
  UsersIcon,
  ServerIcon,
  PlusIcon,
  UserPlusIcon,
  UserIcon
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/companies'
import { useUserStore } from '@/stores/users'

const authStore = useAuthStore()
const companyStore = useCompanyStore()
const userStore = useUserStore()

const stats = ref({
  companies: 0,
  users: 0
})

onMounted(async () => {
  // Load dashboard statistics
  try {
    await Promise.all([
      companyStore.fetchCompanies({ size: 1 }),
      authStore.isAdmin ? userStore.fetchUsers({ size: 1 }) : Promise.resolve()
    ])
    
    stats.value.companies = companyStore.pagination.total
    stats.value.users = userStore.pagination.total
  } catch (error) {
    console.error('Failed to load dashboard stats:', error)
  }
})
</script>