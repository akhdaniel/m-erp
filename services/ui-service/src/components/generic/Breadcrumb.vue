<template>
  <div v-if="breadcrumbs && breadcrumbs.length > 0" class="flex" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-4 whitespace-nowrap">
      <li v-for="(crumb, index) in breadcrumbs" :key="index" class="flex items-center">
        <router-link 
          v-if="crumb.route" 
          :to="crumb.route" 
          class="text-gray-400 hover:text-gray-500"
        >
          {{ crumb.label }}
        </router-link>
        <span v-else class="text-gray-500">{{ crumb.label }}</span>
        <svg 
          v-if="index < breadcrumbs.length - 1" 
          class="flex-shrink-0 w-4 h-4 text-gray-300 ml-4" 
          xmlns="http://www.w3.org/2000/svg" 
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
        </svg>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

// Define the props
interface BreadcrumbItem {
  label: string
  route?: string
}

interface Props {
  breadcrumbs?: BreadcrumbItem[]
}

defineProps<Props>()
</script>

<style scoped>
/* Breadcrumb styles are already defined in the template using Tailwind classes */
</style>