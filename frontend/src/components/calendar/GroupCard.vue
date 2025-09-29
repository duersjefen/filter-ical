<template>
  <!-- Enhanced group card with improved visual hierarchy -->
  <div 
    class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-blue-500/10 dark:hover:shadow-blue-400/20 group hover:scale-[1.02] transform"
    :class="isGroupSelected 
      ? 'ring-2 ring-blue-500 dark:ring-blue-400 shadow-lg shadow-blue-500/20 scale-[1.01]' 
      : isPartiallySelected
        ? 'ring-2 ring-blue-300 dark:ring-blue-400 shadow-md shadow-blue-500/10'
        : 'hover:ring-2 hover:ring-blue-300 dark:hover:ring-blue-600'"
    @click="expandGroup"
    :title="$t('ui.clickAnywhereToToggle', { name: group.name })"
  >
    <!-- Enhanced Group Header with gradient pattern for consistency -->
    <div class="bg-gradient-to-r from-slate-200 to-slate-300 dark:from-gray-700 dark:to-gray-800 px-6 py-5 border-b border-slate-300 dark:border-gray-600 relative overflow-hidden">
      <!-- Subscription status indicator stripe -->
      <div 
        class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
        :class="isGroupSubscribed ? 'bg-green-400' : 'bg-gray-500'"
      ></div>
      
      <!-- Group Title and Info - Enhanced Layout -->
      <div class="flex items-start gap-4">
        <!-- Status Icon and Title Container -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-3 mb-2">
            <!-- Subscription Status Badge -->
            <div 
              class="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition-all duration-300"
              :class="isGroupSubscribed 
                ? 'bg-green-600 text-white ring-1 ring-green-500' 
                : 'bg-gray-500 text-white ring-1 ring-gray-400'"
            >
              <div 
                class="w-2 h-2 rounded-full transition-colors duration-300"
                :class="isGroupSubscribed ? 'bg-green-300' : 'bg-gray-300'"
              ></div>
              <span>{{ isGroupSubscribed ? $t('status.subscribed') : $t('status.notSubscribed') }}</span>
            </div>
          </div>
          
          <!-- Group Title with enhanced typography -->
          <div class="text-xl sm:text-2xl font-bold text-gray-800 dark:text-white mb-2 leading-tight">
            📋 {{ group.name }}
          </div>
          
          <!-- Enhanced Description with event count -->
          <div class="text-sm text-gray-600 dark:text-gray-300 mb-3">
            <div v-if="group.description" class="truncate mb-1">
              {{ group.description }}
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span class="inline-flex items-center gap-1">
                <span class="w-1.5 h-1.5 bg-blue-400 rounded-full"></span>
                {{ totalEventCount }} total events
              </span>
              <span v-if="hasRecurringEvents" class="inline-flex items-center gap-1">
                <span class="w-1.5 h-1.5 bg-purple-400 rounded-full"></span>
                {{ recurringEventsCount }} recurring events
              </span>
            </div>
          </div>
          
          <!-- Enhanced Progress Bar -->
          <div v-if="hasRecurringEvents" class="w-full">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-medium text-gray-700 dark:text-gray-200">
                {{ selectedGroupRecurringEvents.length }}/{{ recurringEventsCount }} selected
              </span>
              <span class="text-xs text-gray-600 dark:text-gray-300">
                {{ Math.round((selectedGroupRecurringEvents.length / recurringEventsCount) * 100) }}%
              </span>
            </div>
            <div class="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
              <div 
                class="h-full transition-all duration-500 ease-out rounded-full"
                :class="selectedGroupRecurringEvents.length === 0 
                  ? 'bg-gray-600 w-0' 
                  : selectedGroupRecurringEvents.length === recurringEventsCount
                    ? 'bg-gradient-to-r from-green-400 to-emerald-500'
                    : 'bg-gradient-to-r from-blue-400 to-indigo-500'"
                :style="{ width: `${(selectedGroupRecurringEvents.length / recurringEventsCount) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- Expansion Arrow - Enhanced Design -->
        <div class="flex-shrink-0 self-start mt-1">
          <div 
            class="w-8 h-8 rounded-full bg-gray-500 shadow-sm border border-gray-400 flex items-center justify-center transition-all duration-300 group-hover:border-blue-400 group-hover:shadow-md group-hover:bg-gray-400"
          >
            <svg 
              class="w-4 h-4 text-white transition-all duration-300"
              :class="{ 'rotate-90': isExpanded }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Enhanced Card Content with modern button design -->
    <div class="p-6 bg-gray-600 dark:bg-gray-800">
      
      <!-- Compact Action Buttons -->
      <div class="space-y-2">
        <!-- Primary Action Button -->
        <button
          @click.stop="toggleSubscribeAndSelect"
          class="w-full px-4 py-3 text-sm font-semibold rounded-lg transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.01] active:scale-[0.99] min-h-[44px] border"
          :class="isBothSubscribedAndSelected 
            ? 'bg-green-500 hover:bg-green-600 text-white border-green-400 hover:border-green-500' 
            : 'bg-blue-500 hover:bg-blue-600 text-white border-blue-400 hover:border-blue-500'"
          :title="isBothSubscribedAndSelected ? $t('ui.unsubscribeAndDeselect') : $t('ui.subscribeAndSelect')"
        >
          <!-- Status icon -->
          <div 
            class="w-5 h-5 rounded-full border border-white bg-white/20 flex items-center justify-center"
          >
            <span v-if="isBothSubscribedAndSelected" class="text-white text-sm">✓</span>
            <span v-else class="text-white text-sm">+</span>
          </div>
          
          <!-- Button text -->
          <span class="font-semibold text-sm">
            {{ isBothSubscribedAndSelected ? $t('groupCard.subscribedSelected') : $t('groupCard.subscribeSelect') }}
          </span>
        </button>
        
        <!-- Individual Control Buttons -->
        <div class="grid grid-cols-2 gap-2">
          <!-- Subscribe Button -->
          <button
            @click.stop="toggleGroupSubscription"
            class="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.01] active:scale-[0.99] min-h-[40px]"
            :class="isGroupSubscribed 
              ? 'bg-blue-500 hover:bg-blue-600 text-white' 
              : 'bg-gray-500 hover:bg-gray-400 text-white border border-gray-400 hover:border-blue-400'"
            :title="isGroupSubscribed ? $t('status.unsubscribeFromGroup') : $t('status.subscribeToGroup')"
          >
            <div 
              class="w-3 h-3 rounded-full"
              :class="isGroupSubscribed ? 'bg-white' : 'bg-gray-400 group-hover:bg-blue-500'"
            ></div>
            <span>{{ isGroupSubscribed ? $t('status.subscribed') : $t('status.subscribe') }}</span>
          </button>
          
          <!-- Select All Button -->
          <button
            @click.stop="toggleSelectAllRecurringEvents"
            class="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-300 flex items-center justify-center gap-2 shadow-sm hover:shadow-md transform hover:scale-[1.01] active:scale-[0.99] min-h-[40px]"
            :class="areAllRecurringEventsSelected 
              ? 'bg-green-500 hover:bg-green-600 text-white' 
              : 'bg-gray-500 hover:bg-gray-400 text-white border border-gray-400 hover:border-green-400'"
            :title="areAllRecurringEventsSelected ? $t('status.deselectAllEvents') : $t('status.selectAllEvents')"
          >
            <div 
              class="w-3 h-3 border rounded flex items-center justify-center"
              :class="areAllRecurringEventsSelected 
                ? 'border-white bg-white/20' 
                : 'border-gray-400 group-hover:border-emerald-500'"
            >
              <span v-if="areAllRecurringEventsSelected" class="text-white text-sm">✓</span>
            </div>
            <span>{{ areAllRecurringEventsSelected ? $t('status.selected') : $t('status.selectAll') }}</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Expandable Recurring Events List -->
    <div v-if="isExpanded && hasRecurringEvents" class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800">
      <div class="p-2">
        
        <!-- Recurring Event Items (sorted by count, descending) -->
        <div>
          <div
            v-for="recurringEvent in sortedRecurringEvents"
            :key="recurringEvent.title"
            class="border rounded-lg transition-all duration-200 cursor-pointer group/item"
            :class="isRecurringEventSelected(recurringEvent.title)
              ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-500 shadow-sm' 
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-sm'"
            @click.stop="toggleRecurringEvent(recurringEvent.title)"
            :title="`Click to ${isRecurringEventSelected(recurringEvent.title) ? 'deselect' : 'select'} ${recurringEvent.title}`"
          >
            <!-- Recurring Event Header - Compact row clickable -->
            <div class="flex items-center gap-2 p-2 transition-colors">
              <!-- Recurring Event Checkbox -->
              <div 
                class="w-3.5 h-3.5 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
                :class="isRecurringEventSelected(recurringEvent.title)
                  ? 'bg-blue-500 border-blue-500 text-white' 
                  : 'border-gray-300 dark:border-gray-400 bg-white dark:bg-gray-700 group-hover/item:border-blue-400'"
              >
                <span v-if="isRecurringEventSelected(recurringEvent.title)" class="text-xs">✓</span>
              </div>
              
              <!-- Recurring Event Info with Day Pattern -->
              <div class="flex-1 min-w-0">
                <div class="text-xs font-medium text-gray-900 dark:text-gray-100 truncate group-hover/item:text-blue-600 dark:group-hover/item:text-blue-400 transition-colors">
                  {{ recurringEvent.title.trim() }}
                </div>
                <!-- Day Pattern Display -->
                <div v-if="getRecurringEventDayPattern(recurringEvent)" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {{ getRecurringEventDayPattern(recurringEvent) }}
                </div>
              </div>
              
              <!-- Count badge and expansion arrow -->
              <div class="flex items-center gap-1.5">
                <!-- Event count badge beside dropdown arrow -->
                <div class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 group-hover/item:bg-blue-200 dark:group-hover/item:bg-blue-900/60 transition-colors">
                  {{ recurringEvent.event_count }}
                </div>
                
                <!-- Enhanced Expansion Button -->
                <button
                  @click.stop="toggleRecurringEventExpansion(recurringEvent.title)"
                  class="flex items-center gap-1 px-1.5 py-0.5 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-all duration-200 flex-shrink-0 group/expand"
                  :class="isRecurringEventExpanded(recurringEvent.title) 
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
                    : 'text-gray-500 dark:text-gray-400'"
                  :title="isRecurringEventExpanded(recurringEvent.title) ? $t('status.hideIndividualEvents') : $t('status.showIndividualEvents')"
                >
                  <span class="text-xs font-medium group-hover/expand:text-blue-600 dark:group-hover/expand:text-blue-400 transition-colors">
                    {{ isRecurringEventExpanded(recurringEvent.title) ? $t('admin.hide') : $t('admin.show') }}
                  </span>
                  <svg 
                    class="w-3 h-3 transition-transform duration-300" 
                    :class="{ 'rotate-180': isRecurringEventExpanded(recurringEvent.title) }"
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            
            <!-- Individual Events List -->
            <div v-if="isRecurringEventExpanded(recurringEvent.title)" class="border-t border-gray-100 dark:border-gray-700 bg-gray-25 dark:bg-gray-900/20">
              <!-- Loading State -->
              <div v-if="recurringEventEvents[recurringEvent.title]?.loading" class="px-3 py-2 text-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ $t('groupCard.loadingEvents') }}</div>
              </div>
              
              <!-- Error State -->
              <div v-else-if="recurringEventEvents[recurringEvent.title]?.error" class="px-3 py-2 text-center">
                <div class="text-xs text-red-500">{{ $t('groupCard.errorPrefix') }} {{ recurringEventEvents[recurringEvent.title].error }}</div>
              </div>
              
              <!-- Ultra-Compact Events List -->
              <div v-else-if="recurringEventEvents[recurringEvent.title]?.events?.length" class="max-h-32 overflow-y-auto">
                <div 
                  v-for="event in recurringEventEvents[recurringEvent.title].events" 
                  :key="event.id"
                  class="px-3 py-1 border-b border-gray-100 dark:border-gray-700 last:border-b-0 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <!-- Single Line Compact Layout -->
                  <div class="flex items-center justify-between gap-2 text-xs">
                    <!-- Left: Date and Title -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <!-- Concise Date with Pattern Awareness -->
                        <span class="font-mono text-gray-600 dark:text-gray-400 whitespace-nowrap">
                          {{ formatCompactEventDate(event, !!getRecurringEventDayPattern(recurringEvent)) }}
                        </span>
                        <!-- Recurring indicator -->
                        <span v-if="event.is_recurring" class="text-blue-500" :title="$t('status.recurringEvent')">🔄</span>
                        <!-- Title (only if different) -->
                        <span v-if="event.title !== recurringEvent.title" class="font-medium text-gray-800 dark:text-gray-200 truncate">
                          {{ event.title.trim() }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Right: Location -->
                    <div v-if="event.location" class="text-gray-500 dark:text-gray-400 text-right truncate max-w-[40%]" :title="event.location.trim()">
                      {{ event.location.trim() }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Empty State -->
              <div v-else class="px-3 py-2 text-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ $t('messages.noEventsFound') }}</div>
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
import { useI18n } from 'vue-i18n'
import { formatDateRange, analyzeSmartRecurringPattern } from '@/utils/dateFormatting'

const { t } = useI18n()

const props = defineProps({
  group: { type: Object, required: true },
  selectedRecurringEvents: { type: Array, default: () => [] },
  subscribedGroups: { type: Set, default: () => new Set() },
  expandedGroups: { type: Set, default: () => new Set() },
  domainId: { type: String, required: true }
})

const emit = defineEmits([
  'toggle-group',
  'toggle-recurring-event',
  'expand-group', 
  'subscribe-to-group',
  'select-all-recurring-events'
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

const totalEventCount = computed(() => {
  if (!hasRecurringEvents.value) return 0
  return props.group.recurring_events.reduce((total, event) => total + (event.event_count || 0), 0)
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

const getSelectionBubbleClasses = () => {
  const selectedCount = selectedGroupRecurringEvents.value.length
  const totalCount = recurringEventsCount.value
  
  if (selectedCount === 0) {
    // None selected - subtle gray
    return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
  } else if (selectedCount === totalCount) {
    // All selected - success green
    return 'bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300'
  } else {
    // Partial selection - attention blue
    return 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300'
  }
}

const toggleGroup = () => {
  emit('toggle-group', props.group.id)
}

const toggleRecurringEvent = (eventTitle) => {
  emit('toggle-recurring-event', eventTitle)
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

// Smart day pattern detection for recurring events with i18n support
const getRecurringEventDayPattern = (recurringEvent) => {
  if (!recurringEvent.events || recurringEvent.events.length === 0) return null
  
  // Use the new smart pattern analysis
  return analyzeSmartRecurringPattern(recurringEvent.events, t)
}


// Enhanced date formatting for individual events with i18n support
function formatCompactEventDate(event, hasConsistentDay = false) {
  const date = new Date(event.start || event.dtstart)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const eventDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  
  // Calculate days difference
  const diffTime = eventDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  // Get current locale for proper formatting
  const locale = t('language.switch') === 'Sprache wechseln' ? 'de-DE' : 'en-US'
  
  // Format time part
  const timeStr = date.toLocaleTimeString(locale, { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: false 
  })
  
  // Smart date formatting based on proximity
  if (diffDays === 0) {
    return `${t('preview.today', 'Today')} ${timeStr}`
  } else if (diffDays === 1) {
    return `${t('preview.tomorrow', 'Tomorrow')} ${timeStr}`
  } else if (diffDays === -1) {
    return `${t('preview.yesterday', 'Yesterday')} ${timeStr}`
  } else if (diffDays > 0 && diffDays <= 14) {
    // For the next two weeks, show day name + date when needed for clarity
    const dayName = date.toLocaleDateString(locale, { weekday: 'short' })
    if (diffDays <= 7) {
      // This week - just show day name
      return `${dayName} ${timeStr}`
    } else {
      // Next week - show day name + date to distinguish from this week
      const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
      return `${dayName} ${monthDay} ${timeStr}`
    }
  } else if (diffDays >= -7 && diffDays < 0) {
    // For last week, show day name + date to distinguish from future events
    const dayName = date.toLocaleDateString(locale, { weekday: 'short' })
    const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    return `${dayName} ${monthDay} ${timeStr}`
  } else {
    // For dates further away, always show month/day regardless of pattern
    const monthDay = date.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    const currentYear = now.getFullYear()
    const eventYear = date.getFullYear()
    
    if (eventYear !== currentYear) {
      return `${monthDay} ${eventYear} ${timeStr}`
    } else {
      return `${monthDay} ${timeStr}`
    }
  }
}

// Use formatDateRange from utils for proper 24h format and multi-day support
</script>