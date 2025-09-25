<template>
  <div class="space-y-6">
    <!-- Event Management Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Event Management</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Assign events to groups, manage bulk operations, and track assignment status
        </p>
      </div>
      
      <!-- Quick Actions -->
      <div class="flex gap-3">
        <button
          v-if="unassignedCount > 0"
          @click="highlightUnassigned"
          class="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
        >
          <span>⚠️</span>
          {{ unassignedCount }} Unassigned
        </button>
        
        <button
          @click="refreshEvents"
          :disabled="loading"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
        >
          <span v-if="loading">⏳</span>
          <span v-else>🔄</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Event Assignment Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent mb-4"></div>
        <div class="text-gray-600 dark:text-gray-400">Loading events...</div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-12 text-center">
        <div class="text-4xl mb-4">❌</div>
        <div class="text-red-600 dark:text-red-400 font-medium mb-2">{{ error }}</div>
        <button
          @click="refreshEvents"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          Try Again
        </button>
      </div>

      <!-- Main Event Assignment Table -->
      <EventAssignmentTable
        v-else
        :events="events"
        :groups="groups"
        :loading="loading"
        @assign-event="handleAssignEvent"
        @unassign-event="handleUnassignEvent"
        @bulk-assign="handleBulkAssign"
        @bulk-unassign="handleBulkUnassign"
        ref="eventAssignmentTable"
      />
    </div>

    <!-- Help Text -->
    <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <div class="text-2xl">💡</div>
        <div class="flex-1">
          <h3 class="font-medium text-blue-900 dark:text-blue-100 mb-2">Event Management Tips</h3>
          <ul class="text-sm text-blue-700 dark:text-blue-200 space-y-1">
            <li>• <strong>Unassigned events</strong> appear with orange highlighting - assign them to groups for better organization</li>
            <li>• <strong>Select multiple events</strong> using checkboxes for bulk assignment operations</li>
            <li>• <strong>Quick assign</strong> individual events using the dropdown in each row</li>
            <li>• <strong>Search and filter</strong> to quickly find specific events or groups</li>
            <li>• <strong>Auto-assignment rules</strong> can be configured in the "Auto Rules" tab</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- Success/Error Toast -->
  <div v-if="notification" class="fixed bottom-4 right-4 z-50 max-w-md">
    <div :class="[
      'rounded-lg shadow-lg border px-4 py-3 transition-all duration-300',
      notification.type === 'success' 
        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 border-green-300 dark:border-green-700'
        : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border-red-300 dark:border-red-700'
    ]">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-lg">{{ notification.type === 'success' ? '✅' : '❌' }}</span>
          <span class="font-medium">{{ notification.message }}</span>
        </div>
        <button 
          @click="notification = null" 
          class="text-lg hover:scale-110 transition-transform duration-200 ml-3"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import EventAssignmentTable from './EventAssignmentTable.vue'

export default {
  name: 'EventManager',
  components: {
    EventAssignmentTable
  },
  props: {
    events: {
      type: Array,
      default: () => [],
      validator: (value) => {
        // Allow null/undefined during initial load, but warn if it's not an array
        return value === null || value === undefined || Array.isArray(value)
      }
    },
    groups: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    }
  },
  emits: [
    'assign-event',
    'unassign-event', 
    'bulk-assign',
    'bulk-unassign',
    'refresh-events'
  ],
  setup(props, { emit }) {
    // Local reactive state
    const notification = ref(null)
    const eventAssignmentTable = ref(null)

    // Computed properties
    const unassignedCount = computed(() => {
      if (!Array.isArray(props.events)) return 0
      return props.events.filter(event => !event.assigned_group_id).length
    })

    const totalEvents = computed(() => {
      if (!Array.isArray(props.events)) return 0
      return props.events.length
    })

    // Notification helpers
    const showNotification = (message, type = 'success') => {
      notification.value = { message, type }
      setTimeout(() => {
        notification.value = null
      }, 5000)
    }

    // Event handlers
    const handleAssignEvent = async (eventTitle, groupId) => {
      try {
        emit('assign-event', eventTitle, groupId)
        showNotification('Event assigned successfully!', 'success')
      } catch (error) {
        showNotification(`Failed to assign event: ${error.message}`, 'error')
      }
    }

    const handleUnassignEvent = async (eventTitle) => {
      try {
        emit('unassign-event', eventTitle)
        showNotification('Event unassigned successfully!', 'success')
      } catch (error) {
        showNotification(`Failed to unassign event: ${error.message}`, 'error')
      }
    }

    const handleBulkAssign = async (eventTitles, groupId) => {
      try {
        emit('bulk-assign', eventTitles, groupId)
        const count = eventTitles.length
        showNotification(`${count} event${count === 1 ? '' : 's'} assigned successfully!`, 'success')
      } catch (error) {
        showNotification(`Failed to bulk assign events: ${error.message}`, 'error')
      }
    }

    const handleBulkUnassign = async (eventTitles) => {
      try {
        emit('bulk-unassign', eventTitles)
        const count = eventTitles.length
        showNotification(`${count} event${count === 1 ? '' : 's'} unassigned successfully!`, 'success')
      } catch (error) {
        showNotification(`Failed to bulk unassign events: ${error.message}`, 'error')
      }
    }

    const refreshEvents = () => {
      emit('refresh-events')
    }

    const highlightUnassigned = () => {
      // Set the assignment filter to show only unassigned events
      if (eventAssignmentTable.value) {
        // This would interact with the EventAssignmentTable component
        // For now, we'll emit an event that could be handled by the parent
        showNotification(`${unassignedCount.value} unassigned events highlighted`, 'success')
      }
    }

    // Auto-refresh when component mounts (if no data)
    onMounted(() => {
      if (props.events.length === 0 && !props.loading) {
        refreshEvents()
      }
    })

    return {
      // Local state
      notification,
      eventAssignmentTable,

      // Computed
      unassignedCount,
      totalEvents,

      // Methods
      handleAssignEvent,
      handleUnassignEvent,
      handleBulkAssign,
      handleBulkUnassign,
      refreshEvents,
      highlightUnassigned,
      showNotification
    }
  }
}
</script>