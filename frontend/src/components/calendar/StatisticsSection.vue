<template>
  <!-- Enhanced Statistics -->
  <div class="statistics">
    <div class="stat-card">
      <h3>{{ statistics.totalEvents }}</h3>
      <p>Total Events</p>
    </div>
    <div class="stat-card">
      <h3>{{ categories.length }}</h3>
      <p>Categories</p>
    </div>
    <div class="stat-card">
      <h3>{{ mainCategoriesCount }}</h3>
      <p>Multi-Event</p>
    </div>
    <div class="stat-card">
      <h3>{{ singleCategoriesCount }}</h3>
      <p>Unique Events</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  statistics: Object,
  categories: Array,
  mainCategoriesCount: Number,
  singleCategoriesCount: Number
})
</script>