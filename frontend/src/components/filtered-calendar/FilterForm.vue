<template>
  <div v-if="shouldShow" class="mb-6 p-4 rounded-lg border"
       :class="isUpdateMode
         ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-300 dark:border-amber-700'
         : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'">

    <!-- Update Mode Header -->
    <div v-if="isUpdateMode" class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="text-2xl">🔄</span>
        <div>
          <h4 class="text-md font-medium text-amber-800 dark:text-amber-200">
            {{ $t('messages.updateFilterFor', { name: updateModeCalendar?.name }) }}
          </h4>
          <p class="text-xs text-amber-700 dark:text-amber-300">
            {{ $t('messages.modifyingExisting') }}
          </p>
        </div>
      </div>
      <button
        @click="$emit('exit-update-mode')"
        class="text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 font-medium text-sm"
      >
        ✕ {{ $t('messages.cancelUpdate') }}
      </button>
    </div>

    <!-- Create Mode Header -->
    <h4 v-else class="text-md font-medium text-gray-800 dark:text-gray-200 mb-3">
      {{ $t('filteredCalendar.createTitle') }}
    </h4>

    <!-- Login Required Message -->
    <div v-if="!isLoggedIn" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-3 mb-4">
      <div class="flex items-center gap-2">
        <div class="text-amber-600 dark:text-amber-400">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-amber-800 dark:text-amber-200 text-sm font-medium">
          {{ $t('messages.pleaseSetUsernameFilters') }}
        </p>
      </div>
    </div>

    <form @submit.prevent="$emit('submit')" class="space-y-4" :class="{ 'opacity-50 pointer-events-none': !isLoggedIn }">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {{ $t('filteredCalendar.name') }}
        </label>
        <input
          :value="formName"
          @input="$emit('update:formName', $event.target.value)"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          :placeholder="$t('filteredCalendar.namePlaceholder')"
        />
      </div>

      <!-- Include Future Events Checkbox -->
      <div v-if="!isDomainCalendar && selectedRecurringEvents.length > 0"
           class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
        <label class="flex items-start gap-3 cursor-pointer">
          <input type="checkbox"
                 :checked="includeNewEvents"
                 @change="$emit('update:includeNewEvents', $event.target.checked)"
                 class="mt-1 text-blue-600 focus:ring-blue-500 w-4 h-4" />
          <div>
            <div class="font-semibold text-gray-900 dark:text-gray-100 text-sm">
              ✨ {{ $t('filteredCalendar.includeNewEvents') }}
            </div>
            <div class="text-xs text-gray-600 dark:text-gray-400">
              {{ $t('filteredCalendar.includeNewEventsDescription') }}
            </div>
          </div>
        </label>
      </div>

      <!-- Groups or Events Overview -->
      <GroupsOverview
        v-if="hasGroups"
        :groups="groups"
        :has-groups="hasGroups"
        :subscribed-groups="subscribedGroups"
        :selected-recurring-events="selectedRecurringEvents"
      />
      <EventsOverview
        v-else
        :selected-recurring-events="selectedRecurringEvents"
        :main-recurring-events="mainRecurringEvents"
        :single-recurring-events="singleRecurringEvents"
      />

      <div class="flex gap-3">
        <button
          type="submit"
          :disabled="!formName.trim() || creating || !isLoggedIn"
          class="px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 flex items-center justify-center gap-2"
          :class="isUpdateMode
            ? 'bg-amber-500 hover:bg-amber-600 disabled:bg-gray-400 text-white border-amber-400 hover:border-amber-500 disabled:border-gray-300'
            : 'bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white border-green-400 hover:border-green-500 disabled:border-gray-300'"
        >
          <span v-if="isUpdateMode">
            {{ creating ? $t('filteredCalendar.updating') : $t('filteredCalendar.updateFilter') }}
          </span>
          <span v-else>
            {{ creating ? $t('filteredCalendar.creating') : $t('filteredCalendar.create') }}
          </span>
        </button>

        <button
          v-if="isUpdateMode"
          type="button"
          @click="$emit('exit-update-mode')"
          class="px-4 py-3 bg-gray-500 hover:bg-gray-400 text-white rounded-xl text-sm font-semibold transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] active:scale-[0.98] min-h-[44px] border-2 border-gray-400 hover:border-gray-300"
        >
          {{ $t('controls.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import GroupsOverview from './GroupsOverview.vue'
import EventsOverview from './EventsOverview.vue'

const props = defineProps({
  selectedRecurringEvents: {
    type: Array,
    required: true
  },
  subscribedGroups: {
    type: Set,
    default: () => new Set()
  },
  isUpdateMode: {
    type: Boolean,
    default: false
  },
  updateModeCalendar: {
    type: Object,
    default: null
  },
  isLoggedIn: {
    type: Boolean,
    required: true
  },
  formName: {
    type: String,
    required: true
  },
  includeNewEvents: {
    type: Boolean,
    default: true
  },
  creating: {
    type: Boolean,
    default: false
  },
  isDomainCalendar: {
    type: Boolean,
    default: false
  },
  groups: {
    type: Object,
    default: () => ({})
  },
  hasGroups: {
    type: Boolean,
    default: false
  },
  mainRecurringEvents: {
    type: Array,
    default: () => []
  },
  singleRecurringEvents: {
    type: Array,
    default: () => []
  }
})

defineEmits(['submit', 'exit-update-mode', 'update:formName', 'update:includeNewEvents'])

const shouldShow = computed(() => {
  return props.selectedRecurringEvents.length > 0 ||
         (props.subscribedGroups && props.subscribedGroups.size > 0) ||
         props.isUpdateMode ||
         !props.isLoggedIn
})
</script>
