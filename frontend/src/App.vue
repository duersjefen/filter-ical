<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCompatibilityStore as useAppStore } from './stores/compatibility'
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
  // Initialize the app and restore user session if available
  const wasRestored = appStore.initializeApp()
  
  // If user session was restored and we're on login page, redirect to home
  if (wasRestored && router.currentRoute.value.path === '/login') {
    await router.push('/')
  }
})
</script>

