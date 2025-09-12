<template>
  <!-- Enhanced Preview Events -->
  <div v-if="selectedCategories.length > 0 && showPreview" class="preview-events">
    <div class="preview-header">
      <h3>Preview Filtered Events ({{ sortedPreviewEvents.length }})</h3>
      <button @click="$emit('hide-preview')" class="close-preview-btn">Hide Preview</button>
    </div>
    
    <!-- Simplified Preview Controls -->
    <div class="preview-controls">
      <div class="control-group">
        <label>View:</label>
        <select :value="previewGroup" @change="$emit('update:preview-group', $event.target.value)" class="preview-select">
          <option value="none">📋 Simple List</option>
          <option value="category">📂 By Category</option>
          <option value="month">📅 By Month</option>
        </select>
      </div>
      <div class="control-group">
        <label>Sort:</label>
        <button 
          @click="$emit('toggle-preview-order')"
          class="order-btn"
          :class="previewOrder"
        >
          {{ previewOrder === 'asc' ? '📅 Oldest First' : '📅 Newest First' }}
        </button>
      </div>
    </div>
    
    <!-- Preview Content -->
    <div class="preview-content">
      <!-- No Grouping -->
      <div v-if="previewGroup === 'none'" class="events-list-preview">
        <div 
          v-for="event in sortedPreviewEvents.slice(0, previewLimit)" 
          :key="event.uid"
          class="preview-event-item"
        >
          <div class="event-main">
            <div class="event-title">{{ event.summary }}</div>
            <div class="event-meta">
              <span class="event-date">📅 {{ formatDateTime(event.dtstart) }}</span>
              <span class="event-category">📂 {{ getCategoryForEvent(event) }}</span>
              <span v-if="event.location" class="event-location">📍 {{ event.location }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Grouped Display -->
      <div v-else class="grouped-events">
        <div 
          v-for="group in groupedPreviewEvents" 
          :key="group.name"
          class="event-group"
        >
          <div class="group-header">
            <h4>{{ group.name }}</h4>
            <span class="group-count">{{ group.events.length }} events</span>
          </div>
          <div class="group-events">
            <div 
              v-for="event in group.events.slice(0, 5)" 
              :key="event.uid"
              class="preview-event-item"
            >
              <div class="event-main">
                <div class="event-title">{{ event.summary }}</div>
                <div class="event-meta">
                  <span class="event-date">📅 {{ formatDateTime(event.dtstart) }}</span>
                  <span v-if="previewGroup !== 'category'" class="event-category">📂 {{ getCategoryForEvent(event) }}</span>
                  <span v-if="event.location" class="event-location">📍 {{ event.location }}</span>
                </div>
              </div>
            </div>
            <div v-if="group.events.length > 5" class="more-events" style="margin-top: 12px;">
              ... and {{ group.events.length - 5 }} more events
            </div>
          </div>
        </div>
      </div>
      
      <!-- Show More Button -->
      <div v-if="sortedPreviewEvents.length > previewLimit" class="show-more">
        <button @click="$emit('increase-preview-limit')" class="show-more-btn">
          Show {{ Math.min(10, sortedPreviewEvents.length - previewLimit) }} more events
          ({{ sortedPreviewEvents.length - previewLimit }} remaining)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  selectedCategories: Array,
  showPreview: Boolean,
  sortedPreviewEvents: Array,
  previewGroup: String,
  previewOrder: String,
  previewLimit: Number,
  groupedPreviewEvents: Array,
  formatDateTime: Function,
  getCategoryForEvent: Function
})

defineEmits([
  'hide-preview',
  'update:preview-group',
  'toggle-preview-order',
  'increase-preview-limit'
])
</script>