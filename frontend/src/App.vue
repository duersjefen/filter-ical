<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import { useRouter } from 'vue-router'
import { useDarkMode } from './composables/useDarkMode'
import { useActivityTracker } from './composables/useActivityTracker'

const appStore = useAppStore()
const router = useRouter()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

// Initialize activity tracking
const { trackActivity } = useActivityTracker()

onMounted(async () => {
  // Initialize the app for public access
  appStore.initializeApp()
  
  // Default routing - redirect to home if on login page
  if (router.currentRoute.value.path === '/login') {
    await router.push('/home')
  }
})
</script>

