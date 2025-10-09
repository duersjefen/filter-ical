<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
    <!-- Language Toggle - Top Right -->
    <div class="fixed top-4 right-4 z-50">
      <LanguageToggle />
    </div>

    <div class="max-w-md w-full">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-8">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 dark:from-purple-600 dark:to-blue-600 rounded-full mb-4">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ activeTab === 'login' ? $t('login.welcomeBack') : $t('login.createAccount') }}</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">{{ activeTab === 'login' ? $t('login.loginToAccount') : $t('login.startFiltering') }}</p>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-t-xl mb-6">
          <button
            @click="activeTab = 'login'"
            class="flex-1 py-3 font-semibold transition-colors rounded-tl-xl"
            :class="activeTab === 'login' ? 'bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
          >
            {{ $t('login.loginTab') }}
          </button>
          <button
            @click="activeTab = 'register'"
            class="flex-1 py-3 font-semibold transition-colors rounded-tr-xl"
            :class="activeTab === 'register' ? 'bg-white dark:bg-gray-800 text-purple-600 dark:text-purple-400 border-b-2 border-purple-600 dark:border-purple-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
          >
            {{ $t('login.registerTab') }}
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
              {{ $t('login.username') }}
            </label>
            <input
              ref="loginUsernameInput"
              v-model="loginUsername"
              type="text"
              required
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              :placeholder="$t('login.usernamePlaceholder')"
            />
          </div>

          <!-- Info: Password requirement status -->
          <div v-if="checkingUsername" class="mb-4 text-xs text-gray-600 dark:text-gray-400 bg-gray-50/50 dark:bg-gray-900/20 rounded-lg px-3 py-2.5 border border-gray-200/50 dark:border-gray-700/50">
            <div class="flex items-center gap-2">
              <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Checking username...</span>
            </div>
          </div>
          <div v-else-if="usernameRequiresPassword === true" class="mb-4 text-xs text-orange-700 dark:text-orange-300 bg-orange-50/50 dark:bg-orange-900/20 rounded-lg px-3 py-2.5 border border-orange-200/50 dark:border-orange-700/50">
            🔒 This account requires a password
          </div>
          <div v-else-if="usernameRequiresPassword === false" class="mb-4 text-xs text-green-700 dark:text-green-300 bg-green-50/50 dark:bg-green-900/20 rounded-lg px-3 py-2.5 border border-green-200/50 dark:border-green-700/50">
            ✓ This account has no password - just click login!
          </div>
          <div v-else class="mb-4 text-xs text-gray-600 dark:text-gray-400 bg-blue-50/50 dark:bg-blue-900/20 rounded-lg px-3 py-2.5 border border-blue-200/50 dark:border-blue-700/50">
            💡 {{ $t('login.passwordOptionalInfo') }}
          </div>

          <div class="opacity-60 focus-within:opacity-100 transition-opacity">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('login.passwordLabel') }} <span class="text-gray-400">{{ $t('login.passwordOptionalLabel') }}</span>
            </label>
            <input
              v-model="loginPassword"
              type="password"
              class="w-full px-4 py-3 border-2 border-gray-300/60 dark:border-gray-600/60 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-all"
              :placeholder="$t('login.passwordPlaceholder')"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 dark:from-purple-600 dark:to-blue-600 dark:hover:from-purple-700 dark:hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-bold transition-all hover:shadow-lg disabled:cursor-not-allowed"
          >
            {{ loading ? $t('login.loggingIn') : $t('login.loginButton') }}
          </button>

          <button
            type="button"
            @click="$router.push('/reset-password')"
            class="w-full text-sm text-purple-600 dark:text-purple-400 hover:underline"
          >
            {{ $t('login.forgotPassword') }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-else-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('login.usernameRequired') }}
            </label>
            <input
              v-model="registerUsername"
              type="text"
              required
              minlength="3"
              maxlength="50"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-colors"
              :placeholder="$t('login.chooseUsername')"
            />
          </div>

          <!-- Info box explaining optional fields -->
          <div class="mb-4 text-xs text-gray-600 dark:text-gray-400 bg-green-50/50 dark:bg-green-900/20 rounded-lg px-3 py-2.5 border border-green-200/50 dark:border-green-700/50">
            <div class="font-semibold mb-1">{{ $t('login.quickStartTitle') }}</div>
            <div class="space-y-1 ml-4">
              <div>{{ $t('login.emailPurpose') }}</div>
              <div>{{ $t('login.passwordPurpose') }}</div>
            </div>
          </div>

          <div class="opacity-60 focus-within:opacity-100 transition-opacity">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('login.email') }} <span class="text-gray-400">{{ $t('login.emailOptionalLabel') }}</span>
            </label>
            <input
              v-model="registerEmail"
              type="email"
              class="w-full px-4 py-3 border-2 border-gray-300/60 dark:border-gray-600/60 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-all"
              :placeholder="$t('login.emailPlaceholder')"
            />
          </div>

          <div class="opacity-60 focus-within:opacity-100 transition-opacity">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ $t('login.passwordLabel') }} <span class="text-gray-400">{{ $t('login.passwordSecurityLabel') }}</span>
            </label>
            <input
              v-model="registerPassword"
              type="password"
              minlength="4"
              class="w-full px-4 py-3 border-2 border-gray-300/60 dark:border-gray-600/60 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-100 dark:focus:ring-purple-900/50 transition-all"
              :placeholder="$t('login.registerPasswordPlaceholder')"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 dark:from-purple-600 dark:to-blue-600 dark:hover:from-purple-700 dark:hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white py-3 rounded-xl font-bold transition-all hover:shadow-lg disabled:cursor-not-allowed"
          >
            {{ loading ? $t('login.creatingAccount') : $t('login.createAccount') }}
          </button>
        </form>

        <!-- Back to Home -->
        <div class="mt-6 text-center">
          <button
            @click="$router.push('/')"
            class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:underline"
          >
            {{ $t('login.backToHome') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../composables/useAuth'
import { useHTTP } from '../composables/useHTTP'
import LanguageToggle from '../components/LanguageToggle.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { register, login } = useAuth()
const { get } = useHTTP()

// State
const activeTab = ref('login')
const loading = ref(false)
const error = ref('')
const success = ref('')

// Login form
const loginUsernameInput = ref(null) // Ref for auto-focus
const loginUsername = ref('')
const loginPassword = ref('')
const usernameRequiresPassword = ref(null) // null = unknown, true/false = known
const checkingUsername = ref(false)

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
    loginPassword.value || null
  )

  loading.value = false

  if (result.success) {
    success.value = t('login.loginSuccessful')
    // Redirect to intended page or home
    const redirect = route.query.redirect || '/home'
    setTimeout(() => {
      router.push(redirect)
    }, 500)
  } else {
    error.value = result.error
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
    success.value = t('login.accountCreated')
    // Redirect to intended page or home
    const redirect = route.query.redirect || '/home'
    setTimeout(() => {
      router.push(redirect)
    }, 500)
  } else {
    error.value = result.error
  }
}

// Auto-focus username input on mount
onMounted(() => {
  if (loginUsernameInput.value) {
    loginUsernameInput.value.focus()
  }
})

// Check username password requirement with debouncing
let usernameCheckTimeout = null
watch(loginUsername, (newUsername) => {
  // Clear previous timeout
  if (usernameCheckTimeout) {
    clearTimeout(usernameCheckTimeout)
  }

  // Reset state if username is empty
  if (!newUsername || newUsername.trim().length < 3) {
    usernameRequiresPassword.value = null
    checkingUsername.value = false
    return
  }

  // Start checking indicator
  checkingUsername.value = true

  // Debounce: wait 500ms after user stops typing
  usernameCheckTimeout = setTimeout(async () => {
    try {
      const result = await get(`/api/users/check/${encodeURIComponent(newUsername.trim())}`)

      if (result.success && result.data) {
        usernameRequiresPassword.value = result.data.has_password
      } else {
        // Username doesn't exist yet - treat as no password required
        usernameRequiresPassword.value = null
      }
    } catch (err) {
      // If endpoint doesn't exist or error, silently fail
      usernameRequiresPassword.value = null
    } finally {
      checkingUsername.value = false
    }
  }, 500)
})
</script>
