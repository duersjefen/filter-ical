<template>
  <AdminCardWrapper
    :title="$t('domainAdmin.autoRules')"
    :subtitle="`${assignmentRules.length} rules • ${$t('domainAdmin.automaticEventAssignmentRules')}`"
    icon="⚙️"
    :expanded="expanded"
    @toggle="$emit('toggle')"
    class="auto-rules-card"
  >
    <!-- Create New Rule -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 space-y-6 shadow-sm hover:shadow-md transition-all duration-200">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
          <span class="text-blue-600 dark:text-blue-400 text-xl">⚡</span>
        </div>
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-1">{{ $t('domainAdmin.createNewAutoRule') }}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ $t('domainAdmin.autoRuleDescription') }}</p>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Rule Type -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('domainAdmin.ruleType') }}</label>
          <div class="flex gap-2">
            <button
              v-for="type in ruleTypes"
              :key="type.value"
              @click="newRule.rule_type = type.value"
              :class="[
                'flex-1 flex items-center gap-2 px-4 py-3 rounded-lg border text-sm font-medium transition-all duration-200',
                newRule.rule_type === type.value
                  ? 'bg-blue-100 border-blue-300 text-blue-800 dark:bg-blue-900/30 dark:border-blue-600 dark:text-blue-200'
                  : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700'
              ]"
            >
              <span>{{ type.icon }}</span>
              <span>{{ type.label }}</span>
            </button>
          </div>
        </div>
        
        <!-- Rule Value -->
        <div class="space-y-3">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            <span class="flex items-center gap-2">
              <span class="text-green-600 dark:text-green-400">🔍</span>
              {{ $t('domainAdmin.searchValue') }}
            </span>
          </label>
          <div class="relative">
            <input
              v-model="newRule.rule_value"
              type="text"
              :placeholder="getRulePlaceholder(newRule.rule_type)"
              class="w-full px-4 py-3.5 border-2 border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200 shadow-sm hover:shadow-md"
              @keyup.enter="createRule"
              @input="debouncedUpdatePreview"
            />
            <div v-if="newRule.rule_value.trim()" class="absolute right-3 top-1/2 transform -translate-y-1/2">
              <span class="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full">
                {{ newRule.rule_value.length }} chars
              </span>
            </div>
          </div>
        </div>
        
        <!-- Target Group -->
        <div class="space-y-3">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            <span class="flex items-center gap-2">
              <span class="text-purple-600 dark:text-purple-400">📁</span>
              {{ $t('domainAdmin.targetGroup') }}
            </span>
          </label>
          <select 
            v-model="newRule.target_group_id"
            class="w-full px-4 py-3.5 border-2 border-gray-200 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-200 shadow-sm hover:shadow-md cursor-pointer"
          >
            <option value="" disabled>{{ $t('messages.selectTargetGroup') }}</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }} ({{ getGroupEventCount(group.id) }} events)
            </option>
          </select>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-2">
        <div class="flex items-center gap-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            <span v-if="newRule.rule_type && newRule.rule_value.trim()" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse-green"></span>
              <span class="font-medium text-green-700 dark:text-green-300">{{ getLiveMatchingEvents(newRule).length }} events match</span>
              <span v-if="getLiveMatchingEvents(newRule).filter(e => e.willChange).length > 0" class="text-blue-600 dark:text-blue-400">
                ({{ getLiveMatchingEvents(newRule).filter(e => e.willChange).length }} {{ $t('messages.willBeAssigned') }})
              </span>
            </span>
            <span v-else class="flex items-center gap-2">
              <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
              {{ $t('domainAdmin.fillAllFieldsForPreview') }}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="newRule.rule_type || newRule.rule_value || newRule.target_group_id"
            @click="resetForm"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-xl font-medium transition-all duration-200 text-sm"
          >
            <span>🔄</span>
            Reset
          </button>
          <button
            @click="createRule"
            :disabled="!isFormValid"
            class="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-semibold text-sm shadow-sm hover:shadow-md disabled:cursor-not-allowed transition-all duration-200"
            :class="{ 'animate-bounce-subtle': isFormValid }"
          >
            <span class="text-lg">⚡</span>
            <span>{{ $t('controls.createRule') }}</span>
            <span v-if="isFormValid" class="text-xs opacity-75">({{ $t('controls.enterKey') }})</span>
          </button>
        </div>
      </div>
      
      <!-- Live Preview (Enhanced Design) -->
      <div v-if="newRule.rule_type && newRule.rule_value.trim()" class="border-t border-gray-200 dark:border-gray-600 pt-4">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-medium text-gray-900 dark:text-white flex items-center gap-2">
            <span class="text-lg">🔍</span>
            Live Preview
          </h4>
          <span class="text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
            {{ getLiveMatchingEvents(newRule).length }} matches
          </span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <!-- Event Cards (matching EventManagementCard style) -->
          <div 
            v-for="event in getLiveMatchingEvents(newRule)"
            :key="event.title"
            :class="[
              'relative border rounded-lg px-3 py-2 transition-all duration-200',
              event.willChange 
                ? 'border-green-300 bg-green-50 dark:border-green-600 dark:bg-green-900/20' 
                : 'border-gray-300 dark:border-gray-600'
            ]"
          >
            <!-- Status Icon -->
            <div class="absolute top-3 right-3">
              <div :class="[
                'w-6 h-6 rounded-full flex items-center justify-center text-xs',
                event.willChange 
                  ? 'bg-green-200 dark:bg-green-700 text-green-800 dark:text-green-200'
                  : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
              ]">
                <span v-if="event.willChange">🔄</span>
                <span v-else>✓</span>
              </div>
            </div>
            
            <!-- Event Title with Count -->
            <div class="pr-8 mb-2">
              <div class="flex items-start gap-2">
                <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300 flex-shrink-0">
                  {{ event.event_count }}
                </span>
                <div class="flex-1">
                  <h5 
                    class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-5 cursor-help" 
                    :title="event.title"
                  >
                    {{ event.title }}
                  </h5>
                  <!-- Show description for description rules -->
                  <div 
                    v-if="newRule.rule_type === 'description_contains' && event.description" 
                    class="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2 cursor-help" 
                    :title="event.description"
                  >
                    <span class="font-medium">{{ t('domainAdmin.description') }}:</span> {{ event.description }}
                  </div>
                  <!-- Show categories for category rules -->
                  <div 
                    v-if="newRule.rule_type === 'category_contains' && event.categories && event.categories.length > 0" 
                    class="text-xs text-gray-600 dark:text-gray-400 mt-1 cursor-help" 
                    :title="event.categories.join(', ')"
                  >
                    <span class="font-medium">{{ t('domainAdmin.categories') }}:</span> {{ event.categories.join(', ') }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Assignment Status -->
            <div class="text-xs text-gray-500 dark:text-gray-400">
              <span v-if="event.willChange" class="text-green-700 dark:text-green-300">
                <strong>{{ $t('messages.willAddTo') }}</strong> {{ getGroupName(newRule.target_group_id) }}
                <span v-if="event.currentGroupName && event.currentGroupName !== t('domainAdmin.unassigned')" class="text-gray-500 dark:text-gray-400 ml-1">
                  (currently: {{ event.currentGroupName }}{{ event.allGroupIds?.length > 1 ? ` +${event.allGroupIds.length - 1} more` : '' }})
                </span>
              </span>
              <span v-else class="text-gray-600 dark:text-gray-400">
                <strong>{{ $t('messages.alreadyIn') }}</strong> {{ getGroupName(newRule.target_group_id) }}
              </span>
            </div>
          </div>
          
          
          <!-- No Matches State -->
          <div v-if="getLiveMatchingEvents(newRule).length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">🔍</div>
            <p class="text-sm font-medium">{{ $t('messages.noEventsMatch') }}</p>
            <p class="text-xs mt-1">{{ $t('messages.tryAdjustingCriteria') }}</p>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- Rules List -->
    <div class="space-y-6">
      <div v-if="assignmentRules.length > 0" class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <span class="text-2xl">🎯</span>
          {{ $t('domainAdmin.activeRules') }} ({{ assignmentRules.length }})
        </h3>
      </div>
      
      <div 
        v-for="(rule, index) in assignmentRules" 
        :key="rule.id"
        class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-200"
        :class="{ 'ring-2 ring-blue-500 dark:ring-blue-400': expandedRules[rule.id] }"
      >
        <!-- Rule Header (Clickable) -->
        <div 
          class="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-all duration-200"
          @click="toggleRuleDropdown(rule.id)"
        >
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-4 flex-1">
              
              <!-- Rule Type Icon -->
              <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm" :class="getRuleTypeIconClass(rule.rule_type)">
                <span class="text-xl">{{ getRuleTypeIcon(rule.rule_type) }}</span>
              </div>
              
              <!-- Rule Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <h3 class="text-lg font-bold text-gray-900 dark:text-white">
                    {{ getRuleTypeLabel(rule.rule_type) }}
                  </h3>
                  <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold badge-bounce" :class="getMatchCountBadgeClass(rule)">
                    {{ getLiveMatchingEvents(rule).length }} matches
                  </span>
                </div>
                <p class="text-sm text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
                  {{ $t('domainAdmin.when') }} <span class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded font-medium">{{ getRuleTypeDescription(rule.rule_type) }}</span> <span class="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded font-medium">"{{ rule.rule_value }}"</span> 
                  → {{ $t('domainAdmin.assignTo') }} <span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded font-medium">{{ getGroupName(rule.target_group_id) }}</span>
                </p>
                <div v-if="getRuleStatus(rule) !== t('domainAdmin.complete')" class="flex items-center gap-6 text-xs">
                  <div class="flex items-center gap-2">
                    <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span class="text-green-700 dark:text-green-300 font-medium">{{ getLiveMatchingEvents(rule).filter(e => e.willChange).length }} {{ $t('messages.willBeAssigned') }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <div class="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <span class="text-gray-600 dark:text-gray-400">{{ getLiveMatchingEvents(rule).filter(e => !e.willChange).length }} {{ $t('messages.alreadyAssigned') }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex items-center gap-3 flex-shrink-0">
              <!-- Rule Status -->
              <div class="text-right">
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ $t('messages.ruleStatus') }}</div>
                <div :class="getRuleStatusClass(rule)" class="text-xs font-semibold px-2 py-1 rounded-full">
                  {{ getRuleStatus(rule) }}
                </div>
              </div>
              
              <!-- Expand/Collapse Indicator -->
              <div class="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 dark:text-gray-500 group-hover:bg-white group-hover:shadow-sm dark:group-hover:bg-gray-700 transition-all duration-200">
                <svg 
                  class="w-5 h-5 transition-transform duration-300"
                  :class="{ 'rotate-180': expandedRules[rule.id] }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              
              <!-- Action Buttons -->
              <div class="flex items-center gap-2">
                <button
                  @click.stop="applyRule(rule)"
                  :disabled="applyLoading || getLiveMatchingEvents(rule).filter(e => e.willChange).length === 0"
                  class="inline-flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg text-sm font-semibold shadow-sm hover:shadow-md disabled:cursor-not-allowed transition-all duration-200"
                  :class="{ 'animate-gradient': applyLoading, 'shadow-lift': !applyLoading }"
                  :title="getLiveMatchingEvents(rule).filter(e => e.willChange).length === 0 ? 'No events need to be assigned' : 'Apply this rule to matching events'"
                >
                  <span v-if="applyLoading" class="text-base">⏳</span>
                  <span v-else class="text-base">⚡</span>
                  <span>{{ t('domainAdmin.apply') }}</span>
                </button>
                <button
                  @click.stop="deleteRuleConfirm(rule)"
                  class="w-10 h-10 rounded-xl flex items-center justify-center text-red-600 hover:text-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200 shadow-sm hover:shadow-md"
                  title="Delete this rule"
                >
                  <span class="text-base">🗑️</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Matching Events Dropdown -->
        <div v-if="expandedRules[rule.id]" class="border-t border-gray-200 dark:border-gray-600 p-6 bg-gray-50 dark:bg-gray-800">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <span class="text-2xl">🎯</span>
              Matching Events
            </h4>
            <div class="flex items-center gap-4 text-sm">
              <span class="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 font-semibold">
                {{ getLiveMatchingEvents(rule).length }} total matches
              </span>
              <span v-if="getLiveMatchingEvents(rule).filter(e => e.willChange).length > 0" class="inline-flex items-center px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 font-semibold">
                {{ getLiveMatchingEvents(rule).filter(e => e.willChange).length }} {{ $t('messages.willBeAssigned') }}
              </span>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <!-- Event Cards (same style as live preview) -->
            <div 
              v-for="event in getLiveMatchingEvents(rule)"
              :key="event.title"
              :class="[
                'relative border rounded-lg px-3 py-2 transition-all duration-200',
                event.willChange 
                  ? 'border-green-300 bg-green-50 dark:border-green-600 dark:bg-green-900/20' 
                  : 'border-gray-300 dark:border-gray-600'
              ]"
            >
              <!-- Status Icon -->
              <div class="absolute top-3 right-3">
                <div :class="[
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs',
                  event.willChange 
                    ? 'bg-green-200 dark:bg-green-700 text-green-800 dark:text-green-200'
                    : 'bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300'
                ]">
                  <span v-if="event.willChange">🔄</span>
                  <span v-else>✓</span>
                </div>
              </div>
              
              <!-- Event Title with Count -->
              <div class="pr-8 mb-2">
                <div class="flex items-start gap-2">
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-600 dark:text-gray-300 flex-shrink-0">
                    {{ event.event_count }}
                  </span>
                  <div class="flex-1">
                    <h5 
                      class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-5 cursor-help" 
                      :title="event.title"
                    >
                      {{ event.title }}
                    </h5>
                    <!-- Show description for description rules -->
                    <div 
                      v-if="rule.rule_type === 'description_contains' && event.description" 
                      class="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2 cursor-help" 
                      :title="event.description"
                    >
                      <span class="font-medium">{{ t('domainAdmin.description') }}:</span> {{ event.description }}
                    </div>
                    <!-- Show categories for category rules -->
                    <div 
                      v-if="rule.rule_type === 'category_contains' && event.categories && event.categories.length > 0" 
                      class="text-xs text-gray-600 dark:text-gray-400 mt-1 cursor-help" 
                      :title="event.categories.join(', ')"
                    >
                      <span class="font-medium">{{ t('domainAdmin.categories') }}:</span> {{ event.categories.join(', ') }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Assignment Status -->
              <div class="text-xs text-gray-500 dark:text-gray-400">
                <span v-if="event.willChange" class="text-green-700 dark:text-green-300">
                  <strong>{{ $t('messages.willAddTo') }}</strong> {{ getGroupName(rule.target_group_id) }}
                  <span v-if="event.currentGroupName && event.currentGroupName !== t('domainAdmin.unassigned')" class="text-gray-500 dark:text-gray-400 ml-1">
                    (currently: {{ event.currentGroupName }}{{ event.allGroupIds?.length > 1 ? ` +${event.allGroupIds.length - 1} more` : '' }})
                  </span>
                </span>
                <span v-else class="text-gray-600 dark:text-gray-400">
                  <strong>{{ $t('messages.alreadyIn') }}</strong> {{ getGroupName(rule.target_group_id) }}
                </span>
              </div>
            </div>
            
            <!-- No Matches State -->
            <div v-if="getLiveMatchingEvents(rule).length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
              <div class="text-4xl mb-2">🔍</div>
              <p class="text-sm font-medium">No events match this rule</p>
              <p class="text-xs mt-1">{{ $t('messages.ruleMightNeedUpdate') }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Enhanced Empty State -->
    <div v-if="assignmentRules.length === 0" class="text-center py-12 px-6">
      <div class="max-w-md mx-auto">
        <div class="w-24 h-24 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
          <span class="text-4xl">⚙️</span>
        </div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3">{{ $t('messages.noAutoRulesYet') }}</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
          Auto rules help you automatically organize events into groups based on their content. 
          Start by creating your first rule above using the form.
        </p>
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div class="flex items-start gap-3 text-sm text-blue-800 dark:text-blue-200">
            <span class="text-lg flex-shrink-0">💡</span>
            <div class="text-left">
              <p class="font-semibold mb-1">{{ t('domainAdmin.proTips') }}</p>
              <ul class="space-y-1 text-xs">
                <li>• {{ t('domainAdmin.useMeetingInTitleRules') }}</li>
                <li>• {{ t('domainAdmin.descriptionRulesForProjects') }}</li>
                <li>• {{ t('domainAdmin.categoryRulesForOrganization') }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminCardWrapper>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
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
    // Translation
    const { t } = useI18n()
    
    // Local state
    const newRule = ref({
      rule_type: 'title_contains', // Default to title
      rule_value: '',
      target_group_id: ''
    })
    
    const expandedRules = ref({})
    
    // Rule types for easy selection
    const ruleTypes = computed(() => [
      {
        value: 'title_contains',
        label: t('domainAdmin.title'),
        icon: '📄'
      },
      {
        value: 'description_contains',
        label: t('domainAdmin.description'),
        icon: '📝'
      },
      {
        value: 'category_contains',
        label: t('domainAdmin.category'),
        icon: '🏷️'
      }
    ])
    
    
    // Computed properties
    const isFormValid = computed(() => {
      return newRule.value.rule_type && 
             newRule.value.rule_value.trim() && 
             newRule.value.target_group_id
    })
    
    // Debounced preview update (simple implementation)
    let previewTimeout = null
    
    // Keyboard shortcuts
    const handleKeyboardShortcuts = (event) => {
      // Handle keyboard shortcuts when component is active
      if (event.target.closest('.auto-rules-card') && props.expanded) {
        switch (event.key) {
          case 'Escape':
            if (newRule.value.rule_type || newRule.value.rule_value || newRule.value.target_group_id) {
              resetForm()
              event.preventDefault()
            }
            break
          case 'Enter':
            if (event.ctrlKey || event.metaKey) {
              if (isFormValid.value) {
                createRule()
                event.preventDefault()
              }
            }
            break
        }
      }
    }
    
    // Setup keyboard event listeners
    onMounted(() => {
      document.addEventListener('keydown', handleKeyboardShortcuts)
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeyboardShortcuts)
      if (previewTimeout) {
        clearTimeout(previewTimeout)
      }
    })
    
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
        rule_type: 'title_contains',
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
    
    
    const resetForm = () => {
      newRule.value = {
        rule_type: 'title_contains',
        rule_value: '',
        target_group_id: ''
      }
    }
    
    const updateRuleTypePreview = () => {
      // Trigger preview update when rule type changes
      // Implementation could be enhanced with specific logic per type
    }
    
    const debouncedUpdatePreview = () => {
      clearTimeout(previewTimeout)
      previewTimeout = setTimeout(() => {
        // Force reactivity update for live preview
        // This helps with performance on rapid typing
      }, 300)
    }
    
    const getGroupEventCount = (groupId) => {
      if (!Array.isArray(props.recurringEvents)) return 0
      return props.recurringEvents.filter(event => 
        event.assigned_group_ids && event.assigned_group_ids.includes(parseInt(groupId))
      ).length
    }
    
    
    const getMatchCountBadgeClass = (rule) => {
      const matchCount = getLiveMatchingEvents(rule).length
      if (matchCount === 0) {
        return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
      } else if (matchCount < 5) {
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
      } else if (matchCount < 20) {
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
      } else {
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
      }
    }
    
    const getRuleStatus = (rule) => {
      const willChangeCount = getLiveMatchingEvents(rule).filter(e => e.willChange).length
      if (willChangeCount === 0) {
        return t('domainAdmin.complete')
      } else if (willChangeCount < 5) {
        return t('domainAdmin.ready')
      } else {
        return t('status.pending')
      }
    }
    
    const getRuleStatusClass = (rule) => {
      const status = getRuleStatus(rule)
      switch (status) {
        case t('domainAdmin.complete'):
          return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
        case t('domainAdmin.ready'):
          return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
        case t('status.pending'):
          return 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200'
        default:
          return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
      }
    }
    
    const getRuleTypeLabel = (ruleType) => {
      const labels = {
        title_contains: t('domainAdmin.titleContains'),
        description_contains: t('domainAdmin.descriptionContains'), 
        category_contains: t('domainAdmin.categoryContains')
      }
      return labels[ruleType] || ruleType
    }
    
    const getRuleTypeDescription = (ruleType) => {
      const descriptions = {
        title_contains: t('domainAdmin.titleContainsDesc'),
        description_contains: t('domainAdmin.descriptionContainsDesc'),
        category_contains: t('domainAdmin.categoryContainsDesc')
      }
      return descriptions[ruleType] || t('domainAdmin.matches')
    }
    
    const getRuleTypeIcon = (ruleType) => {
      const icons = {
        title_contains: '📄',
        description_contains: '📝',
        category_contains: '🏷️'
      }
      return icons[ruleType] || '⚡'
    }
    
    const getRuleTypeIconClass = (ruleType) => {
      const classes = {
        title_contains: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
        description_contains: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        category_contains: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
      }
      return classes[ruleType] || 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
    }
    
    const getRulePlaceholder = (ruleType) => {
      const placeholders = {
        title_contains: t('domainAdmin.ruleTypePlaceholders.title_contains'),
        description_contains: t('domainAdmin.ruleTypePlaceholders.description_contains'),
        category_contains: t('domainAdmin.ruleTypePlaceholders.category_contains')
      }
      return placeholders[ruleType] || t('domainAdmin.enterSearchValue')
    }
    
    const getGroupName = (groupId) => {
      const group = props.groups.find(g => g.id === groupId)
      return group ? group.name : 'Unknown Group'
    }
    
    const extractDescriptionFromRawICal = (rawICal) => {
      /**
       * Extract DESCRIPTION value from raw iCal content.
       */
      if (!rawICal || typeof rawICal !== 'string') {
        return ''
      }
      
      const lines = rawICal.split(/\r?\n/)
      
      for (const line of lines) {
        const trimmedLine = line.trim()
        
        // Match DESCRIPTION: lines (case insensitive)
        const descriptionMatch = trimmedLine.match(/^DESCRIPTION:\s*(.+)$/i)
        if (descriptionMatch) {
          return descriptionMatch[1].trim()
        }
      }
      
      return ''
    }
    
    const extractCategoriesFromRawICal = (rawICal) => {
      /**
       * Extract CATEGORY values from raw iCal content.
       * Fixed version that handles the actual iCal format properly.
       */
      const categories = []
      if (!rawICal || typeof rawICal !== 'string') {
        console.log('No raw_ical data or invalid format:', rawICal)
        return categories
      }
      
      // Split by both \n and actual newlines to handle different formats
      const lines = rawICal.split(/\r?\n/)
      console.log('Processing', lines.length, 'lines from raw_ical')
      
      for (const line of lines) {
        const trimmedLine = line.trim()
        
        // Debug: Log any line containing CATEGOR
        if (trimmedLine.toUpperCase().includes('CATEGOR')) {
          console.log('Found CATEGORY-related line:', trimmedLine)
        }
        
        // Match CATEGORY: or CATEGORIES: lines (case insensitive)
        const categoryMatch = trimmedLine.match(/^CATEGOR(?:Y|IES):\s*(.+)$/i)
        if (categoryMatch) {
          const category = categoryMatch[1].trim()
          if (category) {
            console.log('✅ Extracted category:', category)
            categories.push(category)
          }
        }
      }
      
      console.log('📋 Final extracted categories:', categories)
      return categories
    }
    
    const getLiveMatchingEvents = (rule) => {
      if (!rule || !rule.rule_type || !rule.rule_value || !Array.isArray(props.recurringEvents)) {
        return []
      }
      
      const matchingEvents = []
      
      // Check each recurring event against the rule
      props.recurringEvents.forEach(event => {
        let matches = false
        const searchValue = rule.rule_value.toLowerCase()
        
        switch (rule.rule_type) {
          case 'title_contains':
            matches = event.title.toLowerCase().includes(searchValue)
            break
          case 'description_contains':
            // Use enhanced backend data: sample_description with fallback to extraction
            const description = event.sample_description || 
                              extractDescriptionFromRawICal(event.sample_raw_ical || '')
            matches = description.toLowerCase().includes(searchValue)
            break  
          case 'category_contains':
            // Use enhanced backend data: sample_categories with fallback to extraction
            const categories = event.sample_categories || 
                             extractCategoriesFromRawICal(event.sample_raw_ical || '')
            matches = categories.some(cat => cat.toLowerCase().includes(searchValue))
            break
        }
        
        if (matches) {
          // Check if target group is already assigned (handle multi-group assignments)
          const targetGroupId = parseInt(rule.target_group_id)
          const assignedGroupIds = event.assigned_group_ids || []
          const isAlreadyAssigned = assignedGroupIds.includes(targetGroupId)
          const willChange = !isAlreadyAssigned
          
          const primaryGroupId = assignedGroupIds.length > 0 ? assignedGroupIds[0] : null
          
          // Extract description and categories for display
          const description = event.sample_description || 
                            extractDescriptionFromRawICal(event.sample_raw_ical || '')
          const categories = event.sample_categories || 
                           extractCategoriesFromRawICal(event.sample_raw_ical || '')
          
          matchingEvents.push({
            title: event.title,
            event_count: event.event_count,
            description: description,
            categories: categories,
            currentGroupId: primaryGroupId,
            currentGroupName: primaryGroupId ? getGroupName(primaryGroupId) : t('domainAdmin.unassigned'),
            allGroupIds: assignedGroupIds,
            willChange
          })
        }
      })
      
      return matchingEvents
    }
    
    return {
      t,
      newRule,
      expandedRules,
      ruleTypes,
      isFormValid,
      toggleRuleDropdown,
      createRule,
      applyRule,
      deleteRuleConfirm,
      resetForm,
      updateRuleTypePreview,
      debouncedUpdatePreview,
      getGroupEventCount,
      getMatchCountBadgeClass,
      getRuleStatus,
      getRuleStatusClass,
      getRuleTypeLabel,
      getRuleTypeDescription,
      getRuleTypeIcon,
      getRuleTypeIconClass,
      getRulePlaceholder,
      getGroupName,
      extractDescriptionFromRawICal,
      extractCategoriesFromRawICal,
      getLiveMatchingEvents
    }
  }
}
</script>

