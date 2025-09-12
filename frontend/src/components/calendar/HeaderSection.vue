<template>
  <div>
    <!-- Header with user info -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
      <div style="display: flex; align-items: center; gap: 16px;">
        <span>{{ user.username }}</span>
        <button @click="$emit('logout')" class="btn btn-secondary">Logout</button>
      </div>
    </div>

    <div class="page-header">
      <h1>Filter: {{ selectedCalendar?.name || 'Loading...' }}</h1>
      <p>Select event types to filter and create custom subscriptions</p>
      
      <div style="margin-top: 20px;">
        <button @click="$emit('navigate-home')" class="btn btn-secondary">
          ← Back to Calendars
        </button>
      </div>
    </div>

    <div v-if="error" class="error">
      {{ error }}
      <button @click="$emit('clear-error')" style="float: right; background: none; border: none; color: inherit; cursor: pointer;">&times;</button>
    </div>

    <div v-if="loading" class="loading">
      Loading events...
    </div>
  </div>
</template>

<script setup>
defineProps({
  user: Object,
  selectedCalendar: Object,
  error: String,
  loading: Boolean
})

defineEmits(['logout', 'navigate-home', 'clear-error'])
</script>