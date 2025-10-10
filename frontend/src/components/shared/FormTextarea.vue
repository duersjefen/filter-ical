<template>
  <div class="space-y-1">
    <!-- Label -->
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-semibold text-gray-700 dark:text-gray-300"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
      <span v-if="optional" class="text-gray-500 dark:text-gray-400 font-normal text-xs ml-1">({{ optional }})</span>
    </label>

    <!-- Textarea Field -->
    <textarea
      :id="id"
      :value="modelValue"
      @input="handleInput"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :minlength="minlength"
      :maxlength="maxlength"
      :rows="rows"
      :class="textareaClasses"
    ></textarea>

    <!-- Helper Text, Error Message, or Character Count -->
    <div class="flex items-center justify-between">
      <div v-if="error || helperText" class="text-xs" :class="error ? 'text-red-600 dark:text-red-400 font-semibold' : 'text-gray-500 dark:text-gray-400'">
        {{ error || helperText }}
      </div>
      <div v-else-if="showCharCount && maxlength" class="text-xs text-gray-500 dark:text-gray-400">
        {{ characterCount }} / {{ maxlength }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  optional: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  minlength: {
    type: [String, Number],
    default: undefined
  },
  maxlength: {
    type: [String, Number],
    default: undefined
  },
  rows: {
    type: [String, Number],
    default: 4
  },
  showCharCount: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const characterCount = computed(() => {
  return props.modelValue ? props.modelValue.length : 0
})

const textareaClasses = computed(() => {
  const classes = [
    'w-full px-4 py-3.5 border-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-4 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500 resize-none'
  ]

  // Error or normal state
  if (props.error) {
    classes.push('border-red-500 dark:border-red-400 focus:border-red-500 dark:focus:border-red-400 focus:ring-red-100 dark:focus:ring-red-900/50')
  } else {
    classes.push('border-gray-300 dark:border-gray-600 focus:border-green-500 dark:focus:border-green-400 focus:ring-green-100 dark:focus:ring-green-900/50 hover:border-gray-400 dark:hover:border-gray-500')
  }

  // Disabled state
  if (props.disabled) {
    classes.push('opacity-50 cursor-not-allowed')
  }

  return classes.join(' ')
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}
</script>
