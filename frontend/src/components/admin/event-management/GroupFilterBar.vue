<template>
  <div class="space-y-3">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
      <h3 class="text-base sm:text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('domainAdmin.filterByGroup') }}</h3>
      <div class="hidden sm:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
        <span>💡 {{ $t('messages.holdCtrlMultipleGroups') }}</span>
      </div>
      <div class="sm:hidden text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
        <span>💡 {{ $t('messages.holdCtrlMobile') }}</span>
      </div>
    </div>
    <div class="flex flex-wrap gap-2 overflow-x-auto">
      <!-- All Events Button -->
      <button
        @click="$emit('toggle-group-filter', 'all', $event)"
        :class="[
          'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
          activeGroupFilters.length === 0
            ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700'
            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
        ]"
        :title="activeGroupFilters.length === 0 ? $t('messages.currentlyShowingAll') : $t('messages.clickToClearFilters')"
      >
        <span>📋</span>
        <span>{{ t('domainAdmin.allEvents') }}</span>
        <span class="text-xs opacity-75">({{ totalEventsCount }})</span>
      </button>

      <!-- Unassigned Button -->
      <button
        @click="$emit('toggle-group-filter', 'unassigned', $event)"
        :class="[
          'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
          activeGroupFilters.includes('unassigned')
            ? 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-200 dark:border-yellow-700'
            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
        ]"
        :title="$t('messages.filterUnassigned')"
      >
        <span>❔</span>
        <span>{{ t('domainAdmin.unassigned') }}</span>
        <span class="text-xs opacity-75">({{ unassignedEventsCount }})</span>
      </button>

      <!-- Group Buttons with Right-Click Context Menu -->
      <button
        v-for="group in groups"
        :key="group.id"
        @click="$emit('toggle-group-filter', group.id, $event)"
        @contextmenu.prevent="$emit('show-context-menu', group, $event)"
        :class="[
          'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
          activeGroupFilters.includes(group.id)
            ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700'
            : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
        ]"
        :title="$t('messages.filterByGroup', { name: group.name })"
      >
        <span v-if="editingGroupId !== group.id" class="truncate max-w-[120px] sm:max-w-none">{{ group.name }}</span>
        <input
          v-else
          :value="editingGroupName"
          @input="$emit('update:editingGroupName', $event.target.value)"
          @keyup.enter="$emit('save-group-edit', group.id)"
          @keyup.escape="$emit('cancel-group-edit')"
          @blur="$emit('save-group-edit', group.id)"
          class="min-w-0 bg-transparent border-none outline-none text-inherit font-medium"
          :style="{ width: Math.max(50, editingGroupName.length * 8) + 'px' }"
        />
        <span class="text-xs opacity-75 flex-shrink-0">({{ getGroupEventCount(group.id) }})</span>
      </button>

      <!-- Add Group Button -->
      <button
        v-if="!showAddGroupForm"
        @click="$emit('start-add-group')"
        class="inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border border-dashed border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-green-400 hover:text-green-600 dark:hover:text-green-400 min-h-[44px] sm:min-h-0 flex-shrink-0"
      >
        <span>➕</span>
        <span>{{ $t('controls.addGroup') }}</span>
      </button>

      <!-- Add Group Form -->
      <div v-else class="flex items-center gap-2 w-full sm:w-auto sm:inline-flex">
        <input
          :value="newGroupName"
          @input="$emit('update:newGroupName', $event.target.value)"
          @keyup.enter="$emit('create-group')"
          @keyup.escape="$emit('cancel-add-group')"
          @blur="handleAddGroupBlur"
          :placeholder="t('domainAdmin.groupNamePlaceholder')"
          class="px-4 py-3 sm:px-3 sm:py-2 border border-green-300 dark:border-green-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 text-base sm:text-sm min-w-32 flex-1 sm:flex-none min-h-[44px] sm:min-h-0"
          ref="newGroupInput"
        />
        <button
          @click="$emit('create-group')"
          :disabled="!newGroupName.trim()"
          class="px-4 py-3 sm:px-2 sm:py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg sm:rounded text-base sm:text-sm min-h-[44px] sm:min-h-0 flex-shrink-0"
        >
          ✓
        </button>
        <button
          @click="$emit('cancel-add-group')"
          class="px-4 py-3 sm:px-2 sm:py-1 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg sm:rounded text-base sm:text-sm min-h-[44px] sm:min-h-0 flex-shrink-0"
        >
          ✗
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

export default {
  name: 'GroupFilterBar',
  props: {
    groups: { type: Array, required: true },
    activeGroupFilters: { type: Array, required: true },
    totalEventsCount: { type: Number, required: true },
    unassignedEventsCount: { type: Number, required: true },
    editingGroupId: { type: Number, default: null },
    editingGroupName: { type: String, default: '' },
    showAddGroupForm: { type: Boolean, default: false },
    newGroupName: { type: String, default: '' },
    getGroupEventCount: { type: Function, required: true }
  },
  emits: [
    'toggle-group-filter',
    'show-context-menu',
    'start-add-group',
    'create-group',
    'cancel-add-group',
    'save-group-edit',
    'cancel-group-edit',
    'update:editingGroupName',
    'update:newGroupName'
  ],
  setup(props, { emit }) {
    const { t } = useI18n()
    const newGroupInput = ref(null)

    const handleAddGroupBlur = () => {
      setTimeout(() => {
        if (document.activeElement !== newGroupInput.value) {
          emit('cancel-add-group')
        }
      }, 150)
    }

    return {
      t,
      newGroupInput,
      handleAddGroupBlur
    }
  }
}
</script>
