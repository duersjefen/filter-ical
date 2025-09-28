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
        <h3 class="text-base sm:text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('admin.filterByGroup') }}</h3>
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
          <span>{{ t('admin.allEvents') }}</span>
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
          <span>{{ t('admin.unassigned') }}</span>
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
            :placeholder="t('admin.groupNamePlaceholder')"
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
        <span>{{ t('admin.deleteGroup') }}</span>
      </button>
    </div>
    
    <!-- Event Context Menu -->
    <div
      v-if="eventContextMenu.visible"
      :style="getContextMenuPosition()"
      :class="[
        'bg-white/98 dark:bg-gray-900/98 border border-gray-200/60 dark:border-gray-700/60 rounded-2xl shadow-[0_20px_25px_-5px_rgb(0_0_0_/_0.1),_0_10px_10px_-5px_rgb(0_0_0_/_0.04)] dark:shadow-[0_20px_25px_-5px_rgb(0_0_0_/_0.4),_0_10px_10px_-5px_rgb(0_0_0_/_0.2)] backdrop-blur-xl overflow-hidden transform transition-all duration-200 scale-100 opacity-100 ring-1 ring-black/5 dark:ring-white/10',
        getContextMenuWidthClass()
      ]"
      @click.stop
    >
      <!-- Context Menu Header - Enhanced -->
      <div class="px-4 py-3 border-b border-gray-100/70 dark:border-gray-700/70 bg-gradient-to-r from-indigo-50/90 via-blue-50/90 to-cyan-50/90 dark:from-indigo-900/30 dark:via-blue-900/30 dark:to-cyan-900/30 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/5 via-blue-500/5 to-cyan-500/5 dark:from-indigo-400/10 dark:via-blue-400/10 dark:to-cyan-400/10"></div>
        <div class="relative flex items-center gap-3">
          <div class="relative">
            <div class="w-2.5 h-2.5 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full shadow-sm"></div>
            <div class="absolute inset-0 w-2.5 h-2.5 bg-blue-400 rounded-full animate-ping opacity-30"></div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-bold text-gray-900 dark:text-gray-100 truncate tracking-tight">{{ eventContextMenu.event?.title || 'Event Actions' }}</div>
          </div>
          <div class="w-1 h-1 bg-gray-300 dark:bg-gray-600 rounded-full opacity-60"></div>
        </div>
      </div>

      <!-- Actions Container - Enhanced Side by Side Layout -->
      <div v-if="getAvailableGroupsForEvent(eventContextMenu.event).length > 0 || getAssignedGroupsForEvent(eventContextMenu.event).length > 0" 
           class="flex divide-x divide-gray-100/80 dark:divide-gray-700/80 bg-gradient-to-r from-gray-50/30 to-gray-100/30 dark:from-gray-800/30 dark:to-gray-700/30">
        
        <!-- Add to Groups Section (Left Side) -->
        <div v-if="getAvailableGroupsForEvent(eventContextMenu.event).length > 0" 
             class="flex-1 p-3 relative">
          <div class="relative flex items-center gap-2 mb-2">
            <span class="text-xs font-bold text-green-700 dark:text-green-300 uppercase tracking-wide">Add to Group</span>
            <div class="flex-1 h-px bg-gradient-to-r from-green-200 to-transparent dark:from-green-700/50"></div>
          </div>
          
          <!-- Groups in responsive grid with proper spacing -->
          <div class="grid gap-2" :class="{
            'grid-cols-1': getAvailableGroupsForEvent(eventContextMenu.event).length <= 3,
            'grid-cols-2': getAvailableGroupsForEvent(eventContextMenu.event).length > 3 && getAvailableGroupsForEvent(eventContextMenu.event).length <= 8,
            'grid-cols-3': getAvailableGroupsForEvent(eventContextMenu.event).length > 8
          }">
            <button
              v-for="group in getAvailableGroupsForEvent(eventContextMenu.event)"
              :key="`add-${group.id}`"
              @click="quickAddToGroup(eventContextMenu.event, group.id)"
              class="group/btn w-full px-3 py-2 text-xs text-gray-700 dark:text-gray-300 bg-gradient-to-r from-green-50/80 to-emerald-50/80 dark:from-green-900/20 dark:to-emerald-900/20 hover:from-green-100 hover:to-emerald-100 dark:hover:from-green-800/40 dark:hover:to-emerald-800/40 transition-all duration-200 rounded-lg border-l-4 border-green-500 hover:border-green-600 hover:shadow-md hover:shadow-green-100/50 dark:hover:shadow-green-900/20 transform hover:scale-[1.01] active:scale-[0.99] min-h-[2rem] cursor-pointer text-center font-medium hover:text-green-800 dark:hover:text-green-200"
              :title="`Add event to ${group.name}`"
            >
              {{ group.name }}
            </button>
          </div>
        </div>
        
        <!-- Remove from Groups Section (Right Side) -->
        <div v-if="getAssignedGroupsForEvent(eventContextMenu.event).length > 0" 
             class="flex-1 p-3 relative">
          <div class="relative flex items-center gap-2 mb-2">
            <span class="text-xs font-bold text-red-700 dark:text-red-300 uppercase tracking-wide">Remove from Group</span>
            <div class="flex-1 h-px bg-gradient-to-r from-red-200 to-transparent dark:from-red-700/50"></div>
          </div>
          
          <!-- Groups in responsive grid with proper spacing -->
          <div class="grid gap-2" :class="{
            'grid-cols-1': getAssignedGroupsForEvent(eventContextMenu.event).length <= 3,
            'grid-cols-2': getAssignedGroupsForEvent(eventContextMenu.event).length > 3 && getAssignedGroupsForEvent(eventContextMenu.event).length <= 8,
            'grid-cols-3': getAssignedGroupsForEvent(eventContextMenu.event).length > 8
          }">
            <button
              v-for="group in getAssignedGroupsForEvent(eventContextMenu.event)"
              :key="`remove-${group.id}`"
              @click="quickRemoveFromGroup(eventContextMenu.event, group.id)"
              class="group/btn w-full px-3 py-2 text-xs text-gray-700 dark:text-gray-300 bg-gradient-to-r from-red-50/80 to-rose-50/80 dark:from-red-900/20 dark:to-rose-900/20 hover:from-red-100 hover:to-rose-100 dark:hover:from-red-800/40 dark:hover:to-rose-800/40 transition-all duration-200 rounded-lg border-l-4 border-red-500 hover:border-red-600 hover:shadow-md hover:shadow-red-100/50 dark:hover:shadow-red-900/20 transform hover:scale-[1.01] active:scale-[0.99] min-h-[2rem] cursor-pointer text-center font-medium hover:text-red-800 dark:hover:text-red-200"
              :title="`Remove event from ${group.name}`"
            >
              {{ group.name }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- No actions available - Enhanced -->
      <div v-if="getAvailableGroupsForEvent(eventContextMenu.event).length === 0 && getAssignedGroupsForEvent(eventContextMenu.event).length === 0" 
           class="px-6 py-8 text-center bg-gradient-to-br from-slate-50/50 to-gray-100/50 dark:from-slate-800/30 dark:to-gray-800/30">
        <div class="relative mx-auto mb-4">
          <div class="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-700 dark:to-slate-600 rounded-2xl flex items-center justify-center shadow-lg ring-1 ring-slate-200/50 dark:ring-slate-600/50">
            <span class="text-slate-400 dark:text-slate-500 text-xl">📋</span>
          </div>
          <div class="absolute -bottom-1 -right-1 w-5 h-5 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-md ring-2 ring-white dark:ring-gray-800">
            <span class="text-white text-xs font-bold">!</span>
          </div>
        </div>
        <div class="space-y-2">
          <div class="font-bold text-sm text-gray-800 dark:text-gray-200">No group actions available</div>
          <div class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed max-w-xs mx-auto">
            This event can't be assigned or removed from any groups right now. 
            <span class="font-medium text-blue-600 dark:text-blue-400">Create some groups first!</span>
          </div>
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
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">{{ $t('admin.updating') }}</span>
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
              {{ selectedEvents.length === 0 ? $t('admin.noEventsSelected') : 
                 selectedEvents.length === 1 ? $t('admin.oneEventSelected') : 
                 $t('admin.eventsSelected', { count: selectedEvents.length }) }}
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
                  <div class="w-2 h-2 bg-orange-500 rounded-full animate-pulse" :title="t('admin.mixedState')"></div>
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
                  :title="`${getSmartGroupAction(group.id).secondaryAction === 'add' ? t('admin.add') : t('admin.remove')} ${getSmartGroupAction(group.id).secondaryCount} ${t('admin.events')} ${getSmartGroupAction(group.id).secondaryAction === 'add' ? t('admin.to') : t('admin.from')} ${group.name}`"
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
        {{ t('admin.showAllEvents') }}
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
            :title="t('admin.clearSearch')"
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
            :title="selectedEvents.length === 0 ? $t('admin.noEventsSelected') : $t('admin.clearSelection', { count: selectedEvents.length })"
          >
            {{ $t('admin.clearSelectionButton') }}
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
                'relative border-2 rounded-lg p-3 cursor-pointer transition-all duration-200 hover:shadow-md transform hover:scale-[1.01]',
                selectedEvents.includes(event.title) 
                  ? 'border-blue-400 bg-blue-50 dark:border-blue-500 dark:bg-blue-900/30 shadow-lg ring-2 ring-blue-200 dark:ring-blue-700/50 scale-[1.01]' 
                  : 'border-gray-200 dark:border-gray-600 hover:border-blue-200 dark:hover:border-blue-600 bg-white dark:bg-gray-800 hover:bg-blue-25 dark:hover:bg-blue-950/10'
              ]"
            >
              <!-- Selection Indicator Line -->
              <div 
                class="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
                :class="selectedEvents.includes(event.title) ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'"
              ></div>
              
              <!-- Event Title with clean layout -->
              <div class="mb-2">
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-5">
                  {{ event.title }}
                </h3>
              </div>
              
              <!-- Group Assignment with count -->
              <div class="space-y-1">
                
                <!-- Multi-Group Display with count -->
                <div v-if="event.assigned_groups && event.assigned_groups.length > 0" class="flex flex-wrap items-center gap-1">
                  <!-- Event count before bubbles -->
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 mr-1">
                    {{ event.event_count }}
                  </span>
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
                  <!-- Overflow Indicator with Tooltip -->
                  <span 
                    v-if="event.assigned_groups.length > 2"
                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 transition-colors"
                    :title="event.assigned_groups.slice(2).map(g => g.name).join(', ')"
                  >
                    +{{ event.assigned_groups.length - 2 }}
                  </span>
                </div>
                <!-- Unassigned State with count -->
                <div v-else class="flex flex-wrap items-center gap-1">
                  <!-- Event count before unassigned badge -->
                  <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 mr-1">
                    {{ event.event_count }}
                  </span>
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200">
                    ❔ {{ t('admin.unassigned') }}
                  </span>
                </div>
              </div>
          </div>
        </div>
      </div>
      
      <div v-if="filteredEvents.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
        <div class="text-4xl mb-2">📅</div>
        <p>{{ t('admin.noEventsFound') }}</p>
      </div>
    </div>
  </AdminCardWrapper>
  
  <!-- Delete Group Confirmation Dialog -->
  <ConfirmDialog
    ref="deleteConfirmDialog"
    :title="t('admin.deleteGroup')"
    :message="deleteConfirmMessage"
    :confirm-text="t('admin.deleteGroup')"
    :cancel-text="t('admin.cancel')"
    @confirm="confirmDeleteGroup"
    @cancel="cancelDeleteGroup"
  />
