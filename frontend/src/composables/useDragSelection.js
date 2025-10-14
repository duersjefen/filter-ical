import { ref, onMounted, onUnmounted } from 'vue'

export function useDragSelection(selectedEvents, cardRefs, filteredEvents, emit) {
  const dragSelection = ref({
    dragging: false,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0,
    initialSelection: [],
    containerRect: null
  })

  // Global escape handler for drag selection cleanup
  onMounted(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && dragSelection.value.dragging) {
        endDragSelection()
      }
    }

    const handleBeforeUnload = () => {
      dragSelection.value.dragging = false
    }

    document.addEventListener('keydown', handleEscape)
    window.addEventListener('beforeunload', handleBeforeUnload)

    onUnmounted(() => {
      document.removeEventListener('keydown', handleEscape)
      window.removeEventListener('beforeunload', handleBeforeUnload)
      dragSelection.value.dragging = false
    })
  })

  const startDragSelection = (event) => {
    if (event.button !== 0) return

    const containerRect = event.currentTarget.getBoundingClientRect()
    dragSelection.value = {
      dragging: true,
      startX: event.clientX - containerRect.left,
      startY: event.clientY - containerRect.top,
      currentX: event.clientX - containerRect.left,
      currentY: event.clientY - containerRect.top,
      initialSelection: [...selectedEvents.value],
      containerRect: containerRect,
      scrollTop: undefined,
      scrollLeft: undefined
    }

    event.preventDefault()
    event.stopPropagation()

    // Attach document-level listeners to capture mouse events outside container
    document.addEventListener('mousemove', updateDragSelection)
    document.addEventListener('mouseup', endDragSelection)
  }

  const updateDragSelection = (event) => {
    if (!dragSelection.value.dragging) return

    const containerRect = dragSelection.value.containerRect
    dragSelection.value.currentX = event.clientX - containerRect.left
    dragSelection.value.currentY = event.clientY - containerRect.top

    event.preventDefault()
    event.stopPropagation()

    const selectionRect = {
      left: Math.min(dragSelection.value.startX, dragSelection.value.currentX),
      top: Math.min(dragSelection.value.startY, dragSelection.value.currentY),
      right: Math.max(dragSelection.value.startX, dragSelection.value.currentX),
      bottom: Math.max(dragSelection.value.startY, dragSelection.value.currentY)
    }

    const newSelection = [...dragSelection.value.initialSelection]

    filteredEvents.value.forEach(event => {
      const cardElement = cardRefs.value[event.title]
      if (cardElement) {
        const cardRect = cardElement.getBoundingClientRect()

        const cardRelativeRect = {
          left: cardRect.left - containerRect.left,
          top: cardRect.top - containerRect.top,
          right: cardRect.right - containerRect.left,
          bottom: cardRect.bottom - containerRect.top
        }

        const intersects = !(cardRelativeRect.right < selectionRect.left ||
                           cardRelativeRect.left > selectionRect.right ||
                           cardRelativeRect.bottom < selectionRect.top ||
                           cardRelativeRect.top > selectionRect.bottom)

        if (intersects) {
          if (!newSelection.includes(event.title)) {
            newSelection.push(event.title)
          }
        }
      }
    })

    selectedEvents.value = newSelection
  }

  const endDragSelection = () => {
    if (!dragSelection.value.dragging) return

    const deltaX = Math.abs(dragSelection.value.currentX - dragSelection.value.startX)
    const deltaY = Math.abs(dragSelection.value.currentY - dragSelection.value.startY)
    const wasClick = deltaX < 5 && deltaY < 5

    if (wasClick) {
      selectedEvents.value = [...dragSelection.value.initialSelection]
      emit('clear-event-selection')
      dragSelection.value.initialSelection.forEach(eventTitle => {
        emit('toggle-event-selection', eventTitle)
      })
    } else {
      emit('clear-event-selection')
      selectedEvents.value.forEach(title => emit('toggle-event-selection', title))
    }

    dragSelection.value.dragging = false

    // Remove document-level listeners
    document.removeEventListener('mousemove', updateDragSelection)
    document.removeEventListener('mouseup', endDragSelection)
  }

  return {
    dragSelection,
    startDragSelection,
    updateDragSelection,
    endDragSelection
  }
}
