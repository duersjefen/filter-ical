<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="edit-user-title"
    @keydown.esc="handleCancel"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="handleCancel"
    ></div>

    <!-- Modal -->
    <div
      class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl border-2 border-gray-200 dark:border-gray-700 max-w-md w-full mx-4 transform transition-all"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b-2 border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-white dark:from-gray-800 dark:to-gray-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </div>
            <h3 id="edit-user-title" class="text-lg font-bold text-gray-900 dark:text-gray-100">
              Edit User
            </h3>
          </div>
          <button
            @click="handleCancel"
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <svg class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="px-6 py-4 space-y-4">
        <!-- Username (Read-only) -->
        <div>
          <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
            Username
          </label>
          <div class="px-4 py-2 bg-gray-50 dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-lg text-gray-500 dark:text-gray-400">
            {{ user.username }}
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Username cannot be changed</p>
        </div>

        <!-- Email -->
        <div>
          <label for="edit-email" class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
            Email
          </label>
          <input
            id="edit-email"
            v-model="formData.email"
            type="email"
            placeholder="user@example.com"
            class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-900/50 transition-all"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="edit-password" class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
            New Password
          </label>
          <div class="relative">
            <input
              id="edit-password"
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Leave blank to keep current password"
              class="w-full px-4 py-2 pr-12 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-900/50 transition-all"
            />
            <button
              v-if="formData.password"
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
            >
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Minimum 8 characters</p>
        </div>

        <!-- Role -->
        <div>
          <label for="edit-role" class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
            Role
          </label>
          <select
            id="edit-role"
            v-model="formData.role"
            class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:border-purple-500 dark:focus:border-purple-400 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-900/50 transition-all"
          >
            <option value="user">User</option>
            <option value="global_admin">Admin</option>
          </select>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Admins have full system access</p>
        </div>

        <!-- Validation Error -->
        <div v-if="validationError" class="bg-red-50 dark:bg-red-900/30 border-2 border-red-200 dark:border-red-700 rounded-lg p-3">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <span class="text-sm font-semibold text-red-800 dark:text-red-200">{{ validationError }}</span>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="px-6 py-4 border-t-2 border-gray-200 dark:border-gray-700 flex justify-end gap-3">
        <button
          @click="handleCancel"
          class="px-6 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg font-semibold transition-all"
        >
          Cancel
        </button>
        <button
          @click="handleSave"
          :disabled="saving"
          class="px-6 py-2 text-white bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

// Form state
const formData = ref({
  email: '',
  password: '',
  role: 'user'
})

const showPassword = ref(false)
const saving = ref(false)
const validationError = ref('')

// Watch for user prop changes to reset form
watch(() => props.user, (newUser) => {
  if (newUser) {
    formData.value = {
      email: newUser.email || '',
      password: '',
      role: newUser.role || 'user'
    }
    validationError.value = ''
  }
}, { immediate: true })

function validateForm() {
  // Email validation
  if (formData.value.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    validationError.value = 'Please enter a valid email address'
    return false
  }

  // Password validation (only if password is being changed)
  if (formData.value.password && formData.value.password.length < 8) {
    validationError.value = 'Password must be at least 8 characters'
    return false
  }

  validationError.value = ''
  return true
}

function handleCancel() {
  emit('close')
}

function handleSave() {
  if (!validateForm()) {
    return
  }

  saving.value = true

  // Build updates object (only include changed fields)
  const updates = {}

  if (formData.value.email !== props.user.email) {
    updates.email = formData.value.email
  }

  if (formData.value.password) {
    updates.password = formData.value.password
  }

  if (formData.value.role !== props.user.role) {
    updates.role = formData.value.role
  }

  // Only emit if there are actual changes
  if (Object.keys(updates).length === 0) {
    validationError.value = 'No changes to save'
    saving.value = false
    return
  }

  emit('save', updates)

  // Reset saving state (parent will close modal on success)
  setTimeout(() => {
    saving.value = false
  }, 500)
}
</script>
