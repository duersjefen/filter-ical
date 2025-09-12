<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <AppHeader 
      title="🗓️ iCal Filter & Subscribe"
      subtitle="Please log in to access your calendars"
    />

    <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 sm:p-8 mb-8 max-w-sm sm:max-w-md mx-auto">
      <h2 class="mb-8 text-center text-2xl font-bold text-gray-900">Login</h2>
      
      <div v-if="appStore.error" class="bg-gradient-to-r from-red-100 to-red-50 text-red-800 px-6 py-4 rounded-xl mb-6 border-2 border-red-300 shadow-lg">
        <div class="flex items-center gap-3">
          <div class="text-2xl">⚠️</div>
          <span class="font-semibold">{{ appStore.error }}</span>
        </div>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-5">
          <label for="username" class="block mb-2 font-medium text-gray-700">Username</label>
          <input
            id="username"
            v-model="appStore.loginForm.username"
            type="text"
            class="w-full px-4 py-3.5 border-2 border-gray-300 rounded-lg text-sm transition-all duration-300 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 hover:border-gray-400 shadow-sm font-medium"
            placeholder="Enter your username"
            required
          />
        </div>

        <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white border-none px-6 py-3.5 rounded-lg cursor-pointer text-sm font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-lg hover:shadow-xl" :disabled="appStore.loading">
          {{ appStore.loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { watch } from 'vue'
import AppHeader from '../components/shared/AppHeader.vue'

const appStore = useAppStore()
const router = useRouter()

const handleLogin = async () => {
  await appStore.login()
  // Explicitly redirect after successful login
  if (appStore.isLoggedIn) {
    router.push('/home')
  }
}
</script>