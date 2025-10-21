<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <p class="mb-4">Test: Adding form submit handler</p>

    <!-- Contact Form -->
    <div class="bg-white rounded-2xl shadow-xl border-2 border-gray-200 p-6 sm:p-8">
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <FormInput
          id="name"
          v-model="form.name"
          type="text"
          label="Name"
          placeholder="Your name"
        />

        <FormInput
          id="email"
          v-model="form.email"
          type="email"
          label="Email"
          placeholder="Your email"
        />

        <FormTextarea
          id="message"
          v-model="form.message"
          label="Message"
          placeholder="Your message"
          :rows="5"
        />

        <button
          type="submit"
          class="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3.5 rounded-xl font-bold"
        >
          Send
        </button>
      </form>
    </div>

    <p class="mt-4">Loading: {{ loading }}</p>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'

const { t } = useI18n()

const form = reactive({
  name: '',
  email: '',
  message: ''
})

const loading = ref(false)

const handleSubmit = async () => {
  console.log('Form submitted!', form)
  loading.value = true

  try {
    const response = await axios.post(`${API_BASE_URL}/api/contact`, {
      name: form.name.trim(),
      email: form.email.trim(),
      subject: 'Test subject',
      message: form.message.trim()
    })
    console.log('Success:', response.data)
  } catch (err) {
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}
</script>
