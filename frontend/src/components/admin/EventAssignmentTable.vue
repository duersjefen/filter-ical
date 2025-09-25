<template>
  <!-- Assignment Summary Cards -->
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg border border-blue-200 dark:border-blue-700">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-blue-600 dark:text-blue-400 text-sm font-medium">Total Events</p>
          <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ totalEvents }}</p>
        </div>
        <div class="text-2xl">📅</div>
      </div>
    </div>

    <div class="bg-orange-50 dark:bg-orange-900/30 p-4 rounded-lg border border-orange-200 dark:border-orange-700">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-orange-600 dark:text-orange-400 text-sm font-medium">Unassigned</p>
          <p class="text-2xl font-bold text-orange-900 dark:text-orange-100">{{ unassignedCount }}</p>
        </div>
        <div class="text-2xl">⚠️</div>
      </div>
    </div>

    <div class="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg border border-green-200 dark:border-green-700">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-green-600 dark:text-green-400 text-sm font-medium">Assigned</p>
          <p class="text-2xl font-bold text-green-900 dark:text-green-100">{{ assignedCount }}</p>
        </div>
        <div class="text-2xl">✅</div>
      </div>
    </div>

    <div class="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg border border-purple-200 dark:border-purple-700">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-purple-600 dark:text-purple-400 text-sm font-medium">Groups</p>
          <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">{{ groups.length }}</p>
        </div>
        <div class="text-2xl">📁</div>
      </div>
    </div>
  </div>

  <!-- Filters and Search -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
    <div class="flex flex-col md:flex-row gap-4">
      <!-- Search -->
      <div class="flex-1">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('admin.searchEvents')"
            class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="text-gray-400">🔍</span>
          </div>
        </div>
      </div>

      <!-- Assignment Filter -->
      <div class="md:w-48">
        <select 
          v-model="assignmentFilter"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="all">All Events</option>
          <option value="assigned">Assigned Only</option>
          <option value="unassigned">Unassigned Only</option>
        </select>
      </div>

      <!-- Group Filter -->
      <div class="md:w-48">
        <select 
          v-model="groupFilter"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Filter by Group</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }}
          </option>
        </select>
      </div>
    </div>
  </div>

  <!-- Bulk Actions Bar -->
  <div v-if="selectedEvents.length > 0" class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg p-4 mb-4 flex items-center justify-between">
    <div class="text-blue-800 dark:text-blue-200">
      <span class="font-medium">{{ selectedEvents.length }}</span> events selected
    </div>
    <div class="flex gap-2">
      <select 
        v-model="bulkAssignGroupId"
        class="px-3 py-1 border border-blue-300 dark:border-blue-600 rounded bg-white dark:bg-blue-800 text-blue-900 dark:text-blue-100 text-sm"
      >
        <option value="">Choose Group</option>
        <option v-for="group in groups" :key="group.id" :value="group.id">
          {{ group.name }}
        </option>
      </select>
      <button
        @click="bulkAssignEvents"
        :disabled="!bulkAssignGroupId"
        class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-1 rounded text-sm font-medium transition-colors duration-200"
      >
        Assign Selected
      </button>
      <button
        @click="bulkUnassignEvents"
        class="bg-red-600 hover:bg-red-700 text-white px-4 py-1 rounded text-sm font-medium transition-colors duration-200"
      >
        Unassign Selected
      </button>
      <button
        @click="clearSelection"
        class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-1 rounded text-sm font-medium transition-colors duration-200"
      >
        Clear
      </button>
    </div>
  </div>

  <!-- Events Table -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
          <tr>
            <th class="w-12 px-4 py-3 text-left">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="isSomeSelected"
                @change="toggleSelectAll"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
              Event
            </th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
              Occurrences
            </th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
              Current Assignment
            </th>
            <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr 
            v-for="event in filteredEvents" 
            :key="event.title"
            :class="['hover:bg-gray-50 dark:hover:bg-gray-700', {'bg-orange-50 dark:bg-orange-900/20': !event.assigned_group}]"
          >
            <!-- Selection Checkbox -->
            <td class="px-4 py-4">
              <input
                type="checkbox"
                :value="event.title"
                v-model="selectedEvents"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
            </td>

            <!-- Event Details -->
            <td class="px-4 py-4">
              <div class="flex flex-col">
                <div class="font-medium text-gray-900 dark:text-white">{{ event.title }}</div>
                <div v-if="event.sample_location" class="text-sm text-gray-500 dark:text-gray-400">
                  📍 {{ event.sample_location }}
                </div>
              </div>
            </td>

            <!-- Occurrences -->
            <td class="px-4 py-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                {{ event.event_count }}
              </span>
            </td>

            <!-- Assignment Status -->
            <td class="px-4 py-4">
              <div v-if="event.assigned_group" class="flex items-center">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  {{ event.assigned_group.name }}
                </span>
              </div>
              <div v-else class="flex items-center">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
                  ⚠️ Unassigned
                </span>
              </div>
            </td>

            <!-- Quick Actions -->
            <td class="px-4 py-4">
              <div class="flex items-center gap-2">
                <!-- Quick Assign Dropdown -->
                <select 
                  :value="event.assigned_group?.id || ''"
                  @change="quickAssignEvent(event.title, $event.target.value)"
                  class="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Unassigned</option>
                  <option v-for="group in groups" :key="group.id" :value="group.id">
                    {{ group.name }}
                  </option>
                </select>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="filteredEvents.length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">📅</div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No Events Found</h3>
      <p class="text-gray-500 dark:text-gray-400">
        {{ searchQuery || assignmentFilter !== 'all' || groupFilter 
           ? 'Try adjusting your filters or search criteria.' 
           : 'No recurring events available for assignment.' }}
      </p>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'EventAssignmentTable',
  props: {
    events: {
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
  emits: ['assign-event', 'unassign-event', 'bulk-assign', 'bulk-unassign'],
  setup(props, { emit }) {
    // Reactive state
    const searchQuery = ref('')
    const assignmentFilter = ref('all')
    const groupFilter = ref('')
    const selectedEvents = ref([])
    const bulkAssignGroupId = ref('')

    // Create a groups map for quick lookups
    const groupsMap = computed(() => {
      const map = {}
      props.groups.forEach(group => {
        map[group.id] = group
      })
      return map
    })

    // Enhanced events with assignment information
    const enhancedEvents = computed(() => {
      if (!Array.isArray(props.events)) return []
      return props.events.map(event => ({
        ...event,
        assigned_group: event.assigned_group_id ? groupsMap.value[event.assigned_group_id] : null
      }))
    })

    // Statistics
    const totalEvents = computed(() => {
      if (!Array.isArray(props.events)) return 0
      return props.events.length
    })
    const assignedCount = computed(() => {
      if (!Array.isArray(enhancedEvents.value)) return 0
      return enhancedEvents.value.filter(e => e.assigned_group).length
    })
    const unassignedCount = computed(() => totalEvents.value - assignedCount.value)

    // Filtered events
    const filteredEvents = computed(() => {
      let filtered = enhancedEvents.value
      
      // Safety check - ensure we have an array
      if (!Array.isArray(filtered)) return []

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(event => 
          event.title.toLowerCase().includes(query) ||
          (event.sample_location && event.sample_location.toLowerCase().includes(query))
        )
      }

      // Assignment filter
      if (assignmentFilter.value === 'assigned') {
        filtered = filtered.filter(event => event.assigned_group)
      } else if (assignmentFilter.value === 'unassigned') {
        filtered = filtered.filter(event => !event.assigned_group)
      }

      // Group filter
      if (groupFilter.value) {
        filtered = filtered.filter(event => 
          event.assigned_group && event.assigned_group.id === parseInt(groupFilter.value)
        )
      }

      return filtered
    })

    // Selection state
    const isAllSelected = computed(() => {
      const filtered = filteredEvents.value
      if (!Array.isArray(filtered) || filtered.length === 0) return false
      return selectedEvents.value.length === filtered.length
    })

    const isSomeSelected = computed(() => {
      const filtered = filteredEvents.value
      if (!Array.isArray(filtered)) return false
      return selectedEvents.value.length > 0 && 
             selectedEvents.value.length < filtered.length
    })

    // Methods
    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        selectedEvents.value = []
      } else {
        selectedEvents.value = filteredEvents.value.map(event => event.title)
      }
    }

    const clearSelection = () => {
      selectedEvents.value = []
      bulkAssignGroupId.value = ''
    }

    const quickAssignEvent = (eventTitle, groupId) => {
      if (groupId) {
        emit('assign-event', eventTitle, parseInt(groupId))
      } else {
        emit('unassign-event', eventTitle)
      }
    }

    const bulkAssignEvents = () => {
      if (bulkAssignGroupId.value && selectedEvents.value.length > 0) {
        emit('bulk-assign', selectedEvents.value, parseInt(bulkAssignGroupId.value))
        clearSelection()
      }
    }

    const bulkUnassignEvents = () => {
      if (selectedEvents.value.length > 0) {
        emit('bulk-unassign', selectedEvents.value)
        clearSelection()
      }
    }

    // Watch for prop changes and clear selection if events change
    watch(() => props.events, () => {
      selectedEvents.value = []
    })

    return {
      // Reactive state
      searchQuery,
      assignmentFilter,
      groupFilter,
      selectedEvents,
      bulkAssignGroupId,

      // Computed
      enhancedEvents,
      filteredEvents,
      totalEvents,
      assignedCount,
      unassignedCount,
      isAllSelected,
      isSomeSelected,

      // Methods
      toggleSelectAll,
      clearSelection,
      quickAssignEvent,
      bulkAssignEvents,
      bulkUnassignEvents
    }
  }
}
</script>