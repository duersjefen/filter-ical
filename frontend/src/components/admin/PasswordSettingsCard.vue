<template>
  <AdminCardWrapper
    :title="$t('admin.domainAuth.passwordSettings.title')"
    :subtitle="$t('admin.domainAuth.passwordSettings.subtitle')"
    icon="🔐"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Password Sections - Side by side on larger screens -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <!-- Admin Password Section -->
        <div class="bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-900/20 dark:to-purple-800/10 rounded-xl p-4 sm:p-6 border-2 border-purple-200 dark:border-purple-700 shadow-sm">
          <div class="mb-4">
            <div class="flex items-start justify-between gap-2 mb-2">
              <h4 class="text-base sm:text-lg font-bold text-purple-900 dark:text-purple-100">
                {{ $t('admin.domainAuth.passwordSettings.adminPassword.title') }}
              </h4>
              <span class="px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap" :class="adminPasswordSet ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'">
                {{ adminPasswordSet ? $t('admin.domainAuth.passwordSettings.adminPassword.enabled') : $t('admin.domainAuth.passwordSettings.adminPassword.disabled') }}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-purple-700 dark:text-purple-300">
              {{ $t('admin.domainAuth.passwordSettings.adminPassword.description', { domain }) }}
            </p>
          </div>

          <div v-if="showAdminForm" class="space-y-3">
            <input
              v-model="adminPassword"
              type="password"
              :placeholder="$t('admin.domainAuth.passwordSettings.adminPassword.placeholder')"
              class="w-full px-4 py-2 border-2 border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:outline-none focus:border-purple-500"
            />
            <input
              v-model="adminPasswordConfirm"
              type="password"
              :placeholder="$t('admin.domainAuth.passwordSettings.adminPassword.confirmPlaceholder')"
              class="w-full px-4 py-2 border-2 border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:outline-none focus:border-purple-500"
            />
            <div class="flex gap-2">
              <button
                @click="handleSetAdminPassword"
                :disabled="!canSetAdminPassword || saving"
                class="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                {{ adminPasswordSet ? $t('admin.domainAuth.passwordSettings.adminPassword.changePassword') : $t('admin.domainAuth.passwordSettings.adminPassword.setPassword') }}
              </button>
              <button
                @click="showAdminForm = false; adminPassword = ''; adminPasswordConfirm = ''"
                class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                {{ $t('common.cancel') }}
              </button>
            </div>
          </div>
          <div v-else class="flex gap-2">
            <button
              @click="showAdminForm = true"
              class="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              {{ adminPasswordSet ? $t('admin.domainAuth.passwordSettings.adminPassword.changePassword') : $t('admin.domainAuth.passwordSettings.adminPassword.setPassword') }}
            </button>
            <button
              v-if="adminPasswordSet"
              @click="handleRemoveAdminPassword"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              {{ $t('admin.domainAuth.passwordSettings.adminPassword.removePassword') }}
            </button>
          </div>
        </div>

        <!-- User Password Section -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-900/20 dark:to-blue-800/10 rounded-xl p-4 sm:p-6 border-2 border-blue-200 dark:border-blue-700 shadow-sm">
          <div class="mb-4">
            <div class="flex items-start justify-between gap-2 mb-2">
              <h4 class="text-base sm:text-lg font-bold text-blue-900 dark:text-blue-100">
                {{ $t('admin.domainAuth.passwordSettings.userPassword.title') }}
              </h4>
              <span class="px-3 py-1 rounded-full text-xs font-bold whitespace-nowrap" :class="userPasswordSet ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'">
                {{ userPasswordSet ? $t('admin.domainAuth.passwordSettings.userPassword.enabled') : $t('admin.domainAuth.passwordSettings.userPassword.disabled') }}
              </span>
            </div>
            <p class="text-xs sm:text-sm text-blue-700 dark:text-blue-300">
              {{ $t('admin.domainAuth.passwordSettings.userPassword.description', { domain }) }}
            </p>
          </div>

          <div v-if="showUserForm" class="space-y-3">
            <input
              v-model="userPassword"
              type="password"
              :placeholder="$t('admin.domainAuth.passwordSettings.userPassword.placeholder')"
              class="w-full px-4 py-2 border-2 border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <input
              v-model="userPasswordConfirm"
              type="password"
              :placeholder="$t('admin.domainAuth.passwordSettings.userPassword.confirmPlaceholder')"
              class="w-full px-4 py-2 border-2 border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <div class="flex gap-2">
              <button
                @click="handleSetUserPassword"
                :disabled="!canSetUserPassword || saving"
                class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                {{ userPasswordSet ? $t('admin.domainAuth.passwordSettings.userPassword.changePassword') : $t('admin.domainAuth.passwordSettings.userPassword.setPassword') }}
              </button>
              <button
                @click="showUserForm = false; userPassword = ''; userPasswordConfirm = ''"
                class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                {{ $t('common.cancel') }}
              </button>
            </div>
          </div>
          <div v-else class="flex gap-2">
            <button
              @click="showUserForm = true"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              {{ userPasswordSet ? $t('admin.domainAuth.passwordSettings.userPassword.changePassword') : $t('admin.domainAuth.passwordSettings.userPassword.setPassword') }}
            </button>
            <button
              v-if="userPasswordSet"
              @click="handleRemoveUserPassword"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              {{ $t('admin.domainAuth.passwordSettings.userPassword.removePassword') }}
            </button>
          </div>
        </div>
      </div>
  </AdminCardWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDomainAuth } from '@/composables/useDomainAuth'
