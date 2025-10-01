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

    <!-- Request Form -->
    <form @submit.prevent="submitRequest" class="space-y-4">
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
          required
        />
      </div>

      <div>
        <label for="description-request" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
          {{ $t('domainRequest.form.description') }}
        </label>
        <textarea
          id="description-request"
          v-model="formData.description"
          rows="4"
          class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-green-500 dark:focus:border-green-400 focus:ring-4 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500 resize-none"
          :placeholder="$t('domainRequest.form.descriptionPlaceholder')"
          minlength="10"
          maxlength="500"
          required
        ></textarea>
        <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ formData.description.length }} / 500 {{ $t('domainRequest.form.characters') }}
        </div>
      </div>

      <button
        type="submit"
        :disabled="loading || !formData.calendar_url || !formData.description || formData.description.length < 10"
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
import { useUsername } from '../../composables/useUsername'
import { useHTTP } from '../../composables/useHTTP'

const { t } = useI18n()
const { username } = useUsername()
const { post } = useHTTP()

const loading = ref(false)
const successMessage = ref(null)
const errorMessage = ref(null)

const formData = ref({
  calendar_url: '',
  description: ''
})

const submitRequest = async () => {
  if (!username.value) {
    errorMessage.value = t('domainRequest.errors.loginRequired')
    return
  }

  if (formData.value.description.length < 10) {
    errorMessage.value = t('domainRequest.errors.descriptionTooShort')
    return
  }

  loading.value = true
  errorMessage.value = null
  successMessage.value = null

  try {
    const result = await post('/domain-requests', {
      username: username.value,
      calendar_url: formData.value.calendar_url,
      description: formData.value.description
    })

    if (result.success) {
      successMessage.value = t('domainRequest.success')
      // Clear form
      formData.value.calendar_url = ''
      formData.value.description = ''
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
