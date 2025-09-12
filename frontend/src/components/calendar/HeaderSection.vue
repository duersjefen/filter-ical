<template>
  <div>
    <!-- Page Header with Gradient -->
    <AppHeader 
      :title="`Filter: ${selectedCalendar?.name || 'Loading...'}`"
      subtitle="Select event types to filter and create custom subscriptions"
      :user="user"
      :show-user-info="true"
      :show-back-button="true"
      back-button-text="← Back to Calendars"
      @logout="$emit('logout')"
      @navigate-back="$emit('navigate-home')"
    />

    <!-- Error Message -->
    <div v-if="error" class="bg-gradient-to-r from-red-100 to-red-50 border-2 border-red-300 text-red-800 px-6 py-4 rounded-xl mb-6 flex justify-between items-center shadow-lg">
      <div class="flex items-center gap-3">
        <div class="text-2xl">⚠️</div>
        <span class="font-semibold">{{ error }}</span>
      </div>
      <button @click="$emit('clear-error')" class="bg-none border-none text-red-800 cursor-pointer text-xl hover:text-red-600 transition-all duration-300 hover:scale-110 p-2 rounded-full hover:bg-red-200 font-bold">
        &times;
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border-2 border-blue-200 shadow-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
      <div class="text-blue-800 font-semibold text-lg">Loading events...</div>
      <div class="text-blue-600 text-sm mt-2">Please wait while we fetch your calendar data</div>
    </div>
  </div>
</template>

<script setup>
import AppHeader from '../shared/AppHeader.vue'

defineProps({
  user: Object,
  selectedCalendar: Object,
  error: String,
  loading: Boolean
})

defineEmits(['logout', 'navigate-home', 'clear-error'])
</script>