<style scoped>
/* Micro-animations and enhanced feedback */
.auto-rules-card {
  /* Smooth transitions for all interactive elements */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Pulse animation for live preview indicator */
@keyframes pulse-green {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  }
  70% {
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

.animate-pulse-green {
  animation: pulse-green 2s infinite;
}

/* Smooth bounce animation for buttons */
@keyframes bounce-subtle {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-2px);
  }
  60% {
    transform: translateY(-1px);
  }
}

.animate-bounce-subtle {
  animation: bounce-subtle 0.6s ease-in-out;
}

/* Gradient shift animation for success states */
@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}

/* Scale and glow on hover for buttons */
.btn-enhanced:hover {
  transform: scale(1.02) translateY(-1px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.btn-enhanced:active {
  transform: scale(0.98) translateY(0);
}

/* Smooth expand/collapse animation */
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.expand-enter-from, .expand-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.expand-enter-to, .expand-leave-from {
  max-height: 500px;
  opacity: 1;
  transform: translateY(0);
}

/* Loading state animation */
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin-slow {
  animation: spin-slow 2s linear infinite;
}

/* Slide in animation for new rules */
@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-in-up {
  animation: slide-in-up 0.4s ease-out forwards;
}

/* Focus states for better accessibility */
.enhanced-focus:focus {
  outline: none;
  ring: 2px;
  ring-color: rgb(59 130 246);
  ring-offset: 2px;
  ring-offset-color: rgb(255 255 255);
}

.dark .enhanced-focus:focus {
  ring-offset-color: rgb(31 41 55);
}

/* Subtle shadow animations */
.shadow-lift {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.shadow-lift:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

/* Number badge animation */
.badge-bounce {
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.badge-bounce:hover {
  transform: scale(1.1);
}
</style>