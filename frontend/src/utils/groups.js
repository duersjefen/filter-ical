/**
 * Group utilities for handling auto-created groups
 *
 * Auto-created groups have special high numeric IDs:
 * - 9998: '📅 Other Recurring Events' (recurring events without custom group)
 * - 9999: '🎯 Special Events' (unique events without custom group)
 */

/**
 * Check if a group is an auto-created group
 * @param {number|string} groupId - Group ID to check
 * @returns {boolean} - True if group is auto-created
 */
export function isAutoGroup(groupId) {
  const numericId = typeof groupId === 'string' ? parseInt(groupId, 10) : groupId
  return numericId >= 9998
}

/**
 * Check if a groups object/array contains any custom (non-auto) groups
 * @param {Object|Array} groups - Groups object or array
 * @returns {boolean} - True if there are any custom groups
 */
export function hasCustomGroups(groups) {
  if (!groups) return false

  // Handle array format
  if (Array.isArray(groups)) {
    return groups.some(group => !isAutoGroup(group.id))
  }

  // Handle object format (keyed by group ID)
  return Object.values(groups).some(group => !isAutoGroup(group.id))
}

/**
 * Filter out auto-created groups from a groups object/array
 * @param {Object|Array} groups - Groups object or array
 * @returns {Object|Array} - Groups without auto-created groups
 */
export function filterAutoGroups(groups) {
  if (!groups) return groups

  // Handle array format
  if (Array.isArray(groups)) {
    return groups.filter(group => !isAutoGroup(group.id))
  }

  // Handle object format (keyed by group ID)
  const filtered = {}
  Object.entries(groups).forEach(([key, group]) => {
    if (!isAutoGroup(group.id)) {
      filtered[key] = group
    }
  })
  return filtered
}

/**
 * Count the number of custom (non-auto) groups
 * @param {Object|Array} groups - Groups object or array
 * @returns {number} - Count of custom groups
 */
export function countCustomGroups(groups) {
  if (!groups) return 0

  // Handle array format
  if (Array.isArray(groups)) {
    return groups.filter(group => !isAutoGroup(group.id)).length
  }

  // Handle object format (keyed by group ID)
  return Object.values(groups).filter(group => !isAutoGroup(group.id)).length
}
