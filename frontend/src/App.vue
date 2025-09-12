<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import { useDarkMode } from './composables/useDarkMode'

const appStore = useAppStore()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

onMounted(() => {
  appStore.initializeApp()
})
</script>

