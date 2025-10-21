<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Header -->
    <AppHeader
      :title="$t('contact.title')"
      :subtitle="$t('contact.subtitle')"
      page-context="contact"
      :hide-subtitle="true"
    />

    <!-- Success Message -->
    <div v-if="submitted" class="bg-green-50 dark:bg-green-900/30 border-2 border-green-300 dark:border-green-700 text-green-900 dark:text-green-200 px-6 py-4 rounded-xl mb-6">
      <div class="flex items-center gap-3">
        <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
        </svg>
        <div>
          <p class="font-bold">{{ $t('contact.success.title') }}</p>
          <p class="text-sm mt-1">{{ $t('contact.success.message') }}</p>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-700 text-red-900 dark:text-red-200 px-6 py-4 rounded-xl mb-6">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
          <span class="font-bold">{{ error }}</span>
        </div>
        <button @click="error = ''" class="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Contact Form -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Name -->
        <div>
          <label for="name" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('contact.form.nameLabel') }} <span class="text-red-500">*</span>
          </label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            minlength="2"
            maxlength="100"
            :placeholder="$t('contact.form.namePlaceholder')"
            class="w-full px-4 py-3 border-2 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/50"
          />
          <p v-if="errors.name" class="text-red-600 dark:text-red-400 text-xs mt-1 font-semibold">{{ errors.name }}</p>
        </div>

        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('contact.form.emailLabel') }} <span class="text-red-500">*</span>
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            maxlength="200"
            :placeholder="$t('contact.form.emailPlaceholder')"
            class="w-full px-4 py-3 border-2 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/50"
          />
          <p v-if="errors.email" class="text-red-600 dark:text-red-400 text-xs mt-1 font-semibold">{{ errors.email }}</p>
        </div>

        <!-- Subject -->
        <div>
          <label for="subject" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('contact.form.subjectLabel') }} <span class="text-red-500">*</span>
          </label>
          <input
            id="subject"
            v-model="form.subject"
            type="text"
            required
            minlength="5"
            maxlength="200"
            :placeholder="$t('contact.form.subjectPlaceholder')"
            class="w-full px-4 py-3 border-2 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/50"
          />
          <p v-if="errors.subject" class="text-red-600 dark:text-red-400 text-xs mt-1 font-semibold">{{ errors.subject }}</p>
        </div>

        <!-- Message -->
        <div>
          <label for="message" class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('contact.form.messageLabel') }} <span class="text-red-500">*</span>
          </label>
          <textarea
            id="message"
            v-model="form.message"
            required
            minlength="20"
            maxlength="2000"
            rows="8"
            :placeholder="$t('contact.form.messagePlaceholder')"
            class="w-full px-4 py-3 border-2 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/50 resize-none"
          ></textarea>
          <div class="flex items-center justify-between mt-1">
            <p v-if="errors.message" class="text-red-600 dark:text-red-400 text-xs font-semibold">{{ errors.message }}</p>
            <p class="text-gray-500 dark:text-gray-400 text-xs ml-auto">{{ form.message.length }} / 2000</p>
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex flex-col sm:flex-row gap-4">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 text-white px-8 py-3.5 rounded-xl font-bold transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span>{{ loading ? $t('contact.buttons.sending') : $t('contact.buttons.send') }}</span>
          </button>

          <router-link
            to="/home"
            class="sm:flex-none bg-gray-500 hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-8 py-3.5 rounded-xl font-bold text-center no-underline flex items-center justify-center gap-2 transition-colors duration-200"
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
    <div class="mt-6 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5">
      <p class="text-gray-800 dark:text-gray-200 font-bold text-sm mb-2">{{ $t('contact.help.title') }}</p>
      <p class="text-gray-600 dark:text-gray-400 text-sm">{{ $t('contact.help.message') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'

const { t } = useI18n()

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
</script>
