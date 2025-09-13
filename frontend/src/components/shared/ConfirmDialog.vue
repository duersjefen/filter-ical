<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div 
      class="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="cancel"
    ></div>
    
    <!-- Modal -->
    <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 max-w-md w-full mx-4 transform transition-all">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-3">
          <div class="text-2xl">⚠️</div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ title }}
          </h3>
        </div>
      </div>
      
      <!-- Content -->
      <div class="px-6 py-4">
        <p class="text-gray-600 dark:text-gray-300">
          {{ message }}
        </p>
      </div>
      
      <!-- Actions -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
        <button
          @click="cancel"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg font-medium transition-colors"
        >
          {{ cancelText }}
        </button>
        <button
          @click="confirm"
          class="px-4 py-2 text-white bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 rounded-lg font-medium transition-colors shadow-md"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: 'Delete'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  }
})

// Emits
const emit = defineEmits(['confirm', 'cancel'])

// State
const show = ref(false)

// Methods
const open = () => {
  show.value = true
}

const close = () => {
  show.value = false
}

const confirm = () => {
  emit('confirm')
  close()
}

const cancel = () => {
  emit('cancel')
  close()
}

// Expose methods
defineExpose({
  open,
  close
})
</script>