<template>
  <AdminCardWrapper
    :title="$t('domainAdmin.eventManagement')"
    :subtitle="`${recurringEvents.length} events • ${assignedEventsCount} assigned • Assign events to groups`"
    icon="📅"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Group Filter Bar -->
    <GroupFilterBar
      :groups="groups"
      :active-group-filters="activeGroupFilters"
      :total-events-count="recurringEvents.length"
      :unassigned-events-count="unassignedEventsCount"
      :editing-group-id="editingGroupId"
      :editing-group-name="editingGroupName"
      :show-add-group-form="showAddGroupForm"
      :new-group-name="newGroupName"
      :get-group-event-count="getGroupEventCount"
      @toggle-group-filter="toggleGroupFilter"
      @show-context-menu="showContextMenu"
      @start-add-group="startAddGroup"
      @create-group="createGroup"
      @cancel-add-group="cancelAddGroup"
      @save-group-edit="saveGroupEdit"
      @cancel-group-edit="cancelGroupEdit"
    />

    <!-- Group Context Menu -->
    <GroupContextMenu
      :context-menu="contextMenu"
      @edit-group="editGroupFromMenu"
      @delete-group="deleteGroupFromMenu"
    />

    <!-- Event Context Menu -->
    <EventContextMenu
      :event-context-menu="eventContextMenu"
      :groups="groups"
      @add-to-group="quickAddToGroup"
      @remove-from-group="quickRemoveFromGroup"
    />

    <!-- Bulk Assignment Panel -->
    <BulkAssignmentPanel
      :groups="groups"
      :selected-events="selectedEvents"
      :recurring-events="recurringEvents"
      :is-updating-groups="isUpdatingGroups"
      :drag-selection="dragSelection"
      :get-smart-group-action="getSmartGroupAction"
      :is-group-updating="isGroupUpdating"
      @smart-group-action="handleSmartGroupAction"
      @unassign-all="handleUnassignAll"
    />

    <!-- Event Search Controls -->
    <EventSearchControls
      v-model:event-search="eventSearch"
      v-model:show-selected-only="showSelectedOnly"
      :selected-events="selectedEvents"
      :filtered-events="filteredEvents"
      :active-group-filters="activeGroupFilters"
      :is-all-events-selected="isAllEventsSelected"
      :is-some-events-selected="isSomeEventsSelected"
      :has-hidden-selected-events="hasHiddenSelectedEvents"
      @toggle-select-all="toggleSelectAllEvents"
      @clear-selection="clearEventSelection"
      @show-selected="showAllSelectedEvents"
    />

    <!-- Events Table -->
    <EventCardGrid
      :filtered-events="filteredEvents"
      :selected-events="selectedEvents"
      :drag-selection="dragSelection"
      :card-refs="cardRefs"
      :get-group-color-classes="getGroupColorClasses"
      @mousedown="startDragSelection"
      @mousemove="updateDragSelection"
      @mouseup="endDragSelection"
      @mouseleave="endDragSelection"
      @card-click="handleEventCardClick"
      @card-contextmenu="showEventContextMenu"
    />
  </AdminCardWrapper>

  <!-- Delete Group Confirmation Dialog -->
  <ConfirmDialog
    ref="deleteConfirmDialog"
    :title="t('domainAdmin.deleteGroup')"
    :message="deleteConfirmMessage"
    :confirm-text="t('domainAdmin.deleteGroup')"
    :cancel-text="t('domainAdmin.cancel')"
    @confirm="confirmDeleteGroup"
    @cancel="cancelDeleteGroup"
  />
</template>

