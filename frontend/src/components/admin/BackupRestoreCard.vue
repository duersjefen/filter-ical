<template>
  <AdminCardWrapper
    :title="$t('admin.backupRestore')"
    subtitle="Create backups, restore previous configurations, or export to file"
    icon="💾"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <div class="space-y-6">

      <!-- Create Backup Section -->
      <div class="space-y-3">
        <input
          v-model="backupDescription"
          type="text"
          :placeholder="$t('admin.backupDescriptionPlaceholder')"
          class="w-full px-4 py-2.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm transition-all duration-200 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 placeholder-gray-400 dark:placeholder-gray-500"
        />

        <div class="flex flex-wrap gap-3">
          <button
            @click="handleCreateBackup"
            :disabled="loading"
            class="flex-1 min-w-[200px] bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <span>💾</span>
            <span>{{ $t('admin.createBackup') }}</span>
          </button>

          <button
            @click="$emit('export-configuration')"
            :disabled="loading"
            class="flex-1 min-w-[200px] bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <span>📤</span>
            <span>{{ $t('admin.exportToFile') }}</span>
          </button>
        </div>
      </div>

      <!-- Backup History -->
      <div v-if="backups && backups.length > 0" class="space-y-3">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <span>📜</span>
          <span>{{ $t('admin.backupHistory') }}</span>
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">({{ backups.length }})</span>
        </h3>

        <div class="space-y-2">
          <div
            v-for="backup in backups"
            :key="backup.id"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-600 transition-colors duration-200"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <!-- Backup Info -->
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xl" :title="getBackupTypeLabel(backup.backup_type)">
                    {{ getBackupTypeIcon(backup.backup_type) }}
                  </span>
                  <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {{ formatDate(backup.created_at) }}
                  </span>
                  <span
                    v-if="backup.backup_type !== 'manual'"
                    class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
                  >
                    {{ getBackupTypeLabel(backup.backup_type) }}
                  </span>
                </div>

                <!-- Description (only show if exists) -->
                <p
                  v-if="backup.description"
                  class="text-sm text-gray-600 dark:text-gray-400 truncate"
                >
                  {{ backup.description }}
                </p>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <button
                  @click="$emit('restore-backup', backup.id)"
                  :disabled="loading"
                  class="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md transition-colors duration-200"
                  :title="$t('admin.restoreBackup')"
                >
                  🔄 {{ $t('admin.restore') }}
                </button>
                <button
                  @click="$emit('download-backup', backup.id)"
                  :disabled="loading"
                  class="px-3 py-1.5 text-sm bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white rounded-md transition-colors duration-200"
                  :title="$t('admin.downloadBackup')"
                >
                  ⬇️
                </button>
                <button
                  @click="$emit('delete-backup', backup.id)"
                  :disabled="loading"
                  class="px-3 py-1.5 text-sm bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-md transition-colors duration-200"
                  :title="$t('admin.deleteBackup')"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading"
        class="text-center py-8 text-gray-500 dark:text-gray-400"
      >
        <div class="text-4xl mb-2">📦</div>
        <p class="text-sm">{{ $t('admin.noBackupsYet') }}</p>
        <p class="text-xs mt-1">{{ $t('admin.createFirstBackup') }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin text-4xl mb-2">⏳</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('admin.loading') }}</p>
      </div>

    </div>
  </AdminCardWrapper>
</template>

<script>
import AdminCardWrapper from './AdminCardWrapper.vue'
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

export default {
  name: 'BackupRestoreCard',
  components: {
    AdminCardWrapper
  },
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    backups: {
      type: Array,
      default: () => []
    }
  },
  emits: [
    'toggle',
    'create-backup',
    'export-configuration',
    'restore-backup',
    'download-backup',
    'delete-backup'
  ],
  setup(props, { emit }) {
    const { t } = useI18n()

    // Backup description state
    const backupDescription = ref('')

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)

      // Check if date is valid
      if (isNaN(date.getTime())) return dateString

      // Format in user's local timezone
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      }).format(date)
    }

    const getBackupTypeIcon = (type) => {
      const icons = {
        'manual': '📝',
        'auto_pre_reset': '🔄',
        'auto_pre_import': '📥',
        'auto_pre_restore': '⏪'
      }
      return icons[type] || '💾'
    }

    const getBackupTypeLabel = (type) => {
      return t(`admin.backupType.${type}`)
    }

    const handleCreateBackup = () => {
      emit('create-backup', backupDescription.value.trim())
      backupDescription.value = '' // Clear after creating
    }

    return {
      formatDate,
      getBackupTypeIcon,
      getBackupTypeLabel,
      backupDescription,
      handleCreateBackup
    }
  }
}
</script>
