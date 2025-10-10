<template>
  <div :class="cardClasses">
    <!-- Header Slot -->
    <div v-if="$slots.header || title" :class="headerClasses">
      <slot name="header">
        <div class="flex items-center gap-3">
          <div v-if="icon" :class="iconContainerClasses">
            <span class="text-2xl">{{ icon }}</span>
          </div>
          <div class="flex-1">
            <h3 :class="titleClasses">{{ title }}</h3>
            <p v-if="subtitle" :class="subtitleClasses">{{ subtitle }}</p>
          </div>
          <slot name="header-actions" />
        </div>
      </slot>
    </div>

    <!-- Body Slot -->
    <div :class="bodyClasses">
      <slot />
    </div>

    <!-- Footer Slot -->
    <div v-if="$slots.footer" :class="footerClasses">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'gradient', 'bordered', 'elevated'].includes(value)
  },
  padding: {
    type: String,
    default: 'md',
    validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
  },
  headerPadding: {
    type: String,
    default: '',
    validator: (value) => ['', 'none', 'sm', 'md', 'lg'].includes(value)
  },
  bodyPadding: {
    type: String,
    default: '',
    validator: (value) => ['', 'none', 'sm', 'md', 'lg'].includes(value)
  },
  footerPadding: {
    type: String,
    default: '',
    validator: (value) => ['', 'none', 'sm', 'md', 'lg'].includes(value)
  },
  color: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'blue', 'green', 'red', 'yellow', 'purple', 'gray'].includes(value)
  }
})

// Padding size mappings
const paddingMap = {
  none: 'p-0',
  sm: 'p-4',
  md: 'p-4 sm:p-6',
  lg: 'p-6 sm:p-8'
}

const cardClasses = computed(() => {
  const classes = ['rounded-xl overflow-hidden transition-all duration-300']

  // Variant styles
  const variantClasses = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    gradient: 'bg-gradient-to-br from-white via-white to-gray-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-gray-900/30 border-2 border-gray-200/80 dark:border-gray-700/80 hover:shadow-2xl hover:border-gray-300/50 dark:hover:border-gray-600/50 backdrop-blur-sm',
    bordered: 'bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600',
    elevated: 'bg-white dark:bg-gray-800 shadow-xl border border-gray-200 dark:border-gray-700'
  }

  classes.push(variantClasses[props.variant])

  // Shadow based on variant
  if (props.variant === 'default' || props.variant === 'gradient') {
    classes.push('shadow-lg')
  }

  return classes.join(' ')
})

const headerClasses = computed(() => {
  const classes = []

  // Use custom header padding or fall back to card padding
  const padding = props.headerPadding || props.padding
  classes.push(paddingMap[padding])

  // Color-specific header styles
  const colorStyles = {
    default: 'bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 border-b border-gray-200 dark:border-gray-700',
    blue: 'bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-blue-200 dark:border-blue-700',
    green: 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-b border-green-200 dark:border-green-700',
    red: 'bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border-b border-red-200 dark:border-red-700',
    yellow: 'bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-b border-yellow-200 dark:border-yellow-700',
    purple: 'bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-b border-purple-200 dark:border-purple-700',
    gray: 'bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-900/20 dark:to-slate-900/20 border-b border-gray-200 dark:border-gray-700'
  }

  classes.push(colorStyles[props.color])

  return classes.join(' ')
})

const bodyClasses = computed(() => {
  const padding = props.bodyPadding || props.padding
  return paddingMap[padding]
})

const footerClasses = computed(() => {
  const classes = []
  const padding = props.footerPadding || props.padding
  classes.push(paddingMap[padding])
  classes.push('bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700')
  return classes.join(' ')
})

const iconContainerClasses = computed(() => {
  const colorStyles = {
    default: 'w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0',
    blue: 'w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center flex-shrink-0',
    green: 'w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center flex-shrink-0',
    red: 'w-10 h-10 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0',
    yellow: 'w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center flex-shrink-0',
    purple: 'w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center flex-shrink-0',
    gray: 'w-10 h-10 bg-gray-100 dark:bg-gray-900/30 rounded-lg flex items-center justify-center flex-shrink-0'
  }

  return colorStyles[props.color]
})

const titleClasses = computed(() => {
  const colorStyles = {
    default: 'text-lg sm:text-xl font-bold text-gray-800 dark:text-gray-100',
    blue: 'text-lg sm:text-xl font-bold text-blue-900 dark:text-blue-100',
    green: 'text-lg sm:text-xl font-bold text-green-900 dark:text-green-100',
    red: 'text-lg sm:text-xl font-bold text-red-900 dark:text-red-100',
    yellow: 'text-lg sm:text-xl font-bold text-yellow-900 dark:text-yellow-100',
    purple: 'text-lg sm:text-xl font-bold text-purple-900 dark:text-purple-100',
    gray: 'text-lg sm:text-xl font-bold text-gray-900 dark:text-gray-100'
  }

  return colorStyles[props.color]
})

const subtitleClasses = computed(() => {
  const colorStyles = {
    default: 'text-sm text-gray-600 dark:text-gray-400 mt-0.5',
    blue: 'text-sm text-blue-700 dark:text-blue-300 mt-0.5',
    green: 'text-sm text-green-700 dark:text-green-300 mt-0.5',
    red: 'text-sm text-red-700 dark:text-red-300 mt-0.5',
    yellow: 'text-sm text-yellow-700 dark:text-yellow-300 mt-0.5',
    purple: 'text-sm text-purple-700 dark:text-purple-300 mt-0.5',
    gray: 'text-sm text-gray-700 dark:text-gray-300 mt-0.5'
  }

  return colorStyles[props.color]
})
</script>
