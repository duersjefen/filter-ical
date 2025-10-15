<template>
  <div
    v-if="show"
    role="dialog"
    aria-modal="true"
    aria-labelledby="reject-modal-title"
    @keydown.esc="$emit('cancel')"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
  >
    <div class="max-w-2xl w-full mx-4">
      <div class="bg-gradient-to-br from-white via-white to-red-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-red-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
        <!-- Icon -->
        <div class="flex items-center justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 dark:from-red-600 dark:to-red-700 rounded-2xl flex items-center justify-center shadow-lg">
            <svg aria-hidden="true" class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </div>
        </div>

        <!-- Title & Description -->
        <h2 id="reject-modal-title" class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
          Reject Domain Request
        </h2>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
          Provide a reason for rejecting this request. The user will receive an email notification with your explanation.
        </p>

        <!-- Warning Box -->
        <div class="bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 px-4 py-3 rounded-xl mb-6 border border-amber-200 dark:border-amber-700">
          <div class="flex items-start gap-3">
            <svg aria-hidden="true" class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <div>
              <p class="font-semibold text-sm mb-1">Email notification will be sent</p>
              <p class="text-sm">The user will receive your rejection reason via email. Please be clear and constructive in your feedback.</p>
            </div>
          </div>
        </div>

        <!-- Rejection Reason Textarea -->
        <div class="mb-4">
          <label for="rejection-reason" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            Rejection Reason
          </label>
          <textarea
            id="rejection-reason"
            :value="reason"
            @input="$emit('update:reason', $event.target.value)"
            rows="6"
            class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-red-500 dark:focus:border-red-400 focus:ring-4 focus:ring-red-100 dark:focus:ring-red-900/50 resize-none"
            placeholder="Example: Your calendar URL is not accessible, or it contains events that don't meet our content guidelines..."
            autofocus
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Be specific and helpful - this helps users understand how to improve their request.
          </p>
        </div>

        <!-- Email Toggle -->
        <div class="mb-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              :checked="sendEmail"
              @change="$emit('update:sendEmail', $event.target.checked)"
              class="w-5 h-5 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500 dark:focus:ring-red-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <div class="flex-1">
              <span class="font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                Send email notification to user
              </span>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">User will receive your rejection reason via email</p>
            </div>
          </label>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button
            @click="$emit('cancel')"
            :disabled="submitting"
            class="flex-1 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
          >
            Cancel
          </button>
          <button
            @click="$emit('confirm')"
            :disabled="submitting || !reason.trim()"
            class="flex-1 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 dark:from-red-600 dark:to-red-700 dark:hover:from-red-700 dark:hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
          >
            {{ submitting ? 'Sending...' : 'Confirm Rejection' }}
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
  reason: {
    type: String,
    default: ''
  },
  sendEmail: {
    type: Boolean,
    default: true
  },
  submitting: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'cancel', 'update:reason', 'update:sendEmail'])
</script>
