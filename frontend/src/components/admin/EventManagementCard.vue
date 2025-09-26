<template>
  <AdminCardWrapper
    :title="$t('admin.eventManagement')"
    :subtitle="`${recurringEvents.length} events • ${assignedEventsCount} assigned • Assign events to groups`"
    icon="📅"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <!-- Group Filter Bar -->
    <div class="space-y-3">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <h3 class="text-base sm:text-sm font-medium text-gray-700 dark:text-gray-300">Filter by Group</h3>
        <div class="hidden sm:flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span>💡 Hold Ctrl to select multiple groups • Right-click groups to edit • Right-click events to assign • Drag to select multiple events</span>
        </div>
        <!-- Mobile-friendly tip -->
        <div class="sm:hidden text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
          <span>💡 Tap groups to filter • Long-press to edit • Tap events to assign</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 overflow-x-auto">
        <!-- All Events Button -->
        <button
          @click="toggleGroupFilter('all', $event)"
          :class="[
            'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
            activeGroupFilters.length === 0
              ? 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="activeGroupFilters.length === 0 ? 'Currently showing all events' : 'Click to clear group filters and show all events • Hold Ctrl to select multiple filters'"
        >
          <span>📋</span>
          <span>All Events</span>
          <span class="text-xs opacity-75">({{ recurringEvents.length }})</span>
        </button>
        
        <!-- Unassigned Button -->
        <button
          @click="toggleGroupFilter('unassigned', $event)"
          :class="[
            'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
            activeGroupFilters.includes('unassigned')
              ? 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900/30 dark:text-yellow-200 dark:border-yellow-700'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="'Filter unassigned events • Hold Ctrl to select multiple filters'"
        >
          <span>❔</span>
          <span>Unassigned</span>
          <span class="text-xs opacity-75">({{ unassignedEventsCount }})</span>
        </button>
        
        <!-- Group Buttons with Right-Click Context Menu -->
        <button
          v-for="group in groups"
          :key="group.id"
          @click="toggleGroupFilter(group.id, $event)"
          @contextmenu.prevent="showContextMenu(group, $event)"
          :class="[
            'inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border min-h-[44px] sm:min-h-0 flex-shrink-0',
            activeGroupFilters.includes(group.id)
              ? 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700'
              : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
          ]"
          :title="`Filter events by ${group.name} • Hold Ctrl to select multiple filters • Right-click for options`"
        >
          <span v-if="editingGroupId !== group.id" class="truncate max-w-[120px] sm:max-w-none">{{ group.name }}</span>
          <input
            v-else
            v-model="editingGroupName"
            @keyup.enter="saveGroupEdit(group.id)"
            @keyup.escape="cancelGroupEdit"
            @blur="saveGroupEdit(group.id)"
            class="min-w-0 bg-transparent border-none outline-none text-inherit font-medium"
            :style="{ width: Math.max(50, editingGroupName.length * 8) + 'px' }"
          />
          <span class="text-xs opacity-75 flex-shrink-0">({{ getGroupEventCount(group.id) }})</span>
        </button>
        
        <!-- Add Group Button -->
        <button
          v-if="!showAddGroupForm"
          @click="startAddGroup"
          class="inline-flex items-center gap-2 px-4 py-3 sm:px-3 sm:py-2 rounded-lg text-base sm:text-sm font-medium transition-all duration-200 border border-dashed border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:border-green-400 hover:text-green-600 dark:hover:text-green-400 min-h-[44px] sm:min-h-0 flex-shrink-0"
        >
          <span>➕</span>
          <span>Add Group</span>
        </button>
        
        <!-- Add Group Form -->
        <div v-else class="flex items-center gap-2 w-full sm:w-auto sm:inline-flex">
          <input
            v-model="newGroupName"
            @keyup.enter="createGroup"
            @keyup.escape="cancelAddGroup"
            @blur="handleAddGroupBlur"
            placeholder="Group name..."
            class="px-4 py-3 sm:px-3 sm:py-2 border border-green-300 dark:border-green-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 text-base sm:text-sm min-w-32 flex-1 sm:flex-none min-h-[44px] sm:min-h-0"
            ref="newGroupInput"
          />
          <button
            @click="createGroup"
            :disabled="!newGroupName.trim()"
            class="px-4 py-3 sm:px-2 sm:py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg sm:rounded text-base sm:text-sm min-h-[44px] sm:min-h-0 flex-shrink-0"
          >
            ✓
          </button>
          <button
            @click="cancelAddGroup"
            class="px-4 py-3 sm:px-2 sm:py-1 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg sm:rounded text-base sm:text-sm min-h-[44px] sm:min-h-0 flex-shrink-0"
          >
            ✗
          </button>
        </div>
      </div>
    </div>
    
    <!-- Group Context Menu -->
    <div
      v-if="contextMenu.visible"
      :style="{
        position: 'fixed',
        top: contextMenu.y + 'px',
        left: contextMenu.x + 'px',
        zIndex: 1000
      }"
      class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg py-1 min-w-32"
      @click.stop
    >
      <button
        @click="editGroupFromMenu"
        class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
      >
        <span>✏️</span>
        <span>Edit Name</span>
      </button>
      <button
        @click="deleteGroupFromMenu"
        class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 flex items-center gap-2"
      >
        <span>🗑️</span>
        <span>Delete Group</span>
      </button>
    </div>
    
    <!-- Event Context Menu -->
    <div
      v-if="eventContextMenu.visible"
      :style="{
        position: 'fixed',
        top: eventContextMenu.y + 'px',
        left: eventContextMenu.x + 'px',
        zIndex: 1000
      }"
      :class="[
        'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-xl py-2 backdrop-blur-sm',
        getContextMenuWidthClass()
      ]"
      @click.stop
    >
      <!-- Context Menu Header -->
      <div class="px-4 py-2 border-b border-gray-100 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-t-xl">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span class="text-xs font-semibold text-gray-700 dark:text-gray-300 truncate">{{ eventContextMenu.event?.title || 'Event Actions' }}</span>
        </div>
      </div>
      <!-- Add to Groups Section -->
      <div v-if="getAvailableGroupsForEvent(eventContextMenu.event).length > 0" class="py-1">
        <div class="px-4 py-2 text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wide flex items-center gap-2">
          <span class="w-3 h-3 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">+</span>
          <span>Add to Group</span>
        </div>
        <div :class="getGroupGridClass(getAvailableGroupsForEvent(eventContextMenu.event).length)">
          <button
            v-for="group in getAvailableGroupsForEvent(eventContextMenu.event)"
            :key="`add-${group.id}`"
            @click="quickAddToGroup(eventContextMenu.event, group.id)"
            class="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-green-900/20 flex items-center gap-2 transition-colors duration-150 rounded-md"
          >
            <div class="w-4 h-4 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-green-600 dark:text-green-400 text-xs font-bold">+</span>
            </div>
            <span class="font-medium truncate text-xs">{{ group.name }}</span>
          </button>
        </div>
      </div>
      
      <!-- Remove from Groups Section -->
      <div v-if="getAssignedGroupsForEvent(eventContextMenu.event).length > 0" class="py-1" :class="{ 'border-t border-gray-100 dark:border-gray-700': getAvailableGroupsForEvent(eventContextMenu.event).length > 0 }">
        <div class="px-4 py-2 text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wide flex items-center gap-2">
          <span class="w-3 h-3 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold">−</span>
          <span>Remove from Group</span>
        </div>
        <div :class="getGroupGridClass(getAssignedGroupsForEvent(eventContextMenu.event).length)">
          <button
            v-for="group in getAssignedGroupsForEvent(eventContextMenu.event)"
            :key="`remove-${group.id}`"
            @click="quickRemoveFromGroup(eventContextMenu.event, group.id)"
            class="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2 transition-colors duration-150 rounded-md"
          >
            <div class="w-4 h-4 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center flex-shrink-0">
              <span class="text-red-600 dark:text-red-400 text-xs font-bold">−</span>
            </div>
            <span class="font-medium truncate text-xs">{{ group.name }}</span>
          </button>
        </div>
      </div>
      
      <!-- No actions available -->
      <div v-if="getAvailableGroupsForEvent(eventContextMenu.event).length === 0 && getAssignedGroupsForEvent(eventContextMenu.event).length === 0" class="px-4 py-6 text-center">
        <div class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-2">
          <span class="text-gray-400 dark:text-gray-500 text-sm">📋</span>
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          <div class="font-medium">No group actions available</div>
          <div class="text-xs mt-1">Create groups to assign events</div>
        </div>
      </div>
    </div>
    
    <!-- Bulk Assignment Panel (Always visible with consistent sizing) -->
    <div class="relative bg-white dark:bg-gray-800 border-2 rounded-lg p-4 shadow-sm transition-all duration-200" 
         :class="[
           selectedEvents.length > 0 
             ? 'border-blue-300 dark:border-blue-600' 
             : 'border-gray-200 dark:border-gray-700 opacity-60',
           dragSelection.dragging ? 'pointer-events-none opacity-75' : ''
         ]">
      
      <!-- Status Indicator (fixed position top-right) -->
      <div v-if="isUpdatingGroups" class="absolute top-3 right-3 z-10">
        <div class="flex items-center gap-2 bg-white dark:bg-gray-800 px-2 py-1 rounded-full shadow-sm border border-gray-200 dark:border-gray-600">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">Updating...</span>
        </div>
      </div>
      <div class="flex items-center justify-center mb-3">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="[
                 selectedEvents.length > 0 
                   ? 'bg-blue-100 dark:bg-blue-900/30' 
                   : 'bg-gray-100 dark:bg-gray-700'
               ]">
            <span class="text-sm font-bold" :class="[
                    selectedEvents.length > 0 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-gray-400 dark:text-gray-500'
                  ]">{{ selectedEvents.length || '0' }}</span>
          </div>
          <div>
            <h4 class="font-medium" :class="[
                 selectedEvents.length > 0 
                   ? 'text-gray-900 dark:text-white' 
                   : 'text-gray-500 dark:text-gray-400'
               ]">
              Bulk Actions
            </h4>
            <p class="text-sm" :class="[
                 selectedEvents.length > 0 
                   ? 'text-gray-600 dark:text-gray-400' 
                   : 'text-gray-400 dark:text-gray-500'
               ]">
              {{ selectedEvents.length === 0 ? 'No events selected' : 
                 selectedEvents.length === 1 ? '1 event selected' : 
                 `${selectedEvents.length} events selected` }}
            </p>
          </div>
        </div>
      </div>
      
      <!-- Smart Group Actions -->
      <div class="space-y-3">
        <!-- Smart Combined Action Buttons Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          
          <div 
            v-for="group in groups" 
            :key="`smart-${group.id}`"
            class="inline-flex"
          >
            <!-- Single Action Button (when clear state) -->
            <button
              v-if="getSmartGroupAction(group.id).type === 'single'"
              @click="handleSmartGroupAction(group.id, getSmartGroupAction(group.id).primaryAction)"
              :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
              :class="[
                'group relative inline-flex items-center justify-between w-full h-16 px-3 rounded-lg text-xs font-medium transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none',
                getSmartGroupAction(group.id).primaryStyle === 'add' 
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 text-green-800 hover:from-green-100 hover:to-emerald-100 hover:border-green-300 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-600 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                  : 'bg-gradient-to-r from-red-50 to-rose-50 border-2 border-red-200 text-red-800 hover:from-red-100 hover:to-rose-100 hover:border-red-300 dark:from-red-900/20 dark:to-rose-900/20 dark:border-red-600 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
              ]"
              :title="`${getSmartGroupAction(group.id).primaryLabel} ${group.name}`"
            >
              <div class="flex items-center gap-3">
                <div :class="[
                  'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                  getSmartGroupAction(group.id).primaryStyle === 'add'
                    ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                    : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
                ]">
                  <span v-if="!isGroupUpdating(group.id)">{{ getSmartGroupAction(group.id).primaryLabel.charAt(0) }}</span>
                  <div v-else class="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div class="flex flex-col text-left">
                  <span class="font-semibold text-sm">{{ group.name }}</span>
                  <span class="text-xs opacity-75">{{ getSmartGroupAction(group.id).primaryLabel.split(' to')[0].split(' from')[0].substring(2) }}</span>
                </div>
              </div>
              <div :class="[
                'text-xs font-bold px-1.5 py-0.5 rounded-full',
                getSmartGroupAction(group.id).primaryStyle === 'add'
                  ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                  : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
              ]">
                {{ getSmartGroupAction(group.id).primaryCount }}
              </div>
            </button>
            
            <!-- Split Action Buttons (when mixed state) -->
            <div 
              v-else-if="getSmartGroupAction(group.id).type === 'split'"
              class="w-full h-16 bg-white dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-600 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col"
            >
              <!-- Group Header -->
              <div class="px-3 py-1 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border-b border-gray-200 dark:border-gray-500 flex-shrink-0">
                <div class="flex items-center justify-between">
                  <span class="font-semibold text-xs text-gray-800 dark:text-gray-200">{{ group.name }}</span>
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse" title="Mixed state - some events in/out"></div>
                </div>
              </div>
              
              <!-- Split Actions -->
              <div class="flex flex-1">
                <!-- Primary Action -->
                <button
                  @click="handleSmartGroupAction(group.id, getSmartGroupAction(group.id).primaryAction)"
                  :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
                  :class="[
                    'flex-1 px-3 py-1 text-xs font-medium transition-all duration-300 border-r border-gray-200 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed',
                    getSmartGroupAction(group.id).primaryStyle === 'add'
                      ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 hover:from-green-100 hover:to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/20 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                      : 'bg-gradient-to-r from-red-50 to-rose-50 text-red-800 hover:from-red-100 hover:to-rose-100 dark:from-red-900/20 dark:to-rose-900/20 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
                  ]"
                  :title="`${getSmartGroupAction(group.id).primaryLabel} ${group.name}`"
                >
                  <div class="flex items-center justify-center gap-2">
                    <div v-if="!isGroupUpdating(group.id)" :class="[
                      'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
                      getSmartGroupAction(group.id).primaryStyle === 'add'
                        ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                        : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
                    ]">
                      {{ getSmartGroupAction(group.id).primaryLabel.charAt(0) }}
                    </div>
                    <div v-else class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                    <span class="font-semibold">{{ getSmartGroupAction(group.id).primaryCount }}</span>
                  </div>
                </button>
                
                <!-- Secondary Action -->
                <button
                  @click="handleSmartGroupAction(group.id, getSmartGroupAction(group.id).secondaryAction)"
                  :disabled="isGroupUpdating(group.id) || selectedEvents.length === 0"
                  :class="[
                    'flex-1 px-3 py-1 text-xs font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed',
                    getSmartGroupAction(group.id).secondaryStyle === 'add'
                      ? 'bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 hover:from-green-100 hover:to-emerald-100 dark:from-green-900/20 dark:to-emerald-900/20 dark:text-green-200 dark:hover:from-green-800/30 dark:hover:to-emerald-800/30'
                      : 'bg-gradient-to-r from-red-50 to-rose-50 text-red-800 hover:from-red-100 hover:to-rose-100 dark:from-red-900/20 dark:to-rose-900/20 dark:text-red-200 dark:hover:from-red-800/30 dark:hover:to-rose-800/30'
                  ]"
                  :title="`${getSmartGroupAction(group.id).secondaryAction === 'add' ? 'Add' : 'Remove'} ${getSmartGroupAction(group.id).secondaryCount} events ${getSmartGroupAction(group.id).secondaryAction === 'add' ? 'to' : 'from'} ${group.name}`"
                >
                  <div class="flex items-center justify-center gap-2">
                    <div v-if="!isGroupUpdating(group.id)" :class="[
                      'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold',
                      getSmartGroupAction(group.id).secondaryStyle === 'add'
                        ? 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-200'
                        : 'bg-red-200 text-red-800 dark:bg-red-700 dark:text-red-200'
                    ]">
                      {{ getSmartGroupAction(group.id).secondaryAction === 'add' ? '+' : '−' }}
                    </div>
                    <div v-else class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                    <span class="font-semibold">{{ getSmartGroupAction(group.id).secondaryCount }}</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Unassign All Button (same size as groups) -->
          <button
            @click="handleUnassignAll"
            :disabled="isUpdatingGroups || selectedEvents.length === 0"
            class="group relative inline-flex items-center justify-between w-full h-16 px-3 rounded-lg text-xs font-medium transition-all duration-300 shadow-sm hover:shadow-md transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 text-yellow-800 hover:from-yellow-100 hover:to-amber-100 hover:border-yellow-300 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-600 dark:text-yellow-200 dark:hover:from-yellow-800/30 dark:hover:to-amber-800/30"
            :title="`Remove ${selectedEvents.length} events from all groups`"
          >
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 bg-yellow-200 dark:bg-yellow-700 rounded-full flex items-center justify-center text-xs font-bold">
                <span v-if="!isUpdatingGroups" class="text-yellow-800 dark:text-yellow-200">🚫</span>
                <div v-else class="w-3 h-3 border-2 border-yellow-800 dark:border-yellow-200 border-t-transparent rounded-full animate-spin"></div>
              </div>
              <div class="flex flex-col text-left">
                <span class="font-semibold text-sm">Unassign All</span>
                <span class="text-xs opacity-75">Remove from all</span>
              </div>
            </div>
            <div class="text-xs font-bold px-1.5 py-0.5 rounded-full bg-yellow-200 dark:bg-yellow-700 text-yellow-800 dark:text-yellow-200">
              {{ selectedEvents.length }}
            </div>
          </button>
        </div>
      </div>
    </div>
    
    
    <!-- Selected-Only Mode Indicator -->
    <div 
      v-if="showSelectedOnly" 
      class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-3 flex items-center justify-between"
    >
      <div class="flex items-center gap-3">
        <div class="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
          <span class="text-blue-600 dark:text-blue-400 text-xs font-bold">👁</span>
        </div>
        <div>
          <p class="text-sm font-medium text-blue-800 dark:text-blue-200">
            Showing only {{ selectedEvents.length }} selected event{{ selectedEvents.length > 1 ? 's' : '' }}
          </p>
          <p class="text-xs text-blue-600 dark:text-blue-400">
            Use filters above to return to normal view
          </p>
        </div>
      </div>
      <button
        @click="showSelectedOnly = false"
        class="px-3 py-1 bg-blue-100 hover:bg-blue-200 dark:bg-blue-800 dark:hover:bg-blue-700 text-blue-800 dark:text-blue-200 rounded-md text-xs font-medium transition-colors"
      >
        Show All Events
      </button>
    </div>
    
    <!-- Events Table -->
    <div class="space-y-4">
      <!-- Desktop: Horizontal Layout | Mobile: Vertical Stacked Layout -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        <!-- Search Bar -->
        <div class="flex-1 relative">
          <input
            v-model="eventSearch"
            type="text"
            :placeholder="activeGroupFilters.length > 0 ? 'Search in filtered groups...' : 'Search events...'"
            class="w-full px-4 py-3 sm:py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 text-base sm:text-sm"
          />
          
          <!-- Search Clear Button -->
          <button
            v-if="eventSearch.trim()"
            @click="eventSearch = ''; showSelectedOnly = false"
            class="absolute right-3 top-1/2 transform -translate-y-1/2 w-6 h-6 sm:w-5 sm:h-5 flex items-center justify-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            title="Clear search"
          >
            <span class="text-base sm:text-sm font-bold">×</span>
          </button>
        </div>
        
        <!-- Selection and Action Controls -->
        <div class="flex flex-col sm:flex-row gap-2 sm:gap-3">
          <!-- Main Selection Button with Event Counter -->
          <button
            @click="toggleSelectAllEvents"
            class="flex items-center justify-center gap-2 px-4 py-3 sm:px-4 sm:py-2 text-base sm:text-sm font-medium rounded-lg transition-all duration-200 border min-h-[44px] sm:min-h-0"
            :class="[
              isAllEventsSelected 
                ? 'bg-green-100 text-green-800 border-green-300 hover:bg-green-200 dark:bg-green-900/30 dark:text-green-200 dark:border-green-700 dark:hover:bg-green-800/30'
                : isSomeEventsSelected
                ? 'bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-700 dark:hover:bg-blue-800/30'
                : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600'
            ]"
            :title="isAllEventsSelected ? `Deselect all ${filteredEvents.length} visible events` : `Select all ${filteredEvents.length} visible events`"
          >
            <div 
              class="w-4 h-4 rounded border-2 flex items-center justify-center text-xs transition-all flex-shrink-0"
              :class="isAllEventsSelected
                ? 'bg-green-500 border-green-500 text-white' 
                : isSomeEventsSelected
                ? 'bg-blue-500 border-blue-500 text-white'
                : 'border-gray-400 bg-white dark:bg-gray-700 dark:border-gray-500'"
            >
              <span v-if="isAllEventsSelected">✓</span>
              <span v-else-if="isSomeEventsSelected">−</span>
            </div>
            <!-- Desktop: Include count in button -->
            <span v-if="isAllEventsSelected" class="hidden sm:inline">All {{ filteredEvents.length }} Selected</span>
            <span v-else-if="isSomeEventsSelected" class="hidden sm:inline">{{ selectedEvents.length }}/{{ filteredEvents.length }} Selected</span>
            <span v-else class="hidden sm:inline">Select {{ filteredEvents.length }} Visible</span>
            <!-- Mobile: Also include count -->
            <span v-if="isAllEventsSelected" class="sm:hidden">All {{ filteredEvents.length }} Selected</span>
            <span v-else-if="isSomeEventsSelected" class="sm:hidden">{{ selectedEvents.length }}/{{ filteredEvents.length }} Selected</span>
            <span v-else class="sm:hidden">Select {{ filteredEvents.length }} Visible</span>
          </button>
          
          <!-- Action Buttons -->
          <button
            @click="clearEventSelection"
            :disabled="selectedEvents.length === 0"
            class="px-4 py-3 sm:px-3 sm:py-2 text-base sm:text-xs font-medium rounded-lg sm:rounded-md transition-all duration-200 border border-gray-300 text-gray-600 hover:bg-gray-100 hover:text-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-200 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] sm:min-h-0"
            :title="selectedEvents.length === 0 ? 'No events selected' : `Clear selection of ${selectedEvents.length} events`"
          >
            Clear Selection
          </button>
          <button
            v-if="hasHiddenSelectedEvents || showSelectedOnly"
            @click="showAllSelectedEvents"
            :disabled="selectedEvents.length === 0"
            :class="[
              'px-4 py-3 sm:px-3 sm:py-2 text-base sm:text-xs font-medium rounded-lg sm:rounded-md transition-all duration-200 border min-h-[44px] sm:min-h-0',
              hasHiddenSelectedEvents
                ? 'bg-amber-100 hover:bg-amber-200 border-amber-300 text-amber-800 dark:bg-amber-900/30 dark:hover:bg-amber-800/50 dark:border-amber-600 dark:text-amber-200'
                : 'bg-blue-100 hover:bg-blue-200 border-blue-300 text-blue-800 dark:bg-blue-900/30 dark:hover:bg-blue-800/50 dark:border-blue-600 dark:text-blue-200'
            ]"
            :title="hasHiddenSelectedEvents ? 'Some selected events are hidden by filters' : 'View only your selected events'"
          >
            <span class="mr-2 sm:mr-1">{{ hasHiddenSelectedEvents ? '⚠️' : '👁' }}</span>
            Show Only Selected
          </button>
        </div>
      </div>
      
      <!-- Events Card Grid -->
      <div 
        class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 relative"
        @mousedown="startDragSelection"
        @mousemove="updateDragSelection"
        @mouseup="endDragSelection"
        @mouseleave="endDragSelection"
      >
        <!-- Drag Selection Overlay -->
        <div
          v-if="dragSelection.dragging"
          class="absolute pointer-events-none bg-gradient-to-br from-blue-300 to-blue-400 dark:from-blue-500 dark:to-blue-600 opacity-30 border-2 border-blue-500 dark:border-blue-400 rounded-lg shadow-lg backdrop-blur-sm"
          :style="{
            left: Math.min(dragSelection.startX, dragSelection.currentX) + 'px',
            top: Math.min(dragSelection.startY, dragSelection.currentY) + 'px',
            width: Math.abs(dragSelection.currentX - dragSelection.startX) + 'px',
            height: Math.abs(dragSelection.currentY - dragSelection.startY) + 'px',
            zIndex: 10
          }"
        >
          <div class="absolute inset-0 bg-white dark:bg-gray-900 opacity-10 rounded-lg"></div>
        </div>
        
        <div class="grid gap-2" :class="{
          'grid-cols-1': filteredEvents.length === 1,
          'grid-cols-1 sm:grid-cols-2': filteredEvents.length === 2,
          'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': filteredEvents.length >= 3 && filteredEvents.length <= 6,
          'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4': filteredEvents.length > 6
        }">
            <!-- Event Cards -->
            <div
              v-for="event in filteredEvents"
              :key="event.title"
              :ref="el => { if (el) cardRefs[event.title] = el }"
              data-event-card
              @click="handleEventCardClick(event.title, $event)"
              @contextmenu.prevent="showEventContextMenu(event, $event)"
              :class="[
                'relative border rounded-lg p-3 cursor-pointer transition-all duration-200 hover:shadow-md',
                selectedEvents.includes(event.title) 
                  ? 'border-blue-300 bg-blue-50 dark:border-blue-600 dark:bg-blue-900/20 shadow-md' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 bg-white dark:bg-gray-800'
              ]"
            >
              <!-- Selection Checkbox -->
              <div class="absolute top-2 right-2">
                <input
                  type="checkbox"
                  :checked="selectedEvents.includes(event.title)"
                  @change="toggleEventSelection(event.title)"
                  @click.stop
                  class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <!-- Event Title with Count -->
              <div class="pr-6 mb-2">
                <div class="flex items-start gap-2">
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 flex-shrink-0">
                    {{ event.event_count }}
                  </span>
                  <h3 class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-5 min-w-0">
                    {{ event.title }}
                  </h3>
                </div>
              </div>
              
              <!-- Group Assignment -->
              <div class="space-y-1">
                
                <!-- Multi-Group Display -->
                <div v-if="event.assigned_groups && event.assigned_groups.length > 0" class="flex flex-wrap gap-1">
                  <!-- Primary Group Badge -->
                  <span :class="`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getGroupColorClasses(event.assigned_groups[0].id)}`">
                    {{ event.assigned_groups[0].name }}
                  </span>
                  <!-- Additional Groups (max 2 more shown) -->
                  <span 
                    v-for="group in event.assigned_groups.slice(1, 2)" 
                    :key="group.id"
                    :class="`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${getGroupColorClasses(group.id)}`"
                  >
                    {{ group.name }}
                  </span>
                  <!-- Overflow Indicator with Popover -->
                  <div 
                    v-if="event.assigned_groups.length > 2"
                    class="relative inline-block"
                  >
                    <span 
                      @click="toggleGroupPopover(event.title)"
                      @click.stop
                      class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                      :title="'Click to see all groups'"
                    >
                      +{{ event.assigned_groups.length - 2 }}
                    </span>
                    <!-- Groups Popover -->
                    <div 
                      v-if="groupPopover.visible && groupPopover.eventTitle === event.title"
                      class="absolute top-full left-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 min-w-48 z-50"
                      @click.stop
                    >
                      <div class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">All Groups:</div>
                      <div class="space-y-1">
                        <div 
                          v-for="group in event.assigned_groups"
                          :key="group.id"
                          :class="`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium mr-1 mb-1 ${getGroupColorClasses(group.id)}`"
                        >
                          {{ group.name }}
                          <span v-if="group === event.assigned_groups[0]" class="text-xs opacity-75">(primary)</span>
                        </div>
                      </div>
                      <button 
                        @click="closeGroupPopover" 
                        class="mt-2 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                </div>
                <!-- Unassigned State -->
                <span v-else class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200">
                  ❔ Unassigned
                </span>
              </div>
          </div>
        </div>
      </div>
      
      <div v-if="filteredEvents.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        <div class="text-4xl mb-2">📅</div>
        <p>No events found matching your criteria</p>
      </div>
    </div>
  </AdminCardWrapper>
  
  <!-- Delete Group Confirmation Dialog -->
  <ConfirmDialog
    ref="deleteConfirmDialog"
    title="Delete Group"
    :message="deleteConfirmMessage"
    confirm-text="Delete Group"
    cancel-text="Cancel"
    @confirm="confirmDeleteGroup"
    @cancel="cancelDeleteGroup"
  />
