<template>
  <div class="relative">
    <!-- Theme Toggle Button -->
    <button
      @click="showDropdown = !showDropdown"
      class="theme-selector-button"
      :style="{
        background: themeStore.themeConfig.primaryGradient,
        color: 'white'
      }"
    >
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
      <span>{{ themeStore.themeConfig.name }}</span>
      <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- Theme Dropdown -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="showDropdown"
        class="theme-dropdown glass-morphism"
      >
        <div class="p-2">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">
            Select Theme
          </h3>
          
          <!-- Blue Theme -->
          <button
            @click="selectTheme('blue')"
            class="theme-option"
            :class="{ 'theme-option-active': themeStore.currentTheme === 'blue' }"
          >
            <div class="theme-preview" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)"></div>
            <div class="flex-1 text-left">
              <div class="font-medium text-gray-300">Ocean Blue</div>
              <div class="text-xs text-gray-500">Cool & Professional</div>
            </div>
            <svg v-if="themeStore.currentTheme === 'blue'" class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Dark Red Theme -->
          <button
            @click="selectTheme('dark-red')"
            class="theme-option"
            :class="{ 'theme-option-active': themeStore.currentTheme === 'dark-red' }"
          >
            <div class="theme-preview" style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%)"></div>
            <div class="flex-1 text-left">
              <div class="font-medium text-gray-300">Crimson Night</div>
              <div class="text-xs text-gray-500">Bold & Energetic</div>
            </div>
            <svg v-if="themeStore.currentTheme === 'dark-red'" class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Purple Theme -->
          <button
            @click="selectTheme('purple')"
            class="theme-option"
            :class="{ 'theme-option-active': themeStore.currentTheme === 'purple' }"
          >
            <div class="theme-preview" style="background: linear-gradient(135deg, #9333ea 0%, #6b21a8 100%)"></div>
            <div class="flex-1 text-left">
              <div class="font-medium text-gray-300">Royal Purple</div>
              <div class="text-xs text-gray-500">Elegant & Modern</div>
            </div>
            <svg v-if="themeStore.currentTheme === 'purple'" class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Light Theme -->
          <button
            @click="selectTheme('light')"
            class="theme-option"
            :class="{ 'theme-option-active': themeStore.currentTheme === 'light' }"
          >
            <div class="theme-preview" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)"></div>
            <div class="flex-1 text-left">
              <div class="font-medium text-gray-300">Light Mode</div>
              <div class="text-xs text-gray-500">Clean & Minimal</div>
            </div>
            <svg v-if="themeStore.currentTheme === 'light'" class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useThemeStore, type ThemeColor } from '@/stores/theme'

const themeStore = useThemeStore()
const showDropdown = ref(false)

// Simple click outside handler
function handleClickOutside(event: MouseEvent) {
  const dropdown = document.querySelector('.theme-dropdown')
  const button = document.querySelector('.theme-selector-button')
  if (dropdown && !dropdown.contains(event.target as Node) && 
      button && !button.contains(event.target as Node)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

function selectTheme(theme: ThemeColor) {
  themeStore.setTheme(theme)
  showDropdown.value = false
}
</script>

<style scoped>
.theme-selector-button {
  @apply inline-flex items-center px-4 py-2 rounded-lg font-medium shadow-lg;
  @apply transition-all duration-200 hover:shadow-xl hover:scale-105;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;
}

.theme-dropdown {
  @apply absolute right-0 mt-2 w-72 rounded-lg shadow-xl;
  @apply border;
  z-index: 9999;
}

.glass-morphism {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.theme-option {
  @apply w-full flex items-center space-x-3 px-3 py-2 rounded-lg;
  @apply transition-all duration-150 hover:bg-gray-100;
  @apply focus:outline-none focus:bg-gray-100;
}

.theme-option-active {
  @apply bg-gray-50;
}

.theme-preview {
  @apply w-10 h-10 rounded-lg shadow-sm;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .glass-morphism {
    background: rgba(31, 41, 55, 0.85);
    border: 1px solid rgba(75, 85, 99, 0.3);
  }
  
  .theme-option:hover {
    @apply hover:bg-gray-700;
  }
  
  .theme-option-active {
    @apply bg-gray-700;
  }
}
</style>