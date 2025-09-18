<template>
  <div class="border rounded-lg bg-white dark:bg-gray-900 transition-all duration-200 border-blue-200 dark:border-blue-700">
    <!-- Event Type Header -->
    <div
      class="cursor-pointer p-3"
      :class="[
        isSelected 
          ? 'bg-blue-400 text-white' 
          : isPartiallySelected 
            ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200'
            : 'hover:bg-blue-50 dark:hover:bg-blue-900/10'
      ]"
      @click="toggleSelection"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <!-- Event Type Icon -->
          <div class="w-1.5 h-1.5 rounded-full opacity-60" :class="isSelected ? 'bg-white' : 'bg-blue-400'"></div>
          <span class="text-sm font-medium">{{ eventTypeName }}</span>
          <span class="text-xs px-2 py-1 rounded opacity-75" :class="isSelected ? 'bg-blue-600' : 'bg-blue-200 dark:bg-blue-800'">
            {{ eventTypeData.count }} events
          </span>
        </div>
        
        <!-- Selection Checkbox -->
        <div
          class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 ml-3"
          :class="selectionCheckboxClass"
        >
          <span v-if="isSelected || isPartiallySelected" class="text-xs">{{ selectionIcon }}</span>
        </div>
      </div>
    </div>

    <!-- Expandable Individual Events -->
    <div 
      v-if="isExpanded" 
      class="border-t border-blue-200 dark:border-blue-700 bg-blue-50/20 dark:bg-blue-900/10"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="p-4 text-center">
        <div class="text-sm text-blue-600 dark:text-blue-400">Loading individual events...</div>
      </div>
      
      <!-- Individual Events List -->
      <div v-else-if="individualEvents.length > 0" class="p-4 space-y-2 max-h-40 overflow-y-auto">
        <h6 class="text-xs font-medium text-blue-800 dark:text-blue-200 uppercase tracking-wide mb-3">
          Individual Events ({{ individualEvents.length }})
        </h6>
        <div class="pl-4 space-y-2">
          <div
            v-for="event in individualEvents"
            :key="event.id"
            class="flex items-center justify-between p-2 rounded bg-white dark:bg-gray-900 border cursor-pointer transition-colors"
            :class="selectedItems.has(`event:${event.id}`) 
              ? 'bg-blue-300 dark:bg-blue-800 border-blue-400 text-white' 
              : 'border-blue-200 dark:border-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20'"
            @click="toggleIndividualEvent(event.id)"
          >
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium truncate">
                {{ event.title }}
              </div>
              <div class="text-xs opacity-75">
                {{ formatEventDate(event.start) }}
                <span v-if="event.location" class="ml-1">• {{ event.location }}</span>
              </div>
            </div>
            
            <!-- Individual Event Selection Checkbox -->
            <div
              class="w-3 h-3 rounded border flex items-center justify-center ml-2 flex-shrink-0"
              :class="selectedItems.has(`event:${event.id}`) 
                ? 'bg-white border-white text-blue-300' 
                : 'border-blue-300 dark:border-blue-600'"
            >
              <span v-if="selectedItems.has(`event:${event.id}`)" class="text-xs">✓</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Error State -->
      <div v-else-if="loadError" class="p-4 text-center">
        <div class="text-sm text-red-500 dark:text-red-400">
          Failed to load individual events: {{ loadError }}
        </div>
      </div>
      
      <!-- Collapse Button -->
      <div class="border-t border-blue-200 dark:border-blue-700 p-3">
        <button
          @click.stop="toggleExpansion"
          class="w-full text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors font-medium"
        >
          ▲ Hide Individual Events
        </button>
      </div>
    </div>
    
    <!-- Expand Button (when collapsed) -->
    <div v-else-if="eventTypeData.count > 0" class="border-t border-blue-200 dark:border-blue-700 p-3">
      <button
        @click.stop="toggleExpansion"
        class="w-full text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors font-medium"
      >
        ▼ Show Individual Events ({{ eventTypeData.count }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  eventTypeName: { type: String, required: true },
  eventTypeData: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  selectedItems: { type: Set, default: () => new Set() },
  expandedEventTypes: { type: Set, default: () => new Set() },
  calendarId: { type: String, default: '' }
})

const emit = defineEmits([
  'toggle-selection',
  'toggle-individual-event',
  'toggle-expansion'
])

// Local state for individual events
const individualEvents = ref([])
const isLoading = ref(false)
const loadError = ref('')

const isExpanded = computed(() => props.expandedEventTypes.has(props.eventTypeName))

const isPartiallySelected = computed(() => {
  // Check if any individual events are selected but not all
  if (props.isSelected) return false // If whole event type is selected, not partial
  
  const selectedEventCount = individualEvents.value.filter(event => 
    props.selectedItems.has(`event:${event.id}`)
  ).length
  
  return selectedEventCount > 0 && selectedEventCount < individualEvents.value.length
})

const selectionCheckboxClass = computed(() => {
  if (props.isSelected) {
    return 'bg-white border-white text-blue-400'
  } else if (isPartiallySelected.value) {
    return 'bg-blue-400 border-blue-400 text-white'
  } else {
    return 'border-blue-300 dark:border-blue-600'
  }
})

const selectionIcon = computed(() => {
  if (props.isSelected) return '✓'
  if (isPartiallySelected.value) return '◐'
  return ''
})

const formatEventDate = (dateString) => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return dateString
  }
}

const toggleSelection = () => {
  emit('toggle-selection', `event_type:${props.eventTypeName}`)
}

const toggleIndividualEvent = (eventId) => {
  emit('toggle-individual-event', `event:${eventId}`)
}

const toggleExpansion = async () => {
  if (isExpanded.value) {
    // Collapse
    emit('toggle-expansion', props.eventTypeName)
  } else {
    // Expand and load individual events
    emit('toggle-expansion', props.eventTypeName)
    await loadIndividualEvents()
  }
}

const loadIndividualEvents = async () => {
  if (individualEvents.value.length > 0) return // Already loaded
  
  isLoading.value = true
  loadError.value = ''
  
  try {
    // Use the events from eventTypeData if available (more efficient)
    if (props.eventTypeData.events && Array.isArray(props.eventTypeData.events)) {
      individualEvents.value = props.eventTypeData.events
    } else {
      // Fallback: fetch from API
      const response = await fetch(`/api/calendar/${props.calendarId}/events?event_type=${encodeURIComponent(props.eventTypeName)}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      individualEvents.value = data.events || []
    }
  } catch (error) {
    loadError.value = error.message
    console.error('Failed to load individual events:', error)
  } finally {
    isLoading.value = false
  }
}
</script>