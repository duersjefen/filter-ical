<template>
  <div v-if="categories.length > 0" class="bg-white rounded-xl shadow-lg border border-gray-200 mb-4 overflow-hidden">
    <!-- Collapsible Header -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 cursor-pointer hover:bg-slate-100 transition-colors duration-200"
      :class="showCategoriesSection ? 'rounded-t-xl' : 'rounded-xl'"
      @click="showCategoriesSection = !showCategoriesSection"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-bold text-gray-900">📂 Event Categories</h3>
          <button class="flex-shrink-0 p-2 rounded-full bg-white/50 hover:bg-white transition-all duration-200">
            <svg 
              class="w-5 h-5 text-gray-600 transition-transform duration-200" 
              :class="{ 'rotate-180': showCategoriesSection }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <!-- Filter Toggle centered on mobile -->
        <div class="flex justify-center mb-2">
          <button
            @click.stop="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
            class="px-3 py-2 border-2 rounded-lg text-xs font-semibold transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95"
            :class="filterMode === 'include' 
              ? 'border-green-400 bg-green-50 text-green-700 hover:bg-green-100 hover:border-green-500' 
              : 'border-red-400 bg-red-50 text-red-700 hover:bg-red-100 hover:border-red-500'"
            :title="filterMode === 'include' 
              ? 'Click to switch to EXCLUDE mode - hide selected categories from export' 
              : 'Click to switch to INCLUDE mode - show only selected categories in export'"
          >
            <span class="flex items-center gap-1">
              <span class="hidden xs:inline">{{ filterMode === 'include' ? '✅ Include selected' : '❌ Exclude selected' }}</span>
              <span class="xs:hidden">{{ filterMode === 'include' ? '✅ Include' : '❌ Exclude' }}</span>
            </span>
          </button>
        </div>
        <!-- Status text on mobile -->
        <p class="text-xs text-gray-600 text-center leading-tight">
          {{ selectedCategories.length > 0 
            ? filterMode === 'include'
              ? `${selectedCategories.length} selected • Export will contain ONLY these`
              : `${selectedCategories.length} selected • Export will EXCLUDE these`
            : 'Select categories below' }}
        </p>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden sm:flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center gap-4 mb-2">
            <h3 class="text-xl font-bold text-gray-900">📂 Event Categories</h3>
            <!-- Filter Mode Toggle in Header -->
            <button
              @click.stop="$emit('switch-filter-mode', filterMode === 'include' ? 'exclude' : 'include')"
              class="px-3 py-1.5 border-2 rounded-lg text-xs font-semibold transition-all duration-200 hover:shadow-md hover:scale-105 active:scale-95"
              :class="filterMode === 'include' 
                ? 'border-green-400 bg-green-50 text-green-700 hover:bg-green-100 hover:border-green-500' 
                : 'border-red-400 bg-red-50 text-red-700 hover:bg-red-100 hover:border-red-500'"
              :title="filterMode === 'include' 
                ? 'Click to switch to EXCLUDE mode - hide selected categories from export' 
                : 'Click to switch to INCLUDE mode - show only selected categories in export'"
            >
              <span class="flex items-center gap-1">
                {{ filterMode === 'include' ? '✅ Include selected' : '❌ Exclude selected' }}
                <svg class="w-3 h-3 opacity-70" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </span>
            </button>
          </div>
          <p class="text-sm text-gray-600">
            {{ selectedCategories.length > 0 
              ? filterMode === 'include'
                ? `${selectedCategories.length} selected • Export will contain ONLY these categories`
                : `${selectedCategories.length} selected • Export will EXCLUDE these categories (show everything else)`
              : 'Select categories below, then choose to include or exclude them from export' }}
          </p>
        </div>
        <button class="flex-shrink-0 p-2 rounded-full bg-white/50 hover:bg-white transition-all duration-200 ml-4">
          <svg 
            class="w-5 h-5 text-gray-600 transition-transform duration-200" 
            :class="{ 'rotate-180': showCategoriesSection }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Collapsible Content -->
    <div v-if="showCategoriesSection" class="p-3 sm:p-4">
      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-2 justify-center mb-4 px-1">
        <!-- When NOT searching: Show All/Clear All -->
        <template v-if="!searchTerm.trim()">
          <button 
            @click="$emit('clear-all')" 
            class="px-4 py-2 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ Clear All
          </button>
          <button 
            @click="$emit('select-all')" 
            class="px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ Select All
          </button>
        </template>
        
        <!-- When searching: Show contextual buttons -->
        <template v-else>
          <button 
            v-if="hasAnyVisibleSelected"
            @click="clearAllVisible"
            class="px-4 py-2 bg-rose-500 text-white rounded-lg font-semibold hover:bg-rose-600 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✗ Clear Visible
          </button>
          <button 
            v-if="!areAllVisibleSelected"
            @click="selectAllVisible"
            class="px-4 py-2 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap text-sm"
          >
            ✓ Select Visible ({{ filteredMainCategories.length }})
          </button>
        </template>
        
        <!-- Show Selected Only Toggle - responsive text -->
        <button
          v-if="selectedCategories.length > 0"
          @click="$emit('toggle-selected-only')"
          class="px-3 py-2 border-2 rounded-lg text-xs font-semibold transition-all duration-200 shadow-sm hover:shadow-md whitespace-nowrap"
          :class="showSelectedOnly 
            ? 'border-blue-400 bg-blue-50 text-blue-700 hover:bg-blue-100' 
            : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50'"
        >
          <span class="hidden sm:inline">{{ showSelectedOnly ? '👁️ Show all' : '🎯 Show selected only' }}</span>
          <span class="sm:hidden">{{ showSelectedOnly ? '👁️ All' : '🎯 Selected' }}</span>
        </button>
        
      </div>

      <!-- Category Search -->
      <div class="mb-4 relative">
        <input 
          :value="searchTerm"
          @input="$emit('update:search-term', $event.target.value)"
          type="text" 
          placeholder="🔍 Search categories..."
          class="w-full px-3 py-2.5 pr-10 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all duration-200 hover:border-gray-400 shadow-sm"
        >
        <!-- Clear search button -->
        <button
          v-if="searchTerm.trim()"
          @click="$emit('update:search-term', '')"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-gray-400 hover:bg-gray-500 text-white rounded-full flex items-center justify-center text-xs transition-all duration-200"
          title="Clear search"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
      
      <!-- Multi-Event Categories -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
        <div 
          v-for="category in filteredMainCategories" 
          :key="category.name"
          class="rounded-lg border-2 transition-all duration-200"
          :class="selectedCategories.includes(category.name) 
            ? 'border-green-500 bg-green-50' 
            : 'border-gray-200'"
        >
          <!-- Category Header -->
          <div 
            class="flex items-center gap-3 p-2.5 cursor-pointer hover:bg-gray-50"
            :class="expandedCategories.includes(category.name) ? 'rounded-t-lg' : 'rounded-lg'"
            @click="$emit('toggle-category', category.name)"
          >
            <!-- Checkbox -->
            <div class="flex-shrink-0">
              <div 
                class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
                :class="selectedCategories.includes(category.name) 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : 'border-gray-300 bg-white'"
              >
                <span v-if="selectedCategories.includes(category.name)">✓</span>
              </div>
            </div>
            
            <!-- Category Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <span class="font-medium text-gray-800 text-xs leading-tight truncate">{{ category.name }}</span>
                <span class="flex-shrink-0 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                  <span class="hidden sm:inline">{{ category.count }} events</span>
                  <span class="sm:hidden">{{ category.count }}</span>
                </span>
              </div>
            </div>
            
            <!-- Expand Button -->
            <button 
              @click.stop="$emit('toggle-expansion', category.name)"
              class="flex-shrink-0 w-10 h-6 flex items-center justify-center rounded-full transition-all duration-200 hover:bg-white"
              :class="expandedCategories.includes(category.name) 
                ? 'bg-blue-100 text-blue-600' 
                : 'bg-gray-100 text-gray-500 hover:text-gray-700'"
            >
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-90': expandedCategories.includes(category.name) }"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          
          <!-- Expandable Events List -->
          <div 
            v-if="expandedCategories.includes(category.name)"
            class="border-t border-gray-200 bg-gray-50 px-6 py-3 rounded-b-lg"
          >
            <div class="space-y-3">
              <div 
                v-for="event in category.events" 
                :key="event.uid"
                class="py-2 border-b border-gray-200 last:border-b-0"
              >
                <div class="font-medium text-gray-800 text-sm mb-1">{{ event.summary }}</div>
                <div class="flex flex-col gap-1 text-xs text-gray-600">
                  <span>📅 {{ formatDateRange(event) }}</span>
                  <span v-if="event.location" class="break-words">📍 {{ event.location }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Individual Events Section -->
      <div 
        v-if="filteredSingleCategories.length > 0" 
        class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border-2 border-purple-200 overflow-hidden"
      >
        <!-- Singles Header - Fully Clickable -->
        <div 
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-purple-100/50 transition-colors duration-200"
          :class="showSingleEvents ? '' : ''"
          @click="areAllSinglesSelected ? $emit('clear-all-singles') : $emit('select-all-singles')"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
              :class="areAllSinglesSelected
                ? 'bg-purple-500 border-purple-500 text-white' 
                : 'border-purple-300 bg-white'"
            >
              <span v-if="areAllSinglesSelected">✓</span>
            </div>
            <span class="font-semibold text-purple-800">📄 Individual Events</span>
            <span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full font-medium">
              {{ selectedSinglesCount }}/{{ filteredSingleCategories.length }}
            </span>
          </div>
          <button 
            @click.stop="showSingleEvents = !showSingleEvents"
            class="px-3 py-1 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-1"
          >
            {{ showSingleEvents ? 'Hide' : 'Show' }}
            <svg 
              class="w-3 h-3 transition-transform duration-200" 
              :class="{ 'rotate-90': showSingleEvents }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <!-- Singles List (when expanded) -->
        <div v-if="showSingleEvents" class="border-t border-purple-200 p-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          <div 
            v-for="category in filteredSingleCategories"
            :key="category.name"
            class="flex items-center gap-2 p-2 rounded-lg border transition-all duration-200 cursor-pointer hover:bg-purple-50"
            :class="selectedCategories.includes(category.name) 
              ? 'border-purple-500 bg-purple-100' 
              : 'border-purple-200 bg-white'"
            @click="$emit('toggle-category', category.name)"
          >
            <!-- Checkbox -->
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200 flex-shrink-0"
              :class="selectedCategories.includes(category.name) 
                ? 'bg-purple-500 border-purple-500 text-white' 
                : 'border-purple-300 bg-white'"
            >
              <span v-if="selectedCategories.includes(category.name)">✓</span>
            </div>
            
            <!-- Event Info -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-purple-800 text-xs leading-tight mb-1 truncate">{{ category.name }}</div>
              <div class="flex flex-col gap-1 text-xs text-purple-600">
                <span class="truncate">📅 {{ formatDateRange(category.events[0]) }}</span>
                <span v-if="category.events[0].location" class="truncate">📍 {{ category.events[0].location }}</span>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  mainCategories: { type: Array, default: () => [] },
  singleCategories: { type: Array, default: () => [] },
  selectedCategories: { type: Array, default: () => [] },
  expandedCategories: { type: Array, default: () => [] },
  showSingleEvents: { type: Boolean, default: false },
  showCategoriesSection: { type: Boolean, default: true },
  showSelectedOnly: { type: Boolean, default: false },
  searchTerm: { type: String, default: '' },
  filterMode: { type: String, default: 'include' },
  formatDateTime: { type: Function, required: true },
  formatDateRange: { type: Function, required: true }
})