<script>
import { ref, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AdminCardWrapper from './AdminCardWrapper.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'
import GroupFilterBar from './event-management/GroupFilterBar.vue'
import GroupContextMenu from './event-management/GroupContextMenu.vue'
import EventContextMenu from './event-management/EventContextMenu.vue'
import BulkAssignmentPanel from './event-management/BulkAssignmentPanel.vue'
import EventSearchControls from './event-management/EventSearchControls.vue'
import EventCardGrid from './event-management/EventCardGrid.vue'
import { useDragSelection } from '../../composables/useDragSelection'

export default {
  name: 'EventManagementCard',
  components: {
    AdminCardWrapper,
    ConfirmDialog,
    GroupFilterBar,
    GroupContextMenu,
    EventContextMenu,
    BulkAssignmentPanel,
    EventSearchControls,
    EventCardGrid
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
    const { t } = useI18n()

    // Local state
    const eventSearch = ref('')
    const selectedEvents = ref([])
    const activeGroupFilters = ref([])
    const showSelectedOnly = ref(false)
    const newGroupName = ref('')
    const showAddGroupForm = ref(false)
    const editingGroupId = ref(null)
    const editingGroupName = ref('')
    const newGroupInput = ref(null)
    const contextMenu = ref({ visible: false, x: 0, y: 0, group: null })
    const eventContextMenu = ref({ visible: false, x: 0, y: 0, event: null })
    const deleteConfirmDialog = ref(null)
    const deleteConfirmMessage = ref('')
    const groupToDelete = ref(null)

    // Loading and visual feedback state
    const isUpdatingGroups = ref(false)
    const updatingGroupIds = ref(new Set())
    const optimisticUpdates = ref(new Map())

    // Card refs for drag selection
    const cardRefs = ref({})

    // Clear selection when search text changes
    watch(eventSearch, (newSearch, oldSearch) => {
      if (newSearch !== oldSearch && selectedEvents.value.length > 0) {
        selectedEvents.value = []
        emit('clear-event-selection')
        showSelectedOnly.value = false
      }
    })

    // Computed properties
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

      if (showSelectedOnly.value) {
        filtered = filtered.filter(event => selectedEvents.value.includes(event.title))
      } else {
        if (activeGroupFilters.value.length > 0) {
          filtered = filtered.filter(event => {
            if (activeGroupFilters.value.includes('unassigned') && (!event.assigned_group_ids || event.assigned_group_ids.length === 0)) {
              return true
            }

            const eventGroupIds = event.assigned_group_ids || []
            return eventGroupIds.some(groupId => activeGroupFilters.value.includes(groupId))
          })
        }

        if (eventSearch.value.trim()) {
          const search = eventSearch.value.toLowerCase().trim()
          filtered = filtered.filter(event =>
            event.title.toLowerCase().includes(search) ||
            (event.description || '').toLowerCase().includes(search)
          )
        }
      }

      // Group by title and preserve API event_count
      const eventsByTitle = {}
      filtered.forEach(event => {
        if (!eventsByTitle[event.title]) {
          const assignedGroupIds = event.assigned_group_ids || []
          const assignedGroups = assignedGroupIds.map(groupId =>
            props.groups.find(g => g.id === groupId)
          ).filter(Boolean)

          eventsByTitle[event.title] = {
            ...event,
            group_id: event.assigned_group_id,
            group_name: assignedGroups[0]?.name || null,
            assigned_group_ids: assignedGroupIds,
            assigned_groups: assignedGroups
          }
        }
      })

      return Object.values(eventsByTitle)
    })

    // Use drag selection composable (must be after filteredEvents is defined)
    const {
      dragSelection,
      startDragSelection,
      updateDragSelection,
      endDragSelection
    } = useDragSelection(selectedEvents, cardRefs, filteredEvents, emit)

    const isAllEventsSelected = computed(() => {
      return filteredEvents.value.length > 0 &&
             filteredEvents.value.every(event => selectedEvents.value.includes(event.title))
    })

    const isSomeEventsSelected = computed(() => {
      return selectedEvents.value.length > 0 && selectedEvents.value.length < filteredEvents.value.length
    })

    const selectedEventsGroupDistribution = computed(() => {
      const distribution = {}

      selectedEvents.value.forEach(eventTitle => {
        const event = props.recurringEvents.find(e => e.title === eventTitle)
        if (event) {
          const eventGroupIds = event.assigned_group_ids || []

          if (eventGroupIds.length === 0) {
            distribution['unassigned'] = (distribution['unassigned'] || 0) + 1
          } else {
            eventGroupIds.forEach(groupId => {
              distribution[groupId] = (distribution[groupId] || 0) + 1
            })
          }
        }
      })

      return distribution
    })

    const hasHiddenSelectedEvents = computed(() => {
      return selectedEvents.value.filter(eventTitle => {
        return !filteredEvents.value.some(event => event.title === eventTitle)
      }).length > 0
    })

    const getSelectedEventsInGroup = (groupId) => {
      return selectedEventsGroupDistribution.value[groupId] || 0
    }

    const getGroupActionState = (groupId) => {
      const eventsInGroup = getSelectedEventsInGroup(groupId)
      const eventsNotInGroup = selectedEvents.value.length - eventsInGroup
      const totalSelected = selectedEvents.value.length

      return {
        eventsInGroup,
        eventsNotInGroup,
        totalSelected,
        hasEventsInGroup: eventsInGroup > 0,
        hasEventsNotInGroup: eventsNotInGroup > 0,
        allInGroup: eventsInGroup === totalSelected && totalSelected > 0,
        noneInGroup: eventsInGroup === 0,
        mixedState: eventsInGroup > 0 && eventsNotInGroup > 0
      }
    }

    const getSmartGroupAction = (groupId) => {
      const state = getGroupActionState(groupId)

      if (state.noneInGroup) {
        return {
          type: 'single',
          primaryAction: 'add',
          primaryLabel: `+ Add ${state.totalSelected} to`,
          primaryCount: state.eventsNotInGroup,
          primaryStyle: 'add'
        }
      } else if (state.allInGroup) {
        return {
          type: 'single',
          primaryAction: 'remove',
          primaryLabel: `− Remove ${state.totalSelected} from`,
          primaryCount: state.eventsInGroup,
          primaryStyle: 'remove'
        }
      } else {
        const addIsPrimary = state.eventsNotInGroup >= state.eventsInGroup

        return {
          type: 'split',
          primaryAction: addIsPrimary ? 'add' : 'remove',
          primaryLabel: addIsPrimary ? `+ Add ${state.eventsNotInGroup} to` : `− Remove ${state.eventsInGroup} from`,
          primaryCount: addIsPrimary ? state.eventsNotInGroup : state.eventsInGroup,
          primaryStyle: addIsPrimary ? 'add' : 'remove',
          secondaryAction: addIsPrimary ? 'remove' : 'add',
          secondaryLabel: addIsPrimary ? `− ${state.eventsInGroup}` : `+ ${state.eventsNotInGroup}`,
          secondaryCount: addIsPrimary ? state.eventsInGroup : state.eventsNotInGroup,
          secondaryStyle: addIsPrimary ? 'remove' : 'add'
        }
      }
    }

    // Methods
    const toggleGroupFilter = (groupId, event) => {
      const isCtrlClick = event.ctrlKey || event.metaKey
      emit('toggle-group-filter', groupId, isCtrlClick, activeGroupFilters.value)

      eventSearch.value = ''
      selectedEvents.value = []
      emit('clear-event-selection')
      showSelectedOnly.value = false

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
      showSelectedOnly.value = false
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

    const startAddGroup = async () => {
      showAddGroupForm.value = true
      await nextTick()
      if (newGroupInput.value) {
        newGroupInput.value.focus()
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

    const deleteGroupConfirm = (group) => {
      groupToDelete.value = group
      deleteConfirmMessage.value = t('domainAdmin.confirmDeleteGroup', { name: group.name })
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

      const closeMenu = () => {
        contextMenu.value.visible = false
        document.removeEventListener('click', closeMenu)
      }

      setTimeout(() => {
        document.addEventListener('click', closeMenu)
      }, 0)
    }

    const editGroupFromMenu = () => {
      const group = contextMenu.value.group
      editingGroupId.value = group.id
      editingGroupName.value = group.name
      contextMenu.value.visible = false

      nextTick(() => {
        const input = document.querySelector(`input[value="${group.name}"]`) ||
                      document.querySelector('input[class*="bg-transparent"]')
        if (input) {
          input.focus()
          input.select()
        }
      })
    }

    const deleteGroupFromMenu = () => {
      deleteGroupConfirm(contextMenu.value.group)
      contextMenu.value.visible = false
    }

    const showEventContextMenu = (event, mouseEvent) => {
      eventContextMenu.value = {
        visible: true,
        x: mouseEvent.clientX,
        y: mouseEvent.clientY,
        event: event
      }

      const closeMenu = () => {
        eventContextMenu.value.visible = false
        document.removeEventListener('click', closeMenu)
      }

      setTimeout(() => {
        document.addEventListener('click', closeMenu)
      }, 0)
    }

    const groupColorPalette = [
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' }
    ]

    const getGroupColors = (groupId) => {
      const sortedGroups = [...props.groups].sort((a, b) => a.id - b.id)
      const groupIndex = sortedGroups.findIndex(g => g.id === groupId)
      const colorIndex = groupIndex >= 0 ? groupIndex % groupColorPalette.length : 0
      return groupColorPalette[colorIndex]
    }

    const getGroupColorClasses = (groupId) => {
      const colors = getGroupColors(groupId)
      return `${colors.bg} ${colors.text} ${colors.darkBg} ${colors.darkText}`
    }

    const quickAddToGroup = async (event, groupId) => {
      eventContextMenu.value.visible = false

      try {
        emit('handle-group-assignment', groupId, [event.title])

        const eventToUpdate = props.recurringEvents.find(e => e.title === event.title)
        if (eventToUpdate && !eventToUpdate.assigned_group_ids?.includes(parseInt(groupId))) {
          eventToUpdate.assigned_group_ids = [...(eventToUpdate.assigned_group_ids || []), parseInt(groupId)]
        }
      } catch (error) {
        console.error('Failed to add event to group:', error)
      }
    }

    const quickRemoveFromGroup = async (event, groupId) => {
      eventContextMenu.value.visible = false

      try {
        emit('remove-from-group', groupId, [event.title])

        const eventToUpdate = props.recurringEvents.find(e => e.title === event.title)
        if (eventToUpdate && eventToUpdate.assigned_group_ids?.includes(parseInt(groupId))) {
          eventToUpdate.assigned_group_ids = eventToUpdate.assigned_group_ids.filter(id => id !== parseInt(groupId))
        }
      } catch (error) {
        console.error('Failed to remove event from group:', error)
      }
    }

    const handleEventCardClick = (eventTitle, event) => {
      if (dragSelection.value.dragging) {
        return
      }
      toggleEventSelection(eventTitle)
    }

    const handleSmartGroupAction = async (groupId, action) => {
      const state = getGroupActionState(groupId)

      isUpdatingGroups.value = true
      updatingGroupIds.value.add(groupId)

      try {
        if (action === 'add') {
          const eventsToAdd = selectedEvents.value.filter(title => {
            const event = props.recurringEvents.find(e => e.title === title)
            return !event?.assigned_group_ids?.includes(parseInt(groupId))
          })

          if (eventsToAdd.length > 0) {
            updateEventsOptimistically(eventsToAdd, groupId, 'add')
            emit('handle-group-assignment', groupId, eventsToAdd)
          }
        } else if (action === 'remove') {
          const eventsToRemove = selectedEvents.value.filter(title => {
            const event = props.recurringEvents.find(e => e.title === title)
            return event?.assigned_group_ids?.includes(parseInt(groupId))
          })

          if (eventsToRemove.length > 0) {
            updateEventsOptimistically(eventsToRemove, groupId, 'remove')
            emit('remove-from-group', groupId, eventsToRemove)
          }
        }

        setTimeout(() => {
          isUpdatingGroups.value = false
          updatingGroupIds.value.delete(groupId)
        }, 300)

      } catch (error) {
        console.error('Group assignment error:', error)
        revertOptimisticUpdates()
        isUpdatingGroups.value = false
        updatingGroupIds.value.delete(groupId)
      }
    }

    const showAllSelectedEvents = () => {
      showSelectedOnly.value = true
      activeGroupFilters.value = []
      eventSearch.value = ''
    }

    const updateEventsOptimistically = (eventTitles, groupId, action) => {
      const groupIdInt = parseInt(groupId)

      eventTitles.forEach(title => {
        const event = props.recurringEvents.find(e => e.title === title)
        if (event) {
          if (!optimisticUpdates.value.has(title)) {
            optimisticUpdates.value.set(title, [...(event.assigned_group_ids || [])])
          }

          if (action === 'add' && !event.assigned_group_ids?.includes(groupIdInt)) {
            event.assigned_group_ids = [...(event.assigned_group_ids || []), groupIdInt]
          } else if (action === 'remove' && event.assigned_group_ids?.includes(groupIdInt)) {
            event.assigned_group_ids = event.assigned_group_ids.filter(id => id !== groupIdInt)
          }
        }
      })
    }

    const revertOptimisticUpdates = () => {
      optimisticUpdates.value.forEach((originalGroupIds, eventTitle) => {
        const event = props.recurringEvents.find(e => e.title === eventTitle)
        if (event) {
          event.assigned_group_ids = originalGroupIds
        }
      })
      optimisticUpdates.value.clear()
    }

    const isGroupUpdating = (groupId) => {
      return updatingGroupIds.value.has(groupId)
    }

    const handleUnassignAll = async () => {
      isUpdatingGroups.value = true

      try {
        selectedEvents.value.forEach(title => {
          const event = props.recurringEvents.find(e => e.title === title)
          if (event) {
            if (!optimisticUpdates.value.has(title)) {
              optimisticUpdates.value.set(title, [...(event.assigned_group_ids || [])])
            }
            event.assigned_group_ids = []
          }
        })

        emit('handle-group-assignment', 'unassigned', [...selectedEvents.value])

        setTimeout(() => {
          isUpdatingGroups.value = false
        }, 300)

      } catch (error) {
        console.error('Unassign all error:', error)
        revertOptimisticUpdates()
        isUpdatingGroups.value = false
      }
    }

    return {
      t,
      eventSearch,
      selectedEvents,
      activeGroupFilters,
      showSelectedOnly,
      newGroupName,
      showAddGroupForm,
      editingGroupId,
      editingGroupName,
      newGroupInput,
      contextMenu,
      eventContextMenu,
      deleteConfirmDialog,
      deleteConfirmMessage,
      groupToDelete,
      isUpdatingGroups,
      updatingGroupIds,
      dragSelection,
      cardRefs,
      assignedEventsCount,
      unassignedEventsCount,
      filteredEvents,
      isAllEventsSelected,
      isSomeEventsSelected,
      hasHiddenSelectedEvents,
      toggleGroupFilter,
      toggleSelectAllEvents,
      toggleEventSelection,
      clearEventSelection,
      showAllSelectedEvents,
      getGroupEventCount,
      getSmartGroupAction,
      handleSmartGroupAction,
      createGroup,
      cancelAddGroup,
      startAddGroup,
      saveGroupEdit,
      cancelGroupEdit,
      deleteGroupConfirm,
      confirmDeleteGroup,
      cancelDeleteGroup,
      showContextMenu,
      editGroupFromMenu,
      deleteGroupFromMenu,
      showEventContextMenu,
      getGroupColorClasses,
      quickAddToGroup,
      quickRemoveFromGroup,
      startDragSelection,
      updateDragSelection,
      endDragSelection,
      handleEventCardClick,
      isGroupUpdating,
      handleUnassignAll
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
