<template>
  <!-- Main app container - login-free direct home access -->
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300" data-test="ci-cd-test">
    <!-- Offline banner -->
    <Transition name="slide-down">
      <div
        v-if="!isOnline"
        class="fixed top-0 left-0 right-0 z-[10000] bg-yellow-500 text-white px-4 py-2 text-center font-medium shadow-lg"
        role="alert"
      >
        📡 You are offline. Some features may not work.
      </div>
    </Transition>

    <div class="flex flex-col min-h-screen">
      <main class="flex-grow">
        <router-view />
      </main>
      <AppFooter />
    </div>

    <!-- Global Notification Toast -->
    <NotificationToast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from './stores/app'
import { useRouter } from 'vue-router'
import { useDarkMode } from './composables/useDarkMode'
import { isOnline } from './composables/useHTTP'
import AppFooter from './components/shared/AppFooter.vue'
import NotificationToast from './components/shared/NotificationToast.vue'

const appStore = useAppStore()
const router = useRouter()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

onMounted(async () => {
  // Initialize the app for public access
  appStore.initializeApp()
})
</script>

<style>
.slide-down-enter-active, .slide-down-leave-active {
  transition: transform 0.3s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  transform: translateY(-100%);
}
</style>

