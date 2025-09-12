<template>
  <!-- Event Preview Section -->
  <div v-if="selectedCategories.length > 0" class="bg-white rounded-xl shadow-lg border border-gray-200 mb-4 overflow-hidden">
    <!-- Collapsible Header -->
    <div 
      class="bg-gradient-to-r from-slate-100 to-slate-50 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 cursor-pointer hover:bg-slate-100 transition-colors duration-200"
      :class="showPreview ? 'rounded-t-xl' : 'rounded-xl'"
      @click="showPreview = !showPreview"
    >
      <!-- Mobile Layout -->
      <div class="block sm:hidden">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800">🔍 Event Preview</h3>
          <button class="flex-shrink-0 p-2 rounded-full bg-white/50 hover:bg-white transition-all duration-200">
            <svg 
              class="w-5 h-5 text-gray-600 transition-transform duration-200" 
              :class="{ 'rotate-180': showPreview }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <p class="text-xs text-gray-600 text-center mt-2">{{ sortedPreviewEvents.length }} events selected</p>
      </div>

      <!-- Desktop Layout -->
      <div class="hidden sm:flex items-center justify-between">
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-gray-800 mb-1">🔍 Event Preview</h3>
          <p class="text-sm text-gray-600">{{ sortedPreviewEvents.length }} events from your selection</p>
        </div>
        <button class="flex-shrink-0 p-2 rounded-full bg-white/50 hover:bg-white transition-all duration-200 ml-4">
          <svg 
            class="w-5 h-5 text-gray-600 transition-transform duration-200" 
            :class="{ 'rotate-180': showPreview }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Collapsible Content -->
    <div v-if="showPreview">
      <!-- Preview Controls -->
      <div class="px-3 sm:px-4 md:px-6 py-3 sm:py-4 border-b border-gray-200 bg-gray-50">
      <div class="flex justify-center">
        <!-- View Mode Buttons -->
        <div class="inline-flex bg-white rounded-lg p-1 shadow-sm border border-gray-200">
          <button 
            @click="$emit('update:preview-group', 'none')"
            class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
            :class="previewGroup === 'none' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'"
          >
            <span class="hidden sm:inline">📋 List</span>
            <span class="sm:hidden">📋</span>
          </button>
          <button 
            @click="$emit('update:preview-group', 'category')"
            class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
            :class="previewGroup === 'category' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'"
          >
            <span class="hidden sm:inline">📂 Category</span>
            <span class="sm:hidden">📂</span>
          </button>
          <button 
            @click="$emit('update:preview-group', 'month')"
            class="px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 rounded-md text-sm font-medium transition-all text-center min-w-0"
            :class="previewGroup === 'month' ? 'bg-blue-500 text-white shadow-md' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'"
          >
            <span class="hidden sm:inline">📅 Month</span>
            <span class="sm:hidden">📅</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Preview Content -->
    <div class="max-h-[600px] overflow-y-auto">
      <!-- Simple List View -->
      <div v-if="previewGroup === 'none'" class="p-4">
        <div class="flex flex-col gap-3">
          <div 
            v-for="event in sortedPreviewEvents" 
            :key="event.uid"
            class="event-item border-b border-gray-100 pb-3 last:border-b-0 last:pb-0"
          >
            <div class="font-semibold text-gray-800 text-sm leading-tight mb-1">{{ event.summary }}</div>
            <div class="text-xs text-gray-600 font-medium mb-1">📅 {{ formatDateRange(event) }}</div>
            <div v-if="event.location" class="text-xs text-gray-500 flex items-center gap-1 mb-1">
              📍 {{ event.location }}
            </div>
            <div v-if="getCategoryForEvent(event) !== event.summary" class="text-xs text-blue-600 font-medium">
              📂 {{ getCategoryForEvent(event) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Grouped by Category -->
      <div v-else-if="previewGroup === 'category'" class="p-4">
        <div class="flex flex-col gap-6">
          <div 
            v-for="group in groupedPreviewEvents" 
            :key="group.name"
            class="bg-white rounded-lg border border-gray-200 overflow-hidden"
          >
            <div 
              @click="toggleGroupExpansion(group.name)"
              class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-3 flex justify-between items-center cursor-pointer hover:from-blue-600 hover:to-blue-700 transition-all"
            >
              <div class="flex items-center gap-3">
                <svg 
                  class="w-4 h-4 transition-transform duration-300" 
                  :class="{ 'rotate-90': expandedGroups.has(group.name) }"
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <h4 class="font-semibold text-base m-0">{{ group.name }}</h4>
              </div>
              <span class="bg-white/20 px-2 py-1 rounded-full text-xs font-medium">
                {{ group.events.length }} events
              </span>
            </div>
            <div v-if="expandedGroups.has(group.name)" class="p-4">
              <div class="flex flex-col gap-3">
                <div 
                  v-for="event in group.events.slice(0, 10)" 
                  :key="event.uid"
                  class="event-item border-b border-gray-100 pb-3 last:border-b-0 last:pb-0"
                >
                  <div class="font-semibold text-gray-800 text-sm leading-tight mb-1">{{ event.summary }}</div>
                  <div class="text-xs text-gray-600 font-medium mb-1">📅 {{ formatDateRange(event) }}</div>
                  <div v-if="event.location" class="text-xs text-gray-500 flex items-center gap-1">
                    📍 {{ event.location }}
                  </div>
                </div>
                <div v-if="group.events.length > 10" class="text-center text-gray-500 italic p-3 bg-gray-100 rounded-lg border text-sm font-medium mt-3">
                  ... and {{ group.events.length - 10 }} more events
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Grouped by Month -->
      <div v-else-if="previewGroup === 'month'" class="p-4">
        <div class="flex flex-col gap-6">
          <div 
            v-for="group in groupedPreviewEvents" 
            :key="group.name"
            class="bg-white rounded-lg border border-gray-200 overflow-hidden"
          >
            <div 
              @click="toggleGroupExpansion(group.name)"
              class="bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-3 flex justify-between items-center cursor-pointer hover:from-green-600 hover:to-green-700 transition-all"
            >
              <div class="flex items-center gap-3">
                <svg 
                  class="w-4 h-4 transition-transform duration-300" 
                  :class="{ 'rotate-90': expandedGroups.has(group.name) }"
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <h4 class="font-semibold text-base m-0">{{ group.name }}</h4>
              </div>
              <span class="bg-white/20 px-2 py-1 rounded-full text-xs font-medium">
                {{ group.events.length }} events
              </span>
            </div>
            <div v-if="expandedGroups.has(group.name)" class="p-4">
              <div class="flex flex-col gap-3">
                <div 
                  v-for="event in group.events.slice(0, 10)" 
                  :key="event.uid"
                  class="event-item border-b border-gray-100 pb-3 last:border-b-0 last:pb-0"
                >
                  <div class="font-semibold text-gray-800 text-sm leading-tight mb-1">{{ event.summary }}</div>
                  <div class="text-xs text-gray-600 font-medium mb-1">📅 {{ formatDateRange(event) }}</div>
                  <div v-if="event.location" class="text-xs text-gray-500 flex items-center gap-1 mb-1">
                    📍 {{ event.location }}
                  </div>
                  <div v-if="getCategoryForEvent(event) !== event.summary" class="text-xs text-blue-600 font-medium">
                    📂 {{ getCategoryForEvent(event) }}
                  </div>
                </div>
                <div v-if="group.events.length > 10" class="text-center text-gray-500 italic p-3 bg-gray-100 rounded-lg border text-sm font-medium mt-3">
                  ... and {{ group.events.length - 10 }} more events
                </div>
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
import { ref, watch } from 'vue'

const props = defineProps({
  selectedCategories: { type: Array, default: () => [] },
  sortedPreviewEvents: { type: Array, default: () => [] },
  previewGroup: { type: String, default: 'none' },
  previewOrder: { type: String, default: 'asc' },
  groupedPreviewEvents: { type: Array, default: () => [] },
  formatDateTime: { type: Function, required: true },
  formatDateRange: { type: Function, required: true },
  getCategoryForEvent: { type: Function, required: true }
})

const emit = defineEmits([
  'update:preview-group'
])

// State for tracking which groups are expanded
const expandedGroups = ref(new Set())

// State for collapsible preview section
const showPreview = ref(false)

// Watch for preview group changes and reset expanded state
watch(() => props.previewGroup, () => {
  expandedGroups.value.clear()
})

// Toggle group expansion
const toggleGroupExpansion = (groupName) => {
  if (expandedGroups.value.has(groupName)) {
    expandedGroups.value.delete(groupName)
  } else {
    expandedGroups.value.add(groupName)
  }
}
</script>