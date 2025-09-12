<template>
  <div v-if="categories.length > 0" class="bg-white rounded-xl shadow-lg border border-gray-200 p-4 sm:p-6 mb-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6 gap-4">
      <h3 class="text-xl sm:text-2xl font-bold text-gray-900 m-0">📂 Select Event Categories</h3>
      <div class="flex flex-row gap-3 justify-center sm:justify-end">
        <button 
          @click="$emit('clear-all')" 
          class="px-6 py-2.5 bg-gray-500 text-white rounded-lg font-semibold hover:bg-gray-600 transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap"
        >
          Clear All
        </button>
        <button 
          @click="$emit('select-all')" 
          class="px-6 py-2.5 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg whitespace-nowrap"
        >
          Select All
        </button>
      </div>
    </div>

    <!-- Category Search -->
    <div class="mb-5">
      <input 
        :value="searchTerm"
        @input="$emit('update:search-term', $event.target.value)"
        type="text" 
        placeholder="🔍 Search categories..."
        class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 hover:border-gray-400 shadow-sm font-medium"
      />
    </div>
    
    <!-- Compact Categories List -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-200 mb-4 overflow-hidden">
      <div class="bg-gradient-to-r from-slate-100 to-slate-50 px-4 sm:px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800">📂 Event Categories</h3>
        <p class="text-sm text-gray-600 mt-1">Select categories to include in your filtered calendar</p>
      </div>
      
      <div class="p-4">
        <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          <div 
            v-for="category in mainCategories" 
            :key="category.name"
            class="rounded-lg border-2 transition-all duration-200"
            :class="selectedCategories.includes(category.name) 
              ? 'border-green-500 bg-green-50' 
              : 'border-gray-200'"
          >
            <!-- Category Header -->
            <div 
              class="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50"
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
                <div class="flex items-center justify-between gap-3">
                  <span class="font-medium text-gray-800 text-xs leading-tight">{{ category.name }}</span>
                  <span class="flex-shrink-0 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                    {{ category.count }} events
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
                    <span>📅 {{ formatDateTime(event.dtstart) }}</span>
                    <span v-if="event.location" class="break-words">📍 {{ event.location }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Individual Events Section -->
    <div 
      v-if="singleCategories.length > 0" 
      class="bg-white rounded-xl shadow-lg border border-gray-200"
      :class="selectedCategories.filter(cat => singleCategories.some(s => s.name === cat)).length === singleCategories.length && singleCategories.length > 0 ? 'border-green-500 bg-green-50' : ''"
    >
      <!-- Header -->
      <div class="bg-gradient-to-r from-slate-100 to-slate-50 px-4 sm:px-6 py-4 border-b border-gray-200"
           :class="showSingleEvents ? 'rounded-t-xl' : 'rounded-xl'">
        <div 
          class="flex items-center gap-3 cursor-pointer"
          @click="areAllSinglesSelected ? $emit('clear-all-singles') : $emit('select-all-singles')"
        >
          <!-- Checkbox -->
          <div 
            class="flex-shrink-0"
          >
            <div 
              class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
              :class="areAllSinglesSelected
                ? 'bg-green-500 border-green-500 text-white' 
                : 'border-gray-300 bg-white'"
            >
              <span v-if="areAllSinglesSelected">✓</span>
            </div>
          </div>
          
          <!-- Header Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-3">
              <span class="font-medium text-gray-800 text-sm leading-tight">📄 Individual Events</span>
              <span class="flex-shrink-0 px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full font-medium">
                {{ selectedSinglesCount }}/{{ singleCategories.length }} events
              </span>
            </div>
          </div>
          
          <!-- Expand Button -->
          <button 
            @click="$emit('toggle-singles-visibility')"
            class="flex-shrink-0 w-10 h-6 flex items-center justify-center rounded-full transition-all duration-200 hover:bg-white"
            :class="showSingleEvents
              ? 'bg-blue-100 text-blue-600' 
              : 'bg-gray-100 text-gray-500 hover:text-gray-700'"
          >
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-90': showSingleEvents }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Collapsible List -->
      <div v-if="showSingleEvents" class="bg-gray-50 px-6 py-3 rounded-b-xl">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          <div 
            v-for="category in singleCategories" 
            :key="category.name"
            class="flex items-center gap-3 py-2 cursor-pointer hover:bg-gray-100 rounded transition-colors duration-200"
            @click="$emit('toggle-category', category.name)"
          >
            <!-- Checkbox -->
            <div class="flex-shrink-0">
              <div 
                class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
                :class="selectedCategories.includes(category.name) 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : 'border-gray-300 bg-white'"
              >
                <span v-if="selectedCategories.includes(category.name)">✓</span>
              </div>
            </div>
            
            <!-- Event Info -->
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-800 text-xs leading-tight mb-1">{{ category.name }}</div>
              <div class="flex flex-col gap-1 text-xs text-gray-600">
                <span>📅 {{ formatDateTime(category.events[0].dtstart) }}</span>
                <span v-if="category.events[0].location" class="break-words">📍 {{ category.events[0].location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Controls Section -->
    <div v-if="selectedCategoriesCount > 0" class="mt-6 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div class="bg-gradient-to-r from-slate-100 to-slate-50 px-4 sm:px-6 py-4 border-b border-gray-200">
        <div class="flex flex-col gap-4">
          <!-- Header Row -->
          <div>
            <h4 class="text-lg font-semibold text-gray-800 m-0">⚙️ Filter Settings</h4>
          </div>
          
          <!-- Controls Row -->
          <div class="flex justify-center sm:justify-start">
            <div class="flex bg-gray-200 rounded-xl p-1 shadow-inner">
            <button 
              @click="$emit('switch-filter-mode', 'include')"
              class="px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 text-center"
              :class="filterMode === 'include' 
                ? 'bg-blue-500 text-white shadow-lg transform scale-105' 
                : 'text-gray-600 hover:bg-gray-300 hover:scale-105'"
            >
              ✅ Show Only These
            </button>
            <button 
              @click="$emit('switch-filter-mode', 'exclude')"
              class="px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 text-center"
              :class="filterMode === 'exclude' 
                ? 'bg-blue-500 text-white shadow-lg transform scale-105' 
                : 'text-gray-600 hover:bg-gray-300 hover:scale-105'"
            >
              ❌ Hide These
            </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Simple Summary -->
      <div class="p-4 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-3 bg-blue-50 border border-blue-200 rounded-xl">
          <span class="text-2xl">
            {{ filterMode === 'include' ? '✅' : '❌' }}
          </span>
          <div class="text-left">
            <div class="font-semibold text-blue-800">
              {{ filterMode === 'include' ? 'Including' : 'Excluding' }} {{ selectedCategories.length }} categories
            </div>
            <div class="text-sm text-blue-600">
              {{ selectedCategoriesCount }} events {{ filterMode === 'include' ? 'selected' : 'excluded' }}
            </div>
          </div>
        </div>
        
        <div v-if="selectedCategories.length > 0" class="mt-3 flex justify-center gap-3">
          <button 
            @click="$emit('clear-all')"
            class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
          >
            Clear All
          </button>
          <button 
            @click="$emit('select-all')"
            class="px-4 py-2 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg font-medium transition-colors"
          >
            Select All
          </button>
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
  searchTerm: { type: String, default: '' },
  filterMode: { type: String, default: 'include' },
  selectedCategoriesCount: { type: Number, default: 0 },
  formatDateTime: { type: Function, required: true }
})


const emit = defineEmits([
  'clear-all',
  'select-all', 
  'update:search-term',
  'toggle-category',
  'toggle-expansion',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles',
  'switch-filter-mode'
])

// Computed property to check if all individual events are selected
const areAllSinglesSelected = computed(() => {
  if (props.singleCategories.length === 0) return false
  const singleCategoryNames = props.singleCategories.map(cat => cat.name)
  return singleCategoryNames.every(name => props.selectedCategories.includes(name))
})

// Computed property to count selected individual events
const selectedSinglesCount = computed(() => {
  if (props.singleCategories.length === 0) return 0
  const singleCategoryNames = props.singleCategories.map(cat => cat.name)
  return singleCategoryNames.filter(name => props.selectedCategories.includes(name)).length
})

</script>

<style scoped>
/* Pure CSS styles without @apply directives for Tailwind v4 compatibility */
.category-card {
  border: 2px solid #e5e7eb;
  border-radius: 1rem;
  padding: 1rem;
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.category-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2), 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px) scale(1.02);
  background: linear-gradient(145deg, #ffffff, #f1f5f9);
}

.category-card.selected {
  border-color: #10b981;
  background: linear-gradient(145deg, #ecfdf5, #f0fdf4);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.25), 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.category-card.selected:hover {
  border-color: #059669;
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3), 0 6px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-4px) scale(1.01);
}

.event-item {
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.event-item:last-child {
  border-bottom: none;
}

.btn-gradient {
  background: linear-gradient(135deg, #22c55e, #16a34a, #15803d);
  color: white;
  padding: 1rem 2rem;
  border-radius: 0.75rem;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35);
  border: none;
  cursor: pointer;
}

.btn-gradient:hover {
  background: linear-gradient(135deg, #16a34a, #15803d, #14532d);
  box-shadow: 0 10px 30px rgba(34, 197, 94, 0.5), 0 4px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px) scale(1.02);
}

/* Individual Event Cards */
.individual-event-card {
  position: relative;
  padding: 1.25rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.individual-event-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.15), 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px) scale(1.01);
  background: linear-gradient(145deg, #ffffff, #f1f5f9);
}

.individual-event-card.selected {
  border-color: #10b981;
  background: linear-gradient(145deg, #ecfdf5, #f0fdf4);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2), 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.individual-event-card.selected:hover {
  border-color: #059669;
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.25), 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px) scale(1.02);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>