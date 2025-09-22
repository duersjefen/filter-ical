<template>
  <div class="border rounded-lg transition-all duration-200 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700">
    <!-- Group Card -->
    <div
      class="p-4 cursor-pointer"
      :class="[
        isSelected 
          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200' 
          : isPartiallySelected 
            ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
            : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
      ]"
      @click="toggleGroupSelection"
    >
      <div class="flex items-center justify-between">
        <!-- Group Header -->
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <h4 class="text-lg font-semibold">{{ group.name }}</h4>
            <div
              class="w-3 h-3 rounded-full opacity-60"
              :style="{ backgroundColor: group.color }"
            ></div>
            <!-- Expand/Collapse indicator -->
            <div class="text-gray-400 dark:text-gray-500">
              <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': isExpanded }" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <span class="text-sm opacity-75">
              {{ totalEventCount }} events
            </span>
          </div>
          
          <!-- Description -->
          <p v-if="group.description" class="text-sm opacity-75 mt-2">
            {{ group.description }}
          </p>
        </div>
        
        <!-- Action Controls -->
        <div class="flex items-center gap-2 ml-4">
          <!-- Dedicated Expansion Button -->
          <button
            v-if="hasExpandableContent"
            @click.stop="toggleExpansion"
            class="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 hover:bg-blue-100 dark:hover:bg-blue-900/30 border border-transparent hover:border-blue-300 dark:hover:border-blue-600"
            :class="isExpanded 
              ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' 
              : 'text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400'"
            :title="isExpanded ? 'Collapse group' : 'Expand group'"
          >
            <svg 
              class="w-4 h-4 transition-transform duration-200" 
              :class="{ 'rotate-180': isExpanded }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          
          <!-- Selection Checkbox (Visual indicator only - card handles selection) -->
          <div
            class="w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 pointer-events-none"
            :class="selectionCheckboxClass"
          >
            <span v-if="isSelected || isPartiallySelected" class="text-sm">{{ selectionIcon }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Expandable Content -->
    <div 
      v-if="isExpanded" 
      class="border-t border-gray-200 dark:border-gray-600 bg-gray-50/30 dark:bg-gray-800/30"
    >
      <!-- Children (Subgroups) -->
      <div v-if="group.children && group.children.length > 0" class="p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">Subgroups</h5>
        <div class="pl-4 space-y-3">
          <SubgroupItem
            v-for="subgroup in group.children"
            :key="subgroup.id"
            :subgroup="subgroup"
            :is-selected="selectedItems.has(`group:${subgroup.id}`)"
            :is-partially-selected="hasPartialSubgroupSelection(subgroup)"
            :selected-items="selectedItems"
            :expanded-groups="expandedGroups"
            :expanded-event-types="expandedEventTypes"
            @toggle-selection="$emit('toggle-selection', `group:${subgroup.id}`)"
            @toggle-event-type="$emit('toggle-selection', $event)"
            @toggle-individual-event="$emit('toggle-selection', $event)"
            @toggle-expansion="$emit('toggle-expansion', $event)"
          />
        </div>
      </div>
      
      <!-- Direct Event Types -->
      <div v-if="group.event_types && Object.keys(group.event_types).length > 0" class="p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3 uppercase tracking-wide">Event Types</h5>
        <div class="pl-4 space-y-2">
          <EventTypeItem
            v-for="(eventTypeData, eventTypeName) in group.event_types"
            :key="eventTypeName"
            :event-type-name="eventTypeName"
            :event-type-data="eventTypeData"
            :is-selected="selectedItems.has(`event_type:${eventTypeName}`)"
            :selected-items="selectedItems"
            :expanded-event-types="expandedEventTypes"
            @toggle-selection="$emit('toggle-selection', `event_type:${eventTypeName}`)"
            @toggle-individual-event="$emit('toggle-selection', $event)"
            @toggle-expansion="$emit('toggle-expansion', $event)"
          />
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import SubgroupItem from './SubgroupItem.vue'
import EventTypeItem from './EventTypeItem.vue'

const props = defineProps({
  group: { type: Object, required: true },
  isSelected: { type: Boolean, default: false },
  isPartiallySelected: { type: Boolean, default: false },
  selectedItems: { type: Set, default: () => new Set() },
  expandedGroups: { type: Set, default: () => new Set() },
  expandedEventTypes: { type: Set, default: () => new Set() }
})

const emit = defineEmits([
  'toggle-selection',
  'toggle-expansion'
])

const isExpanded = computed(() => props.expandedGroups.has(props.group.id))

const hasExpandableContent = computed(() => {
  return (props.group.children && props.group.children.length > 0) ||
         (props.group.event_types && Object.keys(props.group.event_types).length > 0)
})

const childCount = computed(() => {
  const childrenCount = props.group.children ? props.group.children.length : 0
  const eventTypesCount = props.group.event_types ? Object.keys(props.group.event_types).length : 0
  return childrenCount + eventTypesCount
})

const totalEventCount = computed(() => {
  let count = 0
  
  // Count events in direct event types
  if (props.group.event_types) {
    count += Object.values(props.group.event_types).reduce((sum, eventType) => sum + eventType.count, 0)
  }
  
  // Count events in children recursively
  if (props.group.children) {
    count += props.group.children.reduce((sum, child) => {
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
    return 'bg-blue-500 border-blue-500 text-white'
  } else if (props.isPartiallySelected) {
    return 'bg-yellow-500 border-yellow-500 text-white'
  } else {
    return 'border-gray-300 dark:border-gray-600'
  }
})

const selectionIcon = computed(() => {
  if (props.isSelected) return '✓'
  if (props.isPartiallySelected) return '◐'
  return ''
})

const hasPartialSubgroupSelection = (subgroup) => {
  // Check if any items within this subgroup are selected
  const subgroupSelected = props.selectedItems.has(`group:${subgroup.id}`)
  if (subgroupSelected) return false // If whole subgroup is selected, not partial
  
  // Check event types in subgroup
  if (subgroup.event_types) {
    for (const eventTypeName of Object.keys(subgroup.event_types)) {
      if (props.selectedItems.has(`event_type:${eventTypeName}`)) {
        return true
      }
    }
  }
  
  // Check children of subgroup
  if (subgroup.children) {
    for (const child of subgroup.children) {
      if (props.selectedItems.has(`group:${child.id}`) || hasPartialSubgroupSelection(child)) {
        return true
      }
    }
  }
  
  return false
}

// Separate handlers for clarity
const toggleGroupSelection = () => {
  // This should select the entire group and all its children
  emit('toggle-selection', `group:${props.group.id}`)
}

const toggleExpansion = () => {
  emit('toggle-expansion', props.group.id)
}
</script>