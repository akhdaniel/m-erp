import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeColor = 'light' | 'blue' | 'dark-red' | 'purple' 

interface ThemeConfig {
  name: string
  color: ThemeColor
  primaryGradient: string
  secondaryGradient: string
  glassBackground: string
  glassBorder: string
  textPrimary: string
  textSecondary: string
  buttonPrimary: string
  buttonHover: string
}

const themes: Record<ThemeColor, ThemeConfig> = {
  'light': {
    name: 'Light Mode',
    color: 'light',
    primaryGradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
    secondaryGradient: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
    glassBackground: 'rgba(255, 255, 255, 0.8)',
    glassBorder: 'rgba(229, 231, 235, 0.8)',
    textPrimary: '#1f2937',
    textSecondary: '#374151',
    buttonPrimary: '#1f2937',
    buttonHover: '#111827'
  },  
  'blue': {
    name: 'Ocean Blue',
    color: 'blue',
    primaryGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    secondaryGradient: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
    glassBackground: 'rgba(99, 102, 241, 0.1)',
    glassBorder: 'rgba(99, 102, 241, 0.2)',
    textPrimary: '#4f46e5',
    textSecondary: '#6366f1',
    buttonPrimary: '#4f46e5',
    buttonHover: '#4338ca'
  },
  'dark-red': {
    name: 'Crimson Night',
    color: 'dark-red',
    primaryGradient: 'linear-gradient(135deg, #aa1515ff 0%, #81057fff 100%)',
    secondaryGradient: 'linear-gradient(135deg, #b91e1eff 0%, #7f1d1d 100%)',
    glassBackground: 'rgba(220, 38, 38, 0.1)',
    glassBorder: 'rgba(220, 38, 38, 0.2)',
    textPrimary: '#dc2626',
    textSecondary: '#ef4444',
    buttonPrimary: '#dc2626',
    buttonHover: '#b91c1c'
  },
  'purple': {
    name: 'Royal Purple',
    color: 'purple',
    primaryGradient: 'linear-gradient(135deg, #9333ea 0%, #5c0447ff 100%)',
    secondaryGradient: 'linear-gradient(135deg, #7c3aed 0%, #581c87 100%)',
    glassBackground: 'rgba(147, 51, 234, 0.1)',
    glassBorder: 'rgba(147, 51, 234, 0.2)',
    textPrimary: '#9333ea',
    textSecondary: '#a855f7',
    buttonPrimary: '#9333ea',
    buttonHover: '#7e22ce'
  }
}

export const useThemeStore = defineStore('theme', () => {
  // Load saved theme from localStorage or default to blue
  const savedTheme = localStorage.getItem('userTheme') as ThemeColor || 'light'
  const currentTheme = ref<ThemeColor>(savedTheme)
  const themeConfig = ref<ThemeConfig>(themes[savedTheme])

  // Watch for theme changes and save to localStorage
  watch(currentTheme, (newTheme) => {
    themeConfig.value = themes[newTheme]
    localStorage.setItem('userTheme', newTheme)
    applyThemeToDocument(themes[newTheme])
  })

  // Apply theme CSS variables to document
  function applyThemeToDocument(theme: ThemeConfig) {
    const root = document.documentElement
    root.style.setProperty('--theme-primary-gradient', theme.primaryGradient)
    root.style.setProperty('--theme-secondary-gradient', theme.secondaryGradient)
    root.style.setProperty('--theme-glass-bg', theme.glassBackground)
    root.style.setProperty('--theme-glass-border', theme.glassBorder)
    root.style.setProperty('--theme-text-primary', theme.textPrimary)
    root.style.setProperty('--theme-text-secondary', theme.textSecondary)
    root.style.setProperty('--theme-button-primary', theme.buttonPrimary)
    root.style.setProperty('--theme-button-hover', theme.buttonHover)
    
    // Set data-theme attribute for CSS selectors
    root.setAttribute('data-theme', theme.color)
  }

  // Set theme
  function setTheme(theme: ThemeColor) {
    currentTheme.value = theme
  }

  // Initialize theme on store creation
  applyThemeToDocument(themeConfig.value)

  return {
    currentTheme,
    themeConfig,
    themes,
    setTheme
  }
})