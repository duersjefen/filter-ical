<template>
  <div
    v-if="show"
    role="dialog"
    aria-modal="true"
    aria-labelledby="approve-modal-title"
    @keydown.esc="$emit('cancel')"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
  >
    <div class="max-w-2xl w-full mx-4">
      <div class="bg-gradient-to-br from-white via-white to-green-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-green-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
        <!-- Icon -->
        <div class="flex items-center justify-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 rounded-2xl flex items-center justify-center shadow-lg">
            <svg aria-hidden="true" class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
        </div>

        <!-- Title & Description -->
        <h2 id="approve-modal-title" class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
          Approve Domain Request
        </h2>
        <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
          This will create the domain calendar and make it accessible to the user.
        </p>

        <!-- Info Box -->
        <div class="bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-4 py-3 rounded-xl mb-6 border border-green-200 dark:border-green-700">
          <div class="flex items-start gap-3">
            <svg aria-hidden="true" class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>
            <div>
              <p class="font-semibold text-sm mb-1">What happens next</p>
              <p class="text-sm">The domain will be created immediately and the user will be able to access their calendar.</p>
            </div>
          </div>
        </div>

        <!-- Custom Message (Optional) -->
        <div class="mb-4">
          <label for="approval-message" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
            Custom Message (Optional)
          </label>
          <textarea
            id="approval-message"
            :value="message"
            @input="$emit('update:message', $event.target.value)"
            rows="3"
            class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-green-500 dark:focus:border-green-400 focus:ring-4 focus:ring-green-100 dark:focus:ring-green-900/50 resize-none"
            placeholder="Add a personal message or instructions for the user (optional)..."
          />
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
            This will be included in the approval email if you choose to send one.
          </p>
        </div>

        <!-- Email Toggle -->
        <div class="mb-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              :checked="sendEmail"
              @change="$emit('update:sendEmail', $event.target.checked)"
              class="w-5 h-5 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <div class="flex-1">
              <span class="font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <svg aria-hidden="true" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                Send email notification to user
              </span>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">User will receive their domain URL and admin panel link</p>
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
            :disabled="submitting"
            class="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 dark:from-green-600 dark:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
          >
            {{ submitting ? 'Approving...' : 'Confirm Approval' }}
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
  message: {
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

defineEmits(['confirm', 'cancel', 'update:message', 'update:sendEmail'])
</script>
