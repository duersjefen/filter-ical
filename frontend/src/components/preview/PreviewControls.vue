<template>
  <div class="px-3 sm:px-4 md:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
    <div class="flex justify-center">
      <!-- View Mode Buttons -->
      <div class="inline-flex bg-white dark:bg-gray-700 rounded-lg p-1 shadow-sm border border-gray-200 dark:border-gray-600">
        <button 
          @click="$emit('update:view-mode', 'list')"
          class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
          :class="viewMode === 'list' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-gray-800 dark:hover:text-gray-200'"
        >
          <span class="hidden sm:inline">📋 {{ $t('preview.list') }}</span>
          <span class="sm:hidden">📋</span>
        </button>
        
        <button 
          @click="$emit('update:view-mode', 'category')"
          class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
          :class="viewMode === 'category' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-gray-800 dark:hover:text-gray-200'"
        >
          <span class="hidden sm:inline">📂 {{ $t('preview.byRecurringEvent') }}</span>
          <span class="sm:hidden">📂</span>
        </button>
        
        <button 
          @click="$emit('update:view-mode', 'month')"
          class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
          :class="viewMode === 'month' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-gray-800 dark:hover:text-gray-200'"
        >
          <span class="hidden sm:inline">📅 {{ $t('preview.byMonth') }}</span>
          <span class="sm:hidden">📅</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  viewMode: { type: String, default: 'list', validator: value => ['list', 'category', 'month'].includes(value) }
})

const emit = defineEmits(['update:view-mode'])
</script>