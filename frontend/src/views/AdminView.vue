<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 overflow-x-hidden">
    <AppHeader 
      :title="$t('admin.manageEventsGroups', { domain })"
      :back-button-text="$t('admin.backToCalendar', { domain })"
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
            {{ $t('admin.mobileNotOptimized') }}
          </h3>
          <p class="text-amber-700 dark:text-amber-300 text-sm leading-relaxed">
            {{ $t('admin.mobileUseDesktop') }}
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
      
      <!-- 💾 Configuration Card (Third Position) -->
      <ConfigurationCard
        :expanded="expandedCards.config"
        :loading="loading"
        @toggle="toggleCard('config')"
        @export-configuration="exportConfiguration"
        @handle-file-upload="handleFileUpload"
        @reset-configuration-confirm="resetConfigurationConfirm"
      />
      
    </div>
  </div>

  <!-- Notification Toast -->
  <div v-if="notification" class="fixed top-4 right-4 z-50 max-w-md">
    <div :class="[
      'rounded-xl shadow-lg border-2 px-6 py-4 transition-all duration-300',
      notification.type === 'success' 
        ? 'bg-gradient-to-r from-green-100 to-green-50 dark:from-green-900/30 dark:to-green-800/30 text-green-800 dark:text-green-200 border-green-300 dark:border-green-700'
        : 'bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 text-red-800 dark:text-red-200 border-red-300 dark:border-red-700'
    ]">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="text-2xl">{{ notification.type === 'success' ? '✅' : '❌' }}</div>
          <span class="font-semibold">{{ notification.message }}</span>
        </div>
        <button 
          @click="notification = null" 
          class="text-xl hover:scale-110 transition-transform duration-200"
        >
          &times;
        </button>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <div v-if="confirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ $t('admin.confirmAction') }}</h3>
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
          {{ $t('admin.confirm') }}
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
import { API_BASE_URL } from '../constants/api'
import { useI18n } from 'vue-i18n'
import AppHeader from '../components/shared/AppHeader.vue'
import AutoRulesCard from '../components/admin/AutoRulesCard.vue'
import EventManagementCard from '../components/admin/EventManagementCard.vue'
import ConfigurationCard from '../components/admin/ConfigurationCard.vue'

export default {
  name: 'AdminView',
  components: {
    AppHeader,
    AutoRulesCard,
    EventManagementCard,
    ConfigurationCard
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
    const { post } = useHTTP()

    // UI State - Expandable Cards
    const expandedCards = ref({
      rules: false,   // Auto Rules card starts collapsed
      events: true,   // Events card starts expanded
      config: false   // Configuration card starts collapsed
    })
    // HMR trigger

    // Loading states
    const applyLoading = ref(false)

    // Notification State
    const notification = ref(null)
    const confirmDialog = ref(null)

    // Card Management
    const toggleCard = (cardName) => {
      expandedCards.value[cardName] = !expandedCards.value[cardName]
    }

    // Notification Helpers
    const showNotification = (message, type = 'success') => {
      notification.value = { message, type }
      setTimeout(() => {
        notification.value = null
      }, 5000)
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
        result.success ? t('admin.groupCreatedSuccessfully') : t('admin.failedToCreateGroup', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const handleUpdateGroup = async (groupId, newName) => {
      const result = await updateGroup(groupId, newName)
      showNotification(
        result.success ? t('admin.groupUpdatedSuccessfully') : t('admin.failedToUpdateGroup', { error: result.error }),
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
          const groupName = groups.value.find(g => g.id === groupId)?.name || t('admin.unknownGroup')
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
        result.success ? t('admin.assignmentRuleCreatedSuccessfully') : t('admin.failedToCreateAssignmentRule', { error: result.error }),
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
      const message = t('admin.confirmDeleteRule', { ruleType: rule.rule_type, ruleValue: rule.rule_value })
      showConfirmDialog(message, () => deleteRule(rule.id))
    }

    const deleteRule = async (ruleId) => {
      const result = await deleteAssignmentRule(ruleId)
      if (result.success) {
        showNotification(t('admin.assignmentRuleDeletedSuccessfully'), 'success')
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
          url: `${API_BASE_URL}/domains/${props.domain}/export-config`,
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

        showNotification(t('admin.configurationExportedSuccessfully'), 'success')
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

        const result = await post(`/domains/${props.domain}/import-config`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (result.success) {
          showNotification(t('admin.configurationImportedSuccessfully'), 'success')
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
      const message = t('admin.confirmResetConfiguration')
      showConfirmDialog(message, resetConfiguration)
    }

    const resetConfiguration = async () => {
      try {
        const result = await post(`/domains/${props.domain}/reset-config`)

        if (result.success) {
          showNotification(t('admin.configurationResetSuccessfully'), 'success')
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
        result.success ? t('admin.groupDeletedSuccessfully') : t('admin.failedToDeleteGroup', { error: result.error }),
        result.success ? 'success' : 'error'
      )
    }

    const handleRemoveFromGroup = async (groupId, eventTitles) => {
      const result = await removeEventsFromGroup(groupId, eventTitles)
      if (result.success) {
        const groupName = groups.value.find(g => g.id === parseInt(groupId))?.name || t('admin.unknownGroup')
        showNotification(`Successfully removed ${eventTitles.length} event${eventTitles.length > 1 ? 's' : ''} from ${groupName}!`, 'success')
      } else {
        showNotification(`Failed to remove events from group: ${result.error}`, 'error')
      }
    }

    // Load data on mount
    let hasInitiallyLoaded = false
    onMounted(async () => {
      if (!hasInitiallyLoaded) {
        hasInitiallyLoaded = true
        loadAllAdminData()
      }
    })

    return {
      // Mobile detection
      isMobile,
      
      // UI State
      expandedCards,
      loading,
      error,
      applyLoading,

      // Notification States
      notification,
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
      
      // Group management
      handleDeleteGroup,
      handleRemoveFromGroup
    }
  }
}
</script>