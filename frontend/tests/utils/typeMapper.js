/**
 * Type Mapper Utilities
 *
 * Converts API response types to match Vue component prop expectations.
 *
 * Problem: Backend API returns database types (integers, etc.) but Vue components
 * may expect different types (strings, etc.) for flexibility and prop validation.
 *
 * Solution: Contract tests validate API responses and provide type conversion utilities.
 */

/**
 * Convert API domain response to component-compatible format
 *
 * API returns:
 *   { id: 1, domain_key: "exter", name: "Exter", ... }
 *
 * Components expect:
 *   { id: "1", domain_key: "exter", name: "Exter", ... }
 */
export function convertApiToDomainContext(apiDomain) {
  if (!apiDomain) return null

  return {
    id: String(apiDomain.id),  // Number → String conversion
    domain_key: apiDomain.domain_key,
    name: apiDomain.name,
    calendar_url: apiDomain.calendar_url,
    status: apiDomain.status,
    is_owner: apiDomain.is_owner ?? false,
    is_admin: apiDomain.is_admin ?? false,
    has_admin_access: apiDomain.has_admin_access ?? false
  }
}

/**
 * Convert API group response to component-compatible format
 *
 * API returns:
 *   { id: 1, name: "BCC Events", domain_key: "exter", ... }
 *
 * Components may use id as number or string depending on context
 */
export function convertApiToGroup(apiGroup) {
  if (!apiGroup) return null

  return {
    id: apiGroup.id,  // Keep as Number - GroupCard expects Number
    name: apiGroup.name,
    domain_key: apiGroup.domain_key,
    recurring_event_titles: apiGroup.recurring_event_titles ?? []
  }
}

/**
 * Convert API event response to component-compatible format
 */
export function convertApiToEvent(apiEvent) {
  if (!apiEvent) return null

  return {
    id: apiEvent.id,  // Keep as Number
    title: apiEvent.title,
    start: apiEvent.start,
    end: apiEvent.end,
    location: apiEvent.location ?? null,
    description: apiEvent.description ?? null
  }
}

/**
 * Validate that API data types match component prop expectations
 *
 * @param {Object} apiData - Data from API response
 * @param {Object} componentPropTypes - Expected prop types from component
 * @throws {Error} If type mismatch detected
 */
export function validatePropTypes(apiData, componentPropTypes) {
  const errors = []

  for (const [key, expectedType] of Object.entries(componentPropTypes)) {
    const actualValue = apiData[key]
    const actualType = typeof actualValue

    // Handle null/undefined
    if (actualValue === null || actualValue === undefined) {
      if (expectedType.required) {
        errors.push(`Missing required prop '${key}'`)
      }
      continue
    }

    // Check type match
    const expectedTypeName = expectedType.type?.name?.toLowerCase() || expectedType.toLowerCase()

    if (expectedTypeName === 'string' && actualType !== 'string') {
      errors.push(
        `Type mismatch for '${key}': expected String, got ${actualType} (${JSON.stringify(actualValue)})`
      )
    } else if (expectedTypeName === 'number' && actualType !== 'number') {
      errors.push(
        `Type mismatch for '${key}': expected Number, got ${actualType} (${JSON.stringify(actualValue)})`
      )
    } else if (expectedTypeName === 'boolean' && actualType !== 'boolean') {
      errors.push(
        `Type mismatch for '${key}': expected Boolean, got ${actualType} (${JSON.stringify(actualValue)})`
      )
    } else if (expectedTypeName === 'object' && actualType !== 'object') {
      errors.push(
        `Type mismatch for '${key}': expected Object, got ${actualType} (${JSON.stringify(actualValue)})`
      )
    } else if (expectedTypeName === 'array' && !Array.isArray(actualValue)) {
      errors.push(
        `Type mismatch for '${key}': expected Array, got ${actualType} (${JSON.stringify(actualValue)})`
      )
    }
  }

  if (errors.length > 0) {
    throw new Error(`API/Component type mismatch:\n${errors.join('\n')}`)
  }
}

/**
 * Get type name from prop type definition
 */
function getTypeName(propType) {
  if (typeof propType === 'string') return propType.toLowerCase()
  if (typeof propType === 'function') return propType.name.toLowerCase()
  if (propType?.type) return getTypeName(propType.type)
  return 'unknown'
}
