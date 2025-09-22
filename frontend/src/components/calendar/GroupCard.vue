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
      <!-- Group Title and Info -->
      <div class="flex items-center gap-3 mb-3">
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-gray-900 dark:text-gray-100 truncate">
            {{ group.name }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400 truncate">
            {{ group.description || `${eventTypesCount} ${eventTypesCount === 1 ? 'event type' : 'event types'}` }}
          </div>
        </div>
        
        <!-- Expansion Indicator -->
        <div 
          class="flex-shrink-0 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors rounded p-1"
          @click="expandGroup"
          title="Click to expand/collapse group details"
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
      
      <!-- Action Buttons: Subscribe vs Select All -->
      <div class="flex gap-2 mt-3">
        <!-- Subscribe Button - Group-level subscription -->
        <button
          @click.stop="toggleGroupSubscription"
          class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
          :class="isGroupSubscribed 
            ? 'bg-blue-500 hover:bg-blue-600 text-white' 
            : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
          :title="isGroupSubscribed ? 'Unsubscribe from this group' : 'Subscribe to all events in this group automatically'"
        >
          <span v-if="isGroupSubscribed">✓ Subscribed</span>
          <span v-else>📥 Subscribe</span>
        </button>
        
        <!-- Select All Button - Individual event type selection -->
        <button
          @click.stop="toggleSelectAllEventTypes"
          class="flex-1 px-3 py-2 text-sm rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
          :class="areAllEventTypesSelected 
            ? 'bg-green-500 hover:bg-green-600 text-white' 
            : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300'"
          :title="areAllEventTypesSelected ? 'Deselect all event types' : 'Select all event types individually'"
        >
          <span v-if="areAllEventTypesSelected">✓ All Selected</span>
          <span v-else>☐ Select All</span>
        </button>
      </div>
    </div>
    
    <!-- Expandable Event Types List -->
    <div v-if="isExpanded && hasEventTypes" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-900">
      <div class="p-3 space-y-2">
        <div class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
          Event Types ({{ eventTypesCount }})
        </div>
        
        <!-- Event Type Checkboxes -->
        <div class="space-y-1">
          <div
            v-for="(eventTypeData, eventTypeName) in group.event_types"
            :key="eventTypeName"
            class="border border-gray-100 dark:border-gray-700 rounded-md"
          >
            <!-- Event Type Header -->
            <div class="flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <!-- Event Type Checkbox -->
              <div 
                class="w-3 h-3 rounded border flex items-center justify-center text-xs transition-all flex-shrink-0 cursor-pointer"
                :class="isEventTypeSelected(eventTypeName)
                  ? 'bg-blue-500 border-blue-500 text-white' 
                  : 'border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700'"
                @click.stop="toggleEventType(eventTypeName)"
              >
                <span v-if="isEventTypeSelected(eventTypeName)">✓</span>
              </div>
              
              <!-- Event Type Info -->
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {{ eventTypeName }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {{ eventTypeData.count }} events
                </div>
              </div>
              
              <!-- Expansion Arrow -->
              <button
                @click.stop="toggleEventTypeExpansion(eventTypeName)"
                class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                :class="{ 'transform rotate-180': isEventTypeExpanded(eventTypeName) }"
              >
                <svg class="w-3 h-3 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            
            <!-- Individual Events List -->
            <div v-if="isEventTypeExpanded(eventTypeName)" class="border-t border-gray-100 dark:border-gray-700 bg-gray-25 dark:bg-gray-900/20">
              <!-- Loading State -->
              <div v-if="eventTypeEvents[eventTypeName]?.loading" class="p-3 text-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">Loading events...</div>
              </div>
              
              <!-- Error State -->
              <div v-else-if="eventTypeEvents[eventTypeName]?.error" class="p-3 text-center">
                <div class="text-xs text-red-500">Error: {{ eventTypeEvents[eventTypeName].error }}</div>
              </div>
              
              <!-- Events List -->
              <div v-else-if="eventTypeEvents[eventTypeName]?.events?.length" class="max-h-48 overflow-y-auto">
                <div 
                  v-for="event in eventTypeEvents[eventTypeName].events" 
                  :key="event.id"
                  class="px-3 py-2 border-b border-gray-100 dark:border-gray-700 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors"
                >
                  <div class="flex items-start gap-2">
                    <!-- Individual Event Checkbox -->
                    <div class="w-2 h-2 rounded-sm border border-gray-300 dark:border-gray-500 bg-white dark:bg-gray-700 mt-1 flex-shrink-0"></div>
                    
                    <!-- Event Details -->
                    <div class="flex-1 min-w-0">
                      <div class="text-xs font-medium text-gray-800 dark:text-gray-200 truncate">
                        {{ event.title }}
                      </div>
                      <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {{ formatEventDate(event.start) }}
                        <span v-if="event.location" class="ml-2">📍 {{ event.location }}</span>
                        <span v-if="event.is_recurring" class="ml-2">🔄</span>
                      </div>
                    </div>
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

const props = defineProps({
  group: { type: Object, required: true },
  selectedEventTypes: { type: Array, default: () => [] },
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

// State for expanded event types and their events
const expandedEventTypes = ref(new Set())
const eventTypeEvents = ref({}) // eventTypeName -> {events: [...], loading: false}

// Computed properties
const hasEventTypes = computed(() => {
  return props.group.event_types && Object.keys(props.group.event_types).length > 0
})

const eventTypesCount = computed(() => {
  return hasEventTypes.value ? Object.keys(props.group.event_types).length : 0
})

const isExpanded = computed(() => {
  return props.expandedGroups.has(props.group.id)
})

const groupEventTypes = computed(() => {
  return hasEventTypes.value ? Object.keys(props.group.event_types) : []
})

const selectedGroupEventTypes = computed(() => {
  return groupEventTypes.value.filter(eventType => 
    props.selectedEventTypes.includes(eventType)
  )
})

const isGroupSelected = computed(() => {
  return groupEventTypes.value.length > 0 && 
         groupEventTypes.value.every(eventType => 
           props.selectedEventTypes.includes(eventType)
         )
})

const isPartiallySelected = computed(() => {
  return selectedGroupEventTypes.value.length > 0 && 
         selectedGroupEventTypes.value.length < groupEventTypes.value.length
})

// New computed properties for Subscribe and Select All buttons
const isGroupSubscribed = computed(() => {
  return props.subscribedGroups.has(props.group.id)
})

const areAllEventTypesSelected = computed(() => {
  return groupEventTypes.value.length > 0 && 
         groupEventTypes.value.every(eventType => 
           props.selectedEventTypes.includes(eventType)
         )
})

// Methods
const isEventTypeSelected = (eventTypeName) => {
  return props.selectedEventTypes.includes(eventTypeName)
}

const toggleGroup = () => {
  emit('toggle-group', props.group.id)
}

const toggleEventType = (eventTypeName) => {
  emit('toggle-event-type', eventTypeName)
}

const expandGroup = () => {
  emit('expand-group', props.group.id)
}

// New methods for Subscribe and Select All buttons
const toggleGroupSubscription = () => {
  emit('subscribe-to-group', props.group.id)
}

const toggleSelectAllEventTypes = () => {
  emit('select-all-event-types', {
    groupId: props.group.id,
    eventTypes: groupEventTypes.value,
    selectAll: !areAllEventTypesSelected.value
  })
}

// Event type expansion methods
const isEventTypeExpanded = (eventTypeName) => {
  return expandedEventTypes.value.has(eventTypeName)
}

const toggleEventTypeExpansion = async (eventTypeName) => {
  if (isEventTypeExpanded(eventTypeName)) {
    expandedEventTypes.value.delete(eventTypeName)
  } else {
    expandedEventTypes.value.add(eventTypeName)
    await fetchEventTypeEvents(eventTypeName)
  }
}

const fetchEventTypeEvents = async (eventTypeName) => {
  // Set loading state
  eventTypeEvents.value[eventTypeName] = {
    events: [],
    loading: true,
    error: null
  }
  
  try {
    // Handle domain ID format - strip 'cal_domain_' prefix if present
    const cleanDomainId = props.domainId.startsWith('cal_domain_') 
      ? props.domainId.replace('cal_domain_', '') 
      : props.domainId
    
    const response = await fetch(`/api/domains/${cleanDomainId}/types/${encodeURIComponent(eventTypeName)}/events`)
    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Filter events to show recent and future events (hide old past events)
    const now = new Date()
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const recentAndFutureEvents = (data.events || []).filter(event => {
      if (!event.start) return true // Keep events without start date
      const eventDate = new Date(event.start)
      return eventDate >= oneWeekAgo // Show events from last week onward
    })
    
    eventTypeEvents.value[eventTypeName] = {
      events: recentAndFutureEvents,
      loading: false,
      error: null
    }
  } catch (error) {
    console.error('Error fetching event type events:', error)
    eventTypeEvents.value[eventTypeName] = {
      events: [],
      loading: false,
      error: error.message
    }
  }
}

// Date formatting utility
const formatEventDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}
</script>