</template>

<script>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
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
    // i18n
    const { t } = useI18n()
    
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
      deleteConfirmMessage.value = t('admin.confirmDeleteGroup', { name: group.name })
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

    // Smart positioning to prevent menu from going off-screen
    const getContextMenuPosition = () => {
      if (!eventContextMenu.value.visible) return {}
      
      const x = eventContextMenu.value.x
      const y = eventContextMenu.value.y
      
      // Estimate menu dimensions (more compact now)
      const menuWidth = 400 // Reasonable estimate for most cases
      const menuHeight = 200 // Much more compact height
      
      // Get viewport dimensions
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      // Calculate best position
      let finalX = x
      let finalY = y
      
      // Check if menu would go off right edge
      if (x + menuWidth > viewportWidth - 20) {
        finalX = x - menuWidth - 10 // Show to the left of cursor
      }
      
      // Check if menu would go off bottom edge
      if (y + menuHeight > viewportHeight - 20) {
        finalY = y - menuHeight - 10 // Show above cursor
      }
      
      // Ensure menu doesn't go off top or left edges
      finalX = Math.max(10, finalX)
      finalY = Math.max(10, finalY)
      
      return {
        position: 'fixed',
        top: finalY + 'px',
        left: finalX + 'px',
        zIndex: 1000
      }
    }

    // Helper function to determine context menu width (adaptive for better UX)
    const getContextMenuWidthClass = () => {
      if (!eventContextMenu.value.event) return 'min-w-96 max-w-4xl w-auto'
      
      const availableGroups = getAvailableGroupsForEvent(eventContextMenu.value.event)
      const assignedGroups = getAssignedGroupsForEvent(eventContextMenu.value.event)
      
      // Calculate longest group name to ensure no truncation
      const allGroups = [...availableGroups, ...assignedGroups]
      const longestName = allGroups.length > 0 ? 
        Math.max(...allGroups.map(g => g.name.length)) : 10
      
      // Base width calculation - ensuring group names fit comfortably
      // Each character ≈ 0.5rem, plus padding, icon space, etc.
      const baseWidth = Math.max(24, longestName * 0.7 + 12) // More generous sizing
      const maxGroups = Math.max(availableGroups.length, assignedGroups.length)
      
      // Adjust for grid layout (more columns = wider needed)
      const cols = maxGroups <= 3 ? 1 : maxGroups <= 8 ? 2 : 3
      const finalWidth = Math.max(baseWidth, cols * 12) // Ensure width accommodates columns
      
      return `min-w-96 max-w-5xl w-[${Math.min(finalWidth, 64)}rem]` // Cap at reasonable max
    }

    // Helper function to determine grid layout for groups based on count
    const getGroupGridClass = (groupCount) => {
      if (groupCount <= 6) return 'grid grid-cols-1 gap-1 px-2'
      if (groupCount <= 12) return 'grid grid-cols-2 gap-1 px-2' 
      if (groupCount <= 18) return 'grid grid-cols-3 gap-1 px-2'
      return 'grid grid-cols-4 gap-1 px-2'
    }

    // Ultra-minimal monochrome palette - uniform appearance with subtle text variations
    const groupColorPalette = [
      // All groups use same neutral background with slight text variations for distinction
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' },
      { bg: 'bg-gray-100', text: 'text-gray-600', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-400' },
      { bg: 'bg-gray-100', text: 'text-gray-700', darkBg: 'dark:bg-gray-700/30', darkText: 'dark:text-gray-300' }
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
            emit('remove-from-group', groupId, eventsToRemove)
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
      // i18n
      t,
      
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
      showEventContextMenu,
      getAvailableGroupsForEvent,
      getAssignedGroupsForEvent,
      getContextMenuPosition,
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