<template>
  <div class="border rounded-lg transition-all duration-200 bg-white dark:bg-gray-900">
    <!-- Group Card -->
    <div
      class="cursor-pointer p-4"
      :class="[
        isSelected 
          ? 'bg-blue-600 text-white' 
          : isPartiallySelected 
            ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 border-blue-200 dark:border-blue-700'
            : 'hover:bg-blue-50 dark:hover:bg-blue-900/10 border-blue-200 dark:border-blue-700'
      ]"
      @click="toggleSelection"
    >
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <h4 class="text-lg font-semibold">{{ group.name }}</h4>
            <div
              class="w-3 h-3 rounded-full opacity-60"
              :style="{ backgroundColor: group.color }"
            ></div>
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
        
        <!-- Selection Checkbox -->
        <div
          class="w-5 h-5 rounded border-2 flex items-center justify-center ml-4 flex-shrink-0"
          :class="selectionCheckboxClass"
        >
          <span v-if="isSelected || isPartiallySelected" class="text-sm">{{ selectionIcon }}</span>
        </div>
      </div>
    </div>

    <!-- Expandable Content -->
    <div 
      v-if="isExpanded" 
      class="border-t border-blue-200 dark:border-blue-700 bg-blue-50/30 dark:bg-blue-900/10"
    >
      <!-- Children (Subgroups) -->
      <div v-if="group.children && group.children.length > 0" class="p-4 space-y-3">
        <h5 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-3 uppercase tracking-wide">Subgroups</h5>
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
        <h5 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-3 uppercase tracking-wide">Event Types</h5>
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
      
      <!-- Collapse Button -->
      <div class="border-t border-blue-200 dark:border-blue-700 p-3">
        <button
          @click.stop="toggleExpansion"
          class="w-full text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors font-medium"
        >
          ▲ Collapse Details
        </button>
      </div>
    </div>
    
    <!-- Expand Button (when collapsed) -->
    <div 
      v-else-if="hasExpandableContent" 
      class="border-t border-blue-200 dark:border-blue-700 p-3"
    >
      <button
        @click.stop="toggleExpansion"
        class="w-full text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors font-medium"
      >
        ▼ Show Details ({{ childCount }} items)
      </button>
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
    return 'bg-white border-white text-blue-600'
  } else if (props.isPartiallySelected) {
    return 'bg-blue-600 border-blue-600 text-white'
  } else {
    return 'border-blue-300 dark:border-blue-600'
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

const toggleSelection = () => {
  emit('toggle-selection', `group:${props.group.id}`)
}

const toggleExpansion = () => {
  emit('toggle-expansion', props.group.id)
}
</script>