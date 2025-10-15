<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center"
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
    @keydown.esc="cancel"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="cancel"
    ></div>

    <!-- Modal -->
    <div
      ref="dialogContent"
      class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 max-w-md w-full mx-4 transform transition-all"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-3">
          <div class="text-2xl">⚠️</div>
          <h3 id="dialog-title" class="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {{ displayTitle }}
          </h3>
        </div>
      </div>

      <!-- Content -->
      <div class="px-6 py-4">
        <p id="dialog-description" class="text-gray-600 dark:text-gray-300">
          {{ message }}
        </p>
      </div>
      
      <!-- Actions -->
      <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
        <button
          @click="cancel"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg font-medium transition-colors"
        >
          {{ displayCancelText }}
        </button>
        <button
          @click="confirm"
          class="px-4 py-2 text-white bg-red-500 hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 rounded-lg font-medium transition-colors shadow-md"
        >
          {{ displayConfirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Dialog content ref for focus management
const dialogContent = ref(null)

// Props
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  confirmText: {
    type: String,
    default: ''
  },
  cancelText: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['confirm', 'cancel'])

// State
const show = ref(false)

// Computed properties for defaults
const displayTitle = computed(() => props.title || t('domainAdmin.confirmAction'))
const displayConfirmText = computed(() => props.confirmText || t('domainAdmin.delete'))
const displayCancelText = computed(() => props.cancelText || t('domainAdmin.cancel'))

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

// Focus management - focus first button when dialog opens
watch(() => props.show, (isShown) => {
  if (isShown) {
    nextTick(() => {
      const firstButton = dialogContent.value?.querySelector('button')
      firstButton?.focus()
    })
  }
})

// Expose methods
defineExpose({
  open,
  close
})
</script>