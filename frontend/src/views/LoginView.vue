<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 dark:from-purple-600 dark:to-blue-600 rounded-full mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{activeTab === 'login' ? 'Welcome Back' : 'Create Account' }}</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">{{ activeTab === 'login' ? 'Login to your account' : 'Start filtering your calendars' }}</p>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-t-xl mb-6">
          <button
            @click="activeTab = 'login'"
            class="flex-1 py-3 font-semibold transition-colors rounded-tl-xl"
            :class="activeTab === 'login' ? 'bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
          >
            Login
          </button>
          <button
            @click="activeTab = 'register'"
            class="flex-1 py-3 font-semibold transition-colors rounded-tr-xl"
            :class="activeTab === 'register' ? 'bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
          >
            Register
          </button>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded-lg border border-red-200 dark:border-red-700">
          {{ error }}
        </div>

        <!-- Success Message -->
        <div v-if="success" class="mb-4 p-3 bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-lg border border-green-200 dark:border-green-700">
          {{ success }}
        </div>

        <!-- Login Form -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Username
            </label>
            <input
              v-model="loginUsername"
              type="text"
              required
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              placeholder="Enter your username"
            />
          </div>

          <div v-if="showLoginPassword">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Password
            </label>
            <input
              v-model="loginPassword"
              type="password"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 dark:from-purple-600 dark:to-blue-600 dark:hover:from-purple-700 dark:hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-bold transition-all hover:shadow-lg disabled:cursor-not-allowed"
          >
            {{ loading ? 'Logging in...' : 'Login' }}
          </button>

          <button
            v-if="showLoginPassword"
            type="button"
            @click="$router.push('/reset-password')"
            class="w-full text-sm text-purple-600 dark:text-purple-400 hover:underline"
          >
            Forgot password?
          </button>
        </form>

        <!-- Register Form -->
        <form v-else-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Username <span class="text-red-500">*</span>
            </label>
            <input
              v-model="registerUsername"
              type="text"
              required
              minlength="3"
              maxlength="50"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              placeholder="Choose a username"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Email <span class="text-gray-400">(optional)</span>
            </label>
            <input
              v-model="registerEmail"
              type="email"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Password <span class="text-gray-400">(optional)</span>
            </label>
            <input
              v-model="registerPassword"
              type="password"
              minlength="4"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              placeholder="Choose a password (optional)"
            />
            <p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
              💡 Email & password are optional. Add them for secure cross-device sync!
            </p>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 dark:from-purple-600 dark:to-blue-600 dark:hover:from-purple-700 dark:hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-bold transition-all hover:shadow-lg disabled:cursor-not-allowed"
          >
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>

        <!-- Back to Home -->
        <div class="mt-6 text-center">
          <button
            @click="$router.push('/')"
            class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:underline"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { register, login } = useAuth()

// State
const activeTab = ref('login')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Login form
const loginUsername = ref('')
const loginPassword = ref('')
const showLoginPassword = ref(true)

// Register form
const registerUsername = ref('')
const registerEmail = ref('')
const registerPassword = ref('')

// Handle login
const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  const result = await login(
    loginUsername.value,
    showLoginPassword.value ? loginPassword.value : null
  )

  loading.value = false

  if (result.success) {
    success.value = 'Login successful!'
    // Redirect to intended page or home
    const redirect = route.query.redirect || '/home'
    setTimeout(() => {
      router.push(redirect)
    }, 500)
  } else {
    // Check if error is about password requirement
    if (result.error.includes('Password required')) {
      showLoginPassword.value = true
      error.value = result.error
    } else {
      error.value = result.error
    }
  }
}

// Handle register
const handleRegister = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  const result = await register(
    registerUsername.value,
    registerEmail.value || null,
    registerPassword.value || null
  )

  loading.value = false

  if (result.success) {
    success.value = 'Account created successfully!'
    // Redirect to intended page or home
    const redirect = route.query.redirect || '/home'
    setTimeout(() => {
      router.push(redirect)
    }, 500)
  } else {
    error.value = result.error
  }
}
</script>
