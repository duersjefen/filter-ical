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
    
    sortedPreviewEvents.value.forEach(event => {
      let groupKey
      
      if (previewGroup.value === PREVIEW_GROUPS.CATEGORY) {
        groupKey = getCategoryForEvent(event)
      } else if (previewGroup.value === PREVIEW_GROUPS.MONTH) {
        const date = new Date(event.dtstart)
        groupKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      }
      
      if (!groups[groupKey]) {
        groups[groupKey] = { name: groupKey, events: [] }
      }
      groups[groupKey].events.push(event)
    })

    return Object.values(groups)
  })

  // Methods
  function getCategoryForEvent(event) {
    return event.categories?.[0] || event.summary || 'Uncategorized'
  }

  function formatDateTime(dateString) {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric', 
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      return dateString
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
      // Flip the selection when switching modes
      const allCategories = filteredCategories.value.map(cat => cat.name)
      const currentlyUnselected = allCategories.filter(cat => !selectedCategories.value.includes(cat))
      
      selectedCategories.value = [...currentlyUnselected]
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