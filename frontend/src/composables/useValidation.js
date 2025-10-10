/**
 * useValidation - Validation utilities for forms
 *
 * Provides common validation functions for email, password, URLs, and required fields.
 */

export function useValidation() {
  /**
   * Validates email format
   * @param {string} email - The email to validate
   * @returns {boolean} - True if email is valid
   */
  const isValidEmail = (email) => {
    if (!email || typeof email !== 'string') return false
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email.trim())
  }

  /**
   * Validates password meets minimum length requirement
   * @param {string} password - The password to validate
   * @param {number} minLength - Minimum password length (default: 4)
   * @returns {boolean} - True if password is valid
   */
  const isValidPassword = (password, minLength = 4) => {
    if (!password || typeof password !== 'string') return false
    return password.length >= minLength
  }

  /**
   * Validates URL format
   * @param {string} url - The URL to validate
   * @returns {boolean} - True if URL is valid
   */
  const isValidURL = (url) => {
    if (!url || typeof url !== 'string') return false
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * Checks if a value is not empty
   * @param {*} value - The value to check
   * @returns {boolean} - True if value is not empty
   */
  const isRequired = (value) => {
    if (value === null || value === undefined) return false
    if (typeof value === 'string') return value.trim().length > 0
    return true
  }

  /**
   * Validates password confirmation match
   * @param {string} password - Original password
   * @param {string} confirmPassword - Confirmation password
   * @returns {boolean} - True if passwords match
   */
  const passwordsMatch = (password, confirmPassword) => {
    return password === confirmPassword
  }

  return {
    isValidEmail,
    isValidPassword,
    isValidURL,
    isRequired,
    passwordsMatch
  }
}
