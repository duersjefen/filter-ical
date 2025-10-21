<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="text-3xl font-bold mb-6">Test 1: Adding AppHeader</h1>

    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <p class="text-lg mb-4 mt-6">If you see the header above, AppHeader works!</p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/shared/AppHeader.vue'

const { t } = useI18n()
</script>
