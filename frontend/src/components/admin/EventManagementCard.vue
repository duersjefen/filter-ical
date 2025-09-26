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
          :title="selectedEvents.length > 0 ? `Click to assign ${selectedEvents.length} selected events to Unassigned` : 'Filter unassigned events'"
        >
          <span>❔</span>
          <span>Unassigned</span>
          <span class="text-xs opacity-75">({{ unassignedEventsCount }})</span>
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
          :title="selectedEvents.length > 0 ? `Click to assign ${selectedEvents.length} selected events to ${group.name}` : `Filter events by ${group.name} • Right-click for options`"
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
    
    <!-- Assignment Instructions -->
    <div v-if="selectedEvents.length > 0" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
      <div class="flex items-center gap-3">
        <span class="text-blue-600 dark:text-blue-400 text-lg">👆</span>
        <div>
          <h4 class="font-medium text-blue-800 dark:text-blue-200 mb-1">Assignment Mode Active</h4>
          <p class="text-sm text-blue-700 dark:text-blue-300">
            {{ selectedEvents.length }} event{{ selectedEvents.length > 1 ? 's' : '' }} selected. 
            Click a group above to assign {{ selectedEvents.length > 1 ? 'them' : 'it' }}, or click 
            <button @click="clearEventSelection" class="underline hover:no-underline">here to clear selection</button>.
          </p>
        </div>
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
                <span v-if="event.group_name" class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200">
                  {{ event.group_name }}
                </span>
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
    'clear-event-selection'
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
    
    // Computed properties
    const totalEventCount = computed(() => {
      return props.recurringEvents
        .reduce((total, event) => total + (event.event_count || 1), 0)
    })
    
    const assignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => event.assigned_group_id).length
    })
    
    const unassignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => !event.assigned_group_id).length
    })
    
    const filteredEvents = computed(() => {
      let filtered = props.recurringEvents
      
      // Apply group filters
      if (activeGroupFilters.value.length > 0) {
        filtered = filtered.filter(event => {
          if (activeGroupFilters.value.includes('unassigned') && !event.assigned_group_id) return true
          return activeGroupFilters.value.includes(event.assigned_group_id)
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
      
      // Group by title and preserve API event_count, also compute group_name
      const eventsByTitle = {}
      filtered.forEach(event => {
        if (!eventsByTitle[event.title]) {
          // Find the group name from the groups prop
          const group = props.groups.find(g => g.id === event.assigned_group_id)
          eventsByTitle[event.title] = {
            ...event,
            // Keep the original event_count from API instead of resetting to 0
            group_id: event.assigned_group_id, // Map for backward compatibility
            group_name: group ? group.name : null
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
    
    // Methods
    const toggleGroupFilter = (groupId, event) => {
      if (selectedEvents.value.length > 0) {
        emit('handle-group-assignment', groupId, [...selectedEvents.value])
        selectedEvents.value = []
        return
      }
      
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
      return props.recurringEvents.filter(event => event.assigned_group_id === groupId).length
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
      
      // Computed
      totalEventCount,
      assignedEventsCount,
      unassignedEventsCount,
      filteredEvents,
      isAllEventsSelected,
      isSomeEventsSelected,
      
      // Methods
      toggleGroupFilter,
      toggleSelectAllEvents,
      toggleEventSelection,
      clearEventSelection,
      clearGroupFilters,
      getGroupEventCount,
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
      deleteGroupFromMenu
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