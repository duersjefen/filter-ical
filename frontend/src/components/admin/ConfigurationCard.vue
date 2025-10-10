<template>
  <AdminCardWrapper
    :title="$t('domainAdmin.configuration')"
    :subtitle="$t('domainAdmin.configurationSubtitle')"
    icon="💾"
    :expanded="expanded"
    @toggle="$emit('toggle')"
  >
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Export Configuration -->
      <div class="bg-blue-50 dark:bg-blue-900/30 p-4 sm:p-6 rounded-xl border border-blue-200 dark:border-blue-700">
        <div class="flex items-center mb-3 sm:mb-4">
          <div class="text-2xl mr-3 flex-shrink-0">📤</div>
          <h3 class="text-base sm:text-lg font-semibold text-blue-900 dark:text-blue-100">{{ $t('domainAdmin.export') }}</h3>
        </div>
        <p class="text-blue-700 dark:text-blue-200 text-sm mb-4 leading-relaxed">
          {{ $t('domainAdmin.exportDescription') }}
        </p>
        <BaseButton
          variant="primary"
          size="lg"
          full-width
          :disabled="loading"
          @click="$emit('export-configuration')"
        >
          {{ $t('domainAdmin.exportConfiguration') }}
        </BaseButton>
      </div>

      <!-- Import Configuration -->
      <div class="bg-green-50 dark:bg-green-900/30 p-4 sm:p-6 rounded-xl border border-green-200 dark:border-green-700">
        <div class="flex items-center mb-3 sm:mb-4">
          <div class="text-2xl mr-3 flex-shrink-0">📥</div>
          <h3 class="text-base sm:text-lg font-semibold text-green-900 dark:text-green-100">{{ $t('domainAdmin.import') }}</h3>
        </div>
        <p class="text-green-700 dark:text-green-200 text-sm mb-4 leading-relaxed">
          {{ $t('domainAdmin.importDescription') }}
        </p>
        <div class="space-y-3">
          <input
            type="file"
            accept=".yaml,.yml"
            @change="$emit('handle-file-upload', $event)"
            :disabled="loading"
            class="block w-full text-sm text-green-700 dark:text-green-300 file:mr-4 file:py-3 sm:file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-base sm:file:text-sm file:font-medium file:bg-green-600 file:text-white hover:file:bg-green-700 disabled:opacity-50 file:min-h-[44px] sm:file:min-h-0"
          />
        </div>
      </div>

      <!-- Reset Configuration -->
      <div class="bg-red-50 dark:bg-red-900/30 p-4 sm:p-6 rounded-xl border border-red-200 dark:border-red-700 sm:col-span-2 lg:col-span-1">
        <div class="flex items-center mb-3 sm:mb-4">
          <div class="text-2xl mr-3 flex-shrink-0">🔄</div>
          <h3 class="text-base sm:text-lg font-semibold text-red-900 dark:text-red-100">{{ $t('domainAdmin.reset') }}</h3>
        </div>
        <p class="text-red-700 dark:text-red-200 text-sm mb-4 leading-relaxed">
          {{ $t('domainAdmin.resetDescription') }}
        </p>
        <BaseButton
          variant="danger"
          size="lg"
          full-width
          :disabled="loading"
          @click="$emit('reset-configuration-confirm')"
        >
          {{ $t('domainAdmin.resetConfiguration') }}
        </BaseButton>
      </div>
    </div>
  </AdminCardWrapper>
</template>

<script>
import AdminCardWrapper from './AdminCardWrapper.vue'
import BaseButton from '../shared/BaseButton.vue'

export default {
  name: 'ConfigurationCard',
  components: {
    AdminCardWrapper,
    BaseButton
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