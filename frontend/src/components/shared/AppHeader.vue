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
        
        <!-- Username Control -->
        <div>
          <!-- Editing Mode -->
          <div v-if="isEditing" class="bg-white/95 dark:bg-gray-800/95 backdrop-blur-md rounded-xl shadow-lg border border-white/40 dark:border-gray-600 px-3 py-2 sm:px-4 sm:py-2.5">
            <div class="flex items-center gap-1.5 sm:gap-2">
              <input
                ref="desktopUsernameInputRef"
                v-model="usernameInput"
                @keyup.enter="saveUsername"
                @keyup.escape="cancelEdit"
                @blur="saveUsername"
                type="text"
                class="bg-white dark:bg-gray-700 border-2 border-blue-300 dark:border-blue-500 text-gray-900 dark:text-gray-100 px-3 py-2 rounded-xl text-sm w-32 sm:w-40 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 shadow-md transition-all duration-200"
                :placeholder="$t('ui.enterYourName')"
                maxlength="20"
                autocomplete="off"
              />
              <button 
                @click="saveUsername"
                class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white px-2 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 active:scale-95"
                :title="$t('common.save')"
              >
                ✓
              </button>
              <button 
                @click="cancelEdit"
                class="bg-gray-500 hover:bg-gray-600 active:bg-gray-700 text-white px-2 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 shadow-md hover:shadow-lg hover:scale-105 active:scale-95"
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
            class="bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 backdrop-blur-md rounded-xl shadow-lg border-2 border-blue-400/50 hover:border-blue-300/70 px-3 py-2 cursor-pointer transition-all duration-300 hover:shadow-xl hover:scale-105 group"
          >
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 bg-blue-300 rounded-full animate-pulse shadow-sm"></div>
              <span class="text-white text-xs sm:text-sm font-semibold group-hover:text-blue-100 drop-shadow-sm">
                {{ contextMessage }}
              </span>
              <div class="ml-1 px-2 py-0.5 bg-white/20 rounded-full">
                <span class="text-xs font-bold text-white">{{ $t('admin.click') }}</span>
              </div>
            </div>
          </div>
          
          <!-- Personal Mode -->
          <div v-else class="bg-white/10 backdrop-blur-md rounded-xl shadow-lg border border-white/20 px-3 py-2 sm:px-4 sm:py-2.5">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 bg-green-400 rounded-full"></div>
              <span class="text-white text-xs sm:text-sm font-medium">
                {{ username }}
              </span>
              <button 
                @click="startEdit"
                class="text-white/60 hover:text-white transition-all duration-300 p-1 hover:bg-white/10 rounded-lg hover:scale-110 active:scale-95"
                :title="$t('username.edit')"
              >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                </svg>
              </button>
              <button 
                @click="clearUsername"
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
        <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-white whitespace-nowrap tracking-tight drop-shadow-sm">{{ title }}</h1>
        <p v-if="subtitle && !hideSubtitle" class="text-sm sm:text-base opacity-85 font-medium text-white/90 whitespace-nowrap mt-1">{{ subtitle }}</p>
      </div>

      <!-- Right Side: Admin, Language & Dark Mode -->
      <div class="flex items-center gap-2 justify-self-end">
        <!-- Admin Panel Button (Domain views only, Desktop only) -->
        <button
          v-if="domainContext"
          @click="router.push(`/${domainContext.domain_key}/admin`)"
          class="hidden sm:flex w-9 h-9 sm:w-10 sm:h-10 bg-white/10 hover:bg-white/20 backdrop-blur-sm rounded-xl border border-white/20 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl items-center justify-center group hover:scale-105 active:scale-95"
          :title="$t('admin.adminPanel')"
        >
          <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white group-hover:text-white/90 transition-colors duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

    <!-- Mobile Layout (sm and below) - Single row top controls -->
    <div class="sm:hidden">
      
      <!-- Top Controls Row - Back Button + Toggles -->
      <div class="flex items-center justify-between mb-4">
        <!-- Left Side: Back Button -->
        <div class="flex items-center">
          <!-- Back Navigation -->
          <div v-if="showBackButton">
            <button 
              @click="$emit('navigate-back')" 
              class="w-10 h-10 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-xl border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl flex items-center justify-center group touch-manipulation hover:scale-105 active:scale-95"
              :title="backButtonText"
            >
              <svg class="w-4 h-4 text-white group-hover:text-white/90 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Right Side: Language & Dark Mode Toggles -->
        <div class="flex items-center gap-3">
          <LanguageToggle />
          
          <button 
            @click="toggleDarkMode"
            class="group relative w-12 h-6 bg-white/10 hover:bg-white/20 active:bg-white/30 backdrop-blur-sm rounded-full border border-white/20 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/30 shadow-lg hover:shadow-xl touch-manipulation hover:scale-105 active:scale-95"
            :title="isDarkMode ? $t('darkMode.switchToLight') : $t('darkMode.switchToDark')"
          >
            <!-- Toggle Track -->
            <div class="absolute inset-1 rounded-full bg-gradient-to-r from-blue-400 to-blue-500 dark:from-slate-600 dark:to-slate-700 transition-all duration-300"></div>
            
            <!-- Toggle Switch -->
            <div 
              class="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow-lg transform transition-all duration-300 flex items-center justify-center"
              :class="isDarkMode ? 'translate-x-6' : 'translate-x-0.5'"
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

      <!-- Title Section -->
      <div class="text-center mb-4">
        <h1 class="text-xl font-bold mb-1 tracking-tight drop-shadow-sm">{{ title }}</h1>
        <p v-if="subtitle && !hideSubtitle" class="text-sm opacity-85 font-medium text-white/90 mt-1">{{ subtitle }}</p>
      </div>

      <!-- Username Section - Below title -->
      <div class="flex justify-center">
        <!-- Editing Mode -->
        <div v-if="isEditing" class="bg-white/95 dark:bg-gray-800/95 backdrop-blur-md rounded-xl shadow-lg border border-white/40 dark:border-gray-600 px-4 py-3">
          <div class="flex items-center gap-2">
            <input
              ref="mobileUsernameInputRef"
              v-model="usernameInput"
              @keyup.enter="saveUsername"
              @keyup.escape="cancelEdit"
              @blur="saveUsername"
              type="text"
              class="bg-white dark:bg-gray-700 border-2 border-blue-300 dark:border-blue-500 text-gray-900 dark:text-gray-100 px-3 py-2 rounded-xl text-sm w-36 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20 touch-manipulation shadow-md transition-all duration-200"
              :placeholder="$t('ui.enterYourName')"
              maxlength="20"
              autocomplete="off"
            />
            <button 
              @click="saveUsername"
              class="w-9 h-9 bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white rounded-xl text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('common.save')"
            >
              ✓
            </button>
            <button 
              @click="cancelEdit"
              class="w-9 h-9 bg-gray-500 hover:bg-gray-600 active:bg-gray-700 text-white rounded-xl text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
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
          class="bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30 active:from-blue-500/40 active:to-purple-500/40 backdrop-blur-md rounded-xl shadow-lg border border-blue-400/50 hover:border-blue-300/70 px-5 py-4 cursor-pointer transition-all duration-200 group touch-manipulation hover:scale-105 active:scale-95"
        >
          <div class="flex items-center justify-center gap-2">
            <div class="w-2.5 h-2.5 bg-blue-300 rounded-full animate-pulse shadow-sm"></div>
            <span class="text-white text-sm font-semibold group-hover:text-blue-100 drop-shadow-sm">
              {{ contextMessage }}
            </span>
          </div>
        </div>
        
        <!-- Personal Mode -->
        <div v-else class="bg-white/10 backdrop-blur-md rounded-xl shadow-lg border border-white/20 px-4 py-3">
          <div class="flex items-center gap-3">
            <div class="w-2.5 h-2.5 bg-green-400 rounded-full shadow-sm"></div>
            <span class="text-white text-sm font-medium">
              {{ username }}
            </span>
            <button 
              @click="startEdit"
              class="w-9 h-9 text-white/60 hover:text-white hover:bg-white/10 rounded-xl transition-all duration-200 flex items-center justify-center touch-manipulation hover:scale-110 active:scale-95"
              :title="$t('username.edit')"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
              </svg>
            </button>
            <button 
              @click="clearUsername"
              class="bg-white/20 hover:bg-white/30 active:bg-white/40 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 shadow-md hover:shadow-lg touch-manipulation hover:scale-105 active:scale-95"
              :title="$t('username.logout')"
            >
              {{ $t('username.logout') }}
            </button>
          </div>
        </div>
      </div>
      
    </div>

    <!-- User info section for login views (Desktop only) -->
    <div v-if="showUserInfo" class="mt-5 flex justify-center items-center hidden sm:flex">
      <div class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full border border-white/30 flex items-center gap-4">
        <span class="text-sm sm:text-base font-medium">{{ $t('common.welcome', { username: user?.username || user?.id || 'Guest' }) }}</span>
        <div class="w-px h-5 bg-white/30"></div>
        <button @click="$emit('logout')" class="text-white hover:text-white/80 text-sm font-semibold transition-all duration-300 hover:scale-105">
          {{ $t('navigation.logout') }}
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useDarkMode } from '../../composables/useDarkMode'
import { useUsername } from '../../composables/useUsername'
import LanguageToggle from '../LanguageToggle.vue'

