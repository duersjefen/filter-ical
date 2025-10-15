/**
 * Filter helper utilities
 * Pure functions for event filtering logic
 */

/**
 * Compute three-list model for filter creation/update
 * @param {Array<string>} selectedGroups - Array of selected group IDs
 * @param {Array<string>} selectedEvents - Array of selected event titles
 * @param {Object} groups - Groups object keyed by group ID
 * @returns {Object} Object with subscribedEventIds and unselectedEventIds arrays
 */
export function computeThreeListModel(selectedGroups, selectedEvents, groups) {
  const eventTitlesInSubscribedGroups = new Set()

  // Build set of events covered by subscribed groups
  selectedGroups.forEach(groupId => {
    const group = groups[groupId]
    if (group?.recurring_events) {
      group.recurring_events.forEach(event => {
        if (event.event_count > 0) {
          eventTitlesInSubscribedGroups.add(event.title)
        }
      })
    }
  })

  // Individual events NOT covered by groups
  const subscribedEventIds = selectedEvents.filter(title =>
    !eventTitlesInSubscribedGroups.has(title)
  )

  // Group events NOT in selectedEvents = unselected
  const unselectedEventIds = []
  eventTitlesInSubscribedGroups.forEach(title => {
    if (!selectedEvents.includes(title)) {
      unselectedEventIds.push(title)
    }
  })

  return { subscribedEventIds, unselectedEventIds }
}
