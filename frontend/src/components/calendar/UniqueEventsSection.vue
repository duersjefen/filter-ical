<template>
  <!-- Unique Events - Separate Component -->
  <div 
    v-if="filteredSingleRecurringEvents.length > 0" 
    class="mt-6 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden"
  >
    <!-- Unique Events Header -->
    <div 
      class="bg-gradient-to-r from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-600 cursor-pointer hover:from-gray-200 hover:to-gray-100 dark:hover:from-gray-600 dark:hover:to-gray-700 transition-all duration-200"
      @click="$emit('toggle-singles-visibility')"
      :title="showSingleEvents ? 'Click to collapse unique events' : 'Click to expand unique events'"
    >
      <div class="flex items-center justify-between">
        <!-- Left: Title and Info -->
        <div class="flex items-center gap-3">
          <!-- Expand/Collapse Icon -->
          <div class="flex-shrink-0">
            <div class="w-6 h-6 rounded-md bg-gray-200 dark:bg-gray-600 flex items-center justify-center transition-transform duration-300"
                 :class="{ 'rotate-180': showSingleEvents }">
              <svg class="w-3 h-3 text-gray-600 dark:text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </div>
          </div>
          
          <!-- Title and Description -->
          <div>
            <h4 class="text-sm font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
              📄 {{ $t('recurringEvents.uniqueEvents') }}
            </h4>
            <p class="text-xs text-gray-600 dark:text-gray-400">
              {{ $t('common.onetimeEvents') }} • {{ selectedSinglesCount }}/{{ filteredSingleRecurringEvents.length }} {{ $t('common.selected') }}
            </p>
          </div>
        </div>
        
        <!-- Right: Actions -->
        <div class="flex items-center gap-2">
          <!-- Progress indicator -->
          <div class="hidden sm:flex items-center gap-1">
            <div class="w-12 h-1.5 bg-gray-300 dark:bg-gray-600 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gray-600 dark:bg-gray-400 transition-all duration-300"
                :style="{ width: `${filteredSingleRecurringEvents.length > 0 ? (selectedSinglesCount / filteredSingleRecurringEvents.length) * 100 : 0}%` }"
              ></div>
            </div>
            <span class="text-xs font-medium text-gray-600 dark:text-gray-400 min-w-[2rem]">
              {{ Math.round(filteredSingleRecurringEvents.length > 0 ? (selectedSinglesCount / filteredSingleRecurringEvents.length) * 100 : 0) }}%
            </span>
          </div>
          
          <!-- Select/Deselect Button -->
          <button
            @click.stop="handleSinglesToggle"
            class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200"
            :class="areAllSinglesSelected
              ? 'bg-green-100 hover:bg-green-200 text-green-700 border border-green-300 dark:bg-green-900/20 dark:hover:bg-green-900/30 dark:text-green-400 dark:border-green-600'
              : 'bg-blue-100 hover:bg-blue-200 text-blue-700 border border-blue-300 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 dark:text-blue-400 dark:border-blue-600'"
          >
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path v-if="areAllSinglesSelected" fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              <path v-else fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
            {{ areAllSinglesSelected ? $t('controls.deselectAll') : $t('controls.selectAll') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Unique Events Grid - Same styling as main events grid -->
    <div v-if="showSingleEvents">
      <div 
        class="relative"
        @mousedown="startDragSelection"
        @mousemove="updateDragSelection"
        @mouseup="endDragSelection"
        @mouseleave="endDragSelection"
      >
        <!-- Drag Selection Overlay for Single Events -->
        <div
          v-if="dragSelection.dragging"
          class="absolute pointer-events-none bg-gradient-to-br from-emerald-300 to-teal-400 dark:from-emerald-500 dark:to-teal-600 opacity-30 border-2 border-emerald-500 dark:border-emerald-400 rounded-lg shadow-lg backdrop-blur-sm"
          :style="{
            left: Math.min(dragSelection.startX, dragSelection.currentX) + 'px',
            top: Math.min(dragSelection.startY, dragSelection.currentY) + 'px',
            width: Math.abs(dragSelection.currentX - dragSelection.startX) + 'px',
            height: Math.abs(dragSelection.currentY - dragSelection.startY) + 'px',
            zIndex: 10
          }"
        >
          <div class="absolute inset-0 bg-white dark:bg-gray-900 opacity-10 rounded-lg"></div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 p-3">
          <div 
            v-for="recurringEvent in filteredSingleRecurringEvents"
            :key="recurringEvent.name"
            :ref="el => { if (el) cardRefs[`single-${recurringEvent.name}`] = el }"
            class="group/card relative bg-gray-50 dark:bg-gray-800/50 rounded-lg border-2 transition-all duration-300 cursor-pointer overflow-hidden transform hover:scale-[1.01]"
            :class="selectedRecurringEvents.includes(recurringEvent.name)
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 dark:border-blue-400 shadow-lg ring-2 ring-blue-200 dark:ring-blue-700/50 scale-[1.01]' 
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:bg-blue-25 dark:hover:bg-blue-950/10'"
            @click="handleCardClick(recurringEvent.name, $event)"
            :title="`${selectedRecurringEvents.includes(recurringEvent.name) ? $t('status.deselectEvent') : $t('status.selectEvent')} ${recurringEvent.name} • ${$t('admin.dragToSelectMultiple')}`"
          >
            <!-- Selection Indicator -->
            <div 
              class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
              :class="selectedRecurringEvents.includes(recurringEvent.name) ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'"
            ></div>
            
            <!-- Card Content -->
            <div class="p-4 relative">
              <!-- Selected Indicator Icon (top-right corner) -->
              <div 
                v-if="selectedRecurringEvents.includes(recurringEvent.name)"
                class="absolute top-2 right-2 w-5 h-5 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold shadow-sm z-10"
              >
                ✓
              </div>
              
              <!-- Header -->
              <div class="mb-3 pr-6">
                <!-- Event Title with full space -->
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 text-sm leading-tight truncate transition-colors"
                    :class="selectedRecurringEvents.includes(recurringEvent.name)
                      ? 'text-blue-700 dark:text-blue-300' 
                      : 'group-hover/card:text-blue-600 dark:group-hover/card:text-blue-400'"
                >
                  {{ recurringEvent.name.trim() }}
                </h4>
              </div>
              
              <!-- Event Details -->
              <div class="space-y-2 text-xs">
                <div class="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                  <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                  <span class="font-medium truncate">{{ formatDateRange(recurringEvent.events[0]) }}</span>
                </div>
                
                <div v-if="recurringEvent.events[0].location" class="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                  <svg class="w-3 h-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                  </svg>
                  <span class="truncate">{{ recurringEvent.events[0].location }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Drag selection state
const dragSelection = ref({
  dragging: false,
  startX: 0,
  startY: 0,
  currentX: 0,
  currentY: 0,
  initialSelection: [],
  containerRect: null
})

// Card refs for drag selection
const cardRefs = ref({})

const props = defineProps({
  singleRecurringEvents: { type: Array, default: () => [] },
  selectedRecurringEvents: { type: Array, default: () => [] },
  showSingleEvents: { type: Boolean, default: false },
  showSelectedOnly: { type: Boolean, default: false },
  searchTerm: { type: String, default: '' },
  formatDateRange: { type: Function, required: true }
})

const emit = defineEmits([
  'toggle-recurring-event',
  'toggle-singles-visibility',
  'select-all-singles',
  'clear-all-singles'
])

// Filtered events based on search and selection
const filteredSingleRecurringEvents = computed(() => {
  let recurringEvents = props.singleRecurringEvents
    .filter(recurringEvent => recurringEvent && recurringEvent.name) // Filter out null/undefined events
  
  // Filter by selection if showSelectedOnly is true
  if (props.showSelectedOnly) {
    recurringEvents = recurringEvents.filter(recurringEvent => 
      recurringEvent && recurringEvent.name && props.selectedRecurringEvents.includes(recurringEvent.name)
    )
  }
  
  // Filter by search term
  if (props.searchTerm.trim()) {
    const searchTerm = props.searchTerm.toLowerCase()
    recurringEvents = recurringEvents.filter(recurringEvent => 
      recurringEvent && recurringEvent.name && recurringEvent.name.toLowerCase().includes(searchTerm)
    )
  }
  
  return recurringEvents
})

// Singles selection state
const areAllSinglesSelected = computed(() => {
  if (filteredSingleRecurringEvents.value.length === 0) return false
  const singleNames = filteredSingleRecurringEvents.value
    .filter(recurringEvent => recurringEvent && recurringEvent.name)
    .map(recurringEvent => recurringEvent.name)
  return singleNames.every(name => props.selectedRecurringEvents.includes(name))
})

const selectedSinglesCount = computed(() => {
  const singleNames = filteredSingleRecurringEvents.value
    .filter(recurringEvent => recurringEvent && recurringEvent.name)
    .map(recurringEvent => recurringEvent.name)
  return singleNames.filter(name => props.selectedRecurringEvents.includes(name)).length
})

// Handle singles toggle button explicitly
function handleSinglesToggle() {
  if (areAllSinglesSelected.value) {
    emit('clear-all-singles')
  } else {
    emit('select-all-singles')
  }
}

// Drag selection methods
const startDragSelection = (event) => {
  // Only start drag selection on left mouse button
  if (event.button !== 0) return
  
  const containerRect = event.currentTarget.getBoundingClientRect()
  dragSelection.value = {
    dragging: true,
    startX: event.clientX - containerRect.left,
    startY: event.clientY - containerRect.top,
    currentX: event.clientX - containerRect.left,
    currentY: event.clientY - containerRect.top,
    initialSelection: [...props.selectedRecurringEvents],
    containerRect: containerRect
  }
  
  event.preventDefault()
  event.stopPropagation()
}

const updateDragSelection = (event) => {
  if (!dragSelection.value.dragging) return
  
  // Use stored container rect for stable coordinates
  const containerRect = dragSelection.value.containerRect
  dragSelection.value.currentX = event.clientX - containerRect.left
  dragSelection.value.currentY = event.clientY - containerRect.top
  
  event.preventDefault()
  event.stopPropagation()
  
  // Calculate which cards intersect with selection rectangle
  const selectionRect = {
    left: Math.min(dragSelection.value.startX, dragSelection.value.currentX),
    top: Math.min(dragSelection.value.startY, dragSelection.value.currentY),
    right: Math.max(dragSelection.value.startX, dragSelection.value.currentX),
    bottom: Math.max(dragSelection.value.startY, dragSelection.value.currentY)
  }
  
  const newSelection = [...dragSelection.value.initialSelection]
  
  // Check single recurring events
  filteredSingleRecurringEvents.value.forEach(recurringEvent => {
    const cardElement = cardRefs.value[`single-${recurringEvent.name}`]
    if (cardElement) {
      const cardRect = cardElement.getBoundingClientRect()
      const containerRect = cardElement.closest('.grid').getBoundingClientRect()
      
      const cardRelativeRect = {
        left: cardRect.left - containerRect.left,
        top: cardRect.top - containerRect.top,
        right: cardRect.right - containerRect.left,
        bottom: cardRect.bottom - containerRect.top
      }
      
      // Check if card intersects with selection rectangle
      const intersects = !(cardRelativeRect.right < selectionRect.left || 
                         cardRelativeRect.left > selectionRect.right || 
                         cardRelativeRect.bottom < selectionRect.top || 
                         cardRelativeRect.top > selectionRect.bottom)
      
      if (intersects) {
        if (!newSelection.includes(recurringEvent.name)) {
          newSelection.push(recurringEvent.name)
        }
      }
    }
  })
  
  // Emit selection updates
  const currentlySelected = props.selectedRecurringEvents
  const toDeselect = currentlySelected.filter(name => !newSelection.includes(name))
  const toSelect = newSelection.filter(name => !currentlySelected.includes(name))
  
  toDeselect.forEach(name => emit('toggle-recurring-event', name))
  toSelect.forEach(name => emit('toggle-recurring-event', name))
}

const endDragSelection = () => {
  if (!dragSelection.value.dragging) return
  
  // Check if this was just a click (minimal movement)
  const deltaX = Math.abs(dragSelection.value.currentX - dragSelection.value.startX)
  const deltaY = Math.abs(dragSelection.value.currentY - dragSelection.value.startY) 
  const wasClick = deltaX < 5 && deltaY < 5
  
  if (wasClick) {
    // Restore original selection for clicks - let normal click handler take over
    const currentlySelected = props.selectedRecurringEvents
    const originalSelection = dragSelection.value.initialSelection
    
    const toDeselect = currentlySelected.filter(name => !originalSelection.includes(name))
    const toSelect = originalSelection.filter(name => !currentlySelected.includes(name))
    
    toDeselect.forEach(name => emit('toggle-recurring-event', name))
    toSelect.forEach(name => emit('toggle-recurring-event', name))
  }
  
  // Reset drag state
  dragSelection.value.dragging = false
}

const handleCardClick = (recurringEventName, event) => {
  // If we're currently dragging, don't handle clicks
  if (dragSelection.value.dragging) {
    return
  }
  emit('toggle-recurring-event', recurringEventName)
}

// Global escape handler for drag selection cleanup
onMounted(() => {
  const handleEscape = (event) => {
    if (event.key === 'Escape' && dragSelection.value.dragging) {
      endDragSelection()
    }
  }
  
  // Global cleanup for drag state
  const handleBeforeUnload = () => {
    dragSelection.value.dragging = false
  }
  
  document.addEventListener('keydown', handleEscape)
  window.addEventListener('beforeunload', handleBeforeUnload)
  
  // Cleanup listeners on unmount
  onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape)
    window.removeEventListener('beforeunload', handleBeforeUnload)
    // Reset drag state if component unmounts during drag
    dragSelection.value.dragging = false
  })
})
</script>

<style scoped>
.touch-manipulation {
  touch-action: manipulation;
}
</style>