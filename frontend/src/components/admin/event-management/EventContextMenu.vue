<template>
  <div
    v-if="eventContextMenu.visible"
    :style="getContextMenuPosition()"
    :class="[
      'bg-white/98 dark:bg-gray-900/98 border border-gray-200/60 dark:border-gray-700/60 rounded-2xl shadow-[0_20px_25px_-5px_rgb(0_0_0_/_0.1),_0_10px_10px_-5px_rgb(0_0_0_/_0.04)] dark:shadow-[0_20px_25px_-5px_rgb(0_0_0_/_0.4),_0_10px_10px_-5px_rgb(0_0_0_/_0.2)] backdrop-blur-xl overflow-hidden transform transition-all duration-200 scale-100 opacity-100 ring-1 ring-black/5 dark:ring-white/10',
      getContextMenuWidthClass()
    ]"
    @click.stop
  >
    <!-- Context Menu Header -->
    <div class="px-4 py-3 border-b border-gray-100/70 dark:border-gray-700/70 bg-gradient-to-r from-indigo-50/90 via-blue-50/90 to-cyan-50/90 dark:from-indigo-900/30 dark:via-blue-900/30 dark:to-cyan-900/30 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/5 via-blue-500/5 to-cyan-500/5 dark:from-indigo-400/10 dark:via-blue-400/10 dark:to-cyan-400/10"></div>
      <div class="relative flex items-center gap-3">
        <div class="relative">
          <div class="w-2.5 h-2.5 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full shadow-sm"></div>
          <div class="absolute inset-0 w-2.5 h-2.5 bg-blue-400 rounded-full animate-ping opacity-30"></div>
        </div>
        <div class="flex-1 min-w-0">
          <div class="text-sm font-bold text-gray-900 dark:text-gray-100 truncate tracking-tight">{{ eventContextMenu.event?.title || 'Event Actions' }}</div>
        </div>
        <div class="w-1 h-1 bg-gray-300 dark:bg-gray-600 rounded-full opacity-60"></div>
      </div>
    </div>

    <!-- Actions Container -->
    <div v-if="availableGroups.length > 0 || assignedGroups.length > 0"
         class="flex divide-x divide-gray-100/80 dark:divide-gray-700/80 bg-gradient-to-r from-gray-50/30 to-gray-100/30 dark:from-gray-800/30 dark:to-gray-700/30">

      <!-- Add to Groups Section -->
      <div v-if="availableGroups.length > 0"
           class="flex-1 p-3 relative">
        <div class="relative flex items-center gap-2 mb-2">
          <span class="text-xs font-bold text-green-700 dark:text-green-300 uppercase tracking-wide">Add to Group</span>
          <div class="flex-1 h-px bg-gradient-to-r from-green-200 to-transparent dark:from-green-700/50"></div>
        </div>

        <div class="grid gap-2" :class="{
          'grid-cols-1': availableGroups.length <= 3,
          'grid-cols-2': availableGroups.length > 3 && availableGroups.length <= 8,
          'grid-cols-3': availableGroups.length > 8
        }">
          <button
            v-for="group in availableGroups"
            :key="`add-${group.id}`"
            @click="$emit('add-to-group', eventContextMenu.event, group.id)"
            class="group/btn w-full px-3 py-2 text-xs text-gray-700 dark:text-gray-300 bg-gradient-to-r from-green-50/80 to-emerald-50/80 dark:from-green-900/20 dark:to-emerald-900/20 hover:from-green-100 hover:to-emerald-100 dark:hover:from-green-800/40 dark:hover:to-emerald-800/40 transition-all duration-200 rounded-lg border-l-4 border-green-500 hover:border-green-600 hover:shadow-md hover:shadow-green-100/50 dark:hover:shadow-green-900/20 transform hover:scale-[1.01] active:scale-[0.99] min-h-[2rem] cursor-pointer text-center font-medium hover:text-green-800 dark:hover:text-green-200"
            :title="`Add event to ${group.name}`"
          >
            {{ group.name }}
          </button>
        </div>
      </div>

      <!-- Remove from Groups Section -->
      <div v-if="assignedGroups.length > 0"
           class="flex-1 p-3 relative">
        <div class="relative flex items-center gap-2 mb-2">
          <span class="text-xs font-bold text-red-700 dark:text-red-300 uppercase tracking-wide">Remove from Group</span>
          <div class="flex-1 h-px bg-gradient-to-r from-red-200 to-transparent dark:from-red-700/50"></div>
        </div>

        <div class="grid gap-2" :class="{
          'grid-cols-1': assignedGroups.length <= 3,
          'grid-cols-2': assignedGroups.length > 3 && assignedGroups.length <= 8,
          'grid-cols-3': assignedGroups.length > 8
        }">
          <button
            v-for="group in assignedGroups"
            :key="`remove-${group.id}`"
            @click="$emit('remove-from-group', eventContextMenu.event, group.id)"
            class="group/btn w-full px-3 py-2 text-xs text-gray-700 dark:text-gray-300 bg-gradient-to-r from-red-50/80 to-rose-50/80 dark:from-red-900/20 dark:to-rose-900/20 hover:from-red-100 hover:to-rose-100 dark:hover:from-red-800/40 dark:hover:to-rose-800/40 transition-all duration-200 rounded-lg border-l-4 border-red-500 hover:border-red-600 hover:shadow-md hover:shadow-red-100/50 dark:hover:shadow-red-900/20 transform hover:scale-[1.01] active:scale-[0.99] min-h-[2rem] cursor-pointer text-center font-medium hover:text-red-800 dark:hover:text-red-200"
            :title="`Remove event from ${group.name}`"
          >
            {{ group.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- No actions available -->
    <div v-if="availableGroups.length === 0 && assignedGroups.length === 0"
         class="px-6 py-8 text-center bg-gradient-to-br from-slate-50/50 to-gray-100/50 dark:from-slate-800/30 dark:to-gray-800/30">
      <div class="relative mx-auto mb-4">
        <div class="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-600 rounded-2xl flex items-center justify-center shadow-lg ring-1 ring-slate-200/50 dark:ring-slate-600/50">
          <span class="text-slate-400 dark:text-slate-500 text-xl">📋</span>
        </div>
        <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-md ring-2 ring-white dark:ring-gray-800">
          <span class="text-white text-xs font-bold">!</span>
        </div>
      </div>
      <div class="space-y-2">
        <div class="font-bold text-sm text-gray-800 dark:text-gray-200">{{ $t('messages.noGroupActionsAvailable') }}</div>
        <div class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed max-w-xs mx-auto">
          This event can't be assigned or removed from any groups right now.
          <span class="font-medium text-blue-600 dark:text-blue-400">{{ $t('messages.createSomeGroupsFirst') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'EventContextMenu',
  props: {
    eventContextMenu: {
      type: Object,
      required: true,
      default: () => ({ visible: false, x: 0, y: 0, event: null })
    },
    groups: {
      type: Array,
      required: true
    }
  },
  emits: ['add-to-group', 'remove-from-group'],
  setup(props) {
    const availableGroups = computed(() => {
      if (!props.eventContextMenu.event) return []
      const assignedGroupIds = props.eventContextMenu.event.assigned_group_ids || []
      return props.groups.filter(group => !assignedGroupIds.includes(group.id))
    })

    const assignedGroups = computed(() => {
      if (!props.eventContextMenu.event) return []
      const assignedGroupIds = props.eventContextMenu.event.assigned_group_ids || []
      return props.groups.filter(group => assignedGroupIds.includes(group.id))
    })

    const getContextMenuPosition = () => {
      if (!props.eventContextMenu.visible) return {}

      const x = props.eventContextMenu.x
      const y = props.eventContextMenu.y

      const menuWidth = 400
      const menuHeight = 200

      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight

      let finalX = x
      let finalY = y

      if (x + menuWidth > viewportWidth - 20) {
        finalX = x - menuWidth - 10
      }

      if (y + menuHeight > viewportHeight - 20) {
        finalY = y - menuHeight - 10
      }

      finalX = Math.max(10, finalX)
      finalY = Math.max(10, finalY)

      return {
        position: 'fixed',
        top: finalY + 'px',
        left: finalX + 'px',
        zIndex: 1000
      }
    }

    const getContextMenuWidthClass = () => {
      if (!props.eventContextMenu.event) return 'min-w-96 max-w-4xl w-auto'

      const allGroups = [...availableGroups.value, ...assignedGroups.value]
      const longestName = allGroups.length > 0 ?
        Math.max(...allGroups.map(g => g.name.length)) : 10

      const baseWidth = Math.max(24, longestName * 0.7 + 12)
      const maxGroups = Math.max(availableGroups.value.length, assignedGroups.value.length)

      const cols = maxGroups <= 3 ? 1 : maxGroups <= 8 ? 2 : 3
      const finalWidth = Math.max(baseWidth, cols * 12)

      return `min-w-96 max-w-5xl w-[${Math.min(finalWidth, 64)}rem]`
    }

    return {
      availableGroups,
      assignedGroups,
      getContextMenuPosition,
      getContextMenuWidthClass
    }
  }
}
</script>
