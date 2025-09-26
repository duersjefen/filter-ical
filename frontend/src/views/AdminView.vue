<template>
  <!-- Loading State -->
  <div v-if="loading" class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6">
    <div class="text-center py-12 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-lg">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mb-6"></div>
      <div class="text-blue-800 dark:text-blue-200 font-semibold text-lg">{{ $t('admin.loadingPanel') }}</div>
      <div class="text-blue-600 dark:text-blue-300 text-sm mt-2">{{ $t('admin.pleaseWait') }}</div>
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
        {{ $t('admin.backToCalendar', { domain }) }}
      </router-link>
    </div>
  </div>

  <!-- Main Admin Interface -->
  <div v-else class="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-6 space-y-8">
    
    <!-- Admin Header -->
    <AppHeader 
      :title="`🔧 ${domain.toUpperCase()} Admin Panel`"
      :subtitle="$t('admin.manageEventsGroups', { domain })"
      :show-user-info="false"
      :show-back-button="true"
      :back-button-text="$t('admin.backToCalendar', { domain })"
      page-context="admin"
      @navigate-back="$router.push(`/${domain}`)"
    />

    <!-- Expandable Cards Layout -->
    <div class="space-y-4">
      
      <!-- 📅 Events Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
        <!-- Header with gradient background matching calendar cards -->
        <div 
          class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
          :class="expandedCards.events ? 'rounded-t-xl' : 'rounded-xl'"
        >
          <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="toggleCard('events')">
            <!-- Standardized dropdown arrow -->
            <svg 
              class="w-4 h-4 text-gray-400 transition-transform duration-300"
              :class="{ 'rotate-90': expandedCards.events }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                📅 {{ $t('admin.eventManagement') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ recurringEvents.length }} events • {{ assignedEventsCount }} assigned • Assign events to groups
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="expandedCards.events" class="p-3 sm:p-4 space-y-4">
          
          <!-- Group Filter Bar -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by Group</h3>
              <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <span>💡 Hold Ctrl to select multiple</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <!-- All Events Button -->
              <button
                @click="toggleGroupFilter('all', $event)"
                :class="[
                  'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
                  activeGroupFilters.length === 0
                    ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700'
                    : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
                ]"
              >
                <span>📅</span>
                <span>All Events</span>
                <span class="text-xs opacity-75">({{ recurringEvents.length }})</span>
              </button>
              
              <!-- Unassigned Button -->
              <button
                @click="toggleGroupFilter('unassigned', $event)"
                :class="[
                  'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
                  activeGroupFilters.includes('unassigned')
                    ? 'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900/30 dark:text-orange-200 dark:border-orange-700'
                    : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
                ]"
              >
                <span>⚠️</span>
                <span>Unassigned</span>
                <span class="text-xs opacity-75">({{ unassignedEventsCount }})</span>
              </button>
              
              <!-- Group Buttons -->
              <button
                v-for="group in groups"
                :key="group.id"
                @click="toggleGroupFilter(group.id, $event)"
                :class="[
                  'inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border',
                  activeGroupFilters.includes(group.id)
                    ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700'
                    : selectedEvents.length > 0
                    ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-600 dark:hover:bg-blue-800/30 cursor-pointer transform hover:scale-105'
                    : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
                ]"
                :title="selectedEvents.length > 0 ? `Click to assign ${selectedEvents.length} selected events to ${group.name}` : `Filter events by ${group.name}`"
              >
                <span>📁</span>
                <span>{{ group.name }}</span>
                <span class="text-xs opacity-75">({{ getGroupEventCount(group.id) }})</span>
              </button>
            </div>
          </div>
          
          <!-- Assignment Instructions -->
          <div v-if="selectedEvents.length > 0" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
            <div class="flex items-center gap-3">
              <span class="text-blue-600 dark:text-blue-400 text-lg">👆</span>
              <div>
                <p class="text-blue-800 dark:text-blue-200 font-medium">
                  {{ selectedEvents.length }} events selected - Click a group above to assign them!
                </p>
                <p class="text-blue-600 dark:text-blue-300 text-sm mt-1">
                  💡 Hold Ctrl + click groups to assign to multiple groups at once
                </p>
              </div>
              <button
                @click="clearEventSelection"
                class="ml-auto text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 px-2 py-1 text-sm font-medium"
              >
                Clear Selection
              </button>
            </div>
          </div>
          
          <!-- Search Bar -->
          <div class="flex items-center gap-4">
            <div class="relative flex-1">
              <input
                v-model="eventSearch"
                type="text"
                placeholder="Search events..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <span class="absolute left-3 top-2.5 text-gray-400">🔍</span>
            </div>
          </div>
          
          <!-- Events Table -->
          <div class="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="w-12 px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      :checked="isAllEventsSelected"
                      :indeterminate="isSomeEventsSelected"
                      @change="toggleSelectAllEvents"
                      class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                  </th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">Event Title</th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">Count</th>
                  <th class="px-4 py-3 text-left text-sm font-medium text-gray-900 dark:text-gray-100">Assigned Group</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr 
                  v-for="event in filteredEvents" 
                  :key="event.title"
                  @click="toggleEventSelection(event.title, $event)"
                  :class="[
                    'transition-colors duration-150 cursor-pointer',
                    selectedEvents.includes(event.title)
                      ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700'
                      : !event.assigned_group_id
                      ? 'bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/30'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                  ]"
                >
                  <td class="px-4 py-3" @click.stop>
                    <input
                      type="checkbox"
                      :value="event.title"
                      v-model="selectedEvents"
                      class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                  </td>
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900 dark:text-white">{{ event.title }}</div>
                    <div v-if="event.sample_location" class="text-sm text-gray-500 dark:text-gray-400">📍 {{ event.sample_location }}</div>
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      {{ event.event_count }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span 
                      v-if="event.assigned_group_id" 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                    >
                      {{ getGroupName(event.assigned_group_id) }}
                    </span>
                    <span 
                      v-else 
                      class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
                    >
                      ⚠️ Unassigned
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="filteredEvents.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">📅</div>
            <p>No events found matching your criteria</p>
          </div>
        </div>
      </div>

      <!-- 📁 Groups Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
        <!-- Header with gradient background matching calendar cards -->
        <div 
          class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
          :class="expandedCards.groups ? 'rounded-t-xl' : 'rounded-xl'"
        >
          <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="toggleCard('groups')">
            <!-- Standardized dropdown arrow -->
            <svg 
              class="w-4 h-4 text-gray-400 transition-transform duration-300"
              :class="{ 'rotate-90': expandedCards.groups }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                📁 {{ $t('admin.groups') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ groups.length }} groups • Create and manage event groups
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="expandedCards.groups" class="p-3 sm:p-4 space-y-4">
          <!-- Create New Group -->
          <div class="flex items-center gap-3 mb-4">
            <input
              v-model="newGroupName"
              type="text"
              placeholder="Enter group name..."
              @keyup.enter="createGroup"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
            <button
              @click="createGroup"
              :disabled="!newGroupName.trim() || loading"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
            >
              <span>+</span>
              Create Group
            </button>
          </div>
          
          <!-- Groups List -->
          <div class="space-y-3">
            <div 
              v-for="group in groups" 
              :key="group.id"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <div class="flex-1">
                <div v-if="editingGroupId !== group.id" class="flex items-center gap-3">
                  <h3 class="font-medium text-gray-900 dark:text-white">{{ group.name }}</h3>
                  <span class="text-sm text-gray-500 dark:text-gray-400">({{ getGroupEventCount(group.id) }} events)</span>
                </div>
                <div v-else class="flex items-center gap-3">
                  <input
                    v-model="editingGroupName"
                    type="text"
                    @keyup.enter="saveGroupEdit(group.id)"
                    @keyup.escape="cancelGroupEdit"
                    class="flex-1 px-3 py-1 border border-blue-300 dark:border-blue-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <div class="flex items-center gap-2">
                <template v-if="editingGroupId !== group.id">
                  <button
                    @click="startEditingGroup(group)"
                    :disabled="loading"
                    class="text-blue-600 hover:text-blue-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    @click="confirmDeleteGroup(group)"
                    :disabled="loading"
                    class="text-red-600 hover:text-red-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
                  >
                    🗑️ Delete
                  </button>
                </template>
                <template v-else>
                  <button
                    @click="saveGroupEdit(group.id)"
                    :disabled="!editingGroupName.trim() || loading"
                    class="text-green-600 hover:text-green-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
                  >
                    ✓ Save
                  </button>
                  <button
                    @click="cancelGroupEdit"
                    class="text-gray-600 hover:text-gray-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
                  >
                    ✗ Cancel
                  </button>
                </template>
              </div>
            </div>
          </div>
          
          <div v-if="groups.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">📁</div>
            <p>No groups created yet. Create your first group above!</p>
          </div>
        </div>
      </div>

      <!-- ⚙️ Auto Rules Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
        <!-- Header with gradient background matching calendar cards -->
        <div 
          class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
          :class="expandedCards.rules ? 'rounded-t-xl' : 'rounded-xl'"
        >
          <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="toggleCard('rules')">
            <!-- Standardized dropdown arrow -->
            <svg 
              class="w-4 h-4 text-gray-400 transition-transform duration-300"
              :class="{ 'rotate-90': expandedCards.rules }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                ⚙️ {{ $t('admin.autoRules') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ assignmentRules.length }} rules • Automatic event assignment rules
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="expandedCards.rules" class="p-3 sm:p-4 space-y-4">
          <!-- Create New Rule -->
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg space-y-3">
            <h3 class="font-medium text-gray-900 dark:text-white">Create New Rule</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
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
              <button
                @click="createRule"
                :disabled="!newRule.rule_type || !newRule.rule_value.trim() || !newRule.target_group_id"
                class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                Create Rule
              </button>
            </div>
          </div>
          
          <!-- Rules List -->
          <div class="space-y-3">
            <div 
              v-for="rule in assignmentRules" 
              :key="rule.id"
              class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <div class="flex-1">
                <h3 class="font-medium text-gray-900 dark:text-white">
                  {{ getRuleTypeLabel(rule.rule_type) }}: "{{ rule.rule_value }}"
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  → Assigns to {{ getGroupName(rule.target_group_id) }}
                </p>
              </div>
              <button
                @click="deleteRuleConfirm(rule)"
                class="text-red-600 hover:text-red-800 px-2 py-1 text-sm font-medium transition-colors duration-200"
              >
                🗑️ Delete
              </button>
            </div>
          </div>
          
          <div v-if="assignmentRules.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <div class="text-4xl mb-2">⚙️</div>
            <p>No assignment rules created yet. Create your first rule above!</p>
          </div>
        </div>
      </div>

      <!-- 💾 Configuration Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 mb-4 overflow-hidden">
        <!-- Header with gradient background matching calendar cards -->
        <div 
          class="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-gray-700 dark:to-gray-800 px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-700"
          :class="expandedCards.config ? 'rounded-t-xl' : 'rounded-xl'"
        >
          <div class="flex items-center gap-3 flex-1 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg p-2 -m-2 transition-colors duration-200" @click="toggleCard('config')">
            <!-- Standardized dropdown arrow -->
            <svg 
              class="w-4 h-4 text-gray-400 transition-transform duration-300"
              :class="{ 'rotate-90': expandedCards.config }"
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            
            <div class="flex-1">
              <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                💾 {{ $t('admin.configuration') }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Export, import, and reset domain configuration
              </p>
            </div>
          </div>
        </div>
        
        <div v-if="expandedCards.config" class="p-3 sm:p-4 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Export Configuration -->
            <div class="bg-blue-50 dark:bg-blue-900/30 p-6 rounded-xl border border-blue-200 dark:border-blue-700">
              <div class="flex items-center mb-4">
                <div class="text-2xl mr-3">📤</div>
                <h3 class="text-lg font-semibold text-blue-900 dark:text-blue-100">{{ $t('admin.export') }}</h3>
              </div>
              <p class="text-blue-700 dark:text-blue-200 text-sm mb-4">
                {{ $t('admin.exportDescription') }}
              </p>
              <button
                @click="exportConfiguration"
                :disabled="loading"
                class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                {{ $t('admin.exportConfiguration') }}
              </button>
            </div>

            <!-- Import Configuration -->
            <div class="bg-green-50 dark:bg-green-900/30 p-6 rounded-xl border border-green-200 dark:border-green-700">
              <div class="flex items-center mb-4">
                <div class="text-2xl mr-3">📥</div>
                <h3 class="text-lg font-semibold text-green-900 dark:text-green-100">{{ $t('admin.import') }}</h3>
              </div>
              <p class="text-green-700 dark:text-green-200 text-sm mb-4">
                {{ $t('admin.importDescription') }}
              </p>
              <input
                type="file"
                ref="fileInput"
                accept=".yaml,.yml"
                @change="handleFileUpload"
                class="hidden"
              >
              <button
                @click="$refs.fileInput.click()"
                :disabled="loading"
                class="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                {{ $t('admin.importConfiguration') }}
              </button>
            </div>

            <!-- Reset to Baseline -->
            <div class="bg-orange-50 dark:bg-orange-900/30 p-6 rounded-xl border border-orange-200 dark:border-orange-700">
              <div class="flex items-center mb-4">
                <div class="text-2xl mr-3">🔄</div>
                <h3 class="text-lg font-semibold text-orange-900 dark:text-orange-100">{{ $t('admin.reset') }}</h3>
              </div>
              <p class="text-orange-700 dark:text-orange-200 text-sm mb-4">
                {{ $t('admin.resetDescription') }}
              </p>
              <button
                @click="resetConfigurationConfirm"
                :disabled="loading"
                class="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
              >
                {{ $t('admin.resetToBaseline') }}
              </button>
            </div>
          </div>

          <!-- Configuration Status -->
          <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
            <h3 class="font-medium text-gray-900 dark:text-white mb-2">{{ $t('admin.currentStatus') }}</h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-400">{{ $t('admin.groupsCount') }}</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">{{ groups.length }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">{{ $t('admin.eventsCount') }}</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">{{ recurringEvents.length }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">{{ $t('admin.rulesCount') }}</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">{{ assignmentRules.length }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">{{ $t('admin.domainName') }}</span>
                <span class="ml-2 font-semibold text-gray-900 dark:text-white">{{ domain }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
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
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdmin } from '../composables/useAdmin'
import { useHTTP } from '../composables/useHTTP'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'

export default {
  name: 'AdminView',
  components: {
    AppHeader
  },
  props: {
    domain: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const { t } = useI18n()
    
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
      loadRecurringEventsWithAssignments,
      assignEventsToGroup,
      bulkAssignEventsToGroup,
      bulkUnassignEvents,
      unassignEventFromGroup,
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

    // HTTP functions for configuration management
    const { get, post } = useHTTP()

    // UI State - Expandable Cards
    const expandedCards = ref({
      events: true, // Events card starts expanded
      groups: false,
      rules: false,
      config: false
    })

    // Events UI State
    const eventSearch = ref('')
    const selectedEvents = ref([])
    const activeGroupFilters = ref([]) // Array for multi-group filtering

    // Groups UI State  
    const newGroupName = ref('')
    const editingGroupId = ref(null)
    const editingGroupName = ref('')

    // Rules UI State
    const newRule = ref({
      rule_type: '',
      rule_value: '',
      target_group_id: ''
    })

    // Notification State
    const notification = ref(null)
    const confirmDialog = ref(null)

    // Computed Properties
    const assignedEventsCount = computed(() => {
      if (!Array.isArray(recurringEvents.value)) return 0
      return recurringEvents.value.filter(event => event.assigned_group_id).length
    })

    const unassignedEventsCount = computed(() => {
      if (!Array.isArray(recurringEvents.value)) return 0
      return recurringEvents.value.filter(event => !event.assigned_group_id).length
    })

    const filteredEvents = computed(() => {
      let filtered = Array.isArray(recurringEvents.value) ? recurringEvents.value : []
      
      // Search filter
      if (eventSearch.value) {
        const query = eventSearch.value.toLowerCase()
        filtered = filtered.filter(event => 
          event.title.toLowerCase().includes(query) ||
          (event.sample_location && event.sample_location.toLowerCase().includes(query))
        )
      }

      // Group filter - support multiple group selection
      if (activeGroupFilters.value.length > 0) {
        filtered = filtered.filter(event => {
          // Handle 'unassigned' filter
          if (activeGroupFilters.value.includes('unassigned')) {
            if (!event.assigned_group_id) return true
          }
          
          // Handle specific group filters
          const groupFilters = activeGroupFilters.value.filter(f => f !== 'unassigned')
          if (groupFilters.length > 0) {
            return groupFilters.includes(event.assigned_group_id)
          }
          
          return activeGroupFilters.value.includes('unassigned') && !event.assigned_group_id
        })
      }

      return filtered
    })

    const isAllEventsSelected = computed(() => {
      const filtered = filteredEvents.value
      if (!Array.isArray(filtered) || filtered.length === 0) return false
      return selectedEvents.value.length === filtered.length
    })

    const isSomeEventsSelected = computed(() => {
      const filtered = filteredEvents.value
      if (!Array.isArray(filtered)) return false
      return selectedEvents.value.length > 0 && selectedEvents.value.length < filtered.length
    })

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

    const showConfirm = (message, onConfirm) => {
      confirmDialog.value = { message, onConfirm }
    }

    const closeConfirm = () => {
      confirmDialog.value = null
    }

    // Group Filter Management
    const toggleGroupFilter = (filterValue, event) => {
      const isCtrlClick = event.ctrlKey || event.metaKey
      
      if (filterValue === 'all') {
        // Clear all filters
        activeGroupFilters.value = []
        return
      }
      
      // If selected events exist, this is an assignment action
      if (selectedEvents.value.length > 0 && filterValue !== 'unassigned') {
        handleGroupAssignment(filterValue, isCtrlClick)
        return
      }
      
      // Otherwise, this is a filter action
      if (isCtrlClick) {
        // Multi-select with Ctrl
        const index = activeGroupFilters.value.indexOf(filterValue)
        if (index > -1) {
          activeGroupFilters.value.splice(index, 1)
        } else {
          activeGroupFilters.value.push(filterValue)
        }
      } else {
        // Single select
        if (activeGroupFilters.value.length === 1 && activeGroupFilters.value[0] === filterValue) {
          // Clicking the same filter again clears it
          activeGroupFilters.value = []
        } else {
          activeGroupFilters.value = [filterValue]
        }
      }
    }

    const handleGroupAssignment = async (groupId, isMultiSelect) => {
      if (selectedEvents.value.length === 0) return
      
      try {
        const groupIds = isMultiSelect ? [groupId] : [groupId] // For future multi-group assignment
        
        // For now, assign to single group
        const result = await bulkAssignEventsToGroup(parseInt(groupId), selectedEvents.value)
        
        if (result.success) {
          showNotification(`${selectedEvents.value.length} events assigned to ${getGroupName(groupId)}!`, 'success')
          clearEventSelection()
        } else {
          showNotification(`Failed to assign events: ${result.error}`, 'error')
        }
      } catch (error) {
        showNotification(`Failed to assign events: ${error.message}`, 'error')
      }
    }

    // Events Management
    const toggleSelectAllEvents = () => {
      if (isAllEventsSelected.value) {
        selectedEvents.value = []
      } else {
        selectedEvents.value = filteredEvents.value.map(event => event.title)
      }
    }

    const toggleEventSelection = (eventTitle, event) => {
      // Prevent checkbox from being triggered twice
      if (event.target.type === 'checkbox') return
      
      const index = selectedEvents.value.indexOf(eventTitle)
      if (index > -1) {
        selectedEvents.value.splice(index, 1)
      } else {
        selectedEvents.value.push(eventTitle)
      }
    }

    const clearEventSelection = () => {
      selectedEvents.value = []
    }

    const getGroupEventCount = (groupId) => {
      if (!Array.isArray(recurringEvents.value)) return 0
      return recurringEvents.value.filter(event => event.assigned_group_id === groupId).length
    }

    // Group Management
    const createGroup = async () => {
      const validation = validateGroupName(newGroupName.value)
      if (!validation.valid) {
        showNotification(validation.error, 'error')
        return
      }

      const result = await createGroupAPI(newGroupName.value)
      if (result.success) {
        newGroupName.value = ''
        showNotification('Group created successfully!', 'success')
      } else {
        showNotification(`Failed to create group: ${result.error}`, 'error')
      }
    }

    const startEditingGroup = (group) => {
      editingGroupId.value = group.id
      editingGroupName.value = group.name
    }

    const saveGroupEdit = async (groupId) => {
      const validation = validateGroupName(editingGroupName.value)
      if (!validation.valid) {
        showNotification(validation.error, 'error')
        return
      }

      const result = await updateGroupAPI(groupId, editingGroupName.value)
      if (result.success) {
        editingGroupId.value = null
        editingGroupName.value = ''
        showNotification('Group updated successfully!', 'success')
      } else {
        showNotification(`Failed to update group: ${result.error}`, 'error')
      }
    }

    const cancelGroupEdit = () => {
      editingGroupId.value = null
      editingGroupName.value = ''
    }

    const confirmDeleteGroup = (group) => {
      showConfirm(
        `Are you sure you want to delete "${group.name}"? This will also delete all assignments and rules for this group.`,
        () => deleteGroup(group.id)
      )
    }

    const deleteGroup = async (groupId) => {
      const result = await deleteGroupAPI(groupId)
      if (result.success) {
        showNotification('Group deleted successfully!', 'success')
      } else {
        showNotification(`Failed to delete group: ${result.error}`, 'error')
      }
    }

    // Bulk Unassign Handler (for unassigned group filter)
    const handleBulkUnassign = async () => {
      if (selectedEvents.value.length > 0) {
        const result = await bulkUnassignEvents(selectedEvents.value)
        if (result.success) {
          showNotification(`${selectedEvents.value.length} events unassigned successfully!`, 'success')
          clearEventSelection()
        } else {
          showNotification(`Failed to bulk unassign events: ${result.error}`, 'error')
        }
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
        showNotification(validation.error, 'error')
        return
      }

      const result = await createAssignmentRuleAPI(
        newRule.value.rule_type,
        newRule.value.rule_value,
        newRule.value.target_group_id
      )
      
      if (result.success) {
        newRule.value = { rule_type: '', rule_value: '', target_group_id: '' }
        showNotification('Assignment rule created successfully!', 'success')
      } else {
        showNotification(`Failed to create assignment rule: ${result.error}`, 'error')
      }
    }

    const deleteRuleConfirm = (rule) => {
      showConfirm(
        'Are you sure you want to delete this rule?',
        () => deleteRule(rule.id)
      )
    }

    const deleteRule = async (ruleId) => {
      const result = await deleteAssignmentRuleAPI(ruleId)
      if (result.success) {
        showNotification('Assignment rule deleted successfully!', 'success')
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
          headers: { 'Accept': 'application/x-yaml' },
          responseType: 'text'
        })
        
        const yamlContent = response.data
        const blob = new Blob([yamlContent], { type: 'application/x-yaml' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${props.domain}-config.yaml`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        showNotification('Configuration exported successfully!', 'success')
      } catch (err) {
        console.error('Failed to export configuration:', err)
        showNotification(`Failed to export configuration: ${err.message}`, 'error')
      }
    }

    const handleFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      try {
        // Send raw YAML content to backend for parsing
        const yamlContent = await file.text()
        const result = await post(`/domains/${props.domain}/import-config`, yamlContent, {
          headers: { 'Content-Type': 'application/x-yaml' }
        })
        
        if (result.success) {
          showNotification(`Configuration imported successfully: ${result.message}`, 'success')
          // Reload admin data to reflect changes
          await loadAllAdminData()
        } else {
          showNotification(`Failed to import configuration: ${result.message}`, 'error')
        }
      } catch (err) {
        console.error('Failed to import configuration:', err)
        showNotification(`Failed to import configuration: ${err.message}`, 'error')
      }
      
      // Clear file input
      event.target.value = ''
    }

    const resetConfigurationConfirm = () => {
      showConfirm(
        `Are you sure you want to reset "${props.domain}" to its baseline configuration? This will replace all current groups, assignments, and rules with the default setup.`,
        () => resetConfiguration()
      )
    }

    const resetConfiguration = async () => {
      try {
        const result = await post(`/domains/${props.domain}/reset-config`, {})
        
        if (result.success && result.data) {
          showNotification(result.data.message, 'success')
          // Reload admin data to reflect changes
          await loadAllAdminData()
        } else {
          showNotification(`Failed to reset configuration: ${result.error || 'Unknown error'}`, 'error')
        }
      } catch (err) {
        console.error('Failed to reset configuration:', err)
        showNotification(`Failed to reset configuration: ${err.message}`, 'error')
      }
    }

    // Load data on mount - with guard to prevent multiple loads
    let hasInitiallyLoaded = false
    onMounted(() => {
      if (!hasInitiallyLoaded) {
        hasInitiallyLoaded = true
        loadAllAdminData()
      }
    })

    return {
      // UI State
      expandedCards,
      loading,
      error,

      // Events UI State
      eventSearch,
      selectedEvents,
      activeGroupFilters,

      // Groups UI State
      newGroupName,
      editingGroupId,
      editingGroupName,

      // Rules UI State
      newRule,

      // Notification States
      notification,
      confirmDialog,
      closeConfirm,

      // Data
      groups,
      recurringEvents,
      assignmentRules,

      // Computed
      assignedEventsCount,
      unassignedEventsCount,
      filteredEvents,
      isAllEventsSelected,
      isSomeEventsSelected,

      // Methods
      toggleCard,
      toggleGroupFilter,
      handleGroupAssignment,
      toggleSelectAllEvents,
      toggleEventSelection,
      clearEventSelection,
      getGroupEventCount,
      createGroup,
      startEditingGroup,
      saveGroupEdit,
      cancelGroupEdit,
      confirmDeleteGroup,
      createRule,
      deleteRuleConfirm,
      getRuleTypeLabel,
      getGroupName,
      
      // Remaining Assignment Handlers
      handleBulkUnassign,
      
      // Configuration Methods
      exportConfiguration,
      handleFileUpload,
      resetConfigurationConfirm,
      
      // Admin Data Loading
      loadAllAdminData
    }
  }
}
</script>

<style scoped>
/* Smooth transitions for accordion */
.transform {
  transition: transform 0.2s ease-in-out;
}

.rotate-90 {
  transform: rotate(90deg);
}

/* Indeterminate checkbox styling */
input[type="checkbox"]:indeterminate {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

input[type="checkbox"]:indeterminate:after {
  content: '';
  display: block;
  width: 8px;
  height: 2px;
  background-color: white;
  margin: 2px auto;
}
</style>