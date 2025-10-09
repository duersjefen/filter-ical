<template>
  <div v-if="shouldShowCard" class="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl shadow-lg border-2 border-blue-200 dark:border-blue-700 mb-4 overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-800/40 dark:to-indigo-800/40 px-4 sm:px-6 py-3 sm:py-4 border-b border-blue-200 dark:border-blue-700">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-blue-500 dark:bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
          <span class="text-2xl">⚙️</span>
        </div>
        <div class="flex-1">
          <h3 class="text-lg sm:text-xl font-bold text-blue-900 dark:text-blue-100">
            {{ $t('admin.setupCard.title') }}
          </h3>
          <p class="text-sm text-blue-700 dark:text-blue-300">
            {{ $t('admin.setupCard.subtitle') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 sm:p-6">
      <!-- Description -->
      <div class="mb-4">
        <div class="flex items-start gap-3 mb-3">
          <span class="text-2xl flex-shrink-0">📊</span>
          <div>
            <p class="text-gray-800 dark:text-gray-200 font-medium mb-1">
              {{ $t('admin.setupCard.noGroupsMessage') }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ $t('admin.setupCard.groupsBenefit') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Benefits List -->
      <div class="bg-white/60 dark:bg-gray-800/40 rounded-lg p-3 sm:p-4 mb-4 border border-blue-100 dark:border-blue-800">
        <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('admin.setupCard.benefitsTitle') }}
        </p>
        <ul class="space-y-1.5 text-sm text-gray-600 dark:text-gray-400">
          <li class="flex items-start gap-2">
            <span class="text-green-500 mt-0.5">✓</span>
            <span>{{ $t('admin.setupCard.benefit1') }}</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-green-500 mt-0.5">✓</span>
            <span>{{ $t('admin.setupCard.benefit2') }}</span>
          </li>
          <li class="flex items-start gap-2">
            <span class="text-green-500 mt-0.5">✓</span>
            <span>{{ $t('admin.setupCard.benefit3') }}</span>
          </li>
        </ul>
      </div>

      <!-- CTA Button -->
      <div class="flex justify-center">
        <router-link
          :to="`/${domainKey}/admin`"
          class="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95"
        >
          <span class="text-lg">⚙️</span>
          <span>{{ $t('admin.setupCard.setupButton') }}</span>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '../../composables/useAuth'

const props = defineProps({
  domainContext: {
    type: Object,
    default: null
  },
  hasCustomGroups: {
    type: Boolean,
    default: false
  }
})

const { isLoggedIn } = useAuth()

const domainKey = computed(() => {
  return props.domainContext?.domain_key || ''
})

const hasAdminAccess = computed(() => {
  return props.domainContext?.has_admin_access || false
})

const shouldShowCard = computed(() => {
  // Show card when:
  // 1. User is logged in
  // 2. User has admin access (owner or admin)
  // 3. Domain has no custom groups (only auto-groups exist)
  // 4. We have valid domain context
  return (
    isLoggedIn.value &&
    hasAdminAccess.value &&
    !props.hasCustomGroups &&
    props.domainContext
  )
})
</script>
