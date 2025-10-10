<template>
  <div class="relative bg-white dark:bg-gray-800 border-2 rounded-lg p-4 shadow-sm transition-all duration-200"
       :class="[
         selectedEvents.length > 0
           ? 'border-blue-300 dark:border-blue-600'
           : 'border-gray-200 dark:border-gray-700 opacity-60',
         dragSelection.dragging ? 'pointer-events-none opacity-75' : ''
       ]">

    <!-- Status Indicator -->
    <div v-if="isUpdatingGroups" class="absolute top-3 right-3 z-10">
      <div class="flex items-center gap-2 bg-white dark:bg-gray-800 px-2 py-1 rounded-full shadow-sm border border-gray-200 dark:border-gray-600">
        <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">{{ $t('domainAdmin.updating') }}</span>
      </div>
    </div>

    <div class="flex items-center justify-center mb-3">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="[
          selectedEvents.length > 0
            ? 'bg-blue-100 dark:bg-blue-900/30'
            : 'bg-gray-100 dark:bg-gray-700'
        ]">
          <span class="text-sm font-bold" :class="[
            selectedEvents.length > 0
              ? 'text-blue-600 dark:text-blue-400'
              : 'text-gray-400 dark:text-gray-500'
          ]">{{ selectedEvents.length || '0' }}</span>
        </div>
        <div>
          <h4 class="font-medium" :class="[
            selectedEvents.length > 0
              ? 'text-gray-900 dark:text-white'
              : 'text-gray-500 dark:text-gray-400'
          ]">
            Bulk Actions
          </h4>
          <p class="text-sm" :class="[
            selectedEvents.length > 0
              ? 'text-gray-600 dark:text-gray-400'
              : 'text-gray-400 dark:text-gray-500'
          ]">
            {{ selectedEvents.length === 0 ? $t('domainAdmin.noEventsSelected') :
               selectedEvents.length === 1 ? $t('domainAdmin.oneEventSelected') :
               $t('domainAdmin.eventsSelected', { count: selectedEvents.length }) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Smart Group Actions -->
    <div class="space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">

        <div
          v-for="group in groups"
          :key="`smart-${group.id}`"
          class="inline-flex"
        >
          <!-- Single Action Button -->
          <button
            v-if="getSmartGroupAction(group.id).type === 'single'"
            @click="$emit('smart-group-action', group.id, getSmartGroupAction(group.id).primaryAction)"
            :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
            :class="[
              'group relative inline-flex items-center justify-between w-full h-16 px-3 rounded-lg text-xs font-medium transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
              getSmartGroupAction(group.id).primaryStyle === 'add'
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 text-green-800 hover:from-green-100 hover:to-emerald-100 hover:border-green-300 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-600 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                : 'bg-gradient-to-r from-red-50 to-rose-50 border-2 border-red-200 text-red-800 hover:from-red-100 hover:to-rose-100 hover:border-red-300 dark:from-red-900/20 dark:to-rose-900/20 dark:border-red-600 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
            ]"
            :title="`${getSmartGroupAction(group.id).primaryLabel} ${group.name}`"
          >
            <div class="flex items-center gap-3">
              <div :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                getSmartGroupAction(group.id).primaryStyle === 'add'
                  ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                  : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
              ]">
                <span v-if="!isGroupUpdating(group.id)">{{ getSmartGroupAction(group.id).primaryLabel.charAt(0) }}</span>
                <div v-else class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div class="flex flex-col text-left">
                <span class="font-semibold text-sm">{{ group.name }}</span>
                <span class="text-xs opacity-75">{{ getSmartGroupAction(group.id).primaryLabel.split(' to')[0].split(' from')[0].substring(2) }}</span>
              </div>
            </div>
            <div :class="[
              'text-xs font-bold px-1.5 py-0.5 rounded-full',
              getSmartGroupAction(group.id).primaryStyle === 'add'
                ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
            ]">
              {{ getSmartGroupAction(group.id).primaryCount }}
            </div>
          </button>

          <!-- Split Action Buttons -->
          <div
            v-else-if="getSmartGroupAction(group.id).type === 'split'"
            class="w-full h-16 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-600 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col"
          >
            <!-- Group Header -->
            <div class="px-3 py-1 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border-b border-gray-200 dark:border-gray-500 flex-shrink-0">
              <div class="flex items-center justify-between">
                <span class="font-semibold text-xs text-gray-800 dark:text-gray-200">{{ group.name }}</span>
                <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse" :title="t('domainAdmin.mixedState')"></div>
              </div>
            </div>

            <!-- Split Actions -->
            <div class="flex flex-1">
              <!-- Primary Action -->
              <button
                @click="$emit('smart-group-action', group.id, getSmartGroupAction(group.id).primaryAction)"
                :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
                :class="[
                  'flex-1 px-3 py-1 text-xs font-medium transition-all duration-300 border-r border-gray-200 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed',
                  getSmartGroupAction(group.id).primaryStyle === 'add'
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 hover:from-green-100 hover:to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/20 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                    : 'bg-gradient-to-r from-red-50 to-rose-50 text-red-800 hover:from-red-100 hover:to-rose-100 dark:from-red-900/20 dark:to-rose-900/20 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
                ]"
                :title="`${getSmartGroupAction(group.id).primaryLabel} ${group.name}`"
              >
                <div class="flex items-center justify-center gap-2">
                  <div v-if="!isGroupUpdating(group.id)" :class="[
                    'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
                    getSmartGroupAction(group.id).primaryStyle === 'add'
                      ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                      : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
                  ]">
                    {{ getSmartGroupAction(group.id).primaryLabel.charAt(0) }}
                  </div>
                  <div v-else class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span class="font-semibold">{{ getSmartGroupAction(group.id).primaryCount }}</span>
                </div>
              </button>

              <!-- Secondary Action -->
              <button
                @click="$emit('smart-group-action', group.id, getSmartGroupAction(group.id).secondaryAction)"
                :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
                :class="[
                  'flex-1 px-3 py-1 text-xs font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed',
                  getSmartGroupAction(group.id).secondaryStyle === 'add'
                    ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 hover:from-green-100 hover:to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/20 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                    : 'bg-gradient-to-r from-red-50 to-rose-50 text-red-800 hover:from-red-100 hover:to-rose-100 dark:from-red-900/20 dark:to-rose-900/20 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
                ]"
                :title="`${getSmartGroupAction(group.id).secondaryAction === 'add' ? t('domainAdmin.add') : t('domainAdmin.remove')} ${getSmartGroupAction(group.id).secondaryCount} ${t('domainAdmin.events')} ${getSmartGroupAction(group.id).secondaryAction === 'add' ? t('domainAdmin.to') : t('domainAdmin.from')} ${group.name}`"
              >
                <div class="flex items-center justify-center gap-2">
                  <div v-if="!isGroupUpdating(group.id)" :class="[
                    'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
                    getSmartGroupAction(group.id).secondaryStyle === 'add'
                      ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                      : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
                  ]">
                    {{ getSmartGroupAction(group.id).secondaryAction === 'add' ? '+' : '−' }}
                  </div>
                  <div v-else class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                  <span class="font-semibold">{{ getSmartGroupAction(group.id).secondaryCount }}</span>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- Unassign All Button -->
        <button
          @click="$emit('unassign-all')"
          :disabled="isUpdatingGroups || selectedEvents.length === 0"
          class="group relative inline-flex items-center justify-between w-full h-16 px-3 rounded-lg text-xs font-medium transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 text-yellow-800 hover:from-yellow-100 hover:to-amber-100 hover:border-yellow-300 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-600 dark:text-yellow-200 dark:hover:from-yellow-800/30 dark:hover:to-amber-800/30"
          :title="`Remove ${selectedEvents.length} events from all groups`"
        >
          <div class="flex items-center gap-3">
            <div class="w-6 h-6 bg-yellow-200 dark:bg-yellow-700 rounded-full flex items-center justify-center text-xs font-bold">
              <span v-if="!isUpdatingGroups" class="text-yellow-800 dark:text-yellow-200">🚫</span>
              <div v-else class="w-3 h-3 border-2 border-yellow-800 dark:border-yellow-200 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div class="flex flex-col text-left">
              <span class="font-semibold text-sm">{{ $t('controls.unassignAll') }}</span>
              <span class="text-xs opacity-75">{{ $t('controls.removeFromAll') }}</span>
            </div>
          </div>
          <div class="text-xs font-bold px-1.5 py-0.5 rounded-full bg-yellow-200 dark:bg-yellow-700 text-yellow-800 dark:text-yellow-200">
            {{ selectedEvents.length }}
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'BulkAssignmentPanel',
  props: {
    groups: { type: Array, required: true },
    selectedEvents: { type: Array, required: true },
    recurringEvents: { type: Array, required: true },
    isUpdatingGroups: { type: Boolean, default: false },
    dragSelection: { type: Object, required: true },
    getSmartGroupAction: { type: Function, required: true },
    isGroupUpdating: { type: Function, required: true }
  },
  emits: ['smart-group-action', 'unassign-all'],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>
