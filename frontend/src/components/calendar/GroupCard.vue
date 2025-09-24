<template>
  <!-- Fixed template structure -->
  <div 
    class="rounded-md border transition-all duration-150 bg-white dark:bg-gray-800"
    :class="isGroupSelected 
      ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-500' 
      : isPartiallySelected
        ? 'border-blue-300 bg-blue-50/30 dark:bg-blue-900/10 dark:border-blue-400'
        : 'border-gray-200 dark:border-gray-600'"
  >
    <!-- Group Header -->
    <div class="p-4">
      <!-- Group Title and Info - Fully Clickable Header -->
      <div 
        class="flex items-center gap-3 mb-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200"
        @click="expandGroup"
        title="Click anywhere to expand/collapse group details"
      >
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-gray-900 dark:text-gray-100 truncate">
            {{ group.name }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400 truncate">
            {{ group.description || eventCountDisplay }}
          </div>
        </div>
        
        <!-- Expansion Indicator -->
        <div 
          class="flex-shrink-0 p-1 rounded transition-colors duration-200"
        >
          <svg 
            class="w-5 h-5 text-gray-400 transition-transform duration-200"
            :class="{ 'rotate-180': isExpanded }"
            fill="currentColor" 
            viewBox="0 0 20 20"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
      
      <!-- Action Buttons: Three-Button System -->
      <div class="flex gap-2 mt-3">
        <!-- Combined Button - Primary Action (Subscribe + Select) -->
        <button
          @click.stop="toggleSubscribeAndSelect"
          class="flex-1 px-4 py-2.5 text-sm rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 border-2"
          :class="isBothSubscribedAndSelected 
            ? 'bg-indigo-500 hover:bg-indigo-600 text-white border-indigo-500' 
            : 'bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border-indigo-300 dark:border-indigo-600'"
          :title="isBothSubscribedAndSelected ? 'Unsubscribe and deselect this group' : 'Subscribe to group and select all event types'"
        >
          <span v-if="isBothSubscribedAndSelected">✅ Subscribed & Selected</span>
          <span v-else>🎯 Subscribe & Select</span>
        </button>
      </div>
      
      <!-- Individual Control Buttons - Secondary Actions -->
      <div class="flex gap-2 mt-2">
        <!-- Subscribe Only Button -->
        <button
          @click.stop="toggleGroupSubscription"
          class="flex-1 px-3 py-2 text-xs rounded-md font-medium transition-all duration-200 flex items-center justify-center gap-1"
          :class="isGroupSubscribed 
            ? 'bg-blue-500 hover:bg-blue-600 text-white' 
            : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
          :title="isGroupSubscribed ? 'Unsubscribe from this group' : 'Subscribe to future events from this group'"
        >
          <span v-if="isGroupSubscribed">✅ Subscribed</span>
          <span v-else>📥 Subscribe</span>
        </button>
        
        <!-- Select All Only Button -->
        <button
          @click.stop="toggleSelectAllRecurringEvents"
          class="flex-1 px-3 py-2 text-xs rounded-md font-medium transition-all duration-200 flex items-center justify-center gap-1"
          :class="areAllRecurringEventsSelected 
            ? 'bg-green-500 hover:bg-green-600 text-white' 
            : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
          :title="areAllRecurringEventsSelected ? 'Deselect all recurring events' : 'Select all recurring events for current view'"
        >
          <span v-if="areAllRecurringEventsSelected">✓ Deselect All</span>
          <span v-else>☐ Select All</span>
        </button>
      </div>
    </div>
    
    <!-- Expandable Recurring Events List -->
    <div v-if="isExpanded && hasRecurringEvents" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900">
      <div class="p-3 space-y-2">
        <div class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
          Events ({{ recurringEventsCount }})
        </div>
        
        <!-- Recurring Event Checkboxes (sorted by count, descending) -->
        <div class="space-y-1">
          <div
            v-for="recurringEvent in sortedRecurringEvents"
            :key="recurringEvent.title"
            class="border rounded-md transition-all duration-200"
            :class="isRecurringEventSelected(recurringEvent.title)
              ? 'border-blue-300 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-600' 
              : 'border-gray-100 dark:border-gray-700 hover:border-gray-200 dark:hover:border-gray-600'"
          >
            <!-- Recurring Event Header -->
            <div class="flex items-center gap-2 p-2 transition-colors">
              <!-- Recurring Event Checkbox -->
              <div 
                class="w-3 h-3 rounded border flex items-center justify-center text-xs transition-all flex-shrink-0"
                :class="isRecurringEventSelected(recurringEvent.title)
                  ? 'bg-blue-500 border-blue-500 text-white' 
                  : 'border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700'"
              >
                <span v-if="isRecurringEventSelected(recurringEvent.title)">✓</span>
              </div>
              
              <!-- Recurring Event Info - Fully Clickable for Selection -->
              <div 
                class="flex-1 min-w-0 cursor-pointer rounded p-1 -m-1 transition-colors duration-200"
                :class="isRecurringEventSelected(recurringEvent.title)
                  ? 'hover:bg-blue-100 dark:hover:bg-blue-800/30' 
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700/50'"
                @click.stop="toggleRecurringEvent(recurringEvent.title)"
                :title="`Click to ${isRecurringEventSelected(recurringEvent.title) ? 'deselect' : 'select'} ${recurringEvent.title}`"
              >
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {{ recurringEvent.title }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ recurringEvent.event_count }} events
                </div>
              </div>
              
              <!-- Expansion Arrow -->
              <button
                @click.stop="toggleRecurringEventExpansion(recurringEvent.title)"
                class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                :class="{ 'transform rotate-180': isRecurringEventExpanded(recurringEvent.title) }"
                title="Click to view individual events"
              >
                <svg class="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            
            <!-- Individual Events List -->
            <div v-if="isRecurringEventExpanded(recurringEvent.title)" class="border-t border-gray-100 dark:border-gray-700 bg-gray-25 dark:bg-gray-900/20">
              <!-- Loading State -->
              <div v-if="recurringEventEvents[recurringEvent.title]?.loading" class="p-3 text-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">Loading events...</div>
              </div>
              
              <!-- Error State -->
              <div v-else-if="recurringEventEvents[recurringEvent.title]?.error" class="p-3 text-center">
                <div class="text-xs text-red-500">Error: {{ recurringEventEvents[recurringEvent.title].error }}</div>
              </div>
              
              <!-- Events List (Concise Display) -->
              <div v-else-if="recurringEventEvents[recurringEvent.title]?.events?.length" class="space-y-1">
                <div 
                  v-for="event in recurringEventEvents[recurringEvent.title].events" 
                  :key="event.id"
                  class="px-2 py-1.5 bg-gray-50 dark:bg-gray-800/30 rounded text-xs"
                >
                  <!-- Compact Event Details -->
                  <div class="text-gray-700 dark:text-gray-300">
                    📅 {{ formatDateRange(event) }}
                    <span v-if="event.is_recurring" class="ml-1">🔄</span>
                  </div>
                  <div v-if="event.location" class="text-gray-600 dark:text-gray-400 mt-0.5">
                    📍 {{ event.location }}
                  </div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-else class="p-3 text-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">No events found</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { formatDateRange } from '@/utils/dates'

