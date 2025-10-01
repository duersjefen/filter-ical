import { createI18n } from 'vue-i18n'

// Lazy-load locales on demand instead of loading all upfront
// This reduces the initial bundle size
const messages = {}

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
  return localStorage.getItem('locale') || getBrowserLocale()
}

// Load a locale dynamically
export const loadLocale = async (locale) => {
  // Return if already loaded
  if (i18n.global.availableLocales.includes(locale)) {
    return
  }

  // Load the locale messages
  const messages = await import(`./locales/${locale}.json`)
  i18n.global.setLocaleMessage(locale, messages.default)
}

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getSavedLocale(),
  fallbackLocale: 'en',
  messages, // Start with empty messages
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

// Load the initial locale
loadLocale(getSavedLocale())

// Save locale changes to localStorage and load if needed
export const setLocale = async (locale) => {
  // Load the locale if not already loaded
  await loadLocale(locale)

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