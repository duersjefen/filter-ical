<template>
  <!-- Loading State -->
  <div v-if="loading" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
      <div class="text-blue-800 dark:text-blue-200 font-semibold text-lg">Loading Admin Panel...</div>
      <div class="text-blue-600 dark:text-blue-300 text-sm mt-2">Please wait</div>
    </div>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="bg-gradient-to-r from-red-100 to-red-50 dark:from-red-900/30 dark:to-red-800/30 text-red-800 dark:text-red-200 px-6 py-4 rounded-xl border-2 border-red-300 dark:border-red-700 relative shadow-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="text-2xl">⚠️</div>
          <span class="font-semibold">{{ error }}</span>
        </div>
      </div>
    </div>
    
    <!-- Back to Domain Link on Error -->
    <div class="mt-6 text-center">
      <router-link 
        :to="`/${domain}`" 
        class="inline-flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors duration-200"
      >
        ← Back to {{ domain }} Calendar
      </router-link>
    </div>
  </div>

  <!-- Main Admin Interface -->
  <div v-else class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 space-y-8">
    
    <!-- Admin Header -->
    <div class="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-xl shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold mb-2">🔧 Admin Panel</h1>
          <p class="text-purple-100">Manage {{ domain }} events and groups</p>
        </div>
        <div class="flex gap-3">
          <router-link 
            :to="`/${domain}`" 
            class="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
          >
            ← Back to Calendar
          </router-link>
        </div>
      </div>
    </div>

    <!-- Admin Sections Navigation -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="flex">
          <button
            v-for="section in sections"
            :key="section.id"
            @click="activeSection = section.id"
            :class="[
              'flex-1 px-6 py-4 font-medium transition-colors duration-200',
              activeSection === section.id
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-b-2 border-blue-600'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            <span class="mr-2">{{ section.icon }}</span>
            {{ section.name }}
          </button>
        </nav>
      </div>

      <!-- Section Content -->
      <div class="p-6">
        
        <!-- Groups Management Section -->
        <div v-if="activeSection === 'groups'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Manage Groups</h2>
            <button
              @click="showCreateGroupModal = true"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
            >
              + Create Group
            </button>
          </div>

          <!-- Groups List -->
          <div class="space-y-3">
            <div 
              v-for="group in groups" 
              :key="group.id"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">{{ group.name }}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">ID: {{ group.id }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="editGroup(group)"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors duration-200"
                >
                  Edit
                </button>
                <button
                  @click="deleteGroupConfirm(group)"
                  class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors duration-200"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Event Assignment Section -->
        <div v-if="activeSection === 'events'" class="space-y-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Assign Events to Groups</h2>
          
          <!-- Group Selection -->
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Group for Assignment
            </label>
            <select 
              v-model="selectedGroupId" 
              class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              <option value="">Choose a group...</option>
              <option v-for="group in groups" :key="group.id" :value="group.id">
                {{ group.name }}
              </option>
            </select>
          </div>

          <!-- Available Events -->
          <div v-if="selectedGroupId">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Available Recurring Events</h3>
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div 
                v-for="event in recurringEvents" 
                :key="event.title"
                class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900 dark:text-white">{{ event.title }}</h4>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ event.event_count }} occurrences
                    <span v-if="event.sample_location"> • {{ event.sample_location }}</span>
                  </p>
                </div>
                <button
                  @click="assignEventToGroup(event.title)"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
                >
                  Assign to Group
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Assignment Rules Section -->
        <div v-if="activeSection === 'rules'" class="space-y-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Assignment Rules</h2>
            <button
              @click="showCreateRuleModal = true"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
            >
              + Create Rule
            </button>
          </div>

          <!-- Rules List -->
          <div class="space-y-3">
            <div 
              v-for="rule in assignmentRules" 
              :key="rule.id"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
            >
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">
                  {{ getRuleTypeLabel(rule.rule_type) }}: "{{ rule.rule_value }}"
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Assigns to: {{ getGroupName(rule.target_group_id) }}
                </p>
              </div>
              <button
                @click="deleteRuleConfirm(rule)"
                class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm font-medium transition-colors duration-200"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>

  <!-- Create Group Modal -->
  <div v-if="showCreateGroupModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create New Group</h3>
      <input 
        v-model="newGroupName"
        type="text" 
        placeholder="Enter group name"
        class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
        @keyup.enter="createGroup"
      >
      <div class="flex gap-3 justify-end">
        <button
          @click="showCreateGroupModal = false"
          class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
        >
          Cancel
        </button>
        <button
          @click="createGroup"
          :disabled="!newGroupName.trim()"
          class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          Create
        </button>
      </div>
    </div>
  </div>

  <!-- Create Rule Modal -->
  <div v-if="showCreateRuleModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create Assignment Rule</h3>
      
      <!-- Rule Type Selection -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Rule Type</label>
        <select 
          v-model="newRule.rule_type"
          class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">Select rule type...</option>
          <option value="title_contains">Title contains</option>
          <option value="description_contains">Description contains</option>
          <option value="category_contains">Category contains</option>
        </select>
      </div>

      <!-- Rule Value -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Rule Value</label>
        <input 
          v-model="newRule.rule_value"
          type="text" 
          placeholder="e.g., 'Event' or 'Meeting'"
          class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
      </div>

      <!-- Target Group -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Target Group</label>
        <select 
          v-model="newRule.target_group_id"
          class="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">Select target group...</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }}
          </option>
        </select>
      </div>

      <div class="flex gap-3 justify-end">
        <button
          @click="showCreateRuleModal = false"
          class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
        >
          Cancel
        </button>
        <button
          @click="createRule"
          :disabled="!newRule.rule_type || !newRule.rule_value.trim() || !newRule.target_group_id"
          class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          Create Rule
        </button>
      </div>
    </div>
  </div>

