<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 dark:from-purple-600 dark:to-blue-600 rounded-full mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">Reset Your Password</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">Enter your new password below</p>
        </div>

        <!-- Loading State -->
        <div v-if="verifying" class="text-center py-8">
          <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400">Verifying reset link...</p>
        </div>

        <!-- Invalid Token -->
        <div v-else-if="!tokenValid" class="text-center py-8">
          <div class="text-6xl mb-4">⚠️</div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Invalid Reset Link</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            This password reset link is invalid or has expired.
          </p>
          <router-link
            to="/"
            class="inline-block bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white px-6 py-3 rounded-xl font-bold transition-all"
          >
            Go to Home
          </router-link>
        </div>

        <!-- Reset Form -->
        <form v-else-if="!resetSuccess" @submit.prevent="handleReset" class="space-y-6">
          <!-- Error Message -->
          <div v-if="error" class="p-4 bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded-lg border border-red-200 dark:border-red-700">
            {{ error }}
          </div>

          <!-- New Password -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              New Password
            </label>
            <input
              v-model="newPassword"
              type="password"
              required
              minlength="4"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50"
              placeholder="Enter new password"
            />
          </div>

          <!-- Confirm Password -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Confirm Password
            </label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              minlength="4"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50"
              placeholder="Confirm new password"
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 dark:from-purple-600 dark:to-blue-600 dark:hover:from-purple-700 dark:hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-bold transition-all hover:shadow-lg disabled:cursor-not-allowed"
          >
            {{ loading ? 'Resetting Password...' : 'Reset Password' }}
          </button>
        </form>

        <!-- Success State -->
        <div v-else class="text-center py-8">
          <div class="text-6xl mb-4">✅</div>
          <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Password Reset Successfully!</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            Your password has been updated. You can now log in with your new password.
          </p>
          <router-link
            to="/"
            class="inline-block bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white px-6 py-3 rounded-xl font-bold transition-all"
          >
            Go to Home
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const { verifyResetToken, resetPassword } = useAuth()

// State
const token = ref(route.query.token)
const verifying = ref(true)
const tokenValid = ref(false)
const loading = ref(false)
const error = ref('')
const resetSuccess = ref(false)

// Form fields
const newPassword = ref('')
const confirmPassword = ref('')

// Verify token on mount
onMounted(async () => {
  if (!token.value) {
    verifying.value = false
    tokenValid.value = false
    return
  }

  const result = await verifyResetToken(token.value)
  verifying.value = false
  tokenValid.value = result.success

  if (!result.success) {
    error.value = result.error
  }
})

// Handle password reset
const handleReset = async () => {
  error.value = ''

  // Validate passwords match
  if (newPassword.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  // Validate password length
  if (newPassword.value.length < 4) {
    error.value = 'Password must be at least 4 characters'
    return
  }

  loading.value = true

  const result = await resetPassword(token.value, newPassword.value)

  loading.value = false

  if (result.success) {
    resetSuccess.value = true
  } else {
    error.value = result.error
  }
}
</script>
