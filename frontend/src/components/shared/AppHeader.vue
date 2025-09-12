<template>
  <div class="text-center mb-8 sm:mb-10 py-8 sm:py-10 px-4 sm:px-6 bg-gradient-to-br from-slate-600 via-slate-700 to-slate-800 text-white rounded-lg shadow-lg">
    <h1 class="text-2xl sm:text-3xl lg:text-4xl font-light mb-2">{{ title }}</h1>
    <p class="text-base sm:text-lg opacity-90" :class="{ 'mb-4 sm:mb-5': showUserInfo }">{{ subtitle }}</p>
    
    <!-- User info in header -->
    <div v-if="showUserInfo" class="mt-5 flex justify-center items-center">
      <div class="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full border border-white/30 flex items-center gap-4">
        <span class="text-sm sm:text-base font-medium">Welcome, {{ user?.username }}!</span>
        <div class="w-px h-5 bg-white/30"></div>
        <button @click="$emit('logout')" class="text-white hover:text-white/80 text-sm font-semibold transition-all duration-300 hover:scale-105">
          Logout
        </button>
      </div>
    </div>

    <!-- Navigation button -->
    <div v-if="showBackButton" class="mt-5">
      <button @click="$emit('navigate-back')" class="px-6 sm:px-8 py-2.5 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-semibold transition-all duration-300 hover:-translate-y-0.5 shadow-md hover:shadow-lg text-sm sm:text-base">
        {{ backButtonText }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    required: true
  },
  user: {
    type: Object,
    default: null
  },
  showUserInfo: {
    type: Boolean,
    default: false
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backButtonText: {
    type: String,
    default: '← Back'
  }
})

defineEmits(['logout', 'navigate-back'])
</script>