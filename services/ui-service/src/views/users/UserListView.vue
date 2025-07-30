<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div class="md:flex md:items-center md:justify-between">
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Users
          </h1>
          <div class="mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6">
            <div class="mt-2 flex items-center text-sm text-gray-500">
              <UsersIcon class="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" />
              {{ userStore.pagination.total }} users
            </div>
          </div>
        </div>
        
        <div class="mt-4 flex md:mt-0 md:ml-4">
          <router-link
            to="/users/create"
            class="btn btn-primary inline-flex items-center"
          >
            <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
            Add User
          </router-link>
        </div>
      </div>

      <!-- Loading/Error states -->
      <div v-if="userStore.isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500">Loading users...</p>
      </div>

      <div v-else-if="userStore.error" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading users</h3>
            <div class="mt-2 text-sm text-red-700">{{ userStore.error }}</div>
          </div>
        </div>
      </div>

      <!-- Users table -->
      <div v-else class="card">
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th class="relative px-6 py-3">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in userStore.users" :key="user.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="h-10 w-10 flex-shrink-0">
                      <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span class="text-sm font-medium text-primary-600">
                          {{ getUserInitials(user) }}
                        </span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ user.first_name }} {{ user.last_name }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ user.email }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    user.is_superuser 
                      ? 'bg-purple-100 text-purple-800' 
                      : 'bg-gray-100 text-gray-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]">
                    {{ user.is_superuser ? 'Admin' : 'User' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    user.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800',
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
                  ]">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(user.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <router-link
                    :to="`/users/${user.id}/edit`"
                    class="text-primary-600 hover:text-primary-900"
                  >
                    Edit
                  </router-link>
                  <button
                    @click="resetPassword(user)"
                    class="text-yellow-600 hover:text-yellow-900"
                  >
                    Reset Password
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Empty state -->
          <div v-if="userStore.users.length === 0" class="text-center py-12">
            <UsersIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p class="mt-1 text-sm text-gray-500">Get started by creating a new user.</p>
            <div class="mt-6">
              <router-link to="/users/create" class="btn btn-primary">
                <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
                Add User
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import {
  UsersIcon,
  PlusIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import AppLayout from '@/components/AppLayout.vue'
import { useUserStore } from '@/stores/users'
import type { User } from '@/types'

const userStore = useUserStore()

function getUserInitials(user: User): string {
  const first = user.first_name?.[0] || ''
  const last = user.last_name?.[0] || ''
  return (first + last).toUpperCase()
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString()
}

async function resetPassword(user: User) {
  if (confirm(`Reset password for ${user.first_name} ${user.last_name}?`)) {
    try {
      const tempPassword = await userStore.resetUserPassword(user.id)
      alert(`Password reset successful. Temporary password: ${tempPassword}`)
    } catch (error) {
      alert('Failed to reset password')
    }
  }
}

onMounted(async () => {
  await userStore.fetchUsers()
})
</script>