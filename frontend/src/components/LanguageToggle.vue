<template>
  <!-- Desktop version -->
  <button
    @click="toggleLanguage"
    class="hidden sm:flex w-11 h-11 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-md items-center justify-center group"
    :title="$t('language.switch')"
    :aria-label="$t('language.switch')"
  >
    <span class="text-white text-xs sm:text-sm font-bold group-hover:text-white/90 transition-colors duration-300">
      {{ currentLanguageLabel }}
    </span>
  </button>
  
  <!-- Mobile version with better touch targets -->
  <button
    @click="toggleLanguage"
    class="flex sm:hidden w-16 h-8 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg items-center justify-center group touch-manipulation"
    :title="$t('language.switch')"
    :aria-label="$t('language.switch')"
  >
    <span class="text-white text-base font-bold group-hover:text-white/90 transition-colors duration-200">
      {{ currentLanguageLabel }}
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale } from '../i18n'

const { locale } = useI18n()

const currentLanguageLabel = computed(() => {
  return locale.value === 'en' ? 'EN' : 'DE'
})

const toggleLanguage = async () => {
  const newLocale = locale.value === 'en' ? 'de' : 'en'
  await setLocale(newLocale)
}
</script>