<template>
  <div class="preview-event-item py-1.5 leading-relaxed">
    <!-- Email-Style Single-Line Layout -->
    <div class="flex items-baseline gap-3">
      <!-- Time: Fixed left column -->
      <div class="text-xs text-gray-500 dark:text-gray-400 font-mono whitespace-nowrap flex-shrink-0 w-24">
        {{ formatCompactDate(event) }}
      </div>

      <!-- Title: Flexible center -->
      <div class="font-semibold text-gray-900 dark:text-gray-100 text-base leading-normal flex-1 min-w-0 truncate">
        {{ event.title ? event.title.trim() : (event.summary ? event.summary.trim() : 'Untitled Event') }}
      </div>

      <!-- Badges: Right side, wrappable -->
      <div v-if="hasSecondaryInfo" class="flex flex-wrap items-baseline gap-1.5 justify-end">
        <!-- Location Badge -->
        <span
          v-if="event.location"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600"
          :title="event.location.trim()"
        >
          📍 {{ truncateText(event.location, 30) }}
        </span>

        <!-- Duration Badge (subtle gray styling) -->
        <span
          v-if="eventDuration"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-600"
        >
          ⏱️ {{ eventDuration }}
        </span>

        <!-- Category Badge -->
        <span
          v-if="showCategory && getRecurringEventKey(event) !== event.title"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700"
        >
          📂 {{ truncateText(getRecurringEventKey(event), 25) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  event: { type: Object, required: true },
  showCategory: { type: Boolean, default: true },
  formatDateRange: { type: Function, required: true },
  getRecurringEventKey: { type: Function, required: true }
})

// Check if we have secondary info to show
const hasSecondaryInfo = computed(() => {
  return props.event.location ||
         eventDuration.value ||
         (props.showCategory && props.getRecurringEventKey(props.event) !== props.event.title)
})

// Truncate text intelligently
const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

// Format event duration
const eventDuration = computed(() => {
  const startField = props.event.start || props.event.dtstart
  const endField = props.event.end || props.event.dtend

  if (!startField || !endField) return null

  const start = new Date(startField)
  const end = new Date(endField)

  if (!start || !end || start >= end) return null

  const diffMs = end - start
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  // Multi-day events
  if (diffDays >= 1) {
    return diffDays === 1 ? '1 day' : `${diffDays} days`
  }

  // Hour-based events
  if (diffHours >= 1) {
    const remainingMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
    if (remainingMinutes > 0) {
      return `${diffHours}h ${remainingMinutes}m`
    }
    return `${diffHours}h`
  }

  // Minute-based events
  if (diffMinutes > 0) {
    return `${diffMinutes}m`
  }

  return null
})

// Format date in a more compact way with better readability and i18n support
const formatCompactDate = (event) => {
  const startDate = new Date(event.start || event.dtstart)
  const endField = event.end || event.dtend
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const eventDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())

  // Check if multi-day event
  const isMultiDay = endField ? (() => {
    const endDate = new Date(endField)
    const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
    const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate())
    return startDateOnly.getTime() !== endDateOnly.getTime()
  })() : false

  // Calculate days difference from today
  const diffTime = eventDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  // Get current locale for proper formatting
  const locale = t('language.switch') === 'Sprache wechseln' ? 'de-DE' : 'en-US'

  // For multi-day events, show date range without time
  if (isMultiDay) {
    const monthDay = startDate.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    return `${monthDay}+`  // Simple indicator for multi-day
  }

  // Format time part for single-day events
  const timeStr = startDate.toLocaleTimeString(locale, {
    hour: 'numeric',
    minute: '2-digit',
    hour12: false
  })

  // Smart date formatting based on proximity with consistent spacing
  if (diffDays === 0) {
    return `${t('preview.today')}·${timeStr}`
  } else if (diffDays === 1) {
    return `${t('preview.tomorrow')}·${timeStr}`
  } else if (diffDays === -1) {
    return `${t('preview.yesterday')}·${timeStr}`
  } else if (diffDays > 0 && diffDays <= 7) {
    return `${startDate.toLocaleDateString(locale, { weekday: 'short' })}·${timeStr}`
  } else if (diffDays >= -7 && diffDays < 0) {
    return `${startDate.toLocaleDateString(locale, { weekday: 'short' })}·${timeStr}`
  } else {
    // For dates further away, show month/day with year if needed
    const monthDay = startDate.toLocaleDateString(locale, { month: 'short', day: 'numeric' })
    const currentYear = now.getFullYear()
    const eventYear = startDate.getFullYear()

    if (eventYear !== currentYear) {
      return `${monthDay}·${eventYear}·${timeStr}`
    } else {
      return `${monthDay}·${timeStr}`
    }
  }
}
</script>