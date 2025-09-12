<template>
  <div v-if="categories.length > 0" class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px;">
      <h3 style="margin: 0;">📂 Select Event Categories</h3>
      <div class="category-actions">
        <div class="basic-actions">
          <button @click="$emit('clear-all')" class="btn btn-secondary">Clear All</button>
          <button @click="$emit('select-all')" class="btn">Select All</button>
        </div>
      </div>
    </div>

    <!-- Category Search -->
    <div style="margin-bottom: 20px;">
      <input 
        :value="searchTerm"
        @input="$emit('update:search-term', $event.target.value)"
        type="text" 
        placeholder="🔍 Search categories..."
        class="form-control"
        style="width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px;"
      />
    </div>
    
    <!-- Main Categories (2+ events) -->
    <div class="category-cards">
      <div 
        v-for="category in mainCategories" 
        :key="category.name" 
        class="category-card"
        :class="{ 'selected': selectedCategories.includes(category.name), 'expanded': expandedCategories.includes(category.name) }"
        @click="$emit('toggle-category', category.name)"
      >
        <div class="category-card-header">
          <div class="category-info">
            <strong>{{ category.name }}</strong>
            <span class="event-count">{{ category.count }} events</span>
          </div>
          <div class="category-actions">
            <div class="selected-check">
              <span v-if="selectedCategories.includes(category.name)">✓</span>
            </div>
            <button 
              @click.stop="$emit('toggle-expansion', category.name)"
              class="expand-btn"
              :class="{ 'expanded': expandedCategories.includes(category.name) }"
            >
              {{ expandedCategories.includes(category.name) ? '▼' : '▶' }}
            </button>
          </div>
        </div>
        
        <!-- Expandable Events List -->
        <div v-if="expandedCategories.includes(category.name)" class="category-events">
          <div class="events-list">
            <div 
              v-for="event in category.events.slice(0, 5)" 
              :key="event.uid"
              class="event-item"
            >
              <div class="event-summary">{{ event.summary }}</div>
              <div class="event-date">📅 {{ formatDateTime(event.dtstart) }}</div>
              <div v-if="event.location" class="event-location">📍 {{ event.location }}</div>
            </div>
            <div v-if="category.events.length > 5" class="more-events">
              ... and {{ category.events.length - 5 }} more events
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Single Event Categories (Collapsible) -->
    <div v-if="singleCategories.length > 0" class="single-events-section">
      <div class="single-events-header">
        <div class="section-left" @click="$emit('toggle-singles-visibility')">
          <div class="section-info">
            <strong>📄 Individual Events</strong>
            <span class="section-count">{{ singleCategories.length }} unique events</span>
          </div>
          <button class="section-toggle" :class="{ 'expanded': showSingleEvents }">
            {{ showSingleEvents ? '▼' : '▶' }}
          </button>
        </div>
        <div class="singles-actions">
          <button @click.stop="$emit('select-all-singles')" class="btn-small" title="Select all individual events">
            ✓ All
          </button>
          <button @click.stop="$emit('clear-all-singles')" class="btn-small btn-secondary" title="Deselect all individual events">
            ✗ None
          </button>
        </div>
      </div>
      
      <div v-if="showSingleEvents" class="single-events-grid">
        <div 
          v-for="category in singleCategories" 
          :key="category.name"
          class="single-event-item"
          :class="{ 'selected': selectedCategories.includes(category.name) }"
          @click="$emit('toggle-category', category.name)"
        >
          <div class="single-event-content">
            <div class="single-event-title">{{ category.name }}</div>
            <div class="single-event-datetime">{{ formatDateTime(category.events[0].dtstart) }}</div>
            <div v-if="category.events[0].location" class="single-event-location">📍 {{ category.events[0].location }}</div>
          </div>
          <div class="selected-check">
            <span v-if="selectedCategories.includes(category.name)">✓</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Generate iCal -->
    <div v-if="selectedCategories.length > 0" class="ical-generator">
      <div class="ical-header">
        <h4>📥 Create Filtered Calendar</h4>
        <div class="filter-type-toggle">
          <label class="toggle-label">Filter Mode:</label>
          <div class="toggle-buttons">
            <button 
              class="toggle-btn" 
              :class="{ active: filterMode === 'include' }" 
              @click="$emit('switch-filter-mode', 'include')"
            >
              ✅ Include Only
            </button>
            <button 
              class="toggle-btn" 
              :class="{ active: filterMode === 'exclude' }" 
              @click="$emit('switch-filter-mode', 'exclude')"
            >
              ❌ Exclude These
            </button>
          </div>
        </div>
      </div>
      
      <div class="filter-summary">
        <div class="summary-info">
          <span class="summary-text">
            {{ filterMode === 'include' 
              ? `Including ${selectedCategories.length} categories with ${selectedCategoriesCount} events` 
              : `Excluding ${selectedCategories.length} categories (removing ${selectedCategoriesCount} events)` 
            }}
          </span>
        </div>
        <div class="category-tags">
          <span 
            v-for="category in selectedCategories.slice(0, 3)" 
            :key="category" 
            class="category-tag"
            :class="filterMode"
          >
            {{ category }}
          </span>
          <span v-if="selectedCategories.length > 3" class="more-tag">
            +{{ selectedCategories.length - 3 }} more
          </span>
        </div>
      </div>
      
      <div class="ical-actions">
        <button @click="$emit('generate-ical')" class="btn-download">
          📥 Download Filtered Calendar
        </button>
        <button @click="$emit('toggle-preview')" class="btn-preview">
          {{ showPreview ? 'Hide Preview' : '👀 Preview Events' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  categories: Array,
  mainCategories: Array,
  singleCategories: Array,
  selectedCategories: Array,
  expandedCategories: Array,
  showSingleEvents: Boolean,
  searchTerm: String,
  filterMode: String,
  selectedCategoriesCount: Number,
  showPreview: Boolean,
  formatDateTime: Function
})

defineEmits([
  'clear-all',
  'select-all', 
  'update:search-term',
  'toggle-category',
  'toggle-expansion',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles',
  'switch-filter-mode',
  'generate-ical',
  'toggle-preview'
])
</script>