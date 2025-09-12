import { ref, watch, onMounted } from 'vue'

// Global reactive state
const isDarkMode = ref(false)
let initialized = false

// Initialize dark mode on first load
const init = () => {
  if (initialized || typeof window === 'undefined') return
  
  // Check localStorage first, then system preference
  const stored = localStorage.getItem('darkMode')
  if (stored !== null) {
    isDarkMode.value = JSON.parse(stored)
  } else {
    isDarkMode.value = window.matchMedia?.('(prefers-color-scheme: dark)').matches || false
  }
  
  // Apply initial theme
  updateTheme()
  initialized = true
}

// Update the DOM with current theme
const updateTheme = () => {
  if (typeof document === 'undefined') return
  
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

// Toggle between light and dark mode
const toggleDarkMode = () => {
  if (!initialized) init()
  isDarkMode.value = !isDarkMode.value
}

// Watch for changes and update localStorage + DOM
watch(isDarkMode, (newValue) => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('darkMode', JSON.stringify(newValue))
  }
  updateTheme()
})

// Initialize immediately if in browser
if (typeof window !== 'undefined') {
  init()
}

// Force light mode (for debugging)
const forceLight = () => {
  isDarkMode.value = false
  localStorage.removeItem('darkMode')
  updateTheme()
}

export function useDarkMode() {
  onMounted(() => {
    if (!initialized) init()
  })

  return {
    isDarkMode,
    toggleDarkMode,
    forceLight
  }
}