// Filtered categories based on search and selection
const filteredMainCategories = computed(() => {
  let categories = props.mainCategories
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    categories = categories.filter(category => 
      props.selectedCategories.includes(category.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    categories = categories.filter(category => 
      category.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return categories
})

const filteredSingleCategories = computed(() => {
  let categories = props.singleCategories
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    categories = categories.filter(category => 
      props.selectedCategories.includes(category.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    categories = categories.filter(category => 
      category.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return categories
})

// Singles selection state
const areAllSinglesSelected = computed(() => {
  if (filteredSingleCategories.value.length === 0) return false
  const singleNames = filteredSingleCategories.value.map(cat => cat.name)
  return singleNames.every(name => props.selectedCategories.includes(name))
})

const selectedSinglesCount = computed(() => {
  const singleNames = filteredSingleCategories.value.map(cat => cat.name)
  return singleNames.filter(name => props.selectedCategories.includes(name)).length
})

// Visible selection state for main categories
const areAllVisibleSelected = computed(() => {
  if (filteredMainCategories.value.length === 0) return false
  const visibleNames = filteredMainCategories.value.map(cat => cat.name)
  return visibleNames.every(name => props.selectedCategories.includes(name))
})

const hasAnyVisibleSelected = computed(() => {
  const visibleNames = filteredMainCategories.value.map(cat => cat.name)
  return visibleNames.some(name => props.selectedCategories.includes(name))
})

// Methods for visible category selection
function selectAllVisible() {
  const visibleNames = filteredMainCategories.value.map(cat => cat.name)
  visibleNames.forEach(name => {
    if (!props.selectedCategories.includes(name)) {
      emit('toggle-category', name)
    }
  })
}

function clearAllVisible() {
  const visibleNames = filteredMainCategories.value.map(cat => cat.name)
  visibleNames.forEach(name => {
    if (props.selectedCategories.includes(name)) {
      emit('toggle-category', name)
    }
  })
}

const emit = defineEmits([
  'clear-all',
  'select-all', 
  'update:search-term',
  'toggle-category',
  'toggle-expansion',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles',
  'toggle-selected-only',
  'switch-filter-mode'
])

// Make showSingleEvents and showCategoriesSection writable
const showSingleEvents = computed({
  get: () => props.showSingleEvents,
  set: (value) => emit('toggle-singles-visibility', value)
})

const showCategoriesSection = computed({
  get: () => props.showCategoriesSection,
  set: (value) => emit('toggle-categories-section', value)
})
</script>