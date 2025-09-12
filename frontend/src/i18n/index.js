import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import de from './locales/de.json'

const messages = {
  en,
  de
}

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

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: getSavedLocale(),
  fallbackLocale: 'en',
  messages,
  globalInjection: true,
  pluralizationRules: {
    'en': (choice, choicesLength) => {
      if (choice === 0) return 0
      return choice === 1 ? 0 : 1
    },
    'de': (choice, choicesLength) => {
      if (choice === 0) return 0
      return choice === 1 ? 0 : 1
    }
  }
})

// Save locale changes to localStorage
export const setLocale = (locale) => {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}

export default i18n