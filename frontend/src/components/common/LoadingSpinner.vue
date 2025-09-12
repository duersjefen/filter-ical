<template>
  <div class="loading-container" :class="{ 'overlay': overlay }">
    <div class="loading-content">
      <div class="spinner" :class="size">
        <div class="spinner-circle"></div>
      </div>
      <div v-if="message" class="loading-message">{{ message }}</div>
      <div v-if="showProgress && progress !== null" class="loading-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <div class="progress-text">{{ Math.round(progress) }}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Loading...'
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  overlay: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Number,
    default: null
  },
  showProgress: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.loading-container.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 1000;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  display: inline-block;
  border-radius: 50%;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3182ce;
  animation: spin 1s linear infinite;
}

.spinner.small {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.spinner.medium {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.spinner.large {
  width: 60px;
  height: 60px;
  border-width: 4px;
}

.loading-message {
  color: #4a5568;
  font-size: 14px;
  text-align: center;
}

.loading-progress {
  width: 200px;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3182ce, #63b3ed);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #718096;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Pulsing alternative animation */
.spinner-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(45deg, transparent, #3182ce);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 1; }
}
</style>