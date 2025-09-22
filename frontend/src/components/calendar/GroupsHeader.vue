<template>
  <div class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-6 py-4 border-b">
    <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">🏷️ Event Groups</h3>
    <p class="text-sm text-gray-600 dark:text-gray-400">
      {{ selectionSummary.selected > 0
        ? selectionSummary.text
        : 'Subscribe to groups or select specific event types' }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  selectionSummary: {
    type: Object,
    required: true,
    default: () => ({ selected: 0, total: 0, text: '0 of 0 events selected' })
  }
})
</script>