<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="$emit('click', $event)"
  >
    <span v-if="loading && !hideLoadingText" class="inline-flex items-center gap-2">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span v-if="loadingText">{{ loadingText }}</span>
    </span>
    <slot v-else />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'ghost'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: ''
  },
  hideLoadingText: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'submit', 'reset'].includes(value)
  },
  rounded: {
    type: String,
    default: 'lg',
    validator: (value) => ['none', 'sm', 'md', 'lg', 'xl', 'full'].includes(value)
  }
})

defineEmits(['click'])

const buttonClasses = computed(() => {
  const classes = []

  // Base classes
  classes.push('inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none')

  // Full width
  if (props.fullWidth) {
    classes.push('w-full')
  }

  // Size classes
  const sizeClasses = {
    xs: 'px-2 py-1 text-xs min-h-[24px]',
    sm: 'px-3 py-1.5 text-sm min-h-[32px]',
    md: 'px-4 py-2 text-sm min-h-[40px] sm:px-4 sm:py-2',
    lg: 'px-6 py-3 text-base min-h-[44px] sm:px-6 sm:py-3'
  }
  classes.push(sizeClasses[props.size])

  // Rounded classes
  const roundedClasses = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full'
  }
  classes.push(roundedClasses[props.rounded])

  // Variant classes
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed dark:bg-blue-600 dark:hover:bg-blue-700',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 shadow-sm hover:shadow-md disabled:bg-gray-100 disabled:cursor-not-allowed dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-200',
    success: 'bg-green-600 hover:bg-green-700 text-white shadow-sm hover:shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed dark:bg-green-600 dark:hover:bg-green-700',
    danger: 'bg-red-600 hover:bg-red-700 text-white shadow-sm hover:shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed dark:bg-red-600 dark:hover:bg-red-700',
    warning: 'bg-yellow-500 hover:bg-yellow-600 text-white shadow-sm hover:shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed dark:bg-yellow-600 dark:hover:bg-yellow-700',
    info: 'bg-purple-600 hover:bg-purple-700 text-white shadow-sm hover:shadow-md disabled:bg-gray-400 disabled:cursor-not-allowed dark:bg-purple-600 dark:hover:bg-purple-700',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-700 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed dark:hover:bg-gray-800 dark:text-gray-300 dark:border-gray-600'
  }
  classes.push(variantClasses[props.variant])

  // Disabled state
  if (props.disabled || props.loading) {
    classes.push('opacity-75')
  }

  return classes.join(' ')
})
</script>
