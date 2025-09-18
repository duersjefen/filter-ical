<template>
  <div class="border rounded-lg bg-white dark:bg-gray-900 transition-all duration-200 border-blue-200 dark:border-blue-700">
    <!-- Subgroup Header -->
    <div
      class="cursor-pointer p-3"
      :class="[
        isSelected 
          ? 'bg-blue-500 text-white' 
          : isPartiallySelected 
            ? 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200'
            : 'hover:bg-blue-50 dark:hover:bg-blue-900/10'
      ]"
      @click="toggleSelection"
    >
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-1">
            <!-- Subgroup Icon -->
            <div class="w-2 h-2 rounded-full opacity-60" :class="isSelected ? 'bg-white' : 'bg-blue-400'"></div>
            <h5 class="text-base font-medium">{{ subgroup.name }}</h5>
            <span class="text-sm opacity-75 px-2 py-1 rounded" :class="isSelected ? 'bg-blue-700' : 'bg-blue-200 dark:bg-blue-800'">
              {{ totalEventCount }} events
            </span>
          </div>
          
          <!-- Description -->
          <p v-if="subgroup.description" class="text-sm opacity-75 mt-1 ml-5">
            {{ subgroup.description }}
          </p>
        </div>
        
        <!-- Selection Checkbox -->
        <div
          class="w-4 h-4 rounded border-2 flex items-center justify-center ml-3 flex-shrink-0"
          :class="selectionCheckboxClass"
        >
          <span v-if="isSelected || isPartiallySelected" class="text-xs">{{ selectionIcon }}</span>
        </div>
      </div>
    </div>

    <!-- Expandable Content -->
    <div 
      v-if="isExpanded" 
      class="border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800"
    >
      <!-- Event Types -->
      <div v-if="subgroup.event_types && Object.keys(subgroup.event_types).length > 0" class="p-3 space-y-2">
        <h6 class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Event Types</h6>
        <EventTypeItem
          v-for="(eventTypeData, eventTypeName) in subgroup.event_types"
          :key="eventTypeName"
          :event-type-name="eventTypeName"
          :event-type-data="eventTypeData"
          :is-selected="selectedItems.has(`event_type:${eventTypeName}`)"
          :selected-items="selectedItems"
          :expanded-event-types="expandedEventTypes"
          @toggle-selection="$emit('toggle-event-type', `event_type:${eventTypeName}`)"
          @toggle-individual-event="$emit('toggle-individual-event', $event)"
          @toggle-expansion="$emit('toggle-expansion', $event)"
        />
      </div>
      
      <!-- Nested Children (if any) -->
      <div v-if="subgroup.children && subgroup.children.length > 0" class="p-3 space-y-2">
        <h6 class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Nested Groups</h6>
        <SubgroupItem
          v-for="child in subgroup.children"
          :key="child.id"
          :subgroup="child"
          :is-selected="selectedItems.has(`group:${child.id}`)"
          :is-partially-selected="hasPartialSelection(child)"
          :selected-items="selectedItems"
          @toggle-selection="$emit('toggle-selection', `group:${child.id}`)"
          @toggle-event-type="$emit('toggle-event-type', $event)"
          @toggle-individual-event="$emit('toggle-individual-event', $event)"
        />
      </div>
      
      <!-- Expansion Toggle -->
      <div class="border-t border-gray-200 dark:border-gray-600 p-2">
        <button
          @click.stop="toggleExpansion"
          class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
        >
          {{ isExpanded ? '▲ Collapse' : '▼ Expand' }}
        </button>
      </div>
    </div>
    
    <!-- Expand Button (when collapsed) -->
    <div 
      v-else-if="hasExpandableContent" 
      class="border-t border-gray-200 dark:border-gray-600 p-2"
    >
      <button
        @click.stop="toggleExpansion"
        class="w-full text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
      >
        ▼ Show Details ({{ childCount }} items)
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EventTypeItem from './EventTypeItem.vue'

const props = defineProps({
  subgroup: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  isPartiallySelected: { type: Boolean, default: false },
  selectedItems: { type: Set, default: () => new Set() },
  expandedGroups: { type: Set, default: () => new Set() },
  expandedEventTypes: { type: Set, default: () => new Set() }
})

const emit = defineEmits([
  'toggle-selection',
  'toggle-event-type', 
  'toggle-individual-event',
  'toggle-expansion'
])

const isExpanded = computed(() => props.expandedGroups.has(props.subgroup.id))

const hasExpandableContent = computed(() => {
  return (props.subgroup.children && props.subgroup.children.length > 0) ||
         (props.subgroup.event_types && Object.keys(props.subgroup.event_types).length > 0)
})

const childCount = computed(() => {
  const childrenCount = props.subgroup.children ? props.subgroup.children.length : 0
  const eventTypesCount = props.subgroup.event_types ? Object.keys(props.subgroup.event_types).length : 0
  return childrenCount + eventTypesCount
})

const totalEventCount = computed(() => {
  let count = 0
  
  // Count events in direct event types
  if (props.subgroup.event_types) {
    count += Object.values(props.subgroup.event_types).reduce((sum, eventType) => sum + eventType.count, 0)
  }
  
  // Count events in children recursively
  if (props.subgroup.children) {
    count += props.subgroup.children.reduce((sum, child) => {
      return sum + calculateGroupEventCount(child)
    }, 0)
  }
  
  return count
})

const calculateGroupEventCount = (group) => {
  let count = 0
  
  if (group.event_types) {
    count += Object.values(group.event_types).reduce((sum, eventType) => sum + eventType.count, 0)
  }
  
  if (group.children) {
    count += group.children.reduce((sum, child) => sum + calculateGroupEventCount(child), 0)
  }
  
  return count
}

const selectionCheckboxClass = computed(() => {
  if (props.isSelected) {
    return 'bg-white border-white text-blue-500'
  } else if (props.isPartiallySelected) {
    return 'bg-blue-500 border-blue-500 text-white'
  } else {
    return 'border-blue-300 dark:border-blue-600'
  }
})

const selectionIcon = computed(() => {
  if (props.isSelected) return '✓'
  if (props.isPartiallySelected) return '◐'
  return ''
})

const hasPartialSelection = (group) => {
  // Check if any items within this group are selected
  const groupSelected = props.selectedItems.has(`group:${group.id}`)
  if (groupSelected) return false // If whole group is selected, not partial
  
  // Check event types in group
  if (group.event_types) {
    for (const eventTypeName of Object.keys(group.event_types)) {
      if (props.selectedItems.has(`event_type:${eventTypeName}`)) {
        return true
      }
    }
  }
  
  // Check children of group
  if (group.children) {
    for (const child of group.children) {
      if (props.selectedItems.has(`group:${child.id}`) || hasPartialSelection(child)) {
        return true
      }
    }
  }
  
  return false
}

const toggleSelection = () => {
  emit('toggle-selection', `group:${props.subgroup.id}`)
}

const toggleExpansion = () => {
  emit('toggle-expansion', props.subgroup.id)
}
</script>