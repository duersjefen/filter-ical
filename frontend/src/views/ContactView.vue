<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <!-- Success Message -->
    <div v-if="submitted" class="bg-green-100 border-2 border-green-500 text-green-900 px-6 py-4 rounded-xl mb-6">
      <p class="font-bold">{{ $t('contact.success.title') }}</p>
      <p class="text-sm mt-1">{{ $t('contact.success.message') }} {{ form.email }}</p>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-100 border-2 border-red-500 text-red-900 px-6 py-4 rounded-xl mb-6">
      <p class="font-bold">{{ error }}</p>
    </div>

    <!-- Contact Form -->
    <div class="bg-white rounded-2xl shadow-xl border-2 border-gray-200 p-6 sm:p-8">
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

        <div class="flex gap-4">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-8 py-3.5 rounded-xl font-bold"
          >
            {{ loading ? $t('contact.buttons.sending') : $t('contact.buttons.send') }}
          </button>

          <router-link
            to="/home"
            class="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-8 py-3.5 rounded-xl font-bold text-center no-underline flex items-center justify-center"
          >
            {{ $t('contact.buttons.back') }}
          </router-link>
        </div>
      </form>
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