const props = defineProps({
  group: { type: Object, required: true },
  selectedRecurringEvents: { type: Array, default: () => [] },
  subscribedGroups: { type: Set, default: () => new Set() },
  expandedGroups: { type: Set, default: () => new Set() },
  domainId: { type: String, required: true }
})

const emit = defineEmits([
  'toggle-group',
  'toggle-event-type',
  'expand-group', 
  'subscribe-to-group',
  'select-all-event-types'
])

// State for expanded recurring events and their events
const expandedRecurringEvents = ref(new Set())
const recurringEventEvents = ref({}) // eventTitle -> {events: [...], loading: false}

// Computed properties
const hasRecurringEvents = computed(() => {
  return props.group.recurring_events && props.group.recurring_events.length > 0
})

const recurringEventsCount = computed(() => {
  return hasRecurringEvents.value ? props.group.recurring_events.length : 0
})

const eventCountDisplay = computed(() => {
  if (!hasRecurringEvents.value) return '0/0 events selected'
  
  const totalRecurringEvents = recurringEventsCount.value
  const selectedCount = selectedGroupRecurringEvents.value.length
  
  return `${selectedCount}/${totalRecurringEvents} events selected`
})

// Sort recurring events by count (descending) for better UX
const sortedRecurringEvents = computed(() => {
  if (!hasRecurringEvents.value) return []
  
  return props.group.recurring_events
    .sort((a, b) => (b.event_count || 0) - (a.event_count || 0))
})

const isExpanded = computed(() => {
  return props.expandedGroups.has(props.group.id)
})

const groupRecurringEventTitles = computed(() => {
  return hasRecurringEvents.value ? props.group.recurring_events.map(event => event.title) : []
})