import { useNotification } from '@/composables/useNotification'
import { useI18n } from 'vue-i18n'
import AdminCardWrapper from './AdminCardWrapper.vue'

const props = defineProps({
  domain: {
    type: String,
    required: true
  },
  expanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle'])

const { t } = useI18n()
const notify = useNotification()
const {
  verifyPassword,
  setAdminPassword,
  setUserPassword,
  removeAdminPassword,
  removeUserPassword,
  getPasswordStatus
} = useDomainAuth(props.domain)

const adminPassword = ref('')
const adminPasswordConfirm = ref('')
const userPassword = ref('')
const userPasswordConfirm = ref('')
const adminPasswordSet = ref(false)
const userPasswordSet = ref(false)
const showAdminForm = ref(false)
const showUserForm = ref(false)
const saving = ref(false)

const canSetAdminPassword = computed(() => {
  return adminPassword.value.length >= 4 && adminPassword.value === adminPasswordConfirm.value
})

const canSetUserPassword = computed(() => {
  return userPassword.value.length >= 4 && userPassword.value === userPasswordConfirm.value
})

const loadPasswordStatus = async () => {
  const status = await getPasswordStatus()
  adminPasswordSet.value = status.admin_password_set
  userPasswordSet.value = status.user_password_set
}

const handleSetAdminPassword = async () => {
  if (!canSetAdminPassword.value) return

  saving.value = true
  const result = await setAdminPassword(adminPassword.value)
  saving.value = false

  if (result.success) {
    notify.success(t('admin.domainAuth.passwordSettings.success.adminSet'))
    adminPassword.value = ''
    adminPasswordConfirm.value = ''
    showAdminForm.value = false
    await loadPasswordStatus()
  } else {
    notify.error(result.error || t('admin.domainAuth.passwordSettings.error.adminSet'))
  }
}

const handleSetUserPassword = async () => {
  if (!canSetUserPassword.value) return

  saving.value = true
  const result = await setUserPassword(userPassword.value)
  saving.value = false

  if (result.success) {
    notify.success(t('admin.domainAuth.passwordSettings.success.userSet'))
    userPassword.value = ''
    userPasswordConfirm.value = ''
    showUserForm.value = false
    await loadPasswordStatus()
  } else {
    notify.error(result.error || t('admin.domainAuth.passwordSettings.error.userSet'))
  }
}

const handleRemoveAdminPassword = async () => {
  if (!confirm(t('admin.domainAuth.passwordSettings.confirm.removeAdmin'))) return

  saving.value = true
  const result = await removeAdminPassword()
  saving.value = false

  if (result.success) {
    notify.success(t('admin.domainAuth.passwordSettings.success.adminRemoved'))
    await loadPasswordStatus()
  } else {
    notify.error(result.error || t('admin.domainAuth.passwordSettings.error.adminRemoved'))
  }
}

const handleRemoveUserPassword = async () => {
  if (!confirm(t('admin.domainAuth.passwordSettings.confirm.removeUser'))) return

  saving.value = true
  const result = await removeUserPassword()
  saving.value = false

  if (result.success) {
    notify.success(t('admin.domainAuth.passwordSettings.success.userRemoved'))
    await loadPasswordStatus()
  } else {
    notify.error(result.error || t('admin.domainAuth.passwordSettings.error.userRemoved'))
  }
}

onMounted(() => {
  loadPasswordStatus()
})
</script>
