<template>
  <footer v-if="shouldShowFooter" class="mt-8 mb-6">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Donation & Contact Section -->
      <div class="text-center space-y-4">
        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row justify-center gap-3">
          <!-- Donation Button -->
          <a
            href="https://paypal.me/paissme"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            <span>☕</span>
            <span>{{ $t('footer.donateButton', 'Support Development') }}</span>
          </a>

          <!-- Contact Button -->
          <router-link
            to="/contact"
            class="inline-flex items-center justify-center gap-2 bg-gray-600 hover:bg-gray-700 dark:bg-gray-600 dark:hover:bg-gray-700 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500/50 no-underline"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span>{{ $t('footer.contactButton', 'Contact Us') }}</span>
          </router-link>
        </div>

        <!-- Small disclaimer -->
        <p class="text-xs text-gray-600 dark:text-gray-400">
          {{ $t('footer.paypalNotice', 'Help keep this service running') }} •
          {{ $t('footer.voluntaryNotice', 'Your support is appreciated') }}
        </p>
      </div>

      <!-- Built by paiss Section -->
      <div class="mt-4 text-center">
        <a
          href="https://paiss.me"
          target="_blank"
          rel="noopener noreferrer"
          class="group inline-flex items-center gap-2.5 px-5 py-2.5 rounded-full bg-gradient-to-r from-slate-100/50 to-slate-200/50 dark:from-slate-800/50 dark:to-slate-700/50 hover:from-slate-200/80 hover:to-slate-300/80 dark:hover:from-slate-700/80 dark:hover:to-slate-600/80 border border-slate-300/30 dark:border-slate-600/30 transition-all duration-300 hover:shadow-md hover:-translate-y-0.5"
          aria-label="Visit paiss.me to get your own website built"
        >
          <span class="text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wide">Built by</span>
          <img
            src="https://paiss.me/logo-for-external-use.svg"
            alt="paiss"
            class="h-6 group-hover:scale-105 transition-transform duration-300"
          />
          <span class="mx-1 text-slate-400 dark:text-slate-500">•</span>
          <span class="text-sm font-semibold text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100 transition-colors">
            Want your own?
          </span>
          <svg
            class="w-4 h-4 text-slate-600 dark:text-slate-400 group-hover:translate-x-1 transition-transform duration-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </a>
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