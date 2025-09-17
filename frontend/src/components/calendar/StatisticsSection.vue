<template>
  <!-- Statistics -->
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 mb-4">
    <div class="bg-gradient-to-r from-slate-100 to-slate-50 px-4 sm:px-6 py-4 border-b border-gray-200">
      <h3 class="text-lg font-semibold text-gray-800">📊 Calendar Statistics</h3>
    </div>
    <div class="p-4">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl sm:text-3xl font-bold text-blue-600 mb-1">{{ statistics.totalEvents }}</div>
          <div class="text-sm text-gray-600 font-medium">Total Events</div>
        </div>
        <div class="text-center">
          <div class="text-2xl sm:text-3xl font-bold text-emerald-600 mb-1">{{ selectedEventsCount }}</div>
          <div class="text-sm text-gray-600 font-medium">Selected Events</div>
        </div>
        <div class="text-center">
          <div class="text-2xl sm:text-3xl font-bold text-purple-600 mb-1">{{ eventTypes.length }}</div>
          <div class="text-sm text-gray-600 font-medium">Available Categories</div>
        </div>
        <div class="text-center">
          <div class="text-2xl sm:text-3xl font-bold text-orange-600 mb-1">{{ selectedCategoriesCount }}</div>
          <div class="text-sm text-gray-600 font-medium">Selected Categories</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  statistics: Object,
  categories: Array,
  selectedEventsCount: Number,
  selectedCategoriesCount: Number
})
</script>