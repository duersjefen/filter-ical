<template>
  <!-- Password Gate - Show if admin authentication required and not authenticated -->
  <PasswordGate
    v-if="requiresAdminAuth && !isAdminAuthenticated"
    :domain="domain"
    access-level="admin"
    :title="$t('admin.domainAuth.adminGate.title')"
    :subtitle="$t('admin.domainAuth.adminGate.subtitle', { domain })"
    :password-placeholder="$t('admin.domainAuth.adminGate.passwordPlaceholder')"
    :submit-button-text="$t('admin.domainAuth.adminGate.loginButton')"
    :show-back-button="true"
    @authenticated="onAdminAuthenticated"
    @back="$router.push(`/${domain}`)"
  />

  <div v-else class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden">
    <AppHeader 
      :title="$t('domainAdmin.manageEventsGroups', { domain })"
      :subtitle="$t('domainAdmin.adminPanelSubtitle')"
      :back-button-text="$t('domainAdmin.backToCalendar', { domain })"
      :show-back-button="true"
      page-context="admin"
      @navigate-back="$router.push(`/${domain}`)"
    />

    <!-- Mobile Optimization Notice -->
    <div v-if="isMobile" class="mb-6 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
      <div class="flex items-start gap-3">
        <div class="text-2xl flex-shrink-0">💻</div>
        <div class="min-w-0 flex-1">
          <h3 class="font-semibold text-amber-800 dark:text-amber-200 text-base mb-2">
            {{ $t('domainAdmin.mobileNotOptimized') }}
          </h3>
          <p class="text-amber-700 dark:text-amber-300 text-sm leading-relaxed">
            {{ $t('domainAdmin.mobileUseDesktop') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Expandable Cards Layout -->
    <div class="space-y-4 sm:space-y-6">
      
      <!-- ⚙️ Auto Rules Card (First Position) -->
      <AutoRulesCard
        :expanded="expandedCards.rules"
        :assignment-rules="assignmentRules"
        :groups="groups"
        :recurring-events="recurringEvents"
        :apply-loading="applyLoading"
        @toggle="toggleCard('rules')"
        @create-rule="handleCreateRule"
        @apply-rule="applyRule"
        @delete-rule-confirm="deleteRuleConfirm"
      />
      
      <!-- 📅 Event Management Card (Second Position) -->
      <EventManagementCard
        :expanded="expandedCards.events"
        :recurring-events="recurringEvents"
        :groups="groups"
        :loading="loading"
        @toggle="toggleCard('events')"
        @create-group="handleCreateGroup"
        @update-group="handleUpdateGroup"
        @delete-group="handleDeleteGroup"
        @handle-group-assignment="handleGroupAssignment"
        @remove-from-group="handleRemoveFromGroup"
      />
      
      <!-- 💾 Backup & Restore Card (Third Position) -->
      <BackupRestoreCard
        :expanded="expandedCards.config"
        :loading="loading"
        :backups="backups"
        @toggle="toggleCard('config')"
        @create-backup="createBackup"
        @export-configuration="exportConfiguration"
        @import-configuration="handleFileUpload"
        @restore-backup="restoreBackupConfirm"
        @download-backup="downloadBackup"
        @delete-backup="deleteBackupConfirm"
      />

      <!-- 🔐 Password Settings Card (Fourth Position) -->
      <PasswordSettingsCard
        :domain="domain"
        :expanded="expandedCards.password"
        @toggle="toggleCard('password')"
      />

    </div>
  </div>


  <!-- Confirmation Dialog -->
  <div v-if="confirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ $t('domainAdmin.confirmAction') }}</h3>
      <p class="text-gray-700 dark:text-gray-300 mb-6">{{ confirmDialog.message }}</p>
      <div class="flex gap-3 justify-end">
        <button
          @click="closeConfirm"
          class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors duration-200"
        >
          Cancel
        </button>
        <button
          @click="confirmDialog.onConfirm(); closeConfirm()"
          class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          {{ $t('domainAdmin.confirm') }}
        </button>
      </div>
    </div>
  </div>

</template>

<script>
import { ref, onMounted } from 'vue'
import { useAdmin } from '../composables/useAdmin'
import { useHTTP } from '../composables/useHTTP'
import { useMobileDetection } from '../composables/useMobileDetection'
import { useNotification } from '../composables/useNotification'
import { useDomainAuth } from '../composables/useDomainAuth'
import { API_BASE_URL } from '../constants/api'
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/shared/AppHeader.vue'
import AutoRulesCard from '../components/admin/AutoRulesCard.vue'
import EventManagementCard from '../components/admin/EventManagementCard.vue'
import BackupRestoreCard from '../components/admin/BackupRestoreCard.vue'
import PasswordSettingsCard from '../components/admin/PasswordSettingsCard.vue'
import PasswordGate from '../components/auth/PasswordGate.vue'

export default {
  name: 'AdminView',
  components: {
    AppHeader,
    AutoRulesCard,
    EventManagementCard,
    BackupRestoreCard,
    PasswordSettingsCard,
    PasswordGate
  },
  props: {
    domain: {
      type: String,
      required: true
    }
  },
  setup(props) {
    // Mobile detection
    const { isMobile } = useMobileDetection()

    // i18n
    const { t } = useI18n()

    // Global notification system
    const notify = useNotification()

    // Domain authentication
    const { isAdminAuthenticated, getPasswordStatus, checkAuth } = useDomainAuth(props.domain)
    const requiresAdminAuth = ref(false)

    // Use the admin composable for all data and functionality
    const {
      // Data
      recurringEvents,
      groups,
      assignmentRules,
      loading,
      error,
      
      // API Functions
      loadAllAdminData,
      createGroup: createGroupAPI,
      updateGroup,
      addEventsToGroup,
      bulkUnassignEvents,
      createAssignmentRule,
      deleteAssignmentRule,
      applyExistingRule,
      deleteGroup,
      removeEventsFromGroup
    } = useAdmin(props.domain)

    // HTTP functions for configuration management
    const { post, get, del } = useHTTP()

    // Backup state
    const backups = ref([])

    // UI State - Expandable Cards
    const expandedCards = ref({
      rules: false,    // Auto Rules card starts collapsed
      events: true,    // Events card starts expanded
      config: false,   // Configuration card starts collapsed
      password: false  // Password Settings card starts collapsed
    })
    // HMR trigger

    // Loading states
    const applyLoading = ref(false)

    // Confirmation Dialog State
    const confirmDialog = ref(null)

    // Card Management
    const toggleCard = (cardName) => {
      expandedCards.value[cardName] = !expandedCards.value[cardName]
    }

    // Notification Helpers (wrapper for global notification system)
    const showNotification = (message, type = 'success') => {
      if (type === 'success') {
        notify.success(message)
      } else {
        notify.error(message)
      }
    }

    const closeConfirm = () => {
      confirmDialog.value = null
    }

    const showConfirmDialog = (message, onConfirm) => {
      confirmDialog.value = { message, onConfirm }
    }

    // UI Handlers - Pure presentation logic
    const handleCreateGroup = async (groupName) => {
      const result = await createGroupAPI(groupName)
      showNotification(
        result.success ? t('domainAdmin.groupCreatedSuccessfully') : t('domainAdmin.failedToCreateGroup', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const handleUpdateGroup = async (groupId, newName) => {
      const result = await updateGroup(groupId, newName)
      showNotification(
        result.success ? t('domainAdmin.groupUpdatedSuccessfully') : t('domainAdmin.failedToUpdateGroup', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const handleGroupAssignment = async (groupId, eventTitles) => {
      if (groupId === 'unassigned') {
        const result = await bulkUnassignEvents(eventTitles)
        if (result.success) {
          showNotification(`Successfully unassigned ${eventTitles.length} event${eventTitles.length > 1 ? 's' : ''}!`, 'success')
        } else {
          showNotification(`Failed to unassign events: ${result.error}`, 'error')
        }
      } else {
        const result = await addEventsToGroup(groupId, eventTitles)
        if (result.success) {
          const groupName = groups.value.find(g => g.id === groupId)?.name || t('domainAdmin.unknownGroup')
          showNotification(`Successfully added ${eventTitles.length} event${eventTitles.length > 1 ? 's' : ''} to ${groupName}!`, 'success')
        } else {
          showNotification(`Failed to add events: ${result.error}`, 'error')
        }
      }
    }

    // Rule Management Handlers
    const handleCreateRule = async (ruleData) => {
      const result = await createAssignmentRule(ruleData.rule_type, ruleData.rule_value, ruleData.target_group_id)
      showNotification(
        result.success ? t('domainAdmin.assignmentRuleCreatedSuccessfully') : t('domainAdmin.failedToCreateAssignmentRule', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const applyRule = async (rule) => {
      applyLoading.value = true
      
      try {
        const result = await applyExistingRule(rule)
        
        if (result.success) {
          showNotification(result.message, 'success')
        } else {
          showNotification(`Failed to apply rule: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to apply rule: ${error.message}`, 'error')
      } finally {
        applyLoading.value = false
      }
    }

    const deleteRuleConfirm = (rule) => {
      const message = t('domainAdmin.confirmDeleteRule', { ruleType: rule.rule_type, ruleValue: rule.rule_value })
      showConfirmDialog(message, () => deleteRule(rule.id))
    }

    const deleteRule = async (ruleId) => {
      const result = await deleteAssignmentRule(ruleId)
      if (result.success) {
        showNotification(t('domainAdmin.assignmentRuleDeletedSuccessfully'), 'success')
      } else {
        showNotification(`Failed to delete assignment rule: ${result.error}`, 'error')
      }
    }

    // Configuration Management
    const exportConfiguration = async () => {
      try {
        // Use raw axios request to get YAML content as text
        const { rawRequest } = useHTTP()
        const response = await rawRequest({
          method: 'GET',
          url: `${API_BASE_URL}/api/domains/${props.domain}/export-config`,
          responseType: 'blob',
          headers: {
            'Accept': 'application/x-yaml'
          }
        })

        // Create download
        const blob = new Blob([response.data], { type: 'application/x-yaml' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${props.domain}_config.yaml`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        showNotification(t('domainAdmin.configurationExportedSuccessfully'), 'success')
      } catch (error) {
        showNotification(`Failed to export configuration: ${error.message}`, 'error')
      }
    }

    const handleFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      try {
        const formData = new FormData()
        formData.append('config_file', file)

        const result = await post(`/api/domains/${props.domain}/import-config`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (result.success) {
          showNotification(t('domainAdmin.configurationImportedSuccessfully'), 'success')
          loadAllAdminData() // Reload data
        } else {
          showNotification(`Failed to import configuration: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to import configuration: ${error.message}`, 'error')
      }

      // Clear the file input
      event.target.value = ''
    }

    const resetConfigurationConfirm = () => {
      const message = t('domainAdmin.confirmResetConfiguration')
      showConfirmDialog(message, resetConfiguration)
    }

    const resetConfiguration = async () => {
      try {
        const result = await post(`/api/domains/${props.domain}/reset-config`)

        if (result.success) {
          showNotification(t('domainAdmin.configurationResetSuccessfully'), 'success')
          loadAllAdminData() // Reload data
        } else {
          showNotification(`Failed to reset configuration: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to reset configuration: ${error.message}`, 'error')
      }
    }

    // Delete Group Handler
    const handleDeleteGroup = async (groupId) => {
      const result = await deleteGroup(groupId)
      showNotification(
        result.success ? t('domainAdmin.groupDeletedSuccessfully') : t('domainAdmin.failedToDeleteGroup', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const handleRemoveFromGroup = async (groupId, eventTitles) => {
      const result = await removeEventsFromGroup(groupId, eventTitles)
      if (result.success) {
        const groupName = groups.value.find(g => g.id === parseInt(groupId))?.name || t('domainAdmin.unknownGroup')
        showNotification(`Successfully removed ${eventTitles.length} event${eventTitles.length > 1 ? 's' : ''} from ${groupName}!`, 'success')
      } else {
        showNotification(`Failed to remove events from group: ${result.error}`, 'error')
      }
    }

    // Backup Management
    const loadBackups = async () => {
      try {
        const result = await get(`/api/domains/${props.domain}/backups`)
        if (result.success) {
          backups.value = result.data || []
        }
      } catch (error) {
        console.error('Failed to load backups:', error)
      }
    }

    const createBackup = async (description = '') => {
      try {
        const payload = description ? { description } : {}
        const result = await post(`/api/domains/${props.domain}/backups`, payload)

        if (result.success) {
          showNotification(t('domainAdmin.backupCreatedSuccessfully'), 'success')
          loadBackups() // Reload backup list
        } else {
          showNotification(`Failed to create backup: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to create backup: ${error.message}`, 'error')
      }
    }

    const restoreBackupConfirm = (backupId) => {
      const message = t('domainAdmin.confirmRestoreBackup')
      showConfirmDialog(message, () => restoreBackup(backupId))
    }

    const restoreBackup = async (backupId) => {
      try {
        const result = await post(`/api/domains/${props.domain}/backups/${backupId}/restore`)

        if (result.success) {
          showNotification(t('domainAdmin.backupRestoredSuccessfully'), 'success')
          loadAllAdminData() // Reload all admin data
          loadBackups() // Reload backup list
        } else {
          showNotification(`Failed to restore backup: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to restore backup: ${error.message}`, 'error')
      }
    }

    const downloadBackup = async (backupId) => {
      try {
        const { rawRequest } = useHTTP()
        const response = await rawRequest({
          method: 'GET',
          url: `${API_BASE_URL}/api/domains/${props.domain}/backups/${backupId}/download`,
          responseType: 'blob',
          headers: {
            'Accept': 'application/x-yaml'
          }
        })

        // Create download
        const blob = new Blob([response.data], { type: 'application/x-yaml' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${props.domain}_backup_${backupId}.yaml`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        showNotification('Backup downloaded successfully', 'success')
      } catch (error) {
        showNotification(`Failed to download backup: ${error.message}`, 'error')
      }
    }

    const deleteBackupConfirm = (backupId) => {
      const message = t('domainAdmin.confirmDeleteBackup')
      showConfirmDialog(message, () => deleteBackup(backupId))
    }

    const deleteBackup = async (backupId) => {
      try {
        const result = await del(`/api/domains/${props.domain}/backups/${backupId}`)

        if (result.success) {
          showNotification(t('domainAdmin.backupDeletedSuccessfully'), 'success')
          loadBackups() // Reload backup list
        } else {
          showNotification(`Failed to delete backup: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to delete backup: ${error.message}`, 'error')
      }
    }

    // Check if domain requires admin authentication
    const checkPasswordProtection = async () => {
      const status = await getPasswordStatus()
      requiresAdminAuth.value = status.admin_password_set
    }

    // Handle successful admin authentication
    const onAdminAuthenticated = () => {
      checkAuth()
      loadAllAdminData()
      loadBackups()
    }

    // Load data on mount
    let hasInitiallyLoaded = false
    onMounted(async () => {
      if (!hasInitiallyLoaded) {
        hasInitiallyLoaded = true
        await checkPasswordProtection()

        // Check if user already has access (e.g., granted admin privileges)
        await checkAuth()

        // Only load data if authenticated or no password required
        if (!requiresAdminAuth.value || isAdminAuthenticated.value) {
          loadAllAdminData()
          loadBackups()
        }
      }
    })

    return {
      // Mobile detection
      isMobile,

      // Authentication
      requiresAdminAuth,
      isAdminAuthenticated,
      onAdminAuthenticated,

      // UI State
      expandedCards,
      loading,
      error,
      applyLoading,

      // Confirmation Dialog State
      confirmDialog,
      closeConfirm,

      // Data
      recurringEvents,
      groups,
      assignmentRules,

      // Methods
      toggleCard,
      handleCreateGroup,
      handleUpdateGroup,
      handleGroupAssignment,
      handleCreateRule,
      applyRule,
      deleteRuleConfirm,
      
      // Configuration Methods
      exportConfiguration,
      handleFileUpload,
      resetConfigurationConfirm,

      // Backup Management
      backups,
      createBackup,
      restoreBackupConfirm,
      deleteBackupConfirm,
      downloadBackup,

      // Group management
      handleDeleteGroup,
      handleRemoveFromGroup
    }
  }
}
</script>