const { t } = useI18n()
const router = useRouter()
const { isDarkMode, toggleDarkMode } = useDarkMode()
const { username, setUsername, clearUsername, hasCustomUsername, isValidUsername } = useUsername()

// Simple editing state
const isEditing = ref(false)
const usernameInput = ref('')
const desktopUsernameInputRef = ref(null)
const mobileUsernameInputRef = ref(null)

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
  
  // Focus the appropriate input based on which one is rendered
  const focusInputs = () => {
    let focused = false
    
    // Try desktop input first
    if (desktopUsernameInputRef.value) {
      try {
        desktopUsernameInputRef.value.focus()
        desktopUsernameInputRef.value.select()
        focused = true
      } catch (e) {
        console.debug('Desktop input focus failed:', e)
      }
    }
    
    // Try mobile input if desktop didn't work
    if (!focused && mobileUsernameInputRef.value) {
      try {
        mobileUsernameInputRef.value.focus()
        mobileUsernameInputRef.value.select()
        focused = true
      } catch (e) {
        console.debug('Mobile input focus failed:', e)
      }
    }
    
    return focused
  }
  
  // Try immediately
  if (!focusInputs()) {
    // If that fails, try again after a short delay
    setTimeout(() => {
      focusInputs()
    }, 50)
  }
}

// Save username
const saveUsername = () => {
  const trimmed = usernameInput.value?.trim()
  
  if (trimmed && isValidUsername(trimmed)) {
    setUsername(trimmed)
  } else if (!trimmed) {
    clearUsername()
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
  },
  domainContext: {
    type: Object,
    default: null
  }
})

defineEmits(['logout', 'navigate-back'])
</script>