<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <p class="mb-4">Test: Static form with NO JavaScript logic</p>

    <!-- Contact Form -->
    <div class="bg-white rounded-2xl shadow-xl border-2 border-gray-200 p-6 sm:p-8">
      <div class="space-y-6">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/shared/AppHeader.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'

const { t } = useI18n()

const form = reactive({
  name: '',
  email: '',
  message: ''
})
</script>
