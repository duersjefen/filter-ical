<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <!-- Subtitle Card -->
    <div class="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-2xl shadow-lg border-2 border-blue-200 dark:border-blue-700 p-5 mb-6 backdrop-blur-sm">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <p class="text-gray-800 dark:text-gray-200 text-sm sm:text-base flex-1 pt-1.5">
          {{ $t('contact.subtitle') }}
        </p>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="submitted" class="bg-gradient-to-br from-green-50 via-green-100 to-emerald-50 dark:from-green-900/30 dark:via-green-800/30 dark:to-emerald-900/30 text-green-900 dark:text-green-200 px-6 py-5 rounded-2xl mb-6 border-2 border-green-300 dark:border-green-700 shadow-xl backdrop-blur-sm">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div>
          <p class="font-bold text-base">{{ $t('contact.success.title') }}</p>
          <p class="text-sm mt-1">{{ $t('contact.success.message') }} <strong>{{ form.email }}</strong></p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-gradient-to-br from-red-50 via-red-100 to-orange-50 dark:from-red-900/30 dark:via-red-800/30 dark:to-orange-900/30 text-red-900 dark:text-red-200 px-6 py-5 rounded-2xl mb-6 border-2 border-red-300 dark:border-red-700 shadow-xl backdrop-blur-sm">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 flex-1">
          <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
          </div>
          <span class="font-bold text-sm sm:text-base">{{ error }}</span>
        </div>
        <button @click="error = ''" class="bg-red-200/50 hover:bg-red-300/70 dark:bg-red-800/50 dark:hover:bg-red-700/70 text-red-800 dark:text-red-200 cursor-pointer w-8 h-8 rounded-xl font-bold hover:scale-110 active:scale-95 transition-all duration-200 shadow-md flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Contact Form -->
    <div class="bg-gradient-to-br from-white via-white to-blue-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-blue-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-6 sm:p-8 hover:shadow-2xl hover:border-blue-300/50 dark:hover:border-blue-600/50 transition-all duration-300 backdrop-blur-sm">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <FormInput
          id="name"
          v-model="form.name"
          type="text"
          :label="$t('contact.form.nameLabel')"
          :placeholder="$t('contact.form.namePlaceholder')"
          :required="true"
          :minlength="2"
          :maxlength="100"
          :error="errors.name"
        />

        <FormInput
          id="email"
          v-model="form.email"
          type="email"
          :label="$t('contact.form.emailLabel')"
          :placeholder="$t('contact.form.emailPlaceholder')"
          :required="true"
          :maxlength="200"
          :helper-text="$t('contact.form.emailHelper')"
          :error="errors.email"
        />

        <FormInput
          id="subject"
          v-model="form.subject"
          type="text"
          :label="$t('contact.form.subjectLabel')"
          :placeholder="$t('contact.form.subjectPlaceholder')"
          :required="true"
          :minlength="5"
          :maxlength="200"
          :error="errors.subject"
        />

        <FormTextarea
          id="message"
          v-model="form.message"
          :label="$t('contact.form.messageLabel')"
          :placeholder="$t('contact.form.messagePlaceholder')"
          :required="true"
          :minlength="20"
          :maxlength="2000"
          :rows="8"
          :error="errors.message"
          :show-char-count="true"
        />

        <div class="flex flex-col sm:flex-row gap-4">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-8 py-3.5 rounded-xl cursor-pointer text-base font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg hover:shadow-xl disabled:shadow-sm disabled:transform-none"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ $t('contact.buttons.sending') }}
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              {{ $t('contact.buttons.send') }}
            </span>
          </button>

          <router-link
            to="/home"
            class="flex-1 sm:flex-none bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 dark:from-gray-600 dark:to-gray-700 dark:hover:from-gray-700 dark:hover:to-gray-800 text-white border-none px-8 py-3.5 rounded-xl cursor-pointer text-base font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg hover:shadow-xl text-center flex items-center justify-center gap-2 no-underline"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            {{ $t('contact.buttons.back') }}
          </router-link>
        </div>
      </form>
    </div>

    <!-- Help Text -->
    <div class="mt-6 bg-gradient-to-br from-gray-50 via-gray-100 to-blue-50/30 dark:from-gray-800/50 dark:via-gray-700/50 dark:to-blue-900/10 border-2 border-gray-200 dark:border-gray-700 rounded-2xl p-5 shadow-lg backdrop-blur-sm">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-gray-500 to-gray-600 dark:from-gray-600 dark:to-gray-700 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div>
          <p class="text-gray-800 dark:text-gray-200 font-bold text-sm mb-2">{{ $t('contact.help.title') }}</p>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            {{ $t('contact.help.message') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import { useAuth } from '../composables/useAuth'
import AppHeader from '../components/shared/AppHeader.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'

const { t } = useI18n()

const { user, isLoggedIn } = useAuth()

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const errors = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const loading = ref(false)
const submitted = ref(false)
const error = ref('')

const validateForm = () => {
  // Reset errors
  errors.name = ''
  errors.email = ''
  errors.subject = ''
  errors.message = ''

  let isValid = true

  // Validate name
  if (!form.name || form.name.trim().length < 2) {
    errors.name = t('contact.validation.nameMinLength')
    isValid = false
  } else if (form.name.length > 100) {
    errors.name = t('contact.validation.nameMaxLength')
    isValid = false
  }

  // Validate email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email || !emailRegex.test(form.email)) {
    errors.email = t('contact.validation.emailInvalid')
    isValid = false
  } else if (form.email.length > 200) {
    errors.email = t('contact.validation.emailMaxLength')
    isValid = false
  }

  // Validate subject
  if (!form.subject || form.subject.trim().length < 5) {
    errors.subject = t('contact.validation.subjectMinLength')
    isValid = false
  } else if (form.subject.length > 200) {
    errors.subject = t('contact.validation.subjectMaxLength')
    isValid = false
  }

  // Validate message
  if (!form.message || form.message.trim().length < 20) {
    errors.message = t('contact.validation.messageMinLength')
    isValid = false
  } else if (form.message.length > 2000) {
    errors.message = t('contact.validation.messageMaxLength')
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  // Reset states
  error.value = ''
  submitted.value = false

  // Validate form
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const response = await axios.post(`${API_BASE_URL}/api/contact`, {
      name: form.name.trim(),
      email: form.email.trim(),
      subject: form.subject.trim(),
      message: form.message.trim()
    })

    if (response.data.success) {
      submitted.value = true
      // Reset form
      form.name = ''
      form.email = ''
      form.subject = ''
      form.message = ''

      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  } catch (err) {
    console.error('Contact form error:', err)

    if (err.response?.status === 429) {
      error.value = t('contact.errors.tooManyRequests')
    } else if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = t('contact.errors.failedToSend')
    }
  } finally {
    loading.value = false
  }
}

// Helper function to check if a string looks like an email
const isEmailFormat = (str) => {
  if (!str) return false
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str)
}

// Pre-fill form with user data when logged in
onMounted(() => {
  if (isLoggedIn.value && user.value) {
    // Pre-fill name with username
    if (user.value.username) {
      form.name = user.value.username
    }

    // Pre-fill email if user has one
    if (user.value.email) {
      form.email = user.value.email
    } else if (user.value.username && isEmailFormat(user.value.username)) {
      // If username is an email format, use it
      form.email = user.value.username
    }
  }
})
</script>
