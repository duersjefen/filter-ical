<template>
  <div class="container">
    <div class="page-header">
      <h1>🗓️ iCal Filter & Subscribe</h1>
      <p>Please log in to access your calendars</p>
    </div>

    <div class="card" style="max-width: 400px; margin: 0 auto;">
      <h2 style="margin-bottom: 24px; text-align: center;">Login</h2>
      
      <div v-if="appStore.error" class="error">
        {{ appStore.error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="appStore.loginForm.username"
            type="text"
            class="form-control"
            placeholder="Enter your username"
            required
          />
        </div>

        <button type="submit" class="btn" style="width: 100%;" :disabled="appStore.loading">
          {{ appStore.loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { watch } from 'vue'

const appStore = useAppStore()
const router = useRouter()

const handleLogin = async () => {
  await appStore.login()
  // Explicitly redirect after successful login
  if (appStore.isLoggedIn) {
    router.push('/home')
  }
}
</script>