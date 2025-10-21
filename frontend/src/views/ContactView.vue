<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="text-3xl font-bold mb-6">Test 4: Adding useAuth + onMounted</h1>

    <AppHeader
      :title="$t('contact.title')"
      page-context="contact"
    />

    <p class="text-base text-gray-600 mb-4">Testing if useAuth causes the problem...</p>
    <p class="text-base text-gray-600 mb-4">User logged in: {{ isLoggedIn }}</p>
    <p class="text-base text-gray-600 mb-4">Form name: {{ form.name }}</p>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../composables/useAuth'
import AppHeader from '../components/shared/AppHeader.vue'

const { t } = useI18n()
const { user, isLoggedIn } = useAuth()

const form = reactive({
  name: '',
  email: ''
})

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
