<template>
  <div class="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <div class="max-w-md w-full">
      <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
        <div class="flex items-center justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
        </div>

        <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
          {{ title }}
        </h1>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
          {{ subtitle }}
        </p>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-4 border border-red-200 dark:border-red-700">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <span class="font-semibold text-sm">{{ error }}</span>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label for="password" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="w-full px-4 py-3 pr-12 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-4 focus:ring-purple-100 dark:focus:ring-purple-900/50"
                :placeholder="passwordPlaceholder"
                required
                autofocus
                :disabled="loading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                :disabled="loading"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading || !password"
            class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 dark:from-purple-600 dark:to-purple-700 dark:hover:from-purple-700 dark:hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Authenticating...</span>
            </span>
            <span v-else>{{ submitButtonText }}</span>
          </button>
        </form>

        <!-- Additional Info -->
        <div v-if="showBackButton" class="mt-6 text-center">
          <button
            @click="$emit('back')"
            class="text-sm text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
          >
            ← Back to home
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDomainAuth } from '@/composables/useDomainAuth'
import { useApiErrors } from '@/composables/useApiErrors'

const props = defineProps({
  domain: {
    type: String,
    required: true
  },
  accessLevel: {
    type: String,
    required: true,
    validator: (value) => ['admin', 'user'].includes(value)
  },
  title: {
    type: String,
    default: 'Protected Area'
  },
  subtitle: {
    type: String,
    default: 'Please enter your password to continue'
  },
  passwordPlaceholder: {
    type: String,
    default: 'Enter password'
  },
  submitButtonText: {
    type: String,
    default: 'Login'
  },
  showBackButton: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['authenticated', 'back'])

const { verifyPassword, authLoading, authError } = useDomainAuth(props.domain)
const { error, setError, clearError } = useApiErrors()

const password = ref('')
const showPassword = ref(false)
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  clearError()

  const result = await verifyPassword(password.value, props.accessLevel)

  if (result.success) {
    emit('authenticated')
  } else {
    setError(result.error || authError.value || 'Invalid password')
    password.value = '' // Clear password on error
  }

  loading.value = false
}
</script>
