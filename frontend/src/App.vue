<template>
  <!-- Main app container - login-free direct home access -->
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300" data-test="ci-cd-test">
    <div class="flex flex-col min-h-screen">
      <main class="flex-grow">
        <router-view />
      </main>
      <AppFooter />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import { useRouter } from 'vue-router'
import { useDarkMode } from './composables/useDarkMode'
import AppFooter from './components/shared/AppFooter.vue'
const appStore = useAppStore()
const router = useRouter()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

onMounted(async () => {
  // Initialize the app for public access
  appStore.initializeApp()
})
</script>

