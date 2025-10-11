import { createI18n } from 'vue-i18n'
import enMessages from './locales/en.json'
import deMessages from './locales/de.json'

// Detect browser language or default to English
const getBrowserLocale = () => {
  const navigatorLocale = navigator.languages
    ? navigator.languages[0]
    : navigator.language

  if (navigatorLocale) {
    const trimmedLocale = navigatorLocale.trim().split(/-|_/)[0]
    return trimmedLocale
  }

  return 'en'
}

// Get saved locale from localStorage or use browser locale
const getSavedLocale = () => {
  const savedLocale = localStorage.getItem('locale') || getBrowserLocale()
  // Validate locale is supported
  return ['en', 'de'].includes(savedLocale) ? savedLocale : 'en'
}

// Preload both locales to prevent race conditions
// This ensures translations are always available immediately
const messages = {
  en: enMessages,
  de: deMessages
}

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getSavedLocale(),
  fallbackLocale: 'en',
  messages, // Preloaded messages for both locales
  globalInjection: true,
  pluralizationRules: {
    'en': (choice) => {
      if (choice === 0) return 0
      return choice === 1 ? 0 : 1
    },
    'de': (choice) => {
      if (choice === 0) return 0
      return choice === 1 ? 0 : 1
    }
  }
})

// Save locale changes to localStorage
export const setLocale = (locale) => {
  // Validate locale is supported
  if (!['en', 'de'].includes(locale)) {
    console.warn(`Unsupported locale: ${locale}, falling back to 'en'`)
    locale = 'en'
  }

  // Update the locale (handle both ref and string types)
  if (typeof i18n.global.locale === 'object' && 'value' in i18n.global.locale) {
    i18n.global.locale.value = locale
  } else {
    i18n.global.locale = locale
  }

  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}

export default i18n