</template>

<script>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import AdminCardWrapper from './AdminCardWrapper.vue'
import ConfirmDialog from '../shared/ConfirmDialog.vue'

export default {
  name: 'EventManagementCard',
  components: {
    AdminCardWrapper,
    ConfirmDialog
  },
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    recurringEvents: {
      type: Array,
      default: () => []
    },
    groups: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'toggle', 'create-group', 'update-group', 'delete-group', 'handle-group-assignment',
    'toggle-group-filter', 'toggle-select-all-events', 'toggle-event-selection',
    'clear-event-selection', 'remove-from-group'
  ],
  setup(props, { emit }) {
    // Local state
    const eventSearch = ref('')
    const selectedEvents = ref([])
    const activeGroupFilters = ref([])
    const showSelectedOnly = ref(false)
    const newGroupName = ref('')
    const showAddGroupForm = ref(false)
    const editingGroupId = ref(null)
    const editingGroupName = ref('')
    const newGroupInput = ref(null)
    const contextMenu = ref({ visible: false, x: 0, y: 0, group: null })
    const eventContextMenu = ref({ visible: false, x: 0, y: 0, event: null })
    
    // Drag selection state (simplified - no complex visibility management needed)
    const dragSelection = ref({
      dragging: false,
      startX: 0,
      startY: 0,
      currentX: 0,
      currentY: 0,
      initialSelection: [],
      containerRect: null
    })
    const deleteConfirmDialog = ref(null)
    const deleteConfirmMessage = ref('')
    const groupToDelete = ref(null)
    const groupPopover = ref({ visible: false, eventTitle: null })
    
    // Loading and visual feedback state
    const isUpdatingGroups = ref(false)
    const updatingGroupIds = ref(new Set())
    const optimisticUpdates = ref(new Map()) // Track pending updates
    
    // Card refs for drag selection
    const cardRefs = ref({})
    
    // Clear selection when search text changes (simplifies UX)
    watch(eventSearch, (newSearch, oldSearch) => {
      if (newSearch !== oldSearch && selectedEvents.value.length > 0) {
        selectedEvents.value = []
        emit('clear-event-selection')
        showSelectedOnly.value = false
      }
    })
    
    // Global escape handler for drag selection cleanup
    onMounted(() => {
      const handleEscape = (event) => {
        if (event.key === 'Escape' && dragSelection.value.dragging) {
          endDragSelection()
        }
      }
      
      // Global cleanup for drag state
      const handleBeforeUnload = () => {
        dragSelection.value.dragging = false
      }
      
      document.addEventListener('keydown', handleEscape)
      window.addEventListener('beforeunload', handleBeforeUnload)
      
      // Cleanup listeners on unmount
      onUnmounted(() => {
        document.removeEventListener('keydown', handleEscape)
        window.removeEventListener('beforeunload', handleBeforeUnload)
        // Reset drag state if component unmounts during drag
        dragSelection.value.dragging = false
      })
    })
    
    // Computed properties
    const totalEventCount = computed(() => {
      return props.recurringEvents
        .reduce((total, event) => total + (event.event_count || 1), 0)
    })
    
    const assignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.length > 0
      }).length
    })
    
    const unassignedEventsCount = computed(() => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.length === 0
      }).length
    })
    
    const filteredEvents = computed(() => {
      let filtered = props.recurringEvents
      
      // If showing selected only, filter to just selected events
      if (showSelectedOnly.value) {
        filtered = filtered.filter(event => selectedEvents.value.includes(event.title))
        // Skip other filters when showing selected only - go directly to grouping
      } else {
      
      // Apply group filters (support multi-group assignments)
      if (activeGroupFilters.value.length > 0) {
        filtered = filtered.filter(event => {
          // Handle unassigned filter
          if (activeGroupFilters.value.includes('unassigned') && (!event.assigned_group_ids || event.assigned_group_ids.length === 0)) {
            return true
          }
          
          // Handle group filters - check if event belongs to any of the active filter groups
          const eventGroupIds = event.assigned_group_ids || []
          return eventGroupIds.some(groupId => activeGroupFilters.value.includes(groupId))
        })
      }
      
      // Apply search filter
      if (eventSearch.value.trim()) {
        const search = eventSearch.value.toLowerCase().trim()
        filtered = filtered.filter(event => 
          event.title.toLowerCase().includes(search) ||
          (event.description || '').toLowerCase().includes(search)
        )
      }
      } // End of else block for normal filtering
      
      // Group by title and preserve API event_count, also compute group information
      const eventsByTitle = {}
      filtered.forEach(event => {
        if (!eventsByTitle[event.title]) {
          // Handle multi-group assignments from API
          const assignedGroupIds = event.assigned_group_ids || []
          const assignedGroups = assignedGroupIds.map(groupId => 
            props.groups.find(g => g.id === groupId)
          ).filter(Boolean) // Remove null/undefined results
          
          eventsByTitle[event.title] = {
            ...event,
            // Keep the original event_count from API instead of resetting to 0
            group_id: event.assigned_group_id, // Map for backward compatibility  
            group_name: assignedGroups[0]?.name || null, // Primary group for backward compatibility
            // Multi-group support
            assigned_group_ids: assignedGroupIds,
            assigned_groups: assignedGroups
          }
        }
        // Don't increment event_count since API already provides the correct value
      })
      
      return Object.values(eventsByTitle)
    })
    
    const isAllEventsSelected = computed(() => {
      return filteredEvents.value.length > 0 && 
             filteredEvents.value.every(event => selectedEvents.value.includes(event.title))
    })
    
    const isSomeEventsSelected = computed(() => {
      return selectedEvents.value.length > 0 && selectedEvents.value.length < filteredEvents.value.length
    })
    
    // Selection group distribution for smart filter buttons
    const selectedEventsGroupDistribution = computed(() => {
      const distribution = {}
      
      selectedEvents.value.forEach(eventTitle => {
        const event = props.recurringEvents.find(e => e.title === eventTitle)
        if (event) {
          const eventGroupIds = event.assigned_group_ids || []
          
          if (eventGroupIds.length === 0) {
            // Unassigned event
            distribution['unassigned'] = (distribution['unassigned'] || 0) + 1
          } else {
            // Event with group assignments
            eventGroupIds.forEach(groupId => {
              distribution[groupId] = (distribution[groupId] || 0) + 1
            })
          }
        }
      })
      
      return distribution
    })
    
    // Detection of hidden selected events
    const hiddenSelectedEvents = computed(() => {
      return selectedEvents.value.filter(eventTitle => {
        return !filteredEvents.value.some(event => event.title === eventTitle)
      })
    })
    
    const hasHiddenSelectedEvents = computed(() => {
      return hiddenSelectedEvents.value.length > 0
    })
    
    const visibleSelectedEvents = computed(() => {
      return selectedEvents.value.filter(eventTitle => {
        return filteredEvents.value.some(event => event.title === eventTitle)
      })
    })
    
    const getSelectedEventsInGroup = (groupId) => {
      return selectedEventsGroupDistribution.value[groupId] || 0
    }
    
    // Smart group action button logic
    const getGroupActionState = (groupId) => {
      const eventsInGroup = getSelectedEventsInGroup(groupId)
      const eventsNotInGroup = selectedEvents.value.length - eventsInGroup
      const totalSelected = selectedEvents.value.length
      
      return {
        eventsInGroup,
        eventsNotInGroup,
        totalSelected,
        hasEventsInGroup: eventsInGroup > 0,
        hasEventsNotInGroup: eventsNotInGroup > 0,
        allInGroup: eventsInGroup === totalSelected && totalSelected > 0,
        noneInGroup: eventsInGroup === 0,
        mixedState: eventsInGroup > 0 && eventsNotInGroup > 0
      }
    }
    
    const getSmartGroupAction = (groupId) => {
      const state = getGroupActionState(groupId)
      
      if (state.noneInGroup) {
        // All events are NOT in this group - primary action is ADD
        return {
          type: 'single',
          primaryAction: 'add',
          primaryLabel: `+ Add ${state.totalSelected} to`,
          primaryCount: state.eventsNotInGroup,
          primaryStyle: 'add'
        }
      } else if (state.allInGroup) {
        // All events are IN this group - primary action is REMOVE
        return {
          type: 'single',
          primaryAction: 'remove',
          primaryLabel: `− Remove ${state.totalSelected} from`,
          primaryCount: state.eventsInGroup,
          primaryStyle: 'remove'
        }
      } else {
        // Mixed state - show both actions, prioritize the larger action
        const addIsPrimary = state.eventsNotInGroup >= state.eventsInGroup
        
        return {
          type: 'split',
          primaryAction: addIsPrimary ? 'add' : 'remove',
          primaryLabel: addIsPrimary ? `+ Add ${state.eventsNotInGroup} to` : `− Remove ${state.eventsInGroup} from`,
          primaryCount: addIsPrimary ? state.eventsNotInGroup : state.eventsInGroup,
          primaryStyle: addIsPrimary ? 'add' : 'remove',
          secondaryAction: addIsPrimary ? 'remove' : 'add',
          secondaryLabel: addIsPrimary ? `− ${state.eventsInGroup}` : `+ ${state.eventsNotInGroup}`,
          secondaryCount: addIsPrimary ? state.eventsInGroup : state.eventsNotInGroup,
          secondaryStyle: addIsPrimary ? 'remove' : 'add'
        }
      }
    }
    
    // Methods - Filter mode (clear separation from assignment)
    const toggleGroupFilter = (groupId, event) => {
      const isCtrlClick = event.ctrlKey || event.metaKey
      emit('toggle-group-filter', groupId, isCtrlClick, activeGroupFilters.value)
      
      // Clear search text when switching to group filters
      eventSearch.value = ''
      
      // Clear selection when changing filters (simplifies UX and button logic)
      selectedEvents.value = []
      emit('clear-event-selection')
      
      // Exit selected-only mode when using normal filters
      showSelectedOnly.value = false
      
      if (!isCtrlClick) {
        activeGroupFilters.value = groupId === 'all' ? [] : [groupId]
      } else {
        if (groupId === 'all') {
          activeGroupFilters.value = []
        } else {
          const index = activeGroupFilters.value.indexOf(groupId)
          if (index > -1) {
            activeGroupFilters.value.splice(index, 1)
          } else {
            activeGroupFilters.value.push(groupId)
          }
        }
      }
    }
    
    const toggleSelectAllEvents = () => {
      emit('toggle-select-all-events', isAllEventsSelected.value, filteredEvents.value.map(e => e.title))
      
      if (isAllEventsSelected.value) {
        selectedEvents.value = []
      } else {
        selectedEvents.value = filteredEvents.value.map(event => event.title)
      }
    }
    
    const toggleEventSelection = (eventTitle) => {
      emit('toggle-event-selection', eventTitle)
      
      const index = selectedEvents.value.indexOf(eventTitle)
      if (index > -1) {
        selectedEvents.value.splice(index, 1)
      } else {
        selectedEvents.value.push(eventTitle)
      }
    }
    
    const clearEventSelection = () => {
      emit('clear-event-selection')
      selectedEvents.value = []
      showSelectedOnly.value = false // Exit selected-only mode when clearing selection
    }
    
    const clearGroupFilters = () => {
      activeGroupFilters.value = []
    }
    
    const getGroupEventCount = (groupId) => {
      return props.recurringEvents.filter(event => {
        const eventGroupIds = event.assigned_group_ids || []
        return eventGroupIds.includes(groupId)
      }).length
    }
    
    const createGroup = async () => {
      if (!newGroupName.value.trim()) return
      
      emit('create-group', newGroupName.value.trim())
      newGroupName.value = ''
      showAddGroupForm.value = false
    }
    
    const cancelAddGroup = () => {
      newGroupName.value = ''
      showAddGroupForm.value = false
    }
    
    const handleAddGroupBlur = () => {
      // Small delay to allow click events on buttons to fire first
      setTimeout(() => {
        if (document.activeElement !== newGroupInput.value) {
          cancelAddGroup()
        }
      }, 150)
    }
    
    const startEditingGroup = async (group, event) => {
      if (event) event.preventDefault()
      editingGroupId.value = group.id
      editingGroupName.value = group.name
      
      await nextTick()
      // Focus the input after it's rendered
      const input = document.querySelector(`input[value="${group.name}"]`) || 
                    document.querySelector('input[class*="bg-transparent"]')
      if (input) {
        input.focus()
        input.select()
      }
    }
    
    const saveGroupEdit = async (groupId) => {
      if (!editingGroupName.value.trim()) {
        cancelGroupEdit()
        return
      }
      
      emit('update-group', groupId, editingGroupName.value.trim())
      editingGroupId.value = null
      editingGroupName.value = ''
    }
    
    const cancelGroupEdit = () => {
      editingGroupId.value = null
      editingGroupName.value = ''
    }
    
    const startAddGroup = async () => {
      showAddGroupForm.value = true
      await nextTick()
      // Focus the input after it's rendered
      if (newGroupInput.value) {
        newGroupInput.value.focus()
      }
    }
    
    const deleteGroupConfirm = (group) => {
      groupToDelete.value = group
      deleteConfirmMessage.value = `Are you sure you want to delete the group "${group.name}"? This will unassign all events from this group.`
      deleteConfirmDialog.value.open()
    }
    
    const confirmDeleteGroup = () => {
      if (groupToDelete.value) {
        emit('delete-group', groupToDelete.value.id)
        groupToDelete.value = null
      }
    }
    
    const cancelDeleteGroup = () => {
      groupToDelete.value = null
    }
    
    const showContextMenu = (group, event) => {
      contextMenu.value = {
        visible: true,
        x: event.clientX,
        y: event.clientY,
        group: group
      }
      
      // Close context menu when clicking elsewhere
      const closeMenu = () => {
        contextMenu.value.visible = false
        document.removeEventListener('click', closeMenu)
      }
      
      setTimeout(() => {
        document.addEventListener('click', closeMenu)
      }, 0)
    }
    
    const editGroupFromMenu = () => {
      startEditingGroup(contextMenu.value.group)
      contextMenu.value.visible = false
    }
    
    const deleteGroupFromMenu = () => {
      deleteGroupConfirm(contextMenu.value.group)
      contextMenu.value.visible = false
    }
    
    const toggleGroupPopover = (eventTitle) => {
      if (groupPopover.value.visible && groupPopover.value.eventTitle === eventTitle) {
        closeGroupPopover()
      } else {
        groupPopover.value = {
          visible: true,
          eventTitle: eventTitle
        }
        
        // Close popover when clicking elsewhere
        const closePopover = () => {
          closeGroupPopover()
          document.removeEventListener('click', closePopover)
        }
        
        setTimeout(() => {
          document.addEventListener('click', closePopover)
        }, 0)
      }
    }
    
    const closeGroupPopover = () => {
      groupPopover.value = { visible: false, eventTitle: null }
    }
    
    // Event context menu methods
    const showEventContextMenu = (event, mouseEvent) => {
      eventContextMenu.value = {
        visible: true,
        x: mouseEvent.clientX,
        y: mouseEvent.clientY,
        event: event
      }
      
      // Close context menu when clicking elsewhere
      const closeMenu = () => {
        eventContextMenu.value.visible = false
        document.removeEventListener('click', closeMenu)
      }
      
      setTimeout(() => {
        document.addEventListener('click', closeMenu)
      }, 0)
    }
    
    const getAvailableGroupsForEvent = (event) => {
      if (!event) return []
      const assignedGroupIds = event.assigned_group_ids || []
      return props.groups.filter(group => !assignedGroupIds.includes(group.id))
    }
    
    const getAssignedGroupsForEvent = (event) => {
      if (!event) return []
      const assignedGroupIds = event.assigned_group_ids || []
      return props.groups.filter(group => assignedGroupIds.includes(group.id))
    }

    // Helper function to determine context menu width based on total number of groups
    const getContextMenuWidthClass = () => {
      if (!eventContextMenu.value.event) return 'w-72'
      
      const availableGroups = getAvailableGroupsForEvent(eventContextMenu.value.event)
      const assignedGroups = getAssignedGroupsForEvent(eventContextMenu.value.event)
      const totalGroups = availableGroups.length + assignedGroups.length
      
      // Dynamic width based on total groups to accommodate columns
      if (totalGroups <= 6) return 'w-72'        // 1 column, standard width
      if (totalGroups <= 12) return 'w-96'       // 2 columns, wider
      if (totalGroups <= 18) return 'w-[32rem]'  // 3 columns, much wider  
      return 'w-[40rem]'                          // 4+ columns, extra wide
    }

    // Helper function to determine grid layout for groups based on count
    const getGroupGridClass = (groupCount) => {
      if (groupCount <= 6) return 'grid grid-cols-1 gap-1 px-2'
      if (groupCount <= 12) return 'grid grid-cols-2 gap-1 px-2' 
      if (groupCount <= 18) return 'grid grid-cols-3 gap-1 px-2'
      return 'grid grid-cols-4 gap-1 px-2'
    }

    // Color palette for consistent group coloring
    const groupColorPalette = [
      // Primary colors with good contrast
      { bg: 'bg-green-100', text: 'text-green-800', darkBg: 'dark:bg-green-900/30', darkText: 'dark:text-green-200' },
      { bg: 'bg-blue-100', text: 'text-blue-800', darkBg: 'dark:bg-blue-900/30', darkText: 'dark:text-blue-200' },
      { bg: 'bg-purple-100', text: 'text-purple-800', darkBg: 'dark:bg-purple-900/30', darkText: 'dark:text-purple-200' },
      { bg: 'bg-amber-100', text: 'text-amber-800', darkBg: 'dark:bg-amber-900/30', darkText: 'dark:text-amber-200' },
      { bg: 'bg-rose-100', text: 'text-rose-800', darkBg: 'dark:bg-rose-900/30', darkText: 'dark:text-rose-200' },
      { bg: 'bg-teal-100', text: 'text-teal-800', darkBg: 'dark:bg-teal-900/30', darkText: 'dark:text-teal-200' },
      { bg: 'bg-orange-100', text: 'text-orange-800', darkBg: 'dark:bg-orange-900/30', darkText: 'dark:text-orange-200' },
      { bg: 'bg-indigo-100', text: 'text-indigo-800', darkBg: 'dark:bg-indigo-900/30', darkText: 'dark:text-indigo-200' },
      { bg: 'bg-emerald-100', text: 'text-emerald-800', darkBg: 'dark:bg-emerald-900/30', darkText: 'dark:text-emerald-200' },
      { bg: 'bg-cyan-100', text: 'text-cyan-800', darkBg: 'dark:bg-cyan-900/30', darkText: 'dark:text-cyan-200' },
      { bg: 'bg-pink-100', text: 'text-pink-800', darkBg: 'dark:bg-pink-900/30', darkText: 'dark:text-pink-200' },
      { bg: 'bg-lime-100', text: 'text-lime-800', darkBg: 'dark:bg-lime-900/30', darkText: 'dark:text-lime-200' }
    ]

    // Helper function to get consistent colors for a group
    const getGroupColors = (groupId) => {
      // Find the group's position in the sorted groups list for consistency
      const sortedGroups = [...props.groups].sort((a, b) => a.id - b.id)
      const groupIndex = sortedGroups.findIndex(g => g.id === groupId)
      const colorIndex = groupIndex >= 0 ? groupIndex % groupColorPalette.length : 0
      return groupColorPalette[colorIndex]
    }

    // Helper function to get group color classes as a single string
    const getGroupColorClasses = (groupId) => {
      const colors = getGroupColors(groupId)
      return `${colors.bg} ${colors.text} ${colors.darkBg} ${colors.darkText}`
    }
    
    const quickAddToGroup = async (event, groupId) => {
      eventContextMenu.value.visible = false
      
      try {
        // Use existing group assignment logic
        emit('handle-group-assignment', groupId, [event.title])
        
        // Optimistic update
        const eventToUpdate = props.recurringEvents.find(e => e.title === event.title)
        if (eventToUpdate && !eventToUpdate.assigned_group_ids?.includes(parseInt(groupId))) {
          eventToUpdate.assigned_group_ids = [...(eventToUpdate.assigned_group_ids || []), parseInt(groupId)]
        }
      } catch (error) {
        console.error('Failed to add event to group:', error)
      }
    }
    
    const quickRemoveFromGroup = async (event, groupId) => {
      eventContextMenu.value.visible = false
      
      try {
        // Use existing remove from group logic
        emit('remove-from-group', groupId, [event.title])
        
        // Optimistic update
        const eventToUpdate = props.recurringEvents.find(e => e.title === event.title)
        if (eventToUpdate && eventToUpdate.assigned_group_ids?.includes(parseInt(groupId))) {
          eventToUpdate.assigned_group_ids = eventToUpdate.assigned_group_ids.filter(id => id !== parseInt(groupId))
        }
      } catch (error) {
        console.error('Failed to remove event from group:', error)
      }
    }
    
    // Drag selection utilities (no scroll locking needed anymore)

    // Drag selection methods
    const startDragSelection = (event) => {
      // Only start drag selection on left mouse button
      if (event.button !== 0) return
      
      const containerRect = event.currentTarget.getBoundingClientRect()
      dragSelection.value = {
        dragging: true,
        startX: event.clientX - containerRect.left,
        startY: event.clientY - containerRect.top,
        currentX: event.clientX - containerRect.left,
        currentY: event.clientY - containerRect.top,
        initialSelection: [...selectedEvents.value],
        containerRect: containerRect,
        scrollTop: undefined,
        scrollLeft: undefined
      }
      
      // No need for scroll locking with always-visible panel
      
      event.preventDefault()
      event.stopPropagation()
    }
    
    const updateDragSelection = (event) => {
      if (!dragSelection.value.dragging) return
      
      // Use stored container rect for stable coordinates
      const containerRect = dragSelection.value.containerRect
      dragSelection.value.currentX = event.clientX - containerRect.left
      dragSelection.value.currentY = event.clientY - containerRect.top
      
      event.preventDefault()
      event.stopPropagation()
      
      // Calculate which cards intersect with selection rectangle
      const selectionRect = {
        left: Math.min(dragSelection.value.startX, dragSelection.value.currentX),
        top: Math.min(dragSelection.value.startY, dragSelection.value.currentY),
        right: Math.max(dragSelection.value.startX, dragSelection.value.currentX),
        bottom: Math.max(dragSelection.value.startY, dragSelection.value.currentY)
      }
      
      const newSelection = [...dragSelection.value.initialSelection]
      
      filteredEvents.value.forEach(event => {
        const cardElement = cardRefs.value[event.title]
        if (cardElement) {
          const cardRect = cardElement.getBoundingClientRect()
          const containerRect = cardElement.closest('.grid').getBoundingClientRect()
          
          const cardRelativeRect = {
            left: cardRect.left - containerRect.left,
            top: cardRect.top - containerRect.top,
            right: cardRect.right - containerRect.left,
            bottom: cardRect.bottom - containerRect.top
          }
          
          // Check if card intersects with selection rectangle
          const intersects = !(cardRelativeRect.right < selectionRect.left || 
                             cardRelativeRect.left > selectionRect.right || 
                             cardRelativeRect.bottom < selectionRect.top || 
                             cardRelativeRect.top > selectionRect.bottom)
          
          if (intersects) {
            if (!newSelection.includes(event.title)) {
              newSelection.push(event.title)
            }
          }
        }
      })
      
      selectedEvents.value = newSelection
    }
    
    const endDragSelection = () => {
      if (!dragSelection.value.dragging) return
      
      // Check if this was just a click (minimal movement)
      const deltaX = Math.abs(dragSelection.value.currentX - dragSelection.value.startX)
      const deltaY = Math.abs(dragSelection.value.currentY - dragSelection.value.startY) 
      const wasClick = deltaX < 5 && deltaY < 5
      
      if (wasClick) {
        // Restore original selection for clicks
        selectedEvents.value = [...dragSelection.value.initialSelection]
        emit('clear-event-selection')
        dragSelection.value.initialSelection.forEach(eventTitle => {
          emit('toggle-event-selection', eventTitle)
        })
      } else {
        // For drags, emit the current selection
        emit('clear-event-selection')
        selectedEvents.value.forEach(title => emit('toggle-event-selection', title))
      }
      
      // Reset drag state
      dragSelection.value.dragging = false
    }
    
    const handleEventCardClick = (eventTitle, event) => {
      // If we're currently dragging, don't handle clicks
      if (dragSelection.value.dragging) {
        // No need to set hasDragged anymore
        return
      }
      toggleEventSelection(eventTitle)
    }
    
    // Assignment mode methods
    const handleRemoveFromGroup = async (groupId, eventTitles) => {
      // Get events that are currently in this specific group
      const eventsInGroup = eventTitles.filter(title => {
        const event = props.recurringEvents.find(e => e.title === title)
        return event && event.assigned_group_ids && event.assigned_group_ids.includes(parseInt(groupId))
      })
      
      if (eventsInGroup.length === 0) {
        return // No events to remove from this group
      }
      
      try {
        // We need to implement a "remove from specific group" API call
        // For now, we'll emit this and let the parent handle it
        emit('remove-from-group', groupId, eventsInGroup)
        // Keep selection for multi-group operations
      } catch (error) {
        console.error('Failed to remove events from group:', error)
      }
    }
    
    // Smart group action handlers
    const handleSmartGroupAction = async (groupId, action) => {
      const state = getGroupActionState(groupId)
      
      // Set loading state
      isUpdatingGroups.value = true
      updatingGroupIds.value.add(groupId)
      
      try {
        if (action === 'add') {
          // Add events that are NOT in this group
          const eventsToAdd = selectedEvents.value.filter(title => {
            const event = props.recurringEvents.find(e => e.title === title)
            return !event?.assigned_group_ids?.includes(parseInt(groupId))
          })
          
          if (eventsToAdd.length > 0) {
            // Optimistic update: immediately update local state
            updateEventsOptimistically(eventsToAdd, groupId, 'add')
            
            // Emit for actual API call
            emit('handle-group-assignment', groupId, eventsToAdd)
          }
        } else if (action === 'remove') {
          // Remove events that ARE in this group
          const eventsToRemove = selectedEvents.value.filter(title => {
            const event = props.recurringEvents.find(e => e.title === title)
            return event?.assigned_group_ids?.includes(parseInt(groupId))
          })
          
          if (eventsToRemove.length > 0) {
            // Optimistic update: immediately update local state
            updateEventsOptimistically(eventsToRemove, groupId, 'remove')
            
            // Emit for actual API call
            handleRemoveFromGroup(groupId, eventsToRemove)
          }
        }
        
        // Keep selection for multi-group assignments, just clear loading state
        setTimeout(() => {
          isUpdatingGroups.value = false
          updatingGroupIds.value.delete(groupId)
        }, 300) // Small delay for smooth UX
        
      } catch (error) {
        console.error('Group assignment error:', error)
        // Revert optimistic updates on error
        revertOptimisticUpdates()
        isUpdatingGroups.value = false
        updatingGroupIds.value.delete(groupId)
      }
    }
    
    const showAllSelectedEvents = () => {
      // Enable selected-only mode to show ONLY the selected events
      showSelectedOnly.value = true
      activeGroupFilters.value = []
      eventSearch.value = ''
    }
    
    // Helper functions for optimistic updates
    const updateEventsOptimistically = (eventTitles, groupId, action) => {
      const groupIdInt = parseInt(groupId)
      
      eventTitles.forEach(title => {
        const event = props.recurringEvents.find(e => e.title === title)
        if (event) {
          // Store original state for potential revert
          if (!optimisticUpdates.value.has(title)) {
            optimisticUpdates.value.set(title, [...(event.assigned_group_ids || [])])
          }
          
          // Apply optimistic update
          if (action === 'add' && !event.assigned_group_ids?.includes(groupIdInt)) {
            event.assigned_group_ids = [...(event.assigned_group_ids || []), groupIdInt]
          } else if (action === 'remove' && event.assigned_group_ids?.includes(groupIdInt)) {
            event.assigned_group_ids = event.assigned_group_ids.filter(id => id !== groupIdInt)
          }
        }
      })
    }
    
    const revertOptimisticUpdates = () => {
      optimisticUpdates.value.forEach((originalGroupIds, eventTitle) => {
        const event = props.recurringEvents.find(e => e.title === eventTitle)
        if (event) {
          event.assigned_group_ids = originalGroupIds
        }
      })
      optimisticUpdates.value.clear()
    }
    
    const confirmOptimisticUpdates = () => {
      // Called when API confirms the updates were successful
      optimisticUpdates.value.clear()
    }
    
    const isGroupUpdating = (groupId) => {
      return updatingGroupIds.value.has(groupId)
    }
    
    const handleUnassignAll = async () => {
      isUpdatingGroups.value = true
      
      try {
        // Optimistic update: remove all selected events from all groups
        selectedEvents.value.forEach(title => {
          const event = props.recurringEvents.find(e => e.title === title)
          if (event) {
            if (!optimisticUpdates.value.has(title)) {
              optimisticUpdates.value.set(title, [...(event.assigned_group_ids || [])])
            }
            event.assigned_group_ids = []
          }
        })
        
        // Emit for actual API call
        emit('handle-group-assignment', 'unassigned', [...selectedEvents.value])
        
        // Keep selection for potential reassignment, just clear loading state
        setTimeout(() => {
          isUpdatingGroups.value = false
        }, 300)
        
      } catch (error) {
        console.error('Unassign all error:', error)
        revertOptimisticUpdates()
        isUpdatingGroups.value = false
      }
    }
    
    return {
      // State
      eventSearch,
      selectedEvents,
      activeGroupFilters,
      showSelectedOnly,
      newGroupName,
      showAddGroupForm,
      editingGroupId,
      editingGroupName,
      newGroupInput,
      contextMenu,
      eventContextMenu,
      deleteConfirmDialog,
      deleteConfirmMessage,
      groupToDelete,
      groupPopover,
      isUpdatingGroups,
      updatingGroupIds,
      dragSelection,
      cardRefs,
      
      // Computed
      totalEventCount,
      assignedEventsCount,
      unassignedEventsCount,
      filteredEvents,
      isAllEventsSelected,
      isSomeEventsSelected,
      selectedEventsGroupDistribution,
      hiddenSelectedEvents,
      hasHiddenSelectedEvents,
      visibleSelectedEvents,
      
      // Methods
      toggleGroupFilter,
      toggleSelectAllEvents,
      toggleEventSelection,
      clearEventSelection,
      showAllSelectedEvents,
      getGroupEventCount,
      getSelectedEventsInGroup,
      getGroupActionState,
      getSmartGroupAction,
      handleSmartGroupAction,
      createGroup,
      cancelAddGroup,
      handleAddGroupBlur,
      startAddGroup,
      startEditingGroup,
      saveGroupEdit,
      cancelGroupEdit,
      deleteGroupConfirm,
      confirmDeleteGroup,
      cancelDeleteGroup,
      showContextMenu,
      editGroupFromMenu,
      deleteGroupFromMenu,
      toggleGroupPopover,
      closeGroupPopover,
      showEventContextMenu,
      getAvailableGroupsForEvent,
      getAssignedGroupsForEvent,
      getContextMenuWidthClass,
      getGroupGridClass,
      getGroupColors,
      getGroupColorClasses,
      quickAddToGroup,
      quickRemoveFromGroup,
      startDragSelection,
      updateDragSelection,
      endDragSelection,
      handleEventCardClick,
      handleRemoveFromGroup,
      isGroupUpdating,
      handleUnassignAll,
      confirmOptimisticUpdates,
      revertOptimisticUpdates
    }
  }
}
</script>

<style scoped>
/* Custom checkbox indeterminate styling */
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

/* Text truncation utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>