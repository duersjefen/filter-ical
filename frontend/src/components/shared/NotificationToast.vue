<template>
  <!-- Notification Container (fixed at top-right) -->
  <div class="fixed top-4 right-4 z-[9999] space-y-3 pointer-events-none max-w-md">
    <transition-group
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="pointer-events-auto"
        @mouseenter="pauseAutoDismiss(notification.id)"
        @mouseleave="resumeAutoDismiss(notification.id)"
      >
        <div :class="[
          'rounded-2xl shadow-2xl border backdrop-blur-sm overflow-hidden transition-all duration-300 hover:scale-[1.02]',
          getNotificationStyles(notification.type).border,
          getNotificationStyles(notification.type).bg
        ]">
          <!-- Header with icon and close button -->
          <div class="px-5 py-4">
            <div class="flex items-start gap-4">
              <!-- Icon -->
              <div :class="[
                'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-md',
                getNotificationStyles(notification.type).iconBg
              ]">
                <component :is="getNotificationIcon(notification.type)" class="w-6 h-6 text-white" />
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0 pt-0.5">
                <h4 :class="[
                  'text-sm font-bold mb-1',
                  getNotificationStyles(notification.type).textColor
                ]">
                  {{ getNotificationTitle(notification.type) }}
                </h4>
                <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {{ notification.message }}
                </p>
              </div>

              <!-- Close button -->
              <button
                @click="removeNotification(notification.id)"
                class="flex-shrink-0 w-6 h-6 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-all duration-200 flex items-center justify-center"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Progress bar for auto-dismiss -->
          <div class="h-1 bg-gray-100 dark:bg-gray-700/50">
            <div
              :class="[
                'h-full transition-all duration-75 ease-linear',
                getNotificationStyles(notification.type).progressBg
              ]"
              :style="{ width: notification.progress + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNotificationStore } from '../../stores/notification'

const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)

const removeNotification = (id) => {
  notificationStore.removeNotification(id)
}

const pauseAutoDismiss = (id) => {
  notificationStore.pauseAutoDismiss(id)
}

const resumeAutoDismiss = (id) => {
  notificationStore.resumeAutoDismiss(id)
}

// Get notification styles based on type
const getNotificationStyles = (type) => {
  const styles = {
    success: {
      border: 'border-green-400 dark:border-green-600',
      bg: 'bg-white/95 dark:bg-gray-800/95',
      iconBg: 'bg-gradient-to-br from-green-400 to-green-600',
      textColor: 'text-green-800 dark:text-green-200',
      progressBg: 'bg-gradient-to-r from-green-400 to-green-600'
    },
    error: {
      border: 'border-red-400 dark:border-red-600',
      bg: 'bg-white/95 dark:bg-gray-800/95',
      iconBg: 'bg-gradient-to-br from-red-400 to-red-600',
      textColor: 'text-red-800 dark:text-red-200',
      progressBg: 'bg-gradient-to-r from-red-400 to-red-600'
    },
    warning: {
      border: 'border-amber-400 dark:border-amber-600',
      bg: 'bg-white/95 dark:bg-gray-800/95',
      iconBg: 'bg-gradient-to-br from-amber-400 to-amber-600',
      textColor: 'text-amber-800 dark:text-amber-200',
      progressBg: 'bg-gradient-to-r from-amber-400 to-amber-600'
    },
    info: {
      border: 'border-blue-400 dark:border-blue-600',
      bg: 'bg-white/95 dark:bg-gray-800/95',
      iconBg: 'bg-gradient-to-br from-blue-400 to-blue-600',
      textColor: 'text-blue-800 dark:text-blue-200',
      progressBg: 'bg-gradient-to-r from-blue-400 to-blue-600'
    }
  }
  return styles[type] || styles.info
}

// Get notification title based on type
const getNotificationTitle = (type) => {
  const titles = {
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    info: 'Information'
  }
  return titles[type] || 'Notification'
}

// Get notification icon component based on type (inline SVG)
const getNotificationIcon = (type) => {
  const icons = {
    success: {
      template: `
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
        </svg>
      `
    },
    error: {
      template: `
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
      `
    },
    warning: {
      template: `
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      `
    },
    info: {
      template: `
        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `
    }
  }
  return icons[type] || icons.info
}
</script>
