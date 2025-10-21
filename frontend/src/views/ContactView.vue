<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <!-- Subtitle Card -->
    <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl border-2 border-blue-200 dark:border-blue-700 p-5 mb-6">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 bg-blue-500 dark:bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
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
    <div v-if="submitted" class="bg-green-50 dark:bg-green-900/30 border-2 border-green-300 dark:border-green-700 text-green-900 dark:text-green-200 px-6 py-4 rounded-xl mb-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
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
    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-700 text-red-900 dark:text-red-200 px-6 py-4 rounded-xl mb-6">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 flex-1">
          <div class="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
          </div>
          <span class="font-bold text-sm sm:text-base">{{ error }}</span>
        </div>
        <button @click="error = ''" class="bg-red-200/50 hover:bg-red-300/70 dark:bg-red-800/50 dark:hover:bg-red-700/70 text-red-800 dark:text-red-200 w-8 h-8 rounded-lg font-bold hover:scale-110 transition-all flex items-center justify-center">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Contact Form -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border-2 border-gray-200 dark:border-gray-700 p-6 sm:p-8">
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
            class="flex-1 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white px-8 py-3.5 rounded-xl font-bold transition-colors duration-200"
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
            class="flex-1 sm:flex-none bg-gray-500 hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-8 py-3.5 rounded-xl font-bold text-center no-underline flex items-center justify-center gap-2 transition-colors duration-200"
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
    <div class="mt-6 bg-gray-50 dark:bg-gray-800/50 border-2 border-gray-200 dark:border-gray-700 rounded-xl p-5">
      <div class="flex items-start gap-3">
        <div class="w-10 h-10 bg-gray-500 dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
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
  errors.name = ''
  errors.email = ''
  errors.subject = ''
  errors.message = ''

  let isValid = true

  if (!form.name || form.name.trim().length < 2) {
    errors.name = t('contact.validation.nameMinLength')
    isValid = false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email || !emailRegex.test(form.email)) {
    errors.email = t('contact.validation.emailInvalid')
    isValid = false
  }

  if (!form.subject || form.subject.trim().length < 5) {
    errors.subject = t('contact.validation.subjectMinLength')
    isValid = false
  }

  if (!form.message || form.message.trim().length < 20) {
    errors.message = t('contact.validation.messageMinLength')
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  error.value = ''
  submitted.value = false

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
      form.name = ''
      form.email = ''
      form.subject = ''
      form.message = ''
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  } catch (err) {
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

const isEmailFormat = (str) => {
  if (!str) return false
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str)
}

onMounted(() => {
  if (isLoggedIn.value && user.value) {
    if (user.value.username) {
      form.name = user.value.username
    }
    if (user.value.email) {
      form.email = user.value.email
    } else if (user.value.username && isEmailFormat(user.value.username)) {
      form.email = user.value.username
    }
  }
})
</script>
