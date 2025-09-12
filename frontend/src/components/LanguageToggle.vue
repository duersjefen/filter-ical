<template>
  <div class="relative">
    <button
      @click="toggleLanguage"
      class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/10 dark:bg-gray-700/50 hover:bg-white/20 dark:hover:bg-gray-700/70 transition-colors duration-200 text-white dark:text-gray-200 border border-white/20 dark:border-gray-600"
      :title="$t('language.switch')"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
      </svg>
      <span class="text-sm font-medium">{{ currentLanguageLabel }}</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n'

const { locale } = useI18n()

const currentLanguageLabel = computed(() => {
  return locale.value === 'en' ? 'EN' : 'DE'
})

const toggleLanguage = () => {
  const newLocale = locale.value === 'en' ? 'de' : 'en'
  setLocale(newLocale)
}
</script>