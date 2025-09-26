<template>
  <AdminCardWrapper
    :title="$t('admin.autoRules')"
    :subtitle="`${assignmentRules.length} rules • Automatic event assignment rules`"
    icon="⚙️"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Create New Rule -->
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg space-y-3">
      <h3 class="font-medium text-gray-900 dark:text-white">Create New Rule</h3>
      <div class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <select 
            v-model="newRule.rule_type"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select rule type...</option>
            <option value="title_contains">Title Contains</option>
            <option value="description_contains">Description Contains</option>
            <option value="category_contains">Category Contains</option>
          </select>
          <input
            v-model="newRule.rule_value"
            type="text"
            placeholder="Value to match..."
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          />
          <select 
            v-model="newRule.target_group_id"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select target group...</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">{{ group.name }}</option>
          </select>
        </div>
        <div class="flex gap-2 justify-end">
          <button
            @click="createRule"
            :disabled="!newRule.rule_type || !newRule.rule_value.trim() || !newRule.target_group_id"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
          >
            Create Rule
          </button>
        </div>
        
        <!-- Live Matching Events Display -->
        <div v-if="newRule.rule_type && newRule.rule_value.trim() && newRule.target_group_id" class="mt-4">
          <h4 class="font-medium text-gray-900 dark:text-white mb-2">
            📋 Events that will match this rule:
          </h4>
          <div class="max-h-48 overflow-y-auto space-y-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg p-3">
            <div 
              v-for="event in getLiveMatchingEvents(newRule)"
              :key="event.title"
              :class="[
                'flex items-center justify-between p-2 rounded-lg border text-sm',
                event.willChange 
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700'
                  : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
              ]"
            >
              <div class="flex-1">
                <div class="font-medium text-gray-900 dark:text-white">{{ event.title }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ event.event_count }} occurrences • 
                  <span v-if="event.willChange">
                    {{ event.currentGroupName }} → {{ getGroupName(newRule.target_group_id) }}
                  </span>
                  <span v-else>
                    Already in {{ getGroupName(newRule.target_group_id) }}
                  </span>
                </div>
              </div>
              <div class="text-lg">
                <span v-if="event.willChange" class="text-green-600 dark:text-green-400" title="Will change">🔄</span>
                <span v-else class="text-gray-400" title="Already assigned">✓</span>
              </div>
            </div>
            <div v-if="getLiveMatchingEvents(newRule).length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
              <div class="text-2xl mb-1">📭</div>
              <p class="text-sm">No events match this rule</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Rules List -->
    <div class="space-y-3">
      <div 
        v-for="rule in assignmentRules" 
        :key="rule.id"
        class="bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
      >
        <!-- Rule Header -->
        <div class="flex items-center justify-between p-4">
          <div class="flex items-center gap-3 flex-1">
            <!-- Dropdown Arrow -->
            <button
              @click="toggleRuleDropdown(rule.id)"
              class="flex-shrink-0"
            >
              <svg 
                class="w-4 h-4 text-gray-400 transition-transform duration-200"
                :class="{ 'rotate-90': expandedRules[rule.id] }"
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </button>
            
            <!-- Rule Info -->
            <div class="flex-1">
              <h3 class="font-medium text-gray-900 dark:text-white">
                {{ getRuleTypeLabel(rule.rule_type) }}: "{{ rule.rule_value }}"
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                → Assigns to {{ getGroupName(rule.target_group_id) }} • {{ getLiveMatchingEvents(rule).length }} events match
              </p>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex items-center gap-2">
            <button
              @click="applyRule(rule)"
              :disabled="applyLoading"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-sm font-medium transition-colors duration-200 flex items-center gap-1"
            >
              <span v-if="applyLoading">⏳</span>
              <span v-else>▶️</span>
              Apply
            </button>
            <button
              @click="deleteRuleConfirm(rule)"
              class="text-red-600 hover:text-red-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
            >
              🗑️ Delete
            </button>
          </div>
        </div>
        
        <!-- Matching Events Dropdown -->
        <div v-if="expandedRules[rule.id]" class="px-4 pb-4">
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg p-3">
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">
              📋 Events matching this rule ({{ getLiveMatchingEvents(rule).length }}):
            </h4>
            <div class="max-h-48 overflow-y-auto space-y-2">
              <div 
                v-for="event in getLiveMatchingEvents(rule)"
                :key="event.title"
                :class="[
                  'flex items-center justify-between p-2 rounded-lg border text-sm',
                  event.willChange 
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700'
                    : 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                ]"
              >
                <div class="flex-1">
                  <div class="font-medium text-gray-900 dark:text-white">{{ event.title }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {{ event.event_count }} occurrences • 
                    <span v-if="event.willChange">
                      {{ event.currentGroupName }} → {{ getGroupName(rule.target_group_id) }}
                    </span>
                    <span v-else>
                      Already in {{ getGroupName(rule.target_group_id) }}
                    </span>
                  </div>
                </div>
                <div class="text-lg">
                  <span v-if="event.willChange" class="text-green-600 dark:text-green-400" title="Will change">🔄</span>
                  <span v-else class="text-gray-400" title="Already assigned">✓</span>
                </div>
              </div>
              <div v-if="getLiveMatchingEvents(rule).length === 0" class="text-center py-4 text-gray-500 dark:text-gray-400">
                <div class="text-2xl mb-1">📭</div>
                <p class="text-sm">No events match this rule</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="assignmentRules.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
      <div class="text-4xl mb-2">⚙️</div>
      <p>No assignment rules created yet. Create your first rule above!</p>
    </div>
  </AdminCardWrapper>
</template>

<script>
import { ref } from 'vue'
import AdminCardWrapper from './AdminCardWrapper.vue'

export default {
  name: 'AutoRulesCard',
  components: {
    AdminCardWrapper
  },
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    assignmentRules: {
      type: Array,
      default: () => []
    },
    groups: {
      type: Array,
      default: () => []
    },
    recurringEvents: {
      type: Array,
      default: () => []
    },
    applyLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle', 'create-rule', 'apply-rule', 'delete-rule-confirm'],
  setup(props, { emit }) {
    // Local state
    const newRule = ref({
      rule_type: '',
      rule_value: '',
      target_group_id: ''
    })
    
    const expandedRules = ref({})
    
    // Methods
    const toggleRuleDropdown = (ruleId) => {
      expandedRules.value = {
        ...expandedRules.value,
        [ruleId]: !expandedRules.value[ruleId]
      }
    }
    
    const createRule = () => {
      emit('create-rule', { ...newRule.value })
      // Reset form after creation
      newRule.value = {
        rule_type: '',
        rule_value: '',
        target_group_id: ''
      }
    }
    
    const applyRule = (rule) => {
      emit('apply-rule', rule)
    }
    
    const deleteRuleConfirm = (rule) => {
      emit('delete-rule-confirm', rule)
    }
    
    const getRuleTypeLabel = (ruleType) => {
      const labels = {
        title_contains: 'Title Contains',
        description_contains: 'Description Contains', 
        category_contains: 'Category Contains'
      }
      return labels[ruleType] || ruleType
    }
    
    const getGroupName = (groupId) => {
      const group = props.groups.find(g => g.id === groupId)
      return group ? group.name : 'Unknown Group'
    }
    
    const getLiveMatchingEvents = (rule) => {
      if (!rule || !rule.rule_type || !rule.rule_value || !Array.isArray(props.recurringEvents)) {
        return []
      }
      
      const matchingEvents = []
      
      // Group events by title to get unique events with occurrence counts
      const eventsByTitle = {}
      
      props.recurringEvents.forEach(event => {
        if (!eventsByTitle[event.title]) {
          eventsByTitle[event.title] = {
            title: event.title,
            event_count: 0,
            currentGroupId: event.group_id,
            currentGroupName: getGroupName(event.group_id) || 'Unassigned'
          }
        }
        eventsByTitle[event.title].event_count++
      })
      
      // Check each unique event against the rule
      Object.values(eventsByTitle).forEach(eventSummary => {
        let matches = false
        const searchValue = rule.rule_value.toLowerCase()
        
        // Find a representative event to check fields
        const sampleEvent = props.recurringEvents.find(e => e.title === eventSummary.title)
        if (!sampleEvent) return
        
        switch (rule.rule_type) {
          case 'title_contains':
            matches = eventSummary.title.toLowerCase().includes(searchValue)
            break
          case 'description_contains':
            matches = (sampleEvent.description || '').toLowerCase().includes(searchValue)
            break  
          case 'category_contains':
            matches = (sampleEvent.category || '').toLowerCase().includes(searchValue)
            break
        }
        
        if (matches) {
          const willChange = eventSummary.currentGroupId !== rule.target_group_id
          matchingEvents.push({
            ...eventSummary,
            willChange
          })
        }
      })
      
      return matchingEvents
    }
    
    return {
      newRule,
      expandedRules,
      toggleRuleDropdown,
      createRule,
      applyRule,
      deleteRuleConfirm,
      getRuleTypeLabel,
      getGroupName,
      getLiveMatchingEvents
    }
  }
}
</script>