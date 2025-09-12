<template>
  <div class="relative text-center mb-8 sm:mb-10 py-8 sm:py-10 px-4 sm:px-6 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 dark:from-slate-800 dark:via-slate-900 dark:to-black text-white rounded-lg shadow-lg">
    <!-- Language Toggle - Top Left Corner -->
    <div class="absolute top-4 left-4 sm:top-6 sm:left-6">
      <LanguageToggle />
    </div>

    <!-- Dark Mode Toggle - Top Right Corner -->
    <div class="absolute top-4 right-4 sm:top-6 sm:right-6">
      <!-- Dark Mode Toggle -->
      <button 
        @click="toggleDarkMode"
        class="group relative w-16 h-8 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg"
        :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
      >
        <!-- Toggle Track -->
        <div class="absolute inset-1 rounded-full bg-gradient-to-r from-blue-400 to-blue-500 dark:from-slate-600 dark:to-slate-700 transition-all duration-300"></div>
        
        <!-- Toggle Switch -->
        <div 
          class="absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg transform transition-all duration-300 flex items-center justify-center"
          :class="isDarkMode ? 'translate-x-8' : 'translate-x-1'"
        >
          <!-- Sun Icon (Light Mode) -->
          <svg 
            v-if="!isDarkMode" 
            class="w-3.5 h-3.5 text-yellow-500"
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
          </svg>
          
          <!-- Moon Icon (Dark Mode) -->
          <svg 
            v-else 
            class="w-3.5 h-3.5 text-slate-700"
            fill="currentColor" 
            viewBox="0 0 24 24"
          >
            <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
          </svg>
        </div>
      </button>
    </div>

    <h1 class="text-2xl sm:text-3xl lg:text-4xl font-light mb-2">{{ title }}</h1>
    <p class="text-base sm:text-lg opacity-90" :class="{ 'mb-4 sm:mb-5': showUserInfo }">{{ subtitle }}</p>
    
    <!-- User info in header -->
    <div v-if="showUserInfo" class="mt-5 flex justify-center items-center">
      <div class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full border border-white/30 flex items-center gap-4">
        <span class="text-sm sm:text-base font-medium">{{ $t('common.welcome', { username: user?.username }) }}</span>
        <div class="w-px h-5 bg-white/30"></div>
        <button @click="$emit('logout')" class="text-white hover:text-white/80 text-sm font-semibold transition-all duration-300 hover:scale-105">
          {{ $t('navigation.logout') }}
        </button>
      </div>
    </div>

    <!-- Navigation button -->
    <div v-if="showBackButton" class="mt-5">
      <button @click="$emit('navigate-back')" class="px-6 sm:px-8 py-2.5 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg text-sm sm:text-base">
        {{ backButtonText }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useDarkMode } from '../../composables/useDarkMode'
import LanguageToggle from '../LanguageToggle.vue'

const { isDarkMode, toggleDarkMode } = useDarkMode()

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  user: {
    type: Object,
    default: null
  },
  showUserInfo: {
    type: Boolean,
    default: false
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backButtonText: {
    type: String,
    default: '← Back'
  }
})

defineEmits(['logout', 'navigate-back'])
</script>