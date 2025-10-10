<template>
  <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-600 shadow-sm">
    <div v-if="hasGroups && groups && Object.keys(groups).length > 0">
      <!-- Header label -->
      <div class="mb-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>{{ $t('filteredCalendar.currentFilter') }}</span>
      </div>

      <!-- Groups Grid -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        <div
          v-for="(group, groupId) in groups"
          :key="groupId"
          class="relative bg-white dark:bg-gray-800 rounded-xl p-3 border shadow-sm cursor-default overflow-hidden"
          :class="getGroupDisplayClass(groupId, groups, subscribedGroups, selectedRecurringEvents)"
        >
          <!-- Status indicator -->
          <div
            class="absolute top-0 left-0 right-0 h-1.5 rounded-t-xl transition-all duration-300"
            :class="getProgressBarClass(groupId, groups, subscribedGroups, selectedRecurringEvents)"
          ></div>

          <!-- Group Content -->
          <div class="pt-2">
            <div class="flex items-start gap-2 mb-2">
              <span class="text-lg leading-none">{{ getGroupDisplayName(group).split(' ')[0] || '📋' }}</span>
              <span class="text-sm font-bold text-gray-900 dark:text-gray-100 leading-tight line-clamp-2 flex-1">
                {{ getGroupDisplayName(group).substring(getGroupDisplayName(group).indexOf(' ') + 1) || group.name }}
              </span>
            </div>

            <div class="flex items-center justify-between mt-2">
              <div class="flex items-center gap-1">
                <span
                  class="px-2.5 py-1 rounded-lg text-xs font-bold shadow-sm border"
                  :class="getCountDisplayClass(groupId, groups, subscribedGroups, selectedRecurringEvents)"
                >
                  {{ getGroupSelectedCount(groupId, groups, selectedRecurringEvents) }}/{{ getGroupTotalCount(group) }}
                </span>
              </div>

              <div class="flex items-center gap-1">
                <div
                  class="w-3 h-3 rounded-full border-2 border-white dark:border-gray-700 shadow-sm"
                  :class="getGroupSubscriptionDotClass(groupId, groups, subscribedGroups, selectedRecurringEvents)"
                  :title="getGroupSubscriptionStatus(groupId, groups, subscribedGroups, selectedRecurringEvents)"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary stats -->
      <div class="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">
            {{ Object.keys(groups).length }} {{ t('common.totalGroups') }}
          </span>
          <span class="text-gray-600 dark:text-gray-400">
            {{ groupBreakdown }}
          </span>
        </div>
      </div>
    </div>

    <!-- Display for Personal Calendars (Non-Group) -->
    <div v-else>
      <slot name="no-groups">
        <div class="text-center py-4">
          <div class="text-gray-500 dark:text-gray-400 text-lg mb-2">📂</div>
          <div class="text-sm text-gray-600 dark:text-gray-400 font-medium">
            {{ $t('preview.noEventsSelected') }}
          </div>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGroupDisplay } from '@/composables/useGroupDisplay'

const props = defineProps({
  groups: {
    type: Object,
    default: () => ({})
  },
  hasGroups: {
    type: Boolean,
    default: false
  },
  subscribedGroups: {
    type: Set,
    default: () => new Set()
  },
  selectedRecurringEvents: {
    type: Array,
    default: () => []
  }
})

const { t } = useI18n()
const {
  getGroupRecurringEvents,
  getGroupSelectedCount,
  getGroupTotalCount,
  getGroupDisplayName,
  getGroupSubscriptionStatus,
  getGroupDisplayClass,
  getCountDisplayClass,
  getGroupSubscriptionDotClass,
  getProgressBarClass
} = useGroupDisplay()

const groupBreakdown = computed(() => {
  if (!props.hasGroups || !props.groups) {
    return ''
  }

  const totalGroups = Object.keys(props.groups).length
  const subscribedGroups = props.subscribedGroups ? props.subscribedGroups.size : 0
  const selectedEvents = props.selectedRecurringEvents ? props.selectedRecurringEvents.length : 0

  const parts = []
  if (subscribedGroups > 0) {
    parts.push(`${subscribedGroups}/${totalGroups} ${t('common.groupsSubscribed')}`)
  }
  if (selectedEvents > 0) {
    parts.push(`${selectedEvents} ${t('common.eventsSelected')}`)
  }

  return parts.length > 0 ? parts.join(' • ') : t('preview.noEventsSelected')
})
</script>
