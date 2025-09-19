<template>
  <div class="border rounded-lg bg-white dark:bg-gray-900 transition-all duration-200 border-gray-200 dark:border-gray-600">
    <!-- Event Type Header -->
    <div
      class="cursor-pointer p-3"
      :class="[
        isSelected 
          ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' 
          : isPartiallySelected 
            ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
            : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
      ]"
      @click="toggleSelection"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <!-- Event Type Icon -->
          <div class="w-2 h-2 rounded-full" :class="isSelected ? 'bg-green-500' : isPartiallySelected ? 'bg-yellow-500' : 'bg-gray-400'"></div>
          <span class="text-sm font-medium">{{ eventTypeName }}</span>
          <span class="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
            {{ eventTypeData.count || 0 }} events
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
      class="border-t border-gray-200 dark:border-gray-600 bg-gray-50/50 dark:bg-gray-800/50"
    >
      <!-- Loading State -->
      <div v-if="isLoading" class="p-4 text-center">
        <div class="text-sm text-gray-600 dark:text-gray-400">Loading individual events...</div>
      </div>
      
      <!-- Individual Events List -->
      <div v-else-if="individualEvents.length > 0" class="p-4 space-y-2 max-h-60 overflow-y-auto">
        <h6 class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-3">
          Individual Events ({{ individualEvents.length }})
        </h6>
        <div class="space-y-2">
          <div
            v-for="event in individualEvents"
            :key="event.id"
            class="flex items-center justify-between p-2 rounded bg-white dark:bg-gray-700 border cursor-pointer transition-colors"
            :class="selectedItems.has(`event:${event.id}`) 
              ? 'bg-blue-100 dark:bg-blue-900/40 border-blue-300 dark:border-blue-600 text-blue-800 dark:text-blue-200' 
              : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
            @click="toggleIndividualEvent(event.id)"
          >
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium truncate">
                {{ event.summary || event.title || 'Untitled Event' }}
              </div>
              <div class="text-xs opacity-75">
                {{ formatEventDate(event.start || event.dtstart) }}
                <span v-if="event.location" class="ml-1">• {{ event.location }}</span>
              </div>
            </div>
            
            <!-- Individual Event Selection Checkbox -->
            <div
              class="w-3 h-3 rounded border flex items-center justify-center ml-2 flex-shrink-0"
              :class="selectedItems.has(`event:${event.id}`) 
                ? 'bg-blue-500 border-blue-500 text-white' 
                : 'border-gray-300 dark:border-gray-600'"
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
      
      <!-- No Events State -->
      <div v-else class="p-4 text-center">
        <div class="text-sm text-gray-500 dark:text-gray-400">
          No individual events found
        </div>
      </div>
      
      <!-- Collapse Button -->
      <div class="border-t border-gray-200 dark:border-gray-600 p-2">
        <button
          @click.stop="toggleExpansion"
          class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors font-medium"
        >
          ▲ Hide Individual Events
        </button>
      </div>
    </div>
    
    <!-- Expand Button (when collapsed) -->
    <div v-else-if="(eventTypeData.count || 0) > 0" class="border-t border-gray-200 dark:border-gray-600 p-2">
      <button
        @click.stop="toggleExpansion"
        class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors font-medium"
      >
        ▼ Show Individual Events ({{ eventTypeData.count || 0 }})
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
    return 'bg-green-500 border-green-500 text-white'
  } else if (isPartiallySelected.value) {
    return 'bg-yellow-500 border-yellow-500 text-white'
  } else {
    return 'border-gray-300 dark:border-gray-600'
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