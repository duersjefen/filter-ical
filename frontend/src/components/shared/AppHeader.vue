<template>
  <div class="relative mb-6 sm:mb-8 py-4 sm:py-6 px-4 sm:px-6 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 dark:from-slate-800 dark:via-slate-900 dark:to-black text-white rounded-lg shadow-lg">
    
    <!-- Top Controls Row - Desktop -->
    <div class="hidden sm:flex justify-between items-center mb-4 sm:mb-6">
      <!-- Left Control - Fixed width to balance right side -->
      <div class="w-24 sm:w-28 flex justify-start">
        <!-- Back Navigation -->
        <div v-if="showBackButton">
          <button 
            @click="$emit('navigate-back')" 
            class="w-8 h-8 sm:w-9 sm:h-9 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-md flex items-center justify-center group"
            :title="backButtonText"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:text-white/90 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
        </div>
        <!-- Empty space on home page to maintain layout balance -->
        <div v-else class="w-8 h-8 sm:w-9 sm:h-9"></div>
      </div>

      <!-- Center Username Control -->
      <div class="flex-1 flex justify-center">
        <!-- Editing Mode -->
        <div v-if="isEditing" class="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg shadow-md border border-white/30 dark:border-gray-600 px-2 py-1.5 sm:px-3 sm:py-2">
          <div class="flex items-center gap-1.5 sm:gap-2">
            <input
              ref="usernameInputRef"
              v-model="usernameInput"
              @keyup.enter="saveUsername"
              @keyup.escape="cancelEdit"
              @blur="saveUsername"
              type="text"
              class="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 px-2 py-1 rounded text-xs sm:text-sm w-24 sm:w-32 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400"
              :placeholder="$t('username.placeholder')"
              maxlength="20"
            />
            <button 
              @click="saveUsername"
              class="bg-blue-500 hover:bg-blue-600 text-white px-1.5 py-1 rounded text-xs font-medium transition-colors duration-200"
              :title="$t('common.save')"
            >
              ✓
            </button>
            <button 
              @click="cancelEdit"
              class="bg-gray-500 hover:bg-gray-600 text-white px-1.5 py-1 rounded text-xs font-medium transition-colors duration-200"
              :title="$t('common.cancel')"
            >
              ✕
            </button>
          </div>
        </div>
        
        <!-- Anonymous Mode -->
        <div 
          v-else-if="!hasCustomUsername()" 
          @click="startEdit"
          class="bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-lg shadow-md border border-white/20 px-2.5 py-1.5 sm:px-3 sm:py-2 cursor-pointer transition-all duration-300 hover:shadow-lg group"
        >
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-amber-400 rounded-full animate-pulse"></div>
            <span class="text-white text-xs sm:text-sm font-medium group-hover:text-white/90">
              {{ contextMessage }}
            </span>
            <svg class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-white/60 group-hover:text-white/80 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
          </div>
        </div>
        
        <!-- Personal Mode -->
        <div v-else class="bg-white/10 backdrop-blur-sm rounded-lg shadow-md border border-white/20 px-2.5 py-1.5 sm:px-3 sm:py-2">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-green-400 rounded-full"></div>
            <span class="text-white text-xs sm:text-sm font-medium">
              {{ username }}
            </span>
            <button 
              @click="startEdit"
              class="text-white/60 hover:text-white transition-colors duration-300 p-0.5 hover:bg-white/10 rounded"
              :title="$t('username.edit')"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
              </svg>
            </button>
            <button 
              @click="clearUsername"
              class="bg-white/20 hover:bg-white/30 text-white px-2 py-0.5 rounded text-xs font-medium transition-all duration-300 hover:shadow-md"
              :title="$t('username.logout')"
            >
              {{ $t('username.logout') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Right Control - Fixed width to balance left side -->
      <div class="w-24 sm:w-28 flex justify-end">
        <div class="flex items-center gap-2">
          <!-- Always show Language Toggle -->
          <LanguageToggle />
          
          <!-- Always show Dark Mode Toggle -->
          <button 
            @click="toggleDarkMode"
            class="group relative w-12 h-6 sm:w-14 sm:h-7 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-md"
            :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
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
              >
                <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
              </svg>
              
              <!-- Moon Icon (Dark Mode) -->
              <svg 
                v-else 
                class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-slate-700"
                fill="currentColor" 
                viewBox="0 0 24 24"
              >
                <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Layout (sm and below) - Clean stacked design -->
    <div class="sm:hidden">
      
      <!-- Back Button Row (if present) -->
      <div v-if="showBackButton" class="flex justify-start mb-3">
        <button 
          @click="$emit('navigate-back')" 
          class="w-11 h-11 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg flex items-center justify-center group touch-manipulation"
          :title="backButtonText"
        >
          <svg class="w-5 h-5 text-white group-hover:text-white/90 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
      </div>

      <!-- Title Section -->
      <div class="text-center mb-4">
        <h1 class="text-xl font-semibold mb-1">{{ title }}</h1>
        <p v-if="subtitle && !hideSubtitle" class="text-sm opacity-80 font-medium">{{ subtitle }}</p>
      </div>

      <!-- Controls Section - Language & Dark Mode -->
      <div class="flex justify-center items-center gap-6 mb-3">
        <LanguageToggle />
        
        <button 
          @click="toggleDarkMode"
          class="group relative w-16 h-8 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg touch-manipulation"
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

      <!-- Username Section - Prominent and centered -->
      <div class="flex justify-center px-4">
        <!-- Editing Mode -->
        <div v-if="isEditing" class="w-full max-w-sm bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 dark:border-gray-600 p-4">
          <div class="flex items-center gap-3">
            <input
              ref="usernameInputRef"
              v-model="usernameInput"
              @keyup.enter="saveUsername"
              @keyup.escape="cancelEdit"
              @blur="saveUsername"
              type="text"
              class="flex-1 bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 px-4 py-3 rounded-xl text-base focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 touch-manipulation"
              :placeholder="$t('username.placeholder')"
              maxlength="20"
            />
            <button 
              @click="saveUsername"
              class="w-11 h-11 bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white rounded-xl font-semibold transition-colors duration-200 shadow-md touch-manipulation"
              :title="$t('common.save')"
            >
              ✓
            </button>
            <button 
              @click="cancelEdit"
              class="w-11 h-11 bg-gray-500 hover:bg-gray-600 active:bg-gray-700 text-white rounded-xl font-semibold transition-colors duration-200 shadow-md touch-manipulation"
              :title="$t('common.cancel')"
            >
              ✕
            </button>
          </div>
        </div>
        
        <!-- Anonymous Mode -->
        <div 
          v-else-if="!hasCustomUsername()" 
          @click="startEdit"
          class="w-full max-w-sm bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-4 cursor-pointer transition-all duration-200 hover:shadow-xl group touch-manipulation"
        >
          <div class="flex items-center justify-center gap-3">
            <div class="w-3 h-3 bg-amber-400 rounded-full animate-pulse shadow-sm"></div>
            <span class="text-white text-base font-medium group-hover:text-white/90 text-center">
              {{ contextMessage }}
            </span>
            <svg class="w-4 h-4 text-white/60 group-hover:text-white/80 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
          </div>
        </div>
        
        <!-- Personal Mode -->
        <div v-else class="w-full max-w-sm bg-white/10 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 bg-green-400 rounded-full shadow-sm"></div>
              <span class="text-white text-base font-medium">
                {{ username }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <button 
                @click="startEdit"
                class="w-10 h-10 text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-200 flex items-center justify-center touch-manipulation"
                :title="$t('username.edit')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                </svg>
              </button>
              <button 
                @click="clearUsername"
                class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 shadow-md touch-manipulation"
                :title="$t('username.logout')"
              >
                {{ $t('username.logout') }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
    </div>

    <!-- Content Section (Desktop only) -->
    <div class="text-center hidden sm:block">
      <h1 class="text-xl sm:text-2xl lg:text-3xl font-semibold mb-1 sm:mb-2">{{ title }}</h1>
      <p v-if="subtitle && !hideSubtitle" class="text-sm sm:text-base opacity-80 font-medium" :class="{ 'mb-3 sm:mb-4': showUserInfo }">{{ subtitle }}</p>
    
    <!-- User info in header -->
    <div v-if="showUserInfo" class="mt-5 flex justify-center items-center">
      <div class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full border border-white/30 flex items-center gap-4">
        <span class="text-sm sm:text-base font-medium">{{ $t('common.welcome', { username: user?.username || user?.id || 'Guest' }) }}</span>
        <div class="w-px h-5 bg-white/30"></div>
        <button @click="$emit('logout')" class="text-white hover:text-white/80 text-sm font-semibold transition-all duration-300 hover:scale-105">
          {{ $t('navigation.logout') }}
        </button>
      </div>
    </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDarkMode } from '../../composables/useDarkMode'
import { useUsername } from '../../composables/useUsername'
import LanguageToggle from '../LanguageToggle.vue'

const { t } = useI18n()
const { isDarkMode, toggleDarkMode } = useDarkMode()
const { username, setUsername, clearUsername, hasCustomUsername, isValidUsername } = useUsername()

// Simple editing state
const isEditing = ref(false)
const usernameInput = ref('')
const usernameInputRef = ref(null)

// Context-aware message for anonymous mode
const contextMessage = computed(() => {
  if (props.pageContext === 'calendar') {
    return t('username.loginToSaveFilters')
  } else {
    return t('username.loginToSaveCalendars')
  }
})

// Start editing
const startEdit = async () => {
  isEditing.value = true
  usernameInput.value = username.value
  await nextTick()
  if (usernameInputRef.value) {
    usernameInputRef.value.focus()
    usernameInputRef.value.select()
  }
}

// Save username
const saveUsername = () => {
  const trimmed = usernameInput.value?.trim()
  
  if (trimmed && isValidUsername(trimmed)) {
    setUsername(trimmed)
    console.log(`Username set to: ${trimmed}`)
  } else if (!trimmed) {
    clearUsername()
    console.log('Username cleared - switched to public mode')
  }
  
  isEditing.value = false
}

// Cancel editing
const cancelEdit = () => {
  isEditing.value = false
  usernameInput.value = username.value
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
  },
  pageContext: {
    type: String,
    default: 'home' // 'home' or 'calendar'
  },
  hideSubtitle: {
    type: Boolean,
    default: false
  }
})

defineEmits(['logout', 'navigate-back'])
</script>