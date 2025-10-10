<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
    <div class="max-w-md w-full">
      <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
        <div class="flex items-center justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
          </div>
        </div>

        <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
          Reset Admin Password
        </h1>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
          Enter your new password below
        </p>

        <div v-if="success" class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg mb-4">
          <p class="font-semibold mb-2">✅ Password reset successfully!</p>
          <p class="text-sm mb-3">{{ successMessage }}</p>
          <router-link to="/admin" class="text-sm font-semibold underline">
            Go to Admin Panel →
          </router-link>
        </div>

        <div v-else>
          <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-4">
            {{ error }}
          </div>

          <form @submit.prevent="resetPassword" class="space-y-4">
            <div>
              <label for="new-password" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
                New Password
              </label>
              <input
                id="new-password"
                v-model="newPassword"
                type="password"
                class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400"
                placeholder="Enter new password (min 8 characters)"
                required
                minlength="8"
                autofocus
              />
            </div>

            <div>
              <label for="confirm-password" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
                Confirm Password
              </label>
              <input
                id="confirm-password"
                v-model="confirmPassword"
                type="password"
                class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400"
                placeholder="Confirm new password"
                required
                minlength="8"
              />
            </div>

            <button
              type="submit"
              :disabled="resetting || newPassword.length < 8 || newPassword !== confirmPassword"
              class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg disabled:shadow-sm"
            >
              {{ resetting ? 'Resetting Password...' : 'Reset Password' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useValidation } from '@/composables/useValidation'
import { useApiErrors } from '@/composables/useApiErrors'

const route = useRoute()
const router = useRouter()
const adminStore = useAdminStore()
const { isValidPassword, passwordsMatch } = useValidation()
const { error, setError, clearError } = useApiErrors()

const newPassword = ref('')
const confirmPassword = ref('')
const resetting = ref(false)
const success = ref(false)
const successMessage = ref('')

const token = ref('')

onMounted(() => {
  token.value = route.query.token || ''

  if (!token.value) {
    setError('Invalid reset link - no token provided')
  }
})

async function resetPassword() {
  if (!passwordsMatch(newPassword.value, confirmPassword.value)) {
    setError('Passwords do not match')
    return
  }

  if (!isValidPassword(newPassword.value, 8)) {
    setError('Password must be at least 8 characters')
    return
  }

  resetting.value = true
  clearError()

  try {
    const response = await adminStore.resetPassword(token.value, newPassword.value)
    success.value = true
    successMessage.value = response.message

    // Redirect to admin panel after 3 seconds
    setTimeout(() => {
      router.push('/admin')
    }, 3000)
  } catch (err) {
    setError(err.message || 'Failed to reset password')
  } finally {
    resetting.value = false
  }
}
</script>
