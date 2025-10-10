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

    <!-- Input Container (for password toggle button positioning) -->
    <div class="relative">
      <!-- Input Field -->
      <input
        :id="id"
        :type="computedType"
        :value="modelValue"
        @input="handleInput"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :minlength="minlength"
        :maxlength="maxlength"
        :pattern="pattern"
        :autocomplete="autocomplete"
        :class="inputClasses"
      />

      <!-- Password Toggle Button -->
      <button
        v-if="isPasswordType && modelValue"
        type="button"
        @click="togglePasswordVisibility"
        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        :title="showPassword ? 'Hide password' : 'Show password'"
      >
        <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        </svg>
      </button>
    </div>

    <!-- Helper Text or Error Message -->
    <div v-if="error || helperText" class="text-xs" :class="error ? 'text-red-600 dark:text-red-400 font-semibold' : 'text-gray-500 dark:text-gray-400'">
      {{ error || helperText }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'email', 'password', 'url', 'tel', 'number', 'search'].includes(value)
  },
  modelValue: {
    type: [String, Number],
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
  pattern: {
    type: String,
    default: undefined
  },
  autocomplete: {
    type: String,
    default: undefined
  }
})

const emit = defineEmits(['update:modelValue'])

const showPassword = ref(false)

const isPasswordType = computed(() => props.type === 'password')

const computedType = computed(() => {
  if (isPasswordType.value && showPassword.value) {
    return 'text'
  }
  return props.type
})

const inputClasses = computed(() => {
  const classes = [
    'w-full px-4 py-3.5 border-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-4 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500'
  ]

  // Add padding for password toggle button
  if (isPasswordType.value && props.modelValue) {
    classes.push('pr-12')
  }

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

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}
</script>