const selectedGroupRecurringEvents = computed(() => {
  return groupRecurringEventTitles.value.filter(eventTitle => 
    props.selectedRecurringEvents.includes(eventTitle)
  )
})

const isGroupSelected = computed(() => {
  return groupRecurringEventTitles.value.length > 0 && 
         groupRecurringEventTitles.value.every(eventTitle => 
           props.selectedRecurringEvents.includes(eventTitle)
         )
})

const isPartiallySelected = computed(() => {
  return selectedGroupRecurringEvents.value.length > 0 && 
         selectedGroupRecurringEvents.value.length < groupRecurringEventTitles.value.length
})

// New computed properties for Subscribe and Select All buttons
const isGroupSubscribed = computed(() => {
  return props.subscribedGroups.has(props.group.id)
})

const areAllRecurringEventsSelected = computed(() => {
  return groupRecurringEventTitles.value.length > 0 && 
         groupRecurringEventTitles.value.every(eventTitle => 
           props.selectedRecurringEvents.includes(eventTitle)
         )
})

// Combined state computed property
const isBothSubscribedAndSelected = computed(() => {
  return isGroupSubscribed.value && areAllRecurringEventsSelected.value
})

// Get recurring events from group (for emit payloads)
const groupRecurringEvents = computed(() => {
  return groupRecurringEventTitles.value
})

// Methods
const isRecurringEventSelected = (eventTitle) => {
  return props.selectedRecurringEvents.includes(eventTitle)
}

const toggleGroup = () => {
  emit('toggle-group', props.group.id)
}

const toggleRecurringEvent = (eventTitle) => {
  emit('toggle-event-type', eventTitle)
}

const expandGroup = () => {
  emit('expand-group', props.group.id)
}

// New methods for Subscribe and Select All buttons
const toggleGroupSubscription = () => {
  emit('subscribe-to-group', props.group.id)
}

const toggleSelectAllRecurringEvents = () => {
  emit('select-all-recurring-events', {
    groupId: props.group.id,
    recurringEvents: groupRecurringEvents.value,
    selectAll: !areAllRecurringEventsSelected.value
  })
}

// Combined action method for Subscribe & Select
const toggleSubscribeAndSelect = () => {
  if (isBothSubscribedAndSelected.value) {
    // If both are active, deactivate both
    emit('subscribe-to-group', props.group.id)  // Toggle subscription off
    emit('select-all-recurring-events', {
      groupId: props.group.id,
      recurringEvents: groupRecurringEvents.value,
      selectAll: false  // Deselect all
    })
  } else {
    // Activate both subscription and selection
    if (!isGroupSubscribed.value) {
      emit('subscribe-to-group', props.group.id)  // Subscribe
    }
    if (!areAllRecurringEventsSelected.value) {
      emit('select-all-recurring-events', {
        groupId: props.group.id,
        recurringEvents: groupRecurringEvents.value,
        selectAll: true  // Select all
      })
    }
  }
}

// Event type expansion methods
const isRecurringEventExpanded = (eventTitle) => {
  return expandedRecurringEvents.value.has(eventTitle)
}

const toggleRecurringEventExpansion = async (eventTitle) => {
  if (isRecurringEventExpanded(eventTitle)) {
    expandedRecurringEvents.value.delete(eventTitle)
  } else {
    expandedRecurringEvents.value.add(eventTitle)
    await fetchRecurringEventEvents(eventTitle)
  }
}

const fetchRecurringEventEvents = async (eventTitle) => {
  // Set loading state
  recurringEventEvents.value[eventTitle] = {
    events: [],
    loading: true,
    error: null
  }
  
  try {
    // Events are already processed and available in recurring_events
    const recurringEventData = props.group.recurring_events?.find(event => event.title === eventTitle)
    
    if (recurringEventData && recurringEventData.events) {
      // Events are already available in the group data - no API call needed!
      recurringEventEvents.value[eventTitle] = {
        events: Array.isArray(recurringEventData.events) ? recurringEventData.events : [],
        loading: false,
        error: null
      }
    } else {
      // Fallback if events not found in group data
      recurringEventEvents.value[eventTitle] = {
        events: [],
        loading: false,
        error: `No events found for ${eventTitle}`
      }
    }
  } catch (error) {
    console.error('Error loading recurring event events:', error)
    recurringEventEvents.value[eventTitle] = {
      events: [],
      loading: false,
      error: error.message
    }
  }
}

// Use formatDateRange from utils for proper 24h format and multi-day support
</script>