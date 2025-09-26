<template>
  <AdminCardWrapper
    :title="$t('admin.eventManagement')"
    :subtitle="`${recurringEvents.length} events • ${assignedEventsCount} assigned • Assign events to groups`"
    icon="📅"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Group Filter Bar -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by Group</h3>
        <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span>💡 Hold Ctrl to select multiple • Right-click to edit</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <!-- All Events Button -->
        <button
          @click="toggleGroupFilter('all', $event)"
          :class="[
            'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
            activeGroupFilters.length === 0
              ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
        >
          <span>📋</span>
          <span>All Events</span>
          <span class="text-xs opacity-75">({{ recurringEvents.length }})</span>
        </button>
        
        <!-- Unassigned Button -->
        <button
          @click="toggleGroupFilter('unassigned', $event)"
          :class="[
            'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
            activeGroupFilters.includes('unassigned')
              ? 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-200 dark:border-yellow-700'
              : selectedEvents.length > 0
              ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600 dark:hover:bg-blue-800/30 cursor-pointer transform hover:scale-105'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="'Filter unassigned events • Hold Ctrl to select multiple filters'"
        >
          <span>❔</span>
          <span>Unassigned</span>
          <span class="text-xs opacity-75">({{ unassignedEventsCount }})</span>
          <!-- Selection indicator -->
          <span 
            v-if="selectedEvents.length > 0 && getSelectedEventsInGroup('unassigned') > 0"
            class="ml-1 px-1 py-0.5 bg-blue-500 text-white rounded text-xs font-bold"
          >
            {{ getSelectedEventsInGroup('unassigned') }}
          </span>
        </button>
        
        <!-- Group Buttons with Right-Click Context Menu -->
        <button
          v-for="group in groups"
          :key="group.id"
          @click="toggleGroupFilter(group.id, $event)"
          @contextmenu.prevent="showContextMenu(group, $event)"
          :class="[
            'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
            activeGroupFilters.includes(group.id)
              ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700'
              : selectedEvents.length > 0
              ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600 dark:hover:bg-blue-800/30 cursor-pointer transform hover:scale-105'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="`Filter events by ${group.name} • Hold Ctrl to select multiple filters • Right-click for options`"
        >
          <span v-if="editingGroupId !== group.id">{{ group.name }}</span>
          <input
            v-else
            v-model="editingGroupName"
            @keyup.enter="saveGroupEdit(group.id)"
            @keyup.escape="cancelGroupEdit"
            @blur="saveGroupEdit(group.id)"
            class="min-w-0 bg-transparent border-none outline-none text-inherit font-medium"
            :style="{ width: Math.max(50, editingGroupName.length * 8) + 'px' }"
          />
          <span class="text-xs opacity-75">({{ getGroupEventCount(group.id) }})</span>
          <!-- Selection indicator -->
          <span 
            v-if="selectedEvents.length > 0 && getSelectedEventsInGroup(group.id) > 0"
            class="ml-1 px-1 py-0.5 bg-blue-500 text-white rounded text-xs font-bold"
          >
            {{ getSelectedEventsInGroup(group.id) }}
          </span>
        </button>
        
        <!-- Add Group Button -->
        <button
          v-if="!showAddGroupForm"
          @click="startAddGroup"
          class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border border-dashed border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-green-400 hover:text-green-600 dark:hover:text-green-400"
        >
          <span>➕</span>
          <span>Add Group</span>
        </button>
        
        <!-- Add Group Form -->
        <div v-else class="inline-flex items-center gap-2">
          <input
            v-model="newGroupName"
            @keyup.enter="createGroup"
            @keyup.escape="cancelAddGroup"
            @blur="handleAddGroupBlur"
            placeholder="Group name..."
            class="px-3 py-2 border border-green-300 dark:border-green-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 text-sm min-w-32"
            ref="newGroupInput"
          />
          <button
            @click="createGroup"
            :disabled="!newGroupName.trim()"
            class="px-2 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded text-sm"
          >
            ✓
          </button>
          <button
            @click="cancelAddGroup"
            class="px-2 py-1 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 rounded text-sm"
          >
            ✗
          </button>
        </div>
      </div>
    </div>
    
    <!-- Context Menu -->
    <div
      v-if="contextMenu.visible"
      :style="{
        position: 'fixed',
        top: contextMenu.y + 'px',
        left: contextMenu.x + 'px',
        zIndex: 1000
      }"
      class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg py-1 min-w-32"
      @click.stop
    >
      <button
        @click="editGroupFromMenu"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
      >
        <span>✏️</span>
        <span>Edit Name</span>
      </button>
      <button
        @click="deleteGroupFromMenu"
        class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 flex items-center gap-2"
      >
        <span>🗑️</span>
        <span>Delete Group</span>
      </button>
    </div>
    
    <!-- Bulk Assignment Panel (shown when events are selected) -->
    <div v-if="selectedEvents.length > 0" class="bg-white dark:bg-gray-800 border-2 border-blue-300 dark:border-blue-600 rounded-lg p-4 shadow-sm">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
            <span class="text-blue-600 dark:text-blue-400 text-sm font-bold">{{ selectedEvents.length }}</span>
          </div>
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white">Bulk Actions</h4>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ selectedEvents.length }} event{{ selectedEvents.length > 1 ? 's' : '' }} selected
            </p>
          </div>
        </div>
        <button 
          @click="clearEventSelection"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded"
          title="Clear selection"
        >
          <span class="text-xl">×</span>
        </button>
      </div>
      
      <!-- Assignment Actions -->
      <div class="flex flex-wrap gap-2">
        <!-- Add to Group Buttons -->
        <div class="flex flex-wrap gap-1">
          <span class="text-xs font-medium text-gray-700 dark:text-gray-300 px-2 py-1">Add to:</span>
          <button
            v-for="group in groups"
            :key="`add-${group.id}`"
            @click="handleGroupAssignment(group.id, [...selectedEvents])"
            class="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium transition-all duration-200 border border-green-300 dark:border-green-600 text-green-700 dark:text-green-300 hover:bg-green-50 dark:hover:bg-green-900/20"
            :title="`Add ${selectedEvents.length} events to ${group.name}`"
          >
            <span>+</span>
            <span>{{ group.name }}</span>
            <span 
              v-if="getSelectedEventsInGroup(group.id) > 0"
              class="ml-1 px-1 py-0.5 bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200 rounded text-xs"
            >
              {{ getSelectedEventsInGroup(group.id) }}
            </span>
          </button>
        </div>
        
        <!-- Remove from Group Buttons (only show groups that have selected events) -->
        <div 
          v-if="Object.keys(selectedEventsGroupDistribution).some(id => id !== 'unassigned' && selectedEventsGroupDistribution[id] > 0)"
          class="flex flex-wrap gap-1 ml-4"
        >
          <span class="text-xs font-medium text-gray-700 dark:text-gray-300 px-2 py-1">Remove from:</span>
          <button
            v-for="groupId in Object.keys(selectedEventsGroupDistribution).filter(id => id !== 'unassigned' && selectedEventsGroupDistribution[id] > 0)"
            :key="`remove-${groupId}`"
            @click="handleRemoveFromGroup(groupId, [...selectedEvents])"
            class="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium transition-all duration-200 border border-red-300 dark:border-red-600 text-red-700 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
            :title="`Remove ${getSelectedEventsInGroup(groupId)} events from ${groups.find(g => g.id == groupId)?.name}`"
          >
            <span>−</span>
            <span>{{ groups.find(g => g.id == groupId)?.name }}</span>
            <span class="ml-1 px-1 py-0.5 bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200 rounded text-xs">
              {{ selectedEventsGroupDistribution[groupId] }}
            </span>
          </button>
        </div>
        
        <!-- Unassign All Button -->
        <button
          @click="handleGroupAssignment('unassigned', [...selectedEvents])"
          class="inline-flex items-center gap-1 px-3 py-1 rounded-md text-xs font-medium transition-all duration-200 border border-yellow-300 dark:border-yellow-600 text-yellow-700 dark:text-yellow-300 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 ml-4"
          :title="`Remove ${selectedEvents.length} events from all groups`"
        >
          <span>🚫</span>
          <span>Unassign All</span>
        </button>
      </div>
    </div>
    
    <!-- Events Table -->
    <div class="space-y-4">
      <!-- Search and Controls -->
      <div class="flex items-center justify-between gap-4">
        <div class="flex-1 relative">
          <input
            v-model="eventSearch"
            type="text"
            :placeholder="activeGroupFilters.length > 0 ? 'Search in filtered groups...' : 'Search events...'"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            :class="{ 'pr-32': activeGroupFilters.length > 0 }"
          />
          <!-- Clear Filter Button - shows when filtering by specific groups -->
          <button
            v-if="activeGroupFilters.length > 0"
            @click="clearGroupFilters"
            class="absolute right-2 top-1/2 -translate-y-1/2 px-2 py-1 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors flex items-center gap-1"
            title="Clear group filters to search in all groups"
          >
            <span>🔍</span>
            <span>All Groups</span>
          </button>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="toggleSelectAllEvents"
            class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 border flex items-center gap-2"
            :class="[
              isAllEventsSelected 
                ? 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700 dark:hover:bg-green-800/30'
                : isSomeEventsSelected
                ? 'bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700 dark:hover:bg-blue-800/30'
                : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
            ]"
            :title="isAllEventsSelected ? `Deselect all ${filteredEvents.length} visible events` : `Select all ${filteredEvents.length} visible events`"
          >
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all"
              :class="isAllEventsSelected
                ? 'bg-green-500 border-green-500 text-white' 
                : isSomeEventsSelected
                ? 'bg-blue-500 border-blue-500 text-white'
                : 'border-gray-400 bg-white dark:bg-gray-700 dark:border-gray-500'"
            >
              <span v-if="isAllEventsSelected">✓</span>
              <span v-else-if="isSomeEventsSelected">−</span>
            </div>
            <span v-if="isAllEventsSelected">All Selected</span>
            <span v-else-if="isSomeEventsSelected">{{ selectedEvents.length }} Selected</span>
            <span v-else>Select All</span>
          </button>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ filteredEvents.length }} event{{ filteredEvents.length !== 1 ? 's' : '' }} shown
          </span>
        </div>
      </div>
      
      <!-- Events Table -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="w-12 px-4 py-3 text-left">
                <input
                  type="checkbox"
                  :checked="isAllEventsSelected"
                  :indeterminate="isSomeEventsSelected && !isAllEventsSelected"
                  @change="toggleSelectAllEvents"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  :title="`Select all ${filteredEvents.length} visible events`"
                />
              </th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Event</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Group</th>
              <th class="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300">Occurrences</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="event in filteredEvents"
              :key="event.title"
              @click="toggleEventSelection(event.title)"
              :class="[
                'hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer',
                selectedEvents.includes(event.title) ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              ]"
            >
              <td class="px-4 py-3">
                <input
                  type="checkbox"
                  :checked="selectedEvents.includes(event.title)"
                  @change="toggleEventSelection(event.title)"
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </td>
              <td class="px-4 py-3">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ event.title }}
                </div>
              </td>
              <td class="px-4 py-3">
                <!-- Multi-Group Display -->
                <div v-if="event.assigned_groups && event.assigned_groups.length > 0" class="flex flex-wrap gap-1">
                  <!-- Primary Group Badge -->
                  <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200">
                    {{ event.assigned_groups[0].name }}
                  </span>
                  <!-- Additional Groups (max 2 more shown) -->
                  <span 
                    v-for="group in event.assigned_groups.slice(1, 3)" 
                    :key="group.id"
                    class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200"
                  >
                    {{ group.name }}
                  </span>
                  <!-- Overflow Indicator with Popover -->
                  <div 
                    v-if="event.assigned_groups.length > 3"
                    class="relative inline-block"
                  >
                    <span 
                      @click="toggleGroupPopover(event.title)"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                      :title="'Click to see all groups'"
                    >
                      +{{ event.assigned_groups.length - 3 }} more
                    </span>
                    <!-- Groups Popover -->
                    <div 
                      v-if="groupPopover.visible && groupPopover.eventTitle === event.title"
                      class="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 min-w-48 z-50"
                      @click.stop
                    >
                      <div class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">All Groups:</div>
                      <div class="space-y-1">
                        <div 
                          v-for="group in event.assigned_groups"
                          :key="group.id"
                          class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium mr-1 mb-1"
                          :class="[
                            group === event.assigned_groups[0] 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'
                              : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200'
                          ]"
                        >
                          {{ group.name }}
                          <span v-if="group === event.assigned_groups[0]" class="text-xs opacity-75">(primary)</span>
                        </div>
                      </div>
                      <button 
                        @click="closeGroupPopover" 
                        class="mt-2 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </div>
                <!-- Unassigned State -->
                <span v-else class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200">
                  ❔ Unassigned
                </span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                {{ event.event_count }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="filteredEvents.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        <div class="text-4xl mb-2">📅</div>
        <p>No events found matching your criteria</p>
      </div>
    </div>
  </AdminCardWrapper>
  
  <!-- Delete Group Confirmation Dialog -->
  <ConfirmDialog
    ref="deleteConfirmDialog"
    title="Delete Group"
    :message="deleteConfirmMessage"
    confirm-text="Delete Group"
    cancel-text="Cancel"
    @confirm="confirmDeleteGroup"
    @cancel="cancelDeleteGroup"
  />
</template>

<script>
import { ref, computed, nextTick } from 'vue'
import AdminCardWrapper from './AdminCardWrapper.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'

export default {
  name: 'EventManagementCard',
  components: {
    AdminCardWrapper,
    ConfirmDialog
  },
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    recurringEvents: {
      type: Array,
      default: () => []
    },
    groups: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'toggle', 'create-group', 'update-group', 'delete-group', 'handle-group-assignment',
    'toggle-group-filter', 'toggle-select-all-events', 'toggle-event-selection',
    'clear-event-selection', 'remove-from-group'
  ],
  setup(props, { emit }) {
    // Local state
    const eventSearch = ref('')
    const selectedEvents = ref([])
    const activeGroupFilters = ref([])
    const newGroupName = ref('')
    const showAddGroupForm = ref(false)
    const editingGroupId = ref(null)
    const editingGroupName = ref('')
    const newGroupInput = ref(null)
    const contextMenu = ref({ visible: false, x: 0, y: 0, group: null })
    const deleteConfirmDialog = ref(null)
    const deleteConfirmMessage = ref('')
    const groupToDelete = ref(null)
    const groupPopover = ref({ visible: false, eventTitle: null })
    
    // Computed properties
    const totalEventCount = computed(() => {
      return props.recurringEvents
        .reduce((total, event) => total + (event.event_count || 1), 0)
    })
    
    const assignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.length > 0
      }).length
    })
    
    const unassignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.length === 0
      }).length
    })
    
    const filteredEvents = computed(() => {
      let filtered = props.recurringEvents
      
      // Apply group filters (support multi-group assignments)
      if (activeGroupFilters.value.length > 0) {
        filtered = filtered.filter(event => {
          // Handle unassigned filter
          if (activeGroupFilters.value.includes('unassigned') && (!event.assigned_group_ids || event.assigned_group_ids.length === 0)) {
            return true
          }
          
          // Handle group filters - check if event belongs to any of the active filter groups
          const eventGroupIds = event.assigned_group_ids || []
          return eventGroupIds.some(groupId => activeGroupFilters.value.includes(groupId))
        })
      }
      
      // Apply search filter
      if (eventSearch.value.trim()) {
        const search = eventSearch.value.toLowerCase().trim()
        filtered = filtered.filter(event => 
          event.title.toLowerCase().includes(search) ||
          (event.description || '').toLowerCase().includes(search)
        )
      }
      
      // Group by title and preserve API event_count, also compute group information
      const eventsByTitle = {}
      filtered.forEach(event => {
        if (!eventsByTitle[event.title]) {
          // Handle multi-group assignments from API
          const assignedGroupIds = event.assigned_group_ids || []
          const assignedGroups = assignedGroupIds.map(groupId => 
            props.groups.find(g => g.id === groupId)
          ).filter(Boolean) // Remove null/undefined results
          
          eventsByTitle[event.title] = {
            ...event,
            // Keep the original event_count from API instead of resetting to 0
            group_id: event.assigned_group_id, // Map for backward compatibility  
            group_name: assignedGroups[0]?.name || null, // Primary group for backward compatibility
            // Multi-group support
            assigned_group_ids: assignedGroupIds,
            assigned_groups: assignedGroups
          }
        }
        // Don't increment event_count since API already provides the correct value
      })
      
      return Object.values(eventsByTitle)
    })
    
    const isAllEventsSelected = computed(() => {
      return filteredEvents.value.length > 0 && 
             filteredEvents.value.every(event => selectedEvents.value.includes(event.title))
    })
    
    const isSomeEventsSelected = computed(() => {
      return selectedEvents.value.length > 0 && selectedEvents.value.length < filteredEvents.value.length
    })
    
    // Selection group distribution for smart filter buttons
    const selectedEventsGroupDistribution = computed(() => {
      const distribution = {}
      
      selectedEvents.value.forEach(eventTitle => {
        const event = props.recurringEvents.find(e => e.title === eventTitle)
        if (event) {
          const eventGroupIds = event.assigned_group_ids || []
          
          if (eventGroupIds.length === 0) {
            // Unassigned event
            distribution['unassigned'] = (distribution['unassigned'] || 0) + 1
          } else {
            // Event with group assignments
            eventGroupIds.forEach(groupId => {
              distribution[groupId] = (distribution[groupId] || 0) + 1
            })
          }
        }
      })
      
      return distribution
    })
    
    const getSelectedEventsInGroup = (groupId) => {
      return selectedEventsGroupDistribution.value[groupId] || 0
    }
    
    // Methods - Filter mode (clear separation from assignment)
    const toggleGroupFilter = (groupId, event) => {
      const isCtrlClick = event.ctrlKey || event.metaKey
      emit('toggle-group-filter', groupId, isCtrlClick, activeGroupFilters.value)
      
      if (!isCtrlClick) {
        activeGroupFilters.value = groupId === 'all' ? [] : [groupId]
      } else {
        if (groupId === 'all') {
          activeGroupFilters.value = []
        } else {
          const index = activeGroupFilters.value.indexOf(groupId)
          if (index > -1) {
            activeGroupFilters.value.splice(index, 1)
          } else {
            activeGroupFilters.value.push(groupId)
          }
        }
      }
    }
    
    const toggleSelectAllEvents = () => {
      emit('toggle-select-all-events', isAllEventsSelected.value, filteredEvents.value.map(e => e.title))
      
      if (isAllEventsSelected.value) {
        selectedEvents.value = []
      } else {
        selectedEvents.value = filteredEvents.value.map(event => event.title)
      }
    }
    
    const toggleEventSelection = (eventTitle) => {
      emit('toggle-event-selection', eventTitle)
      
      const index = selectedEvents.value.indexOf(eventTitle)
      if (index > -1) {
        selectedEvents.value.splice(index, 1)
      } else {
        selectedEvents.value.push(eventTitle)
      }
    }
    
    const clearEventSelection = () => {
      emit('clear-event-selection')
      selectedEvents.value = []
    }
    
    const clearGroupFilters = () => {
      activeGroupFilters.value = []
    }
    
    const getGroupEventCount = (groupId) => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.includes(groupId)
      }).length
    }
    
    const createGroup = async () => {
      if (!newGroupName.value.trim()) return
      
      emit('create-group', newGroupName.value.trim())
      newGroupName.value = ''
      showAddGroupForm.value = false
    }
    
    const cancelAddGroup = () => {
      newGroupName.value = ''
      showAddGroupForm.value = false
    }
    
    const handleAddGroupBlur = () => {
      // Small delay to allow click events on buttons to fire first
      setTimeout(() => {
        if (document.activeElement !== newGroupInput.value) {
          cancelAddGroup()
        }
      }, 150)
    }
    
    const startEditingGroup = async (group, event) => {
      if (event) event.preventDefault()
      editingGroupId.value = group.id
      editingGroupName.value = group.name
      
      await nextTick()
      // Focus the input after it's rendered
      const input = document.querySelector(`input[value="${group.name}"]`) || 
                    document.querySelector('input[class*="bg-transparent"]')
      if (input) {
        input.focus()
        input.select()
      }
    }
    
    const saveGroupEdit = async (groupId) => {
      if (!editingGroupName.value.trim()) {
        cancelGroupEdit()
        return
      }
      
      emit('update-group', groupId, editingGroupName.value.trim())
      editingGroupId.value = null
      editingGroupName.value = ''
    }
    
    const cancelGroupEdit = () => {
      editingGroupId.value = null
      editingGroupName.value = ''
    }
    
    const startAddGroup = async () => {
      showAddGroupForm.value = true
      await nextTick()
      // Focus the input after it's rendered
      if (newGroupInput.value) {
        newGroupInput.value.focus()
      }
    }
    
    const deleteGroupConfirm = (group) => {
      groupToDelete.value = group
      deleteConfirmMessage.value = `Are you sure you want to delete the group "${group.name}"? This will unassign all events from this group.`
      deleteConfirmDialog.value.open()
    }
    
    const confirmDeleteGroup = () => {
      if (groupToDelete.value) {
        emit('delete-group', groupToDelete.value.id)
        groupToDelete.value = null
      }
    }
    
    const cancelDeleteGroup = () => {
      groupToDelete.value = null
    }
    
    const showContextMenu = (group, event) => {
      contextMenu.value = {
        visible: true,
        x: event.clientX,
        y: event.clientY,
        group: group
      }
      
      // Close context menu when clicking elsewhere
      const closeMenu = () => {
        contextMenu.value.visible = false
        document.removeEventListener('click', closeMenu)
      }
      
      setTimeout(() => {
        document.addEventListener('click', closeMenu)
      }, 0)
    }
    
    const editGroupFromMenu = () => {
      startEditingGroup(contextMenu.value.group)
      contextMenu.value.visible = false
    }
    
    const deleteGroupFromMenu = () => {
      deleteGroupConfirm(contextMenu.value.group)
      contextMenu.value.visible = false
    }
    
    const toggleGroupPopover = (eventTitle) => {
      if (groupPopover.value.visible && groupPopover.value.eventTitle === eventTitle) {
        closeGroupPopover()
      } else {
        groupPopover.value = {
          visible: true,
          eventTitle: eventTitle
        }
        
        // Close popover when clicking elsewhere
        const closePopover = () => {
          closeGroupPopover()
          document.removeEventListener('click', closePopover)
        }
        
        setTimeout(() => {
          document.addEventListener('click', closePopover)
        }, 0)
      }
    }
    
    const closeGroupPopover = () => {
      groupPopover.value = { visible: false, eventTitle: null }
    }
    
    // Assignment mode methods
    const handleRemoveFromGroup = async (groupId, eventTitles) => {
      // Get events that are currently in this specific group
      const eventsInGroup = eventTitles.filter(title => {
        const event = props.recurringEvents.find(e => e.title === title)
        return event && event.assigned_group_ids && event.assigned_group_ids.includes(parseInt(groupId))
      })
      
      if (eventsInGroup.length === 0) {
        return // No events to remove from this group
      }
      
      try {
        // We need to implement a "remove from specific group" API call
        // For now, we'll emit this and let the parent handle it
        emit('remove-from-group', groupId, eventsInGroup)
        selectedEvents.value = []
      } catch (error) {
        console.error('Failed to remove events from group:', error)
      }
    }
    
    return {
      // State
      eventSearch,
      selectedEvents,
      activeGroupFilters,
      newGroupName,
      showAddGroupForm,
      editingGroupId,
      editingGroupName,
      newGroupInput,
      contextMenu,
      deleteConfirmDialog,
      deleteConfirmMessage,
      groupToDelete,
      groupPopover,
      
      // Computed
      totalEventCount,
      assignedEventsCount,
      unassignedEventsCount,
      filteredEvents,
      isAllEventsSelected,
      isSomeEventsSelected,
      selectedEventsGroupDistribution,
      
      // Methods
      toggleGroupFilter,
      toggleSelectAllEvents,
      toggleEventSelection,
      clearEventSelection,
      clearGroupFilters,
      getGroupEventCount,
      getSelectedEventsInGroup,
      createGroup,
      cancelAddGroup,
      handleAddGroupBlur,
      startAddGroup,
      startEditingGroup,
      saveGroupEdit,
      cancelGroupEdit,
      deleteGroupConfirm,
      confirmDeleteGroup,
      cancelDeleteGroup,
      showContextMenu,
      editGroupFromMenu,
      deleteGroupFromMenu,
      toggleGroupPopover,
      closeGroupPopover,
      handleRemoveFromGroup
    }
  }
}
</script>

<style scoped>
/* Custom checkbox indeterminate styling */
input[type="checkbox"]:indeterminate {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

input[type="checkbox"]:indeterminate:after {
  content: '';
  display: block;
  width: 8px;
  height: 2px;
  background-color: white;
  margin: 2px auto;
}
</style>