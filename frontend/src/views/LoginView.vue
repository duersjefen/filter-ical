<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <AppHeader 
      title="🗓️ iCal Filter & Subscribe"
      :subtitle="$t('login.subtitle')"
    />

      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 sm:p-8 mb-8 max-w-sm sm:max-w-md mx-auto">
        <h2 class="mb-8 text-center text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('login.title') }}</h2>
        
        <div v-if="appStore.error" class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 text-red-800 dark:text-red-200 px-6 py-4 rounded-xl mb-6 border-2 border-red-300 dark:border-red-700 shadow-lg">
          <div class="flex items-center gap-3">
            <div class="text-2xl">⚠️</div>
            <span class="font-semibold">{{ appStore.error }}</span>
          </div>
        </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-5">
          <label for="username" class="block mb-2 font-medium text-gray-700 dark:text-gray-300">{{ $t('login.username') }}</label>
          <input
            id="username"
            v-model="appStore.loginForm.username"
            type="text"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-500 dark:placeholder-gray-400"
            :placeholder="$t('login.usernamePlaceholder')"
            required
          />
        </div>

        <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed text-white border-none px-6 py-3.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-lg hover:shadow-xl" :disabled="appStore.loading">
          {{ appStore.loading ? $t('login.loggingIn') : $t('login.loginButton') }}
        </button>
      </form>
    </div>
    </div>
  </div>
</template>

<script setup>
import { useCompatibilityStore as useAppStore } from '../stores/compatibility'
import { useRouter } from 'vue-router'
import { watch, onMounted } from 'vue'
import AppHeader from '../components/shared/AppHeader.vue'
import { useDarkMode } from '../composables/useDarkMode'

const appStore = useAppStore()
const router = useRouter()

// Initialize dark mode
const { isDarkMode, toggleDarkMode } = useDarkMode()

const handleLogin = async () => {
  const result = await appStore.login()
  // Explicitly redirect after successful login
  if (result && appStore.isLoggedIn) {
    router.push('/home')
  }
}
</script>