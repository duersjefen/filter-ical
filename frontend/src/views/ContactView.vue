<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="text-3xl font-bold mb-6">Test 3: Adding FormTextarea</h1>

    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <div class="mt-6 bg-white p-6 rounded-lg shadow space-y-4">
      <FormInput
        id="name"
        v-model="form.name"
        type="text"
        :label="$t('contact.form.nameLabel')"
        :placeholder="$t('contact.form.namePlaceholder')"
        :required="true"
      />

      <FormTextarea
        id="message"
        v-model="form.message"
        :label="$t('contact.form.messageLabel')"
        :placeholder="$t('contact.form.messagePlaceholder')"
        :required="true"
        :rows="5"
      />
    </div>

    <p class="text-lg mb-4 mt-6">If you see both inputs above, FormTextarea works!</p>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/shared/AppHeader.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'

const { t } = useI18n()

const form = reactive({
  name: '',
  message: ''
})
</script>
