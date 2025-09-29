<template>
  <div 
    class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
    :class="isCollapsed ? 'rounded-xl' : 'rounded-t-xl'"
  >
    <!-- Mobile Layout -->
    <div class="block sm:hidden">
      <div class="flex items-center justify-between mb-3">
        <div class="flex-1">
          <h3 class="text-2xl font-black text-gray-900 dark:text-gray-100 tracking-tight">
            🏷️ <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('admin.groups') }}</span>
          </h3>
        </div>
        <!-- Mobile Switch Button - Enhanced Modern Design -->
        <button
          @click="$emit('switch-to-types')"
          class="group relative px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-2 transform hover:scale-105 active:scale-95"
          :title="$t('ui.switchToEventsView')"
        >
          <!-- Switch Icon -->
          <div class="flex items-center justify-center w-6 h-6 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors duration-200">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </div>
          
          <!-- Switch Text -->
          <div class="text-xs font-bold text-white">
            Events
          </div>
        </button>
      </div>
      <!-- Enhanced status text on mobile -->
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 text-center leading-tight mt-2">
        {{ selectionSummary.selected > 0
          ? translatedSummaryText
          : $t('status.subscribeToGroupsOrSelectEvents') }}
      </p>
    </div>

    <!-- Desktop Layout -->
    <div class="hidden sm:flex items-center justify-between">
      <!-- Left: Header Info with collapse button -->
      <div class="flex items-center gap-3 flex-1 cursor-pointer" @click="$emit('toggle-collapse')">
        <!-- Dropdown Icon -->
        <svg 
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': !isCollapsed }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
        
        <div class="flex-1">
          <h3 class="text-2xl sm:text-3xl font-black text-gray-900 dark:text-gray-100 mb-2 tracking-tight">
            🏷️ <span class="bg-gradient-to-r from-gray-700 to-gray-600 dark:from-gray-300 dark:to-gray-200 bg-clip-text text-transparent">{{ $t('admin.groups') }}</span>
          </h3>
          <p class="text-base font-medium text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ selectionSummary.selected > 0
              ? translatedSummaryText
              : $t('status.subscribeToGroupsOrSelectEvents') }}
          </p>
        </div>
      </div>
      
      <!-- Desktop Switch Button - Enhanced Modern Design -->
      <button
        @click="$emit('switch-to-types')"
        class="group relative px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 ml-4 transform hover:scale-105 active:scale-95"
        :title="$t('ui.switchToEventsView')"
      >
        <!-- Switch Icon -->
        <div class="flex items-center justify-center w-8 h-8 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors duration-200">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </div>
        
        <!-- Switch Text -->
        <div class="text-left">
          <div class="text-sm font-bold text-white mb-0.5">
            {{ $t('ui.switchToEventsView') }}
          </div>
          <div class="text-xs text-purple-100">
            {{ $t('ui.browseByEventTypes') }}
          </div>
        </div>
        
        <!-- Arrow Icon -->
        <svg class="w-5 h-5 text-white group-hover:translate-x-1 transition-transform duration-200" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  selectionSummary: {
    type: Object,
    required: true,
    default: () => ({ selected: 0, total: 0, text: '0 of 0 events selected' })
  },
  isCollapsed: {
    type: Boolean,
    default: false
  }
})

// Helper to translate text if it's a translation key
const translatedSummaryText = computed(() => {
  const text = props.selectionSummary.compactText || props.selectionSummary.text
  if (text && text.startsWith('common.')) {
    return t(text)
  }
  return text
})

defineEmits([
  'switch-to-types',
  'toggle-collapse'
])
</script>