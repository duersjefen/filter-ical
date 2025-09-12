<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-container">
      <div class="error-icon">⚠️</div>
      <h3>{{ errorTitle }}</h3>
      <p>{{ errorMessage }}</p>
      
      <div v-if="showDetails" class="error-details">
        <button @click="toggleDetails" class="details-toggle">
          {{ showDetailsExpanded ? 'Hide' : 'Show' }} Details
        </button>
        <div v-if="showDetailsExpanded" class="error-stack">
          <code>{{ errorDetails }}</code>
        </div>
      </div>
      
      <div class="error-actions">
        <button @click="retry" class="btn btn-primary" v-if="canRetry">
          🔄 Try Again
        </button>
        <button @click="goHome" class="btn btn-secondary">
          🏠 Go Home
        </button>
        <button @click="refresh" class="btn btn-secondary">
          ↻ Refresh Page
        </button>
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ErrorTypes, ErrorMessages } from '../utils/errorHandler'

const props = defineProps({
  error: Object,
  canRetry: { type: Boolean, default: true },
  showDetails: { type: Boolean, default: false }
})

const emit = defineEmits(['retry', 'clear'])
const router = useRouter()

const showDetailsExpanded = ref(false)

const hasError = computed(() => props.error != null)

const errorTitle = computed(() => {
  if (!props.error) return ''
  
  switch (props.error.type) {
    case ErrorTypes.NETWORK:
      return 'Connection Problem'
    case ErrorTypes.AUTHENTICATION:
      return 'Authentication Required'
    case ErrorTypes.NOT_FOUND:
      return 'Not Found'
    case ErrorTypes.CALENDAR:
      return 'Calendar Error'
    case ErrorTypes.VALIDATION:
      return 'Input Error'
    case ErrorTypes.SERVER:
      return 'Server Error'
    default:
      return 'Something Went Wrong'
  }
})

const errorMessage = computed(() => {
  return props.error?.message || ErrorMessages[ErrorTypes.UNKNOWN]
})

const errorDetails = computed(() => {
  if (!props.error) return ''
  return `${props.error.originalError?.stack || props.error.stack || 'No additional details'}`
})

function toggleDetails() {
  showDetailsExpanded.value = !showDetailsExpanded.value
}

function retry() {
  emit('retry')
}

function goHome() {
  emit('clear')
  router.push('/home')
}

function refresh() {
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  padding: 20px;
  margin: 20px 0;
}

.error-container {
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-container h3 {
  color: #e53e3e;
  margin: 0 0 12px 0;
  font-size: 24px;
}

.error-container p {
  color: #4a5568;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.error-details {
  margin: 20px 0;
  text-align: left;
}

.details-toggle {
  background: none;
  border: 1px solid #cbd5e0;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 12px;
}

.error-stack {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.error-stack code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background: #3182ce;
  color: white;
}

.btn-primary:hover {
  background: #2c5aa0;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}
</style>