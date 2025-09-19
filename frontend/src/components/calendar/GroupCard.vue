<template>
  <div 
    class="rounded-lg border-2 transition-all duration-200 bg-white dark:bg-gray-800"
    :class="isGroupSelected 
      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30' 
      : isPartiallySelected
        ? 'border-blue-300 bg-blue-25 dark:bg-blue-900/10'
        : 'border-gray-200 dark:border-gray-700'"
  >
    <!-- Group Header -->
    <div 
      class="flex items-center gap-3 p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
      :class="isExpanded ? 'rounded-t-lg' : 'rounded-lg'"
      @click="toggleGroup"
    >
      <!-- Group Checkbox -->
      <div class="flex-shrink-0">
        <div 
          class="w-5 h-5 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200"
          :class="isGroupSelected 
            ? 'bg-blue-500 border-blue-500 text-white' 
            : isPartiallySelected
              ? 'bg-blue-200 border-blue-300 text-blue-700'
              : 'border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700'"
        >
          <span v-if="isGroupSelected">✓</span>
          <span v-else-if="isPartiallySelected">◐</span>
        </div>
      </div>
      
      <!-- Group Info -->
      <div class="flex-1 min-w-0">
        <div class="font-medium text-gray-900 dark:text-gray-100 truncate">
          {{ group.name }}
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400 truncate">
          {{ eventTypesCount }} event types
        </div>
      </div>
      
      <!-- Expansion Indicator -->
      <div class="flex-shrink-0">
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
    
    <!-- Expandable Event Types List -->
    <div v-if="isExpanded && hasEventTypes" class="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
      <div class="p-3 space-y-2">
        <div class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide mb-2">
          Event Types ({{ eventTypesCount }})
        </div>
        
        <!-- Event Type Checkboxes -->
        <div class="space-y-1">
          <div
            v-for="(eventTypeData, eventTypeName) in group.event_types"
            :key="eventTypeName"
            class="flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-white dark:hover:bg-gray-700 transition-colors duration-200"
            @click="toggleEventType(eventTypeName)"
          >
            <!-- Event Type Checkbox -->
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold transition-all duration-200 flex-shrink-0"
              :class="isEventTypeSelected(eventTypeName)
                ? 'bg-blue-500 border-blue-500 text-white' 
                : 'border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700'"
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
          </div>
        </div>
      </div>
    </div>
    
    <!-- Expand Button (when collapsed) -->
    <div v-else-if="!isExpanded && hasEventTypes" class="border-t border-gray-200 dark:border-gray-700 p-2">
      <button
        @click.stop="expandGroup"
        class="w-full text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors font-medium"
      >
        ▼ Show {{ eventTypesCount }} event types
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  group: { type: Object, required: true },
  selectedEventTypes: { type: Array, default: () => [] },
  expandedGroups: { type: Set, default: () => new Set() }
})

const emit = defineEmits([
  'toggle-group',
  'toggle-event-type', 
  'expand-group'
])

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
</script>