</template>

<script>
import { ref, onMounted } from 'vue'
import { useAdmin } from '../composables/useAdmin'

export default {
  name: 'AdminView',
  props: {
    domain: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const {
      // State
      groups,
      recurringEvents,
      assignmentRules,
      loading,
      error,
      
      // API Functions
      loadGroups,
      createGroup: createGroupAPI,
      updateGroup: updateGroupAPI,
      deleteGroup: deleteGroupAPI,
      loadRecurringEvents,
      assignEventsToGroup,
      loadAssignmentRules,
      createAssignmentRule: createAssignmentRuleAPI,
      deleteAssignmentRule: deleteAssignmentRuleAPI,
      
      // Utilities
      getGroupName,
      getRuleTypeLabel,
      loadAllAdminData,
      validateGroupName,
      validateAssignmentRule
    } = useAdmin(props.domain)

    // UI State
    const activeSection = ref('groups')
    const sections = ref([
      { id: 'groups', name: 'Groups', icon: '📁' },
      { id: 'events', name: 'Event Assignment', icon: '📅' },
      { id: 'rules', name: 'Auto Rules', icon: '⚙️' }
    ])

    // Form States
    const showCreateGroupModal = ref(false)
    const showCreateRuleModal = ref(false)
    const newGroupName = ref('')
    const selectedGroupId = ref('')
    const newRule = ref({
      rule_type: '',
      rule_value: '',
      target_group_id: ''
    })

    // Group Management
    const createGroup = async () => {
      const validation = validateGroupName(newGroupName.value)
      if (!validation.valid) {
        alert(validation.error)
        return
      }

      const result = await createGroupAPI(newGroupName.value)
      if (result.success) {
        newGroupName.value = ''
        showCreateGroupModal.value = false
      } else {
        alert(`Failed to create group: ${result.error}`)
      }
    }

    const editGroup = (group) => {
      const newName = prompt('Enter new group name:', group.name)
      if (newName && newName.trim() && newName.trim() !== group.name) {
        updateGroup(group.id, newName.trim())
      }
    }

    const updateGroup = async (groupId, name) => {
      const validation = validateGroupName(name)
      if (!validation.valid) {
        alert(validation.error)
        return
      }

      const result = await updateGroupAPI(groupId, name)
      if (!result.success) {
        alert(`Failed to update group: ${result.error}`)
      }
    }

    const deleteGroupConfirm = (group) => {
      if (confirm(`Are you sure you want to delete "${group.name}"? This will also delete all assignments and rules for this group.`)) {
        deleteGroup(group.id)
      }
    }

    const deleteGroup = async (groupId) => {
      const result = await deleteGroupAPI(groupId)
      if (!result.success) {
        alert(`Failed to delete group: ${result.error}`)
      }
    }

    // Event Assignment
    const assignEventToGroup = async (eventTitle) => {
      if (!selectedGroupId.value) return

      const result = await assignEventsToGroup(selectedGroupId.value, eventTitle)
      if (!result.success) {
        alert(`Failed to assign event to group: ${result.error}`)
      }
    }

    // Assignment Rules
    const createRule = async () => {
      const validation = validateAssignmentRule(
        newRule.value.rule_type,
        newRule.value.rule_value,
        newRule.value.target_group_id
      )
      
      if (!validation.valid) {
        alert(validation.error)
        return
      }

      const result = await createAssignmentRuleAPI(
        newRule.value.rule_type,
        newRule.value.rule_value,
        newRule.value.target_group_id
      )
      
      if (result.success) {
        newRule.value = { rule_type: '', rule_value: '', target_group_id: '' }
        showCreateRuleModal.value = false
      } else {
        alert(`Failed to create assignment rule: ${result.error}`)
      }
    }

    const deleteRuleConfirm = (rule) => {
      if (confirm(`Are you sure you want to delete this rule?`)) {
        deleteRule(rule.id)
      }
    }

    const deleteRule = async (ruleId) => {
      const result = await deleteAssignmentRuleAPI(ruleId)
      if (!result.success) {
        alert(`Failed to delete assignment rule: ${result.error}`)
      }
    }

    // Load data on mount
    onMounted(() => {
      loadAllAdminData()
    })

    return {
      // UI State
      activeSection,
      sections,
      loading,
      error,

      // Data
      groups,
      recurringEvents,
      assignmentRules,

      // Form States
      showCreateGroupModal,
      showCreateRuleModal,
      newGroupName,
      selectedGroupId,
      newRule,

      // Methods
      createGroup,
      editGroup,
      deleteGroupConfirm,
      assignEventToGroup,
      createRule,
      deleteRuleConfirm,
      getRuleTypeLabel,
      getGroupName
    }
  }
}
</script>