<template>
  <footer v-if="shouldShowFooter" class="mt-1 mb-6">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Donation & Contact Section -->
      <div class="bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 dark:from-slate-800 dark:via-slate-900 dark:to-black rounded-lg shadow-lg border border-slate-500/20 dark:border-slate-700/30 p-3 sm:p-4">
        <div class="text-center">
          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4">
            <!-- Donation Button -->
            <a
              href="https://paypal.me/paissme"
              target="_blank"
              rel="noopener noreferrer"
              class="group inline-flex items-center justify-center gap-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 text-white px-5 sm:px-7 py-2.5 sm:py-3.5 rounded-lg font-semibold text-sm sm:text-base transition-all duration-300 hover:-translate-y-1 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-blue-500/30 shadow-lg"
            >
              <span class="text-base group-hover:scale-110 transition-transform duration-300">☕</span>
              <span>{{ $t('footer.donateButton', 'Support Server & Development Costs') }}</span>
              <svg
                class="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
            </a>

            <!-- Contact Button -->
            <router-link
              to="/contact"
              class="group inline-flex items-center justify-center gap-3 bg-gradient-to-r from-slate-500 to-slate-600 hover:from-slate-600 hover:to-slate-700 dark:from-slate-600 dark:to-slate-700 dark:hover:from-slate-700 dark:hover:to-slate-800 text-white px-5 sm:px-7 py-2.5 sm:py-3.5 rounded-lg font-semibold text-sm sm:text-base transition-all duration-300 hover:-translate-y-1 hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-slate-500/30 shadow-lg no-underline"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <span>{{ $t('footer.contactButton', 'Contact Us') }}</span>
            </router-link>
          </div>

          <!-- Optional: Small disclaimer -->
          <div class="mt-3 pt-3 border-t border-slate-500/20 dark:border-slate-700/30">
            <p class="text-xs text-slate-300 dark:text-slate-400 opacity-75">
              {{ $t('footer.paypalNotice', 'Secure payments via PayPal') }} •
              {{ $t('footer.voluntaryNotice', 'Completely voluntary') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Copyright/Info Section -->
      <div class="mt-3 text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ $t('footer.copyright') }} •
          <span class="text-gray-500 dark:text-gray-500">
            {{ $t('footer.madeWith') }}
          </span>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { API_BASE_URL } from '../../constants/api'

const route = useRoute()

const footerVisibility = ref('everywhere')

// Check if current route is an admin page
const isAdminPage = computed(() => {
  return route.path.includes('/admin')
})

// Determine if footer should be shown
const shouldShowFooter = computed(() => {
  if (footerVisibility.value === 'nowhere') {
    return false
  }
  if (footerVisibility.value === 'admin_only') {
    return isAdminPage.value
  }
  // 'everywhere'
  return true
})

// Load app settings
onMounted(async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/app-settings`)
    footerVisibility.value = response.data.footer_visibility
  } catch (error) {
    console.error('Failed to load app settings:', error)
    // Default to 'everywhere' on error
    footerVisibility.value = 'everywhere'
  }
})
</script>