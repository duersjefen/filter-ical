<template>
  <div>
    <!-- Page Header with Gradient -->
    <AppHeader 
      :title="domainContext ? `🌐 ${domainContext.name}` : $t('calendar.filterTitle', { name: selectedCalendar?.name || $t('common.loading') })"
      :subtitle="domainContext ? 'Domain Calendar' : $t('calendar.subtitle')"
      :show-user-info="false"
      :show-back-button="true"
      :back-button-text="domainContext ? $t('domain.goToPersonalCalendars') : $t('navigation.backToCalendars')"
      page-context="calendar"
      hide-subtitle
      @navigate-back="domainContext ? $router.push('/home') : $emit('navigate-home')"
    />

    <!-- Error Message -->
    <div v-if="error" class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 border-2 border-red-300 dark:border-red-700 text-red-800 dark:text-red-200 px-6 py-4 rounded-xl mb-6 flex justify-between items-center shadow-lg">
      <div class="flex items-center gap-3">
        <div class="text-2xl">⚠️</div>
        <span class="font-semibold">{{ error }}</span>
      </div>
      <button @click="$emit('clear-error')" class="bg-none border-none text-red-800 dark:text-red-200 cursor-pointer text-xl hover:text-red-600 dark:hover:text-red-300 transition-all duration-300 hover:scale-110 p-2 rounded-full hover:bg-red-200 dark:hover:bg-red-800/50 font-bold">
        &times;
      </button>
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