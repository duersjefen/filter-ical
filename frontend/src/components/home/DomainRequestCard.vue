<template>
  <div class="bg-gradient-to-br from-white via-white to-green-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-green-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-6 sm:p-8 hover:shadow-2xl hover:border-green-300/50 dark:hover:border-green-600/50 transition-all duration-300 backdrop-blur-sm">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 rounded-xl flex items-center justify-center shadow-lg">
        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
      </div>
      <div>
        <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('domainRequest.title') }}</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">{{ $t('domainRequest.subtitle') }}</p>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="bg-gradient-to-br from-green-50 via-green-100 to-emerald-50 dark:from-green-900/30 dark:via-green-800/30 dark:to-emerald-900/30 text-green-900 dark:text-green-200 px-6 py-5 rounded-2xl mb-6 border-2 border-green-300 dark:border-green-700 shadow-xl backdrop-blur-sm">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="font-bold text-sm sm:text-base">{{ successMessage }}</span>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="bg-gradient-to-br from-red-50 via-red-100 to-orange-50 dark:from-red-900/30 dark:via-red-800/30 dark:to-orange-900/30 text-red-900 dark:text-red-200 px-6 py-5 rounded-2xl mb-6 border-2 border-red-300 dark:border-red-700 shadow-xl backdrop-blur-sm">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 flex-1">
          <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
          </div>
          <span class="font-bold text-sm sm:text-base">{{ errorMessage }}</span>
        </div>
        <button @click="errorMessage = null" class="bg-red-200/50 hover:bg-red-300/70 dark:bg-red-800/50 dark:hover:bg-red-700/70 text-red-800 dark:text-red-200 cursor-pointer w-8 h-8 rounded-xl font-bold hover:scale-110 active:scale-95 transition-all duration-200 shadow-md flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Feature Highlights -->
    <div class="bg-gradient-to-br from-green-50/50 to-emerald-50/50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-5 mb-6 border border-green-200 dark:border-green-700/50">
      <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ $t('domainRequest.features.title') }}</h3>
      <ul class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
        <li class="flex items-start gap-2">
          <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span>{{ $t('domainRequest.features.groups') }}</span>
        </li>
        <li class="flex items-start gap-2">
          <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span>{{ $t('domainRequest.features.filters') }}</span>
        </li>
        <li class="flex items-start gap-2">
          <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          <span>{{ $t('domainRequest.features.sharing') }}</span>
        </li>
      </ul>
    </div>

    <!-- Authentication Notice -->
    <div v-if="!canSubmitRequest" class="bg-gradient-to-br from-blue-50 via-blue-100 to-indigo-50 dark:from-blue-900/30 dark:via-blue-800/30 dark:to-indigo-900/30 text-blue-900 dark:text-blue-200 px-6 py-5 rounded-2xl mb-6 border-2 border-blue-300 dark:border-blue-700 shadow-xl backdrop-blur-sm">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="font-bold text-sm sm:text-base">{{ needsEmailMessage }}</span>
      </div>
    </div>

    <!-- Request Form -->
    <form @submit.prevent="submitRequest" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label for="domain-key-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            Desired Domain Key
          </label>
          <input
            id="domain-key-request"
            v-model="formData.requested_domain_key"
            type="text"
            pattern="[a-z0-9-]+"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-green-500 dark:focus:border-green-400 focus:ring-4 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500"
            placeholder="my-calendar"
            minlength="3"
            maxlength="100"
            :disabled="!canSubmitRequest"
            required
          />
          <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Lowercase letters, numbers, hyphens only
          </div>
        </div>

        <div>
          <label for="calendar-url-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            {{ $t('domainRequest.form.calendarUrl') }}
          </label>
          <input
            id="calendar-url-request"
            v-model="formData.calendar_url"
            type="url"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-green-500 dark:focus:border-green-400 focus:ring-4 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500"
            :placeholder="$t('domainRequest.form.calendarUrlPlaceholder')"
            :disabled="!canSubmitRequest"
            required
          />
        </div>
      </div>

      <!-- Passwords: Side by Side -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Admin Password -->
        <div>
          <label for="admin-password-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            Admin Password *
          </label>
          <div class="relative">
            <input
              id="admin-password-request"
              v-model="formData.default_password"
              :type="showAdminPassword ? 'text' : 'password'"
              :class="[
                'w-full px-4 py-3.5 pr-12 border-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-4 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500',
                formData.default_password && !isAdminPasswordValid
                  ? 'border-red-500 dark:border-red-400 focus:border-red-500 dark:focus:border-red-400 focus:ring-red-100 dark:focus:ring-red-900/50'
                  : 'border-gray-300 dark:border-gray-600 focus:border-green-500 dark:focus:border-green-400 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500'
              ]"
              placeholder="Min 4 characters"
              minlength="4"
              maxlength="100"
              :disabled="!canSubmitRequest"
              required
            />
            <button
              v-if="formData.default_password"
              type="button"
              @click="showAdminPassword = !showAdminPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :title="showAdminPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showAdminPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <div v-if="formData.default_password && !isAdminPasswordValid" class="mt-1 text-xs text-red-600 dark:text-red-400 font-semibold">
            {{ $t('domainRequest.errors.passwordTooShort') }}
          </div>
        </div>

        <!-- User Password -->
        <div>
          <label for="user-password-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            User Password <span class="text-gray-500 dark:text-gray-400 font-normal">(Optional)</span>
          </label>
          <div class="relative">
            <input
              id="user-password-request"
              v-model="formData.user_password"
              :type="showUserPassword ? 'text' : 'password'"
              :class="[
                'w-full px-4 py-3.5 pr-12 border-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-4 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500',
                formData.user_password && !isUserPasswordValid
                  ? 'border-red-500 dark:border-red-400 focus:border-red-500 dark:focus:border-red-400 focus:ring-red-100 dark:focus:ring-red-900/50'
                  : 'border-gray-300 dark:border-gray-600 focus:border-green-500 dark:focus:border-green-400 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500'
              ]"
              placeholder="Leave blank if none"
              minlength="4"
              maxlength="100"
              :disabled="!canSubmitRequest"
            />
            <button
              v-if="formData.user_password"
              type="button"
              @click="showUserPassword = !showUserPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :title="showUserPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showUserPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <div v-if="formData.user_password && !isUserPasswordValid" class="mt-1 text-xs text-red-600 dark:text-red-400 font-semibold">
            {{ $t('domainRequest.errors.passwordTooShort') }}
          </div>
        </div>
      </div>

      <div>
        <label for="description-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
          {{ $t('domainRequest.form.description') }}
        </label>
        <textarea
          id="description-request"
          v-model="formData.description"
          rows="4"
          :class="[
            'w-full px-4 py-3.5 border-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-4 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500 resize-none',
            formData.description && !isDescriptionValid
              ? 'border-red-500 dark:border-red-400 focus:border-red-500 dark:focus:border-red-400 focus:ring-red-100 dark:focus:ring-red-900/50'
              : 'border-gray-300 dark:border-gray-600 focus:border-green-500 dark:focus:border-green-400 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500'
          ]"
          :placeholder="$t('domainRequest.form.descriptionPlaceholder')"
          minlength="10"
          maxlength="500"
          :disabled="!canSubmitRequest"
          required
        ></textarea>
        <div class="flex items-center justify-between mt-1">
          <div v-if="formData.description && !isDescriptionValid" class="text-xs text-red-600 dark:text-red-400 font-semibold">
            {{ $t('domainRequest.errors.descriptionTooShort') }}
          </div>
          <div v-else class="text-xs text-gray-500 dark:text-gray-400">
            {{ formData.description.length }} / 500 {{ $t('domainRequest.form.characters') }}
          </div>
        </div>
      </div>

      <button
        type="submit"
        :disabled="loading || !isFormValid"
        class="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 dark:from-green-600 dark:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-6 py-3.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg hover:shadow-xl disabled:shadow-sm disabled:transform-none"
      >
        {{ loading ? $t('domainRequest.form.submitting') : $t('domainRequest.form.submit') }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth'
import { useHTTP } from '../../composables/useHTTP'

const { t } = useI18n()
const { user, isLoggedIn } = useAuth()
const { post } = useHTTP()

const loading = ref(false)
const successMessage = ref(null)
const errorMessage = ref(null)
const showAdminPassword = ref(false)
const showUserPassword = ref(false)

const formData = ref({
  requested_domain_key: '',
  calendar_url: '',
  description: '',
  default_password: '',
  user_password: ''
})

// Check if user can submit (logged in with email)
const canSubmitRequest = computed(() => {
  return isLoggedIn.value && user.value?.email
})

const needsEmailMessage = computed(() => {
  if (!isLoggedIn.value) {
    return 'You must be logged in to request a domain'
  }
  if (!user.value?.email) {
    return 'Please add an email to your profile before requesting a domain'
  }
  return null
})

// Validation computed properties
const isDescriptionValid = computed(() => {
  return formData.value.description.length >= 10
})

const isAdminPasswordValid = computed(() => {
  // Admin password is required and must be at least 4 chars
  return formData.value.default_password && formData.value.default_password.length >= 4
})

const isUserPasswordValid = computed(() => {
  // User password is optional, but if provided, must be at least 4 chars
  return !formData.value.user_password || formData.value.user_password.length >= 4
})

const isFormValid = computed(() => {
  return canSubmitRequest.value &&
         formData.value.requested_domain_key &&
         formData.value.calendar_url &&
         isDescriptionValid.value &&
         isAdminPasswordValid.value &&
         isUserPasswordValid.value
})

const submitRequest = async () => {
  if (!canSubmitRequest.value) {
    errorMessage.value = needsEmailMessage.value
    return
  }

  if (!isFormValid.value) {
    return
  }

  loading.value = true
  errorMessage.value = null
  successMessage.value = null

  try {
    const payload = {
      requested_domain_key: formData.value.requested_domain_key.toLowerCase(),
      calendar_url: formData.value.calendar_url,
      description: formData.value.description,
      default_password: formData.value.default_password
    }

    // Only include user_password if provided
    if (formData.value.user_password) {
      payload.user_password = formData.value.user_password
    }

    const result = await post('/api/domain-requests', payload)

    if (result.success) {
      successMessage.value = t('domainRequest.success')
      // Clear form
      formData.value.requested_domain_key = ''
      formData.value.calendar_url = ''
      formData.value.description = ''
      formData.value.default_password = ''
      formData.value.user_password = ''
      showAdminPassword.value = false
      showUserPassword.value = false
    } else {
      errorMessage.value = result.error || t('domainRequest.errors.submissionFailed')
    }
  } catch (error) {
    errorMessage.value = t('domainRequest.errors.submissionFailed')
  } finally {
    loading.value = false
  }
}
</script>
