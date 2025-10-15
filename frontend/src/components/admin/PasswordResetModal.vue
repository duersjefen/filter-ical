<template>
  <div
    v-if="show"
    role="dialog"
    aria-modal="true"
    aria-labelledby="reset-modal-title"
    @keydown.esc="$emit('close')"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
  >
    <div class="max-w-md w-full mx-4">
      <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
        <h2 id="reset-modal-title" class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-4">
          Reset Admin Password
        </h2>

        <div v-if="!requestSent">
          <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
            A password reset link will be sent to <strong>{{ email }}</strong>
          </p>

          <div v-if="error" role="alert" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-4">
            {{ error }}
          </div>

          <div class="flex gap-3">
            <button
              @click="$emit('close')"
              class="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 rounded-lg font-semibold"
            >
              Cancel
            </button>
            <button
              @click="$emit('confirm')"
              :disabled="requesting"
              class="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg font-semibold"
            >
              {{ requesting ? 'Sending...' : 'Send Reset Link' }}
            </button>
          </div>
        </div>

        <div v-else>
          <div class="bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg mb-4">
            Reset link sent! Check your email.
          </div>
          <button
            @click="$emit('close')"
            class="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    required: true
  },
  email: {
    type: String,
    default: 'info@paiss.me'
  },
  requestSent: {
    type: Boolean,
    default: false
  },
  requesting: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
})

defineEmits(['confirm', 'close'])
</script>
