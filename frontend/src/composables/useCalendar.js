import { ref, computed } from 'vue'
import { useAppStore } from '../stores/app'
import { FILTER_MODES, PREVIEW_GROUPS, SORT_ORDERS, EVENT_LIMITS } from '../constants/ui'

export function useCalendar() {
  const appStore = useAppStore()
  
  // Reactive state
  const selectedCategories = ref([])
  const expandedCategories = ref([])
  const showSingleEvents = ref(false)
  const categorySearch = ref('')
  const filterMode = ref(FILTER_MODES.INCLUDE)
  const showPreview = ref(false)
  const previewGroup = ref(PREVIEW_GROUPS.NONE)
  const previewOrder = ref(SORT_ORDERS.ASC)
  const previewLimit = ref(EVENT_LIMITS.PREVIEW_DEFAULT)

  // Computed properties
  const filteredCategories = computed(() => {
    if (!categorySearch.value.trim()) {
      return appStore.categoriesSortedByCount
    }
    
    const searchTerm = categorySearch.value.toLowerCase()
    return appStore.categoriesSortedByCount.filter(category => 
      category.name.toLowerCase().includes(searchTerm)
    )
  })

  const mainCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count > 1)
  })

  const singleEventCategories = computed(() => {
    return filteredCategories.value.filter(category => category.count === 1)
  })

  const selectedCategoriesCount = computed(() => {
    return appStore.categoriesSortedByCount
      .filter(cat => selectedCategories.value.includes(cat.name))
      .reduce((sum, cat) => sum + cat.count, 0)
  })

  const previewEvents = computed(() => {
    if (selectedCategories.value.length === 0) return []

    const selectedCategoryNames = new Set(selectedCategories.value)
    return appStore.events.filter(event => {
      const eventCategory = getCategoryForEvent(event)
      const isInSelectedCategory = selectedCategoryNames.has(eventCategory)
      
      return filterMode.value === FILTER_MODES.INCLUDE 
        ? isInSelectedCategory 
        : !isInSelectedCategory
    })
  })

  const sortedPreviewEvents = computed(() => {
    const events = [...previewEvents.value]
    const multiplier = previewOrder.value === SORT_ORDERS.ASC ? 1 : -1
    
    return events.sort((a, b) => {
      const dateA = new Date(a.dtstart)
      const dateB = new Date(b.dtstart)
      return (dateA - dateB) * multiplier
    })
  })

  const groupedPreviewEvents = computed(() => {
    if (previewGroup.value === PREVIEW_GROUPS.NONE) return []

    const groups = {}
    
    // First, group events and collect month date info for sorting
    previewEvents.value.forEach(event => {
      let groupKey
      let sortKey
      
      if (previewGroup.value === PREVIEW_GROUPS.CATEGORY) {
        groupKey = getCategoryForEvent(event)
        sortKey = groupKey
      } else if (previewGroup.value === PREVIEW_GROUPS.MONTH) {
        // Handle iCal date format properly
        let date
        if (typeof event.dtstart === 'string') {
          if (event.dtstart.match(/^\d{8}T\d{6}Z?$/)) {
            // Format: 20231215T140000Z
            const year = event.dtstart.substring(0, 4)
            const month = event.dtstart.substring(4, 6)
            const day = event.dtstart.substring(6, 8)
            date = new Date(`${year}-${month}-${day}`)
          } else if (event.dtstart.match(/^\d{8}$/)) {
            // Format: 20231215 (date only)
            const year = event.dtstart.substring(0, 4)
            const month = event.dtstart.substring(4, 6)
            const day = event.dtstart.substring(6, 8)
            date = new Date(`${year}-${month}-${day}`)
          } else {
            date = new Date(event.dtstart)
          }
        } else {
          date = new Date(event.dtstart)
        }
        groupKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
        sortKey = date.getTime() // Use timestamp for chronological sorting
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = { name: groupKey, events: [], sortKey }
      }
      groups[groupKey].events.push(event)
    })

    // Sort groups and events within groups
    const groupedArray = Object.values(groups)

    if (previewGroup.value === PREVIEW_GROUPS.CATEGORY) {
      // Sort category groups by event count (descending)
      groupedArray.sort((a, b) => b.events.length - a.events.length)
    } else if (previewGroup.value === PREVIEW_GROUPS.MONTH) {
      // Sort month groups chronologically
      groupedArray.sort((a, b) => a.sortKey - b.sortKey)
      
      // Sort events within each month group according to previewOrder
      const multiplier = previewOrder.value === SORT_ORDERS.ASC ? 1 : -1
      groupedArray.forEach(group => {
        group.events.sort((a, b) => {
          const dateA = new Date(a.dtstart)
          const dateB = new Date(b.dtstart)
          return (dateA - dateB) * multiplier
        })
      })
    }

    return groupedArray
  })

  // Methods
  function getCategoryForEvent(event) {
    return event.categories?.[0] || event.summary || 'Uncategorized'
  }

  function formatDateTime(dateString) {
    if (!dateString) return 'No date'
    
    try {
      let date
      
      // Handle iCal format dates (YYYYMMDDTHHMMSSZ or YYYYMMDD)
      if (typeof dateString === 'string') {
        if (dateString.match(/^\d{8}T\d{6}Z?$/)) {
          // Format: 20231215T140000Z
          const year = dateString.substring(0, 4)
          const month = dateString.substring(4, 6)
          const day = dateString.substring(6, 8)
          const hour = dateString.substring(9, 11)
          const minute = dateString.substring(11, 13)
          date = new Date(`${year}-${month}-${day}T${hour}:${minute}:00`)
        } else if (dateString.match(/^\d{8}$/)) {
          // Format: 20231215 (date only)
          const year = dateString.substring(0, 4)
          const month = dateString.substring(4, 6)
          const day = dateString.substring(6, 8)
          date = new Date(`${year}-${month}-${day}`)
        } else {
          // Try parsing as regular date string
          date = new Date(dateString)
        }
      } else {
        date = new Date(dateString)
      }
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid date'
      }
      
      // Format based on whether it has time component
      const hasTime = dateString.includes('T') || dateString.includes(':')
      
      if (hasTime) {
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          year: 'numeric', 
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        })
      } else {
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          year: 'numeric', 
          month: 'short',
          day: 'numeric'
        })
      }
    } catch (error) {
      console.warn('Date formatting error:', error, 'for date:', dateString)
      return 'Invalid date'
    }
  }

  function toggleCategory(categoryName) {
    const index = selectedCategories.value.indexOf(categoryName)
    if (index === -1) {
      selectedCategories.value.push(categoryName)
    } else {
      selectedCategories.value.splice(index, 1)
    }
  }

  function toggleCategoryExpansion(categoryName) {
    const index = expandedCategories.value.indexOf(categoryName)
    if (index === -1) {
      expandedCategories.value.push(categoryName)
    } else {
      expandedCategories.value.splice(index, 1)
    }
  }

  function selectAllCategories() {
    selectedCategories.value = filteredCategories.value.map(cat => cat.name)
  }

  function clearAllCategories() {
    selectedCategories.value = []
    showPreview.value = false
  }

  function selectAllSingleEvents() {
    const singleEventNames = singleEventCategories.value.map(cat => cat.name)
    singleEventNames.forEach(name => {
      if (!selectedCategories.value.includes(name)) {
        selectedCategories.value.push(name)
      }
    })
  }

  function clearAllSingleEvents() {
    const singleEventNames = singleEventCategories.value.map(cat => cat.name)
    selectedCategories.value = selectedCategories.value.filter(name => !singleEventNames.includes(name))
  }

  function switchFilterMode(newMode) {
    if (filterMode.value !== newMode) {
      // Just switch the mode, keep the same categories selected
      filterMode.value = newMode
      previewLimit.value = EVENT_LIMITS.PREVIEW_DEFAULT
    }
  }

  function togglePreviewOrder() {
    previewOrder.value = previewOrder.value === SORT_ORDERS.ASC ? SORT_ORDERS.DESC : SORT_ORDERS.ASC
  }

  async function generateIcalFile() {
    try {
      const response = await appStore.generateIcal({
        calendarId: appStore.selectedCalendar.id,
        selectedCategories: selectedCategories.value,
        filterMode: filterMode.value
      })
      
      // Create and trigger download
      const blob = new Blob([response.data], { type: 'text/calendar' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${appStore.selectedCalendar.name}_filtered.ics`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error generating iCal:', error)
    }
  }

  return {
    // State
    selectedCategories,
    expandedCategories,
    showSingleEvents,
    categorySearch,
    filterMode,
    showPreview,
    previewGroup,
    previewOrder,
    previewLimit,
    
    // Computed
    filteredCategories,
    mainCategories,
    singleEventCategories,
    selectedCategoriesCount,
    previewEvents,
    sortedPreviewEvents,
    groupedPreviewEvents,
    
    // Methods
    getCategoryForEvent,
    formatDateTime,
    toggleCategory,
    toggleCategoryExpansion,
    selectAllCategories,
    clearAllCategories,
    selectAllSingleEvents,
    clearAllSingleEvents,
    switchFilterMode,
    togglePreviewOrder,
    generateIcalFile
  }
}