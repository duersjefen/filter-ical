import { useI18n } from 'vue-i18n'

/**
 * Composable for group display helpers
 * Pure functions for group visualization and status
 */
export function useGroupDisplay() {
  const { t } = useI18n()

  const getGroupRecurringEvents = (group) => {
    if (!group || !group.recurring_events) return []
    return group.recurring_events.filter(recurringEvent => {
      return recurringEvent.event_count > 0
    }).map(recurringEvent => recurringEvent.title)
  }

  const getGroupSelectedCount = (groupId, groups, selectedRecurringEvents) => {
    const group = groups[groupId]
    if (!group) return 0

    const groupRecurringEvents = getGroupRecurringEvents(group)

    return groupRecurringEvents.filter(event =>
      selectedRecurringEvents && selectedRecurringEvents.includes(event)
    ).length
  }

  const getGroupTotalCount = (group) => {
    return getGroupRecurringEvents(group).length
  }

  const getGroupDisplayName = (group) => {
    const groupIcon = group.name.match(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u)?.[0] || '📋'
    const groupName = group.name.replace(/[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu, '').trim()
    return `${groupIcon} ${groupName}`
  }

  const getGroupSubscriptionStatus = (groupId, groups, subscribedGroups, selectedRecurringEvents) => {
    const isSubscribed = subscribedGroups && subscribedGroups.has(groupId)
    const selectedCount = getGroupSelectedCount(groupId, groups, selectedRecurringEvents)
    const totalCount = getGroupTotalCount(groups[groupId])

    if (isSubscribed) {
      return t('status.subscribed')
    } else if (selectedCount === totalCount && totalCount > 0) {
      return t('status.allSelected')
    } else if (selectedCount > 0) {
      return t('status.partial')
    } else {
      return t('status.notSelected')
    }
  }

  const getGroupDisplayClass = (groupId, groups, subscribedGroups, selectedRecurringEvents) => {
    const isSubscribed = subscribedGroups && subscribedGroups.has(groupId)
    const selectedCount = getGroupSelectedCount(groupId, groups, selectedRecurringEvents)
    const totalCount = getGroupTotalCount(groups[groupId])

    if (isSubscribed) {
      return 'bg-green-100 dark:bg-green-800/50 border-green-500 dark:border-green-400 text-green-800 dark:text-green-100 shadow-lg shadow-green-200/50 dark:shadow-green-800/30'
    } else if (selectedCount === totalCount && totalCount > 0) {
      return 'bg-blue-100 dark:bg-blue-800/50 border-blue-500 dark:border-blue-400 text-blue-800 dark:text-blue-100 shadow-md shadow-blue-200/50 dark:shadow-blue-800/30'
    } else if (selectedCount > 0) {
      return 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
    } else {
      return 'bg-gray-50 dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400'
    }
  }

  const getCountDisplayClass = (groupId, groups, subscribedGroups, selectedRecurringEvents) => {
    const isSubscribed = subscribedGroups && subscribedGroups.has(groupId)
    const selectedCount = getGroupSelectedCount(groupId, groups, selectedRecurringEvents)
    const totalCount = getGroupTotalCount(groups[groupId])

    if (isSubscribed && selectedCount === totalCount && totalCount > 0) {
      return 'bg-green-600 dark:bg-green-500 text-white'
    } else if (selectedCount === totalCount && totalCount > 0) {
      return 'bg-blue-600 dark:bg-blue-500 text-white'
    } else if (selectedCount > 0 && selectedCount < totalCount) {
      return 'bg-blue-600 dark:bg-blue-500 text-white'
    } else {
      return 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
    }
  }

  const getGroupSubscriptionDotClass = (groupId, groups, subscribedGroups, selectedRecurringEvents) => {
    const isSubscribed = subscribedGroups && subscribedGroups.has(groupId)
    const selectedCount = getGroupSelectedCount(groupId, groups, selectedRecurringEvents)
    const totalCount = getGroupTotalCount(groups[groupId])

    if (isSubscribed) {
      return 'bg-green-600 dark:bg-green-400'
    } else if (selectedCount === totalCount && totalCount > 0) {
      return 'bg-blue-600 dark:bg-blue-400'
    } else if (selectedCount > 0) {
      return 'bg-blue-500 dark:bg-blue-400'
    } else {
      return 'bg-gray-400 dark:bg-gray-500'
    }
  }

  const getProgressBarClass = (groupId, groups, subscribedGroups, selectedRecurringEvents) => {
    const isSubscribed = subscribedGroups && subscribedGroups.has(groupId)
    const selectedCount = getGroupSelectedCount(groupId, groups, selectedRecurringEvents)
    const totalCount = getGroupTotalCount(groups[groupId])

    if (isSubscribed && selectedCount === totalCount && totalCount > 0) {
      return 'bg-gradient-to-r from-green-400 to-blue-500'
    } else if (selectedCount === totalCount && totalCount > 0) {
      return 'bg-gradient-to-r from-blue-400 to-blue-600'
    } else if (selectedCount > 0) {
      return 'bg-gray-300 dark:bg-gray-600'
    } else {
      return 'bg-gray-300 dark:bg-gray-600'
    }
  }

  return {
    getGroupRecurringEvents,
    getGroupSelectedCount,
    getGroupTotalCount,
    getGroupDisplayName,
    getGroupSubscriptionStatus,
    getGroupDisplayClass,
    getCountDisplayClass,
    getGroupSubscriptionDotClass,
    getProgressBarClass
  }
}
