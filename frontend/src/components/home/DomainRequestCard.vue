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
        <FormInput
          id="domain-key-request"
          v-model="formData.requested_domain_key"
          :label="$t('domain.desiredKey')"
          type="text"
          pattern="[a-z0-9-]+"
          :placeholder="$t('domain.keyPlaceholder')"
          minlength="3"
          maxlength="100"
          :disabled="!canSubmitRequest"
          required
          :helper-text="$t('domain.keyHelper')"
        />

        <FormInput
          id="calendar-url-request"
          v-model="formData.calendar_url"
          :label="$t('domainRequest.form.calendarUrl')"
          type="url"
          :placeholder="$t('domainRequest.form.calendarUrlPlaceholder')"
          :disabled="!canSubmitRequest"
          required
        />
      </div>

      <!-- Passwords: Side by Side -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormInput
          id="admin-password-request"
          v-model="formData.default_password"
          :label="$t('domain.adminPassword')"
          type="password"
          :placeholder="$t('domain.passwordMinLength')"
          minlength="4"
          maxlength="100"
          :disabled="!canSubmitRequest"
          required
          :error="formData.default_password && !isAdminPasswordValid ? $t('domainRequest.errors.passwordTooShort') : ''"
        />

        <FormInput
          id="user-password-request"
          v-model="formData.user_password"
          :label="$t('domain.userPassword')"
          optional="Optional"
          type="password"
          :placeholder="$t('domain.leaveBlankIfNone')"
          minlength="4"
          maxlength="100"
          :disabled="!canSubmitRequest"
          :error="formData.user_password && !isUserPasswordValid ? $t('domainRequest.errors.passwordTooShort') : ''"
        />
      </div>

      <FormTextarea
        id="description-request"
        v-model="formData.description"
        :label="$t('domainRequest.form.description')"
        :placeholder="$t('domainRequest.form.descriptionPlaceholder')"
        rows="4"
        minlength="10"
        maxlength="500"
        :disabled="!canSubmitRequest"
        required
        :error="formData.description && !isDescriptionValid ? $t('domainRequest.errors.descriptionTooShort') : ''"
      />

      <BaseButton
        type="submit"
        variant="success"
        size="lg"
        full-width
        :disabled="loading || !isFormValid"
        :loading="loading"
        :loading-text="$t('domainRequest.form.submitting')"
      >
        {{ $t('domainRequest.form.submit') }}
      </BaseButton>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../composables/useAuth'
import { useHTTP } from '../../composables/useHTTP'
import FormInput from '../shared/FormInput.vue'
import FormTextarea from '../shared/FormTextarea.vue'
import BaseButton from '../shared/BaseButton.vue'

const { t } = useI18n()
const { user, isLoggedIn } = useAuth()
const { post } = useHTTP()

const loading = ref(false)
const successMessage = ref(null)
const errorMessage = ref(null)

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
    return t('domain.loginRequired')
  }
  if (!user.value?.email) {
    return t('domain.emailRequired')
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
