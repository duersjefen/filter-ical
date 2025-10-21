<template>
  <div class="relative mb-6 sm:mb-8 py-6 sm:py-8 px-4 sm:px-6 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 dark:from-slate-800 dark:via-slate-900 dark:to-black text-white rounded-xl shadow-xl border border-slate-500/20 dark:border-slate-700/30 backdrop-blur-sm">
    
    <!-- Desktop: Single row layout with Back + Username + Title + Right Controls -->
    <div class="hidden sm:grid sm:grid-cols-3 sm:gap-4 items-center">
      <!-- Left Side: Back Button + Username Control -->
      <div class="flex items-center gap-3 sm:gap-4 justify-self-start">
        <!-- Back Navigation -->
        <div v-if="showBackButton">
          <button 
            @click="$emit('navigate-back')" 
            class="w-9 h-9 sm:w-10 sm:h-10 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-xl border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl flex items-center justify-center group hover:scale-105 active:scale-95"
            :title="backButtonText"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:text-white/90 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
        </div>
        
        <!-- Auth Control -->
        <div>
          <!-- Not Logged In -->
          <button
            v-if="!isLoggedIn"
            @click="navigateToLogin"
            class="bg-white/15 hover:bg-white/25 backdrop-blur-md rounded-xl shadow-lg border border-white/30 hover:border-white/40 px-4 py-2.5 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 active:scale-95 group"
          >
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 text-white transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
              </svg>
              <span class="text-white text-sm font-semibold drop-shadow-sm whitespace-nowrap">
                {{ contextMessage }}
              </span>
            </div>
          </button>

          <!-- Logged In Without Password -->
          <div v-else-if="!hasPassword" class="bg-yellow-500/20 backdrop-blur-md rounded-xl shadow-lg border border-yellow-400/40 px-3 py-2 sm:px-4 sm:py-2.5">
            <div class="flex items-center gap-2">
              <span class="text-lg">🔓</span>
              <span class="text-white text-xs sm:text-sm font-medium">
                {{ user.username }}
              </span>
              <span class="text-yellow-300 text-xs font-semibold">{{ $t('username.unsecured') }}</span>
              <button
                @click="navigateToProfile"
                class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-2 py-1 rounded-lg text-xs font-medium transition-all duration-300 hover:shadow-md hover:scale-105 active:scale-95"
                :title="$t('username.profileButton')"
              >
                {{ $t('username.profileButton') }}
              </button>
              <button
                @click="handleLogout"
                class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-2 py-1 rounded-lg text-xs font-medium transition-all duration-300 hover:shadow-md hover:scale-105 active:scale-95"
                :title="$t('username.logout')"
              >
                {{ $t('username.logout') }}
              </button>
            </div>
          </div>

          <!-- Logged In With Password -->
          <div v-else class="bg-green-500/20 backdrop-blur-md rounded-xl shadow-lg border border-green-400/40 px-3 py-2 sm:px-4 sm:py-2.5">
            <div class="flex items-center gap-2">
              <span class="text-lg">🔒</span>
              <span class="text-white text-xs sm:text-sm font-medium">
                {{ user.username }}
              </span>
              <button
                @click="navigateToProfile"
                class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-2 py-1 rounded-lg text-xs font-medium transition-all duration-300 hover:shadow-md hover:scale-105 active:scale-95"
                :title="$t('username.profileButton')"
              >
                {{ $t('username.profileButton') }}
              </button>
              <button
                @click="handleLogout"
                class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-2 py-1 rounded-lg text-xs font-medium transition-all duration-300 hover:shadow-md hover:scale-105 active:scale-95"
                :title="$t('username.logout')"
              >
                {{ $t('username.logout') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Center: Title (perfectly centered) -->
      <div class="text-center justify-self-center">
        <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-white whitespace-nowrap tracking-tight drop-shadow-lg">{{ title }}</h1>
        <div v-if="subtitle && !hideSubtitle" class="inline-block mt-2 px-4 py-1.5 bg-white/15 backdrop-blur-md rounded-xl border border-white/30 shadow-lg">
          <p class="text-[10px] sm:text-xs font-medium text-white/95 tracking-normal leading-snug whitespace-pre-line text-center max-w-2xl">{{ subtitle }}</p>
        </div>
      </div>

      <!-- Right Side: Admin, Language & Dark Mode -->
      <div class="flex items-center gap-2 justify-self-end">
        <!-- Admin Panel Button (Domain views only, Desktop only) -->
        <button
          v-if="domainContext"
          @click="router.push(`/${domainContext.domain_key}/admin`)"
          class="hidden sm:flex w-11 h-11 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-xl border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl items-center justify-center group hover:scale-105 active:scale-95"
          :title="$t('domainAdmin.adminPanel')"
          :aria-label="$t('domainAdmin.adminPanel')"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:text-white/90 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </button>
        
        <!-- Always show Language Toggle -->
        <LanguageToggle />
        
        <!-- Always show Dark Mode Toggle -->
        <button
          @click="toggleDarkMode"
          class="group relative w-12 h-6 sm:w-14 sm:h-7 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
          :title="isDarkMode ? $t('darkMode.switchToLight') : $t('darkMode.switchToDark')"
          :aria-label="isDarkMode ? $t('darkMode.switchToLight') : $t('darkMode.switchToDark')"
          :aria-pressed="isDarkMode"
          role="switch"
        >
          <!-- Toggle Track -->
          <div class="absolute inset-1 rounded-full bg-gradient-to-r from-blue-400 to-blue-500 dark:from-slate-600 dark:to-slate-700 transition-all duration-300"></div>
          
          <!-- Toggle Switch -->
          <div 
            class="absolute top-0.5 w-4 h-4 sm:w-5 sm:h-5 bg-white rounded-full shadow-lg transform transition-all duration-300 flex items-center justify-center"
            :class="isDarkMode ? 'translate-x-6 sm:translate-x-7' : 'translate-x-1'"
          >
            <!-- Sun Icon (Light Mode) -->
            <svg
              v-if="!isDarkMode"
              class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-yellow-500"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
            </svg>
            
            <!-- Moon Icon (Dark Mode) -->
            <svg
              v-else
              class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-slate-700"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
            </svg>
          </div>
        </button>
      </div>
    </div>

    <!-- Mobile Layout (sm and below) - Compact single row -->
    <div class="sm:hidden">

      <!-- Single Row: Back Button + Title + Toggles -->
      <div class="flex items-center justify-between gap-2 mb-4">
        <!-- Left Side: Back Button -->
        <div v-if="showBackButton" class="flex-shrink-0">
          <button
            @click="$emit('navigate-back')"
            class="w-9 h-9 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-lg border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg flex items-center justify-center group touch-manipulation active:scale-95"
            :title="backButtonText"
          >
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
        </div>

        <!-- Center: Title (flexible, can shrink) -->
        <div class="flex-1 min-w-0 text-center">
          <h1 class="text-base font-bold tracking-tight drop-shadow-lg truncate px-1">{{ title }}</h1>
        </div>

        <!-- Right Side: Language & Dark Mode Toggles -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <LanguageToggle />

          <button
            @click="toggleDarkMode"
            class="group relative w-11 h-6 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg touch-manipulation active:scale-95"
            :title="isDarkMode ? $t('darkMode.switchToLight') : $t('darkMode.switchToDark')"
          >
            <!-- Toggle Track -->
            <div class="absolute inset-1 rounded-full bg-gradient-to-r from-blue-400 to-blue-500 dark:from-slate-600 dark:to-slate-700 transition-all duration-300"></div>

            <!-- Toggle Switch -->
            <div
              class="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow-lg transform transition-all duration-300 flex items-center justify-center"
              :class="isDarkMode ? 'translate-x-5' : 'translate-x-0.5'"
            >
              <!-- Sun Icon (Light Mode) -->
              <svg
                v-if="!isDarkMode"
                class="w-3 h-3 text-yellow-500"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
              </svg>

              <!-- Moon Icon (Dark Mode) -->
              <svg
                v-else
                class="w-3 h-3 text-slate-700"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
              </svg>
            </div>
          </button>
        </div>
      </div>

      <!-- Subtitle (if present) -->
      <div v-if="subtitle && !hideSubtitle" class="text-center mb-4">
        <div class="inline-block px-4 py-1.5 bg-white/15 backdrop-blur-md rounded-xl border border-white/30 shadow-lg">
          <p class="text-xs font-medium text-white/95 tracking-normal leading-snug whitespace-pre-line max-w-md">{{ subtitle }}</p>
        </div>
      </div>

      <!-- Auth Section - Below title -->
      <div class="flex justify-center">
        <!-- Not Logged In -->
        <button
          v-if="!isLoggedIn"
          @click="navigateToLogin"
          class="bg-white/15 hover:bg-white/25 active:bg-white/30 backdrop-blur-md rounded-xl shadow-lg border border-white/30 hover:border-white/40 px-6 py-3.5 cursor-pointer transition-all duration-200 group touch-manipulation hover:scale-105 active:scale-95"
        >
          <div class="flex items-center justify-center gap-3">
            <svg class="w-5 h-5 text-white transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/>
            </svg>
            <span class="text-white text-base font-semibold drop-shadow-sm">
              {{ contextMessage }}
            </span>
          </div>
        </button>

        <!-- Logged In Without Password -->
        <div v-else-if="!hasPassword" class="bg-yellow-500/20 backdrop-blur-md rounded-xl shadow-lg border border-yellow-400/40 px-4 py-3">
          <div class="flex items-center gap-3">
            <span class="text-xl">🔓</span>
            <span class="text-white text-sm font-medium">
              {{ user.username }}
            </span>
            <span class="text-yellow-300 text-xs font-semibold">{{ $t('username.unsecured') }}</span>
            <button
              @click="navigateToProfile"
              class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('username.profileButton')"
            >
              {{ $t('username.profileButton') }}
            </button>
            <button
              @click="handleLogout"
              class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('username.logout')"
            >
              {{ $t('username.logout') }}
            </button>
          </div>
        </div>

        <!-- Logged In With Password -->
        <div v-else class="bg-green-500/20 backdrop-blur-md rounded-xl shadow-lg border border-green-400/40 px-4 py-3">
          <div class="flex items-center gap-3">
            <span class="text-xl">🔒</span>
            <span class="text-white text-sm font-medium">
              {{ user.username }}
            </span>
            <button
              @click="navigateToProfile"
              class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('username.profileButton')"
            >
              {{ $t('username.profileButton') }}
            </button>
            <button
              @click="handleLogout"
              class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('username.logout')"
            >
              {{ $t('username.logout') }}
            </button>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useDarkMode } from '../../composables/useDarkMode'
import { useAuth } from '../../composables/useAuth'
import LanguageToggle from '../LanguageToggle.vue'

const { t } = useI18n()
const router = useRouter()
const { isDarkMode, toggleDarkMode } = useDarkMode()
const { user, isLoggedIn, hasPassword, logout } = useAuth()

// Context-aware message for anonymous mode
const contextMessage = computed(() => {
  if (props.pageContext === 'calendar') {
    return t('username.loginToSaveFilters')
  } else {
    return t('username.loginToSaveCalendars')
  }
})

// Navigate to login page
const navigateToLogin = () => {
  router.push('/login')
}

// Navigate to profile page
const navigateToProfile = () => {
  router.push('/profile')
}

// Handle logout
const handleLogout = () => {
  logout()
}

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backButtonText: {
    type: String,
    default: '← Back'
  },
  pageContext: {
    type: String,
    default: 'home' // 'home' or 'calendar'
  },
  hideSubtitle: {
    type: Boolean,
    default: false
  },
  domainContext: {
    type: Object,
    default: null
  }
})

defineEmits(['navigate-back'])
</script>