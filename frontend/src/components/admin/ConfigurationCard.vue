<template>
  <AdminCardWrapper
    :title="$t('admin.configuration')"
    subtitle="Export, import, and reset domain configuration"
    icon="💾"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
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
          @click="$emit('export-configuration')"
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
        <div class="space-y-3">
          <input
            type="file"
            accept=".yaml,.yml"
            @change="$emit('handle-file-upload', $event)"
            :disabled="loading"
            class="block w-full text-sm text-green-700 dark:text-green-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-green-600 file:text-white hover:file:bg-green-700 disabled:opacity-50"
          />
        </div>
      </div>

      <!-- Reset Configuration -->
      <div class="bg-red-50 dark:bg-red-900/30 p-6 rounded-xl border border-red-200 dark:border-red-700">
        <div class="flex items-center mb-4">
          <div class="text-2xl mr-3">🔄</div>
          <h3 class="text-lg font-semibold text-red-900 dark:text-red-100">{{ $t('admin.reset') }}</h3>
        </div>
        <p class="text-red-700 dark:text-red-200 text-sm mb-4">
          {{ $t('admin.resetDescription') }}
        </p>
        <button
          @click="$emit('reset-configuration-confirm')"
          :disabled="loading"
          class="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200"
        >
          {{ $t('admin.resetConfiguration') }}
        </button>
      </div>
    </div>
  </AdminCardWrapper>
</template>

<script>
import AdminCardWrapper from './AdminCardWrapper.vue'

export default {
  name: 'ConfigurationCard',
  components: {
    AdminCardWrapper
  },
  props: {
    expanded: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle', 'export-configuration', 'handle-file-upload', 'reset-configuration-confirm']
}
</script>