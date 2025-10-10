<template>
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
      @click="$emit('edit-group')"
      class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
    >
      <span>✏️</span>
      <span>{{ $t('controls.editName') }}</span>
    </button>
    <button
      @click="$emit('delete-group')"
      class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 flex items-center gap-2"
    >
      <span>🗑️</span>
      <span>{{ t('domainAdmin.deleteGroup') }}</span>
    </button>
  </div>
</template>

<script>
import { useI18n } from 'vue-i18n'

export default {
  name: 'GroupContextMenu',
  props: {
    contextMenu: {
      type: Object,
      required: true,
      default: () => ({ visible: false, x: 0, y: 0, group: null })
    }
  },
  emits: ['edit-group', 'delete-group'],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
</script>
