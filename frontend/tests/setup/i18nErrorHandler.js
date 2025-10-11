/**
 * i18n Error Handler - Strict i18n configuration for tests
 *
 * Creates an i18n instance that throws errors on missing translations
 * instead of silently falling back or showing key names.
 */
import { createI18n } from 'vue-i18n'
import enMessages from '@/i18n/locales/en.json'
import deMessages from '@/i18n/locales/de.json'

/**
 * Create strict i18n instance for testing
 * Fails tests on missing translation keys
 */
export function createStrictI18n(options = {}) {
  const i18n = createI18n({
    legacy: false,
    locale: options.locale || 'en',
    fallbackLocale: 'en',
    messages: {
      en: enMessages,
      de: deMessages
    },
    globalInjection: true,
    // Strict mode - throw errors instead of warnings
    missing: (locale, key) => {
      throw new Error(
        `Missing translation key: "${key}" for locale: "${locale}"`
      )
    },
    missingWarn: false,
    fallbackWarn: false,
    silentTranslationWarn: false,
    silentFallbackWarn: false
  })

  return i18n
}

/**
 * Default i18n instance for tests
 */
export const testI18n = createStrictI18n()
