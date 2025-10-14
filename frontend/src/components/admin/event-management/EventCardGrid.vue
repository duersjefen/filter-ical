<template>
  <div>
    <!-- Events Card Grid -->
    <div
      class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 relative"
      :class="{ 'select-none': dragSelection.dragging }"
      @mousedown="$emit('mousedown', $event)"
      @mousemove="$emit('mousemove', $event)"
      @mouseup="$emit('mouseup', $event)"
      @mouseleave="$emit('mouseleave', $event)"
    >
      <!-- Drag Selection Overlay -->
      <div
        v-if="dragSelection.dragging"
        class="absolute pointer-events-none bg-gradient-to-br from-blue-300 to-blue-400 dark:from-blue-500 dark:to-blue-600 opacity-30 border-2 border-blue-500 dark:border-blue-400 rounded-lg shadow-lg backdrop-blur-sm"
        :style="{
          left: Math.min(dragSelection.startX, dragSelection.currentX) + 'px',
          top: Math.min(dragSelection.startY, dragSelection.currentY) + 'px',
          width: Math.abs(dragSelection.currentX - dragSelection.startX) + 'px',
          height: Math.abs(dragSelection.currentY - dragSelection.startY) + 'px',
          zIndex: 10
        }"
      >
        <div class="absolute inset-0 bg-white dark:bg-gray-900 opacity-10 rounded-lg"></div>
      </div>

      <div class="grid gap-2" :class="{
        'grid-cols-1': filteredEvents.length === 1,
        'grid-cols-1 sm:grid-cols-2': filteredEvents.length === 2,
        'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': filteredEvents.length >= 3 && filteredEvents.length <= 6,
        'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4': filteredEvents.length > 6
      }">
        <!-- Event Cards -->
        <div
          v-for="event in filteredEvents"
          :key="event.title"
          :ref="el => { if (el) cardRefs[event.title] = el }"
          data-event-card
          @click="$emit('card-click', event.title, $event)"
          @contextmenu.prevent="$emit('card-contextmenu', event, $event)"
          :class="[
            'relative border-2 rounded-lg p-3 cursor-pointer transition-all duration-200 hover:shadow-md transform hover:scale-[1.01]',
            selectedEvents.includes(event.title)
              ? 'border-blue-400 bg-blue-50 dark:border-blue-500 dark:bg-blue-900/30 shadow-lg ring-2 ring-blue-200 dark:ring-blue-700/50 scale-[1.01]'
              : 'border-gray-200 dark:border-gray-600 hover:border-blue-200 dark:hover:border-blue-600 bg-white dark:bg-gray-800 hover:bg-blue-25 dark:hover:bg-blue-950/10'
          ]"
        >
          <!-- Selection Indicator Line -->
          <div
            class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
            :class="selectedEvents.includes(event.title) ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'"
          ></div>

          <!-- Event Title with clean layout -->
          <div class="mb-2">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-5">
              {{ event.title }}
            </h3>
          </div>

          <!-- Group Assignment with count -->
          <div class="space-y-1">

            <!-- Multi-Group Display with count -->
            <div v-if="event.assigned_groups && event.assigned_groups.length > 0" class="flex flex-wrap items-center gap-1">
              <!-- Event count before bubbles -->
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 mr-1">
                {{ event.event_count }}
              </span>
              <!-- Primary Group Badge -->
              <span :class="`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getGroupColorClasses(event.assigned_groups[0].id)}`">
                {{ event.assigned_groups[0].name }}
              </span>
              <!-- Additional Groups (max 2 more shown) -->
              <span
                v-for="group in event.assigned_groups.slice(1, 2)"
                :key="group.id"
                :class="`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getGroupColorClasses(group.id)}`"
              >
                {{ group.name }}
              </span>
              <!-- Overflow Indicator with Tooltip -->
              <span
                v-if="event.assigned_groups.length > 2"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 transition-colors"
                :title="event.assigned_groups.slice(2).map(g => g.name).join(', ')"
              >
                +{{ event.assigned_groups.length - 2 }}
              </span>
            </div>
            <!-- Unassigned State with count -->
            <div v-else class="flex flex-wrap items-center gap-1">
              <!-- Event count before unassigned badge -->
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 mr-1">
                {{ event.event_count }}
              </span>
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200">
                ❔ {{ t('domainAdmin.unassigned') }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredEvents.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
      <div class="text-4xl mb-2">📅</div>
      <p>{{ t('domainAdmin.noEventsFound') }}</p>
    </div>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'EventCardGrid',
  props: {
    filteredEvents: { type: Array, required: true },
    selectedEvents: { type: Array, required: true },
    dragSelection: { type: Object, required: true },
    cardRefs: { type: Object, required: true },
    getGroupColorClasses: { type: Function, required: true }
  },
  emits: [
    'mousedown',
    'mousemove',
    'mouseup',
    'mouseleave',
    'card-click',
    'card-contextmenu'
  ],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
