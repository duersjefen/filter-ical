<template>
  <div class="space-y-6">
    <!-- Header with Create Button -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Manage Groups</h2>
      <button
        @click="startCreatingGroup"
        class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
      >
        <span>+</span>
        Create Group
      </button>
    </div>

    <!-- Groups List -->
    <div class="space-y-3">
      
      <!-- New Group Creation Row -->
      <div v-if="creatingGroup" class="flex items-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border-2 border-green-300 dark:border-green-700">
        <div class="flex-1 mr-3">
          <input
            ref="newGroupInput"
            v-model="newGroupName"
            type="text"
            placeholder="Enter group name..."
            @keyup.enter="createGroup"
            @keyup.escape="cancelCreateGroup"
            class="w-full px-3 py-2 border border-green-300 dark:border-green-600 rounded-lg bg-white dark:bg-green-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>
        <div class="flex gap-2">
          <button
            @click="createGroup"
            :disabled="!newGroupName.trim() || loading"
            class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
          >
            ✓ Save
          </button>
          <button
            @click="cancelCreateGroup"
            class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
          >
            ✗ Cancel
          </button>
        </div>
      </div>

      <!-- Existing Groups -->
      <div 
        v-for="group in groups" 
        :key="group.id"
        class="flex items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 transition-colors duration-200"
      >
        
        <!-- Group Display Mode -->
        <div v-if="editingGroupId !== group.id" class="flex-1 mr-3">
          <h3 class="font-medium text-gray-900 dark:text-white">{{ group.name }}</h3>
        </div>

        <!-- Group Edit Mode -->
        <div v-else class="flex-1 mr-3">
          <input
            ref="editGroupInput"
            v-model="editingGroupName"
            type="text"
            @keyup.enter="saveGroupEdit(group.id)"
            @keyup.escape="cancelGroupEdit"
            class="w-full px-3 py-2 border border-blue-300 dark:border-blue-600 rounded-lg bg-white dark:bg-blue-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-2">
          <!-- Display Mode Actions -->
          <template v-if="editingGroupId !== group.id">
            <button
              @click="startEditingGroup(group)"
              :disabled="loading"
              class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            >
              ✏️ Edit
            </button>
            <button
              @click="confirmDeleteGroup(group)"
              :disabled="loading"
              class="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            >
              🗑️ Delete
            </button>
          </template>

          <!-- Edit Mode Actions -->
          <template v-else>
            <button
              @click="saveGroupEdit(group.id)"
              :disabled="!editingGroupName.trim() || loading"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            >
              ✓ Save
            </button>
            <button
              @click="cancelGroupEdit"
              class="bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            >
              ✗ Cancel
            </button>
          </template>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="groups.length === 0 && !creatingGroup" class="text-center py-12 bg-gray-50 dark:bg-gray-700 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div class="text-4xl mb-4">📁</div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">No Groups Yet</h3>
        <p class="text-gray-500 dark:text-gray-400 mb-4">Create your first group to organize events</p>
        <button
          @click="startCreatingGroup"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          + Create First Group
        </button>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <div v-if="confirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-xl max-w-md w-full mx-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ confirmDialog.title }}</h3>
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
          {{ confirmDialog.confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'

export default {
  name: 'GroupsManager',
  props: {
    groups: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['create-group', 'update-group', 'delete-group'],
  setup(props, { emit }) {
    // Reactive state
    const creatingGroup = ref(false)
    const newGroupName = ref('')
    const editingGroupId = ref(null)
    const editingGroupName = ref('')
    const confirmDialog = ref(null)

    // Template refs
    const newGroupInput = ref(null)
    const editGroupInput = ref(null)

    // Group Creation
    const startCreatingGroup = async () => {
      creatingGroup.value = true
      newGroupName.value = ''
      await nextTick()
      if (newGroupInput.value) {
        newGroupInput.value.focus()
      }
    }

    const createGroup = () => {
      if (newGroupName.value.trim()) {
        emit('create-group', newGroupName.value.trim())
        cancelCreateGroup()
      }
    }

    const cancelCreateGroup = () => {
      creatingGroup.value = false
      newGroupName.value = ''
    }

    // Group Editing
    const startEditingGroup = async (group) => {
      editingGroupId.value = group.id
      editingGroupName.value = group.name
      await nextTick()
      if (editGroupInput.value && editGroupInput.value.length > 0) {
        editGroupInput.value[0].focus()
        editGroupInput.value[0].select()
      }
    }

    const saveGroupEdit = (groupId) => {
      if (editingGroupName.value.trim()) {
        emit('update-group', groupId, editingGroupName.value.trim())
        cancelGroupEdit()
      }
    }

    const cancelGroupEdit = () => {
      editingGroupId.value = null
      editingGroupName.value = ''
    }

    // Group Deletion
    const confirmDeleteGroup = (group) => {
      confirmDialog.value = {
        title: 'Delete Group',
        message: `Are you sure you want to delete "${group.name}"? This will also delete all assignments and rules for this group.`,
        confirmText: 'Delete',
        onConfirm: () => emit('delete-group', group.id)
      }
    }

    const closeConfirm = () => {
      confirmDialog.value = null
    }

    return {
      // Reactive state
      creatingGroup,
      newGroupName,
      editingGroupId,
      editingGroupName,
      confirmDialog,

      // Template refs
      newGroupInput,
      editGroupInput,

      // Methods
      startCreatingGroup,
      createGroup,
      cancelCreateGroup,
      startEditingGroup,
      saveGroupEdit,
      cancelGroupEdit,
      confirmDeleteGroup,
      closeConfirm
    }
  }
}
</script>