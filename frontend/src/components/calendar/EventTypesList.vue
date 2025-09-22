<template>
  <div class="space-y-1">
    <div
      v-for="(eventTypeData, eventTypeName) in eventTypes"
      :key="eventTypeName"
      class="border border-gray-200 dark:border-gray-600 rounded bg-gray-50 dark:bg-gray-800"
    >
      <!-- Event Type Header -->
      <div 
        class="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors rounded-t"
        @click="$emit('toggle-event-type-expansion', eventTypeName)"
      >
        <div class="flex items-center space-x-3 flex-1">
          <div class="flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ eventTypeName }}</span>
            <span class="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 bg-white dark:bg-gray-700 rounded">
              {{ eventTypeData.count }} events
            </span>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <!-- Expansion indicator -->
          <div class="text-gray-400 dark:text-gray-500">
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-180': isEventTypeExpanded(eventTypeName) }" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
          
          <!-- Selection checkbox -->
          <div
            @click.stop="$emit('toggle-event-type-selection', eventTypeName)"
            class="w-4 h-4 rounded border-2 flex items-center justify-center flex-shrink-0 cursor-pointer"
            :class="isEventTypeSelected(eventTypeName)
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300 dark:border-gray-600 hover:border-green-400'"
          >
            <span v-if="isEventTypeSelected(eventTypeName)" class="text-xs">✓</span>
          </div>
        </div>
      </div>
      
      <!-- Individual Events List -->
      <EventsList
        v-if="isEventTypeExpanded(eventTypeName) && eventTypeData.events && eventTypeData.events.length > 0"
        :events="eventTypeData.events"
      />
    </div>
  </div>
</template>

<script setup>
import EventsList from './EventsList.vue'

defineProps({
  eventTypes: {
    type: Object,
    default: () => ({})
  },
  isEventTypeExpanded: {
    type: Function,
    required: true
  },
  isEventTypeSelected: {
    type: Function,
    required: true
  }
})

defineEmits([
  'toggle-event-type-expansion',
  'toggle-event-type-selection'
])
</script>