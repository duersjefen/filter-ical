<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
    <!-- Header with gradient background matching calendar cards -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-4 sm:px-4 lg:px-6 py-4 sm:py-4 border-b border-gray-200 dark:border-gray-700"
      :class="expanded ? 'rounded-t-xl' : 'rounded-xl'"
    >
      <div 
        class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-3 sm:p-2 -m-3 sm:-m-2 transition-colors duration-200" 
        @click="$emit('toggle')"
      >
        <!-- Standardized dropdown arrow -->
        <svg 
          class="w-5 h-5 sm:w-4 sm:h-4 text-gray-400 transition-transform duration-300 flex-shrink-0"
          :class="{ 'rotate-90': expanded }"
          fill="currentColor" 
          viewBox="0 0 20 20"
        >
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
        </svg>
        
        <div class="flex-1 min-w-0">
          <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-1 sm:mb-2">
            {{ icon }} {{ title }}
          </h3>
          <p class="text-sm sm:text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {{ subtitle }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- Expandable Content -->
    <div v-if="expanded" class="p-3 sm:p-4 space-y-4">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminCardWrapper',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    expanded: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle']
}
</script>