<template>
  <div>
    <!-- Page Header with Gradient -->
    <AppHeader
      :title="domainContext ? `🌐 ${domainContext.name}` : $t('calendar.filterTitle', { name: selectedCalendar?.name || $t('common.loading') })"
      :subtitle="domainContext ? $t('subtitles.domainCalendar') : $t('calendar.subtitle')"
      :show-back-button="true"
      :back-button-text="domainContext ? $t('domain.goToPersonalCalendars') : $t('navigation.backToCalendars')"
      :domain-context="domainContext"
      page-context="calendar"
      :hide-subtitle="!domainContext"
      @navigate-back="domainContext ? $router.push('/home') : $emit('navigate-home')"
    />

    <!-- Error Message -->
    <div v-if="error" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
      <!-- Header with gradient background matching admin cards -->
      <div class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-red-200 dark:border-red-700">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
              <span class="text-red-600 dark:text-red-400 text-xl">⚠️</span>
            </div>
            <div class="flex-1">
              <h3 class="text-lg sm:text-xl font-bold text-red-800 dark:text-red-200 mb-1">
                📊 Calendar Error
              </h3>
              <p class="text-sm text-red-600 dark:text-red-300">
                An error occurred while loading
              </p>
            </div>
          </div>
          <button @click="$emit('clear-error')" class="w-8 h-8 rounded-lg flex items-center justify-center text-red-600 hover:text-red-800 hover:bg-red-100 dark:hover:bg-red-900/20 transition-all duration-200 flex-shrink-0">
            <span class="text-xl font-bold">&times;</span>
          </button>
        </div>
      </div>
      
      <!-- Content area -->
      <div class="p-4">
        <div class="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-800">
          <p class="text-red-800 dark:text-red-200 font-medium mb-2">{{ $t('messages.errorDetails') }}</p>
          <p class="text-red-700 dark:text-red-300 text-sm leading-relaxed">{{ error }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppHeader from '../shared/AppHeader.vue'

const router = useRouter()

defineProps({
  selectedCalendar: Object,
  error: String,
  domainContext: {
    type: Object,
    default: null
  }
})

defineEmits(['navigate-home', 'clear-error'])
</script>