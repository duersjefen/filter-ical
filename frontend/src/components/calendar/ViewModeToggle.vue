<template>
  <!-- Compact View Mode Toggle -->
  <div class="flex items-center justify-center mb-4">
    <div class="bg-gray-100 dark:bg-gray-700 rounded-lg p-1 flex">
      <!-- Groups Button -->
      <button
        @click="$emit('update:view-mode', 'groups')"
        class="px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2"
        :class="viewMode === 'groups' 
          ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm' 
          : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'"
        :disabled="!hasGroups"
        :title="hasGroups ? 'Organize events by logical groups' : 'No groups available for this calendar'"
      >
        <span>📁</span>
        <span class="hidden sm:inline">Groups</span>
        <span v-if="!hasGroups" class="text-xs opacity-60">(N/A)</span>
      </button>

      <!-- Types Button -->
      <button
        @click="$emit('update:view-mode', 'types')"
        class="px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 flex items-center gap-2"
        :class="viewMode === 'types' 
          ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm' 
          : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'"
      >
        <span>📂</span>
        <span class="hidden sm:inline">Types</span>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  viewMode: { 
    type: String, 
    required: true,
    validator: value => ['groups', 'types'].includes(value)
  },
  hasGroups: { type: Boolean, default: false }
})

defineEmits([
  'update:view-mode'
])
</script>