<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Page header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>
        <p class="mt-2 text-sm text-gray-700">
          Manage your account settings and preferences.
        </p>
      </div>

      <!-- Profile card placeholder -->
      <div class="card">
        <div class="card-body">
          <p class="text-gray-500">Profile management interface would go here.</p>
          <p class="text-sm text-gray-400 mt-2">
            This would include user information editing, password change, etc.
          </p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/AppLayout.vue'
</script>