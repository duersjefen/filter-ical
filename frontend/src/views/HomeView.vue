<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <AppHeader
      :title="$t('titles.icalFilterSubscribe')"
      :subtitle="$t('subtitles.filterCalendarsCreateFeeds')"
      page-context="home"
    />

    <!-- Browse Domains Section - Smart Sorted -->
    <div v-if="appStore.availableDomains.length > 0" class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-6 sm:p-8 mb-8 hover:shadow-2xl hover:border-purple-300/50 dark:hover:border-purple-600/50 transition-all duration-300 backdrop-blur-sm">
      <div class="flex items-center justify-between mb-6 sm:mb-8">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">Browse Domains</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">Explore available calendar domains</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <router-link
          v-for="domain in sortedDomains"
          :key="domain.domain_key"
          :to="`/${domain.domain_key}`"
          class="group relative bg-gradient-to-br from-white to-purple-50/50 dark:from-gray-700 dark:to-purple-900/20 rounded-2xl border-2 border-purple-200 dark:border-purple-700 shadow-lg hover:shadow-2xl p-6 transition-all duration-300 hover:scale-[1.03] hover:border-purple-400 dark:hover:border-purple-500 active:scale-[0.98] no-underline overflow-hidden"
        >
          <!-- Animated background gradient on hover -->
          <div class="absolute inset-0 bg-gradient-to-br from-purple-400/0 to-purple-600/0 group-hover:from-purple-400/10 group-hover:to-purple-600/10 transition-all duration-300 rounded-2xl"></div>

          <div class="relative flex items-center gap-4">
            <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg group-hover:scale-110 transition-all duration-300">
              <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3z"/>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-bold text-gray-900 dark:text-gray-100 text-lg leading-tight group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors capitalize truncate">
                  {{ domain.name }}
                </h3>
                <!-- Filter count badge for logged-in users -->
                <span v-if="getFilterCount(domain.domain_key) > 0" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-md">
                  {{ getFilterCount(domain.domain_key) }} {{ getFilterCount(domain.domain_key) === 1 ? 'filter' : 'filters' }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"/>
                </svg>
                <span>{{ domain.group_count }} {{ domain.group_count === 1 ? 'group' : 'groups' }}</span>
              </p>
            </div>
            <svg class="w-6 h-6 text-purple-500 dark:text-purple-400 group-hover:translate-x-1 transition-transform duration-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
            </svg>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Add Calendar Form -->
    <div class="bg-gradient-to-br from-white via-white to-blue-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-blue-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-6 sm:p-8 mb-8 hover:shadow-2xl hover:border-blue-300/50 dark:hover:border-blue-600/50 transition-all duration-300 backdrop-blur-sm">
      <div class="flex items-center gap-3 mb-6 sm:mb-8">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-xl flex items-center justify-center shadow-lg">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
          </svg>
        </div>
        <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('home.addNewCalendar') }}</h2>
      </div>
      
      <div v-if="appStore.error" class="bg-gradient-to-br from-red-50 via-red-100 to-orange-50 dark:from-red-900/30 dark:via-red-800/30 dark:to-orange-900/30 text-red-900 dark:text-red-200 px-6 py-5 rounded-2xl mb-6 border-2 border-red-300 dark:border-red-700 relative shadow-xl backdrop-blur-sm">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 flex-1">
            <div class="w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
              <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
            </div>
            <span class="font-bold text-sm sm:text-base">{{ appStore.error }}</span>
          </div>
          <button @click="appStore.clearError()" class="bg-red-200/50 hover:bg-red-300/70 dark:bg-red-800/50 dark:hover:bg-red-700/70 text-red-800 dark:text-red-200 cursor-pointer w-8 h-8 rounded-xl font-bold hover:scale-110 active:scale-95 transition-all duration-200 shadow-md flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Login Required Message for Anonymous Users -->
      <div v-if="!hasCustomUsername()" class="bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 dark:from-amber-900/20 dark:via-yellow-900/20 dark:to-orange-900/20 border-2 border-amber-300 dark:border-amber-700 rounded-2xl p-5 mb-6 shadow-xl backdrop-blur-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 dark:from-amber-600 dark:to-orange-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>
          </div>
          <p class="text-amber-900 dark:text-amber-200 font-bold text-sm sm:text-base">
            {{ $t('messages.pleaseSetUsername') }}
          </p>
        </div>
      </div>

      <form @submit.prevent="handleAddCalendar" class="flex flex-col sm:grid sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-[1fr_1fr_auto] gap-4 sm:gap-6 lg:items-end" :class="{ 'opacity-50 pointer-events-none': !hasCustomUsername() }">
        <div class="mb-0">
          <label for="calendar-name" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">{{ $t('home.calendarName') }}</label>
          <input
            id="calendar-name"
            v-model="appStore.newCalendar.name"
            type="text"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-60 disabled:cursor-not-allowed"
            :placeholder="$t('home.calendarNamePlaceholder')"
            :disabled="!hasCustomUsername()"
            required
          />
        </div>

        <div class="mb-0">
          <label for="calendar-url" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">{{ $t('home.icalUrl') }}</label>
          <input
            id="calendar-url"
            v-model="appStore.newCalendar.url"
            type="url"
            class="w-full px-4 py-3.5 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/50 hover:border-gray-400 dark:hover:border-gray-500 shadow-sm font-medium placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-60 disabled:cursor-not-allowed"
            :placeholder="$t('home.icalUrlPlaceholder')"
            :disabled="!hasCustomUsername()"
            required
          />
        </div>

        <button type="submit" class="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-6 sm:px-8 py-3.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg hover:shadow-xl disabled:shadow-sm disabled:transform-none w-full lg:w-auto mt-4 lg:mt-0" :disabled="appStore.loading || !hasCustomUsername()">
          {{ appStore.loading ? $t('home.adding') : $t('home.addCalendar') }}
        </button>
      </form>
    </div>

    <!-- Calendar List -->
    <div class="bg-gradient-to-br from-white via-white to-indigo-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-indigo-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-6 sm:p-8 mb-8 hover:shadow-2xl hover:border-indigo-300/50 dark:hover:border-indigo-600/50 transition-all duration-300 backdrop-blur-sm">
      <div class="flex items-center justify-between mb-6 sm:mb-8">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 dark:from-indigo-600 dark:to-purple-700 rounded-xl flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"/>
            </svg>
          </div>
          <h2 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-gray-100">{{ $t('home.yourCalendars') }}</h2>
        </div>
        
        <!-- Read-only Mode Indicator -->
        <div v-if="!hasCustomUsername()" class="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-sm">
          <svg class="w-4 h-4 text-gray-600 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
          </svg>
          <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ $t('ui.readOnlyMode') }}</span>
        </div>
      </div>
      
      <div v-if="appStore.loading && appStore.calendars.length === 0" class="text-center py-16 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30 rounded-2xl border-2 border-blue-200 dark:border-blue-700 shadow-xl backdrop-blur-sm">
        <div class="mb-6 inline-block relative">
          <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 dark:from-blue-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-2xl">
            <div class="absolute inset-0 rounded-2xl animate-spin border-4 border-transparent border-t-white/50 border-r-white/30"></div>
            <svg class="w-10 h-10 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
        <div class="text-gray-800 dark:text-gray-200 font-bold text-xl mb-2">{{ $t('common.loadingEvents') }}</div>
        <div class="text-gray-600 dark:text-gray-400 text-sm">{{ $t('common.pleaseWait') }}</div>
      </div>

      <div v-else-if="appStore.calendars.length === 0" class="text-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 border-2 border-blue-200 dark:border-blue-700 rounded-2xl py-16 px-8 shadow-xl backdrop-blur-sm">
        <div class="mb-6 inline-block">
          <div class="relative">
            <div class="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 dark:from-blue-600 dark:to-purple-700 rounded-3xl flex items-center justify-center shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-300">
              <svg class="w-14 h-14 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div class="absolute -top-1 -right-1 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg animate-bounce">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
        <p class="text-gray-800 dark:text-gray-200 font-bold text-xl mb-2">{{ $t('home.noCalendarsFound') }}</p>
        <p class="text-gray-600 dark:text-gray-400 text-sm">Add your first calendar above to get started!</p>
      </div>

      <div v-else data-testid="calendar-list">
        <!-- Mobile: Card Layout -->
        <div class="sm:hidden space-y-4">
          <div v-for="calendar in appStore.calendars" :key="calendar.id" :data-testid="`calendar-item-${calendar.id}`" class="bg-gradient-to-br from-white to-gray-50/50 dark:from-gray-700 dark:to-gray-800/50 rounded-2xl border-2 border-gray-200 dark:border-gray-600 shadow-lg hover:shadow-xl p-5 transition-all duration-300 hover:scale-[1.02] active:scale-100">
            <div class="flex flex-col space-y-4">
              <div class="space-y-2">
                <div class="flex items-start gap-2">
                  <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-lg flex items-center justify-center shadow-md flex-shrink-0">
                    <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                  <h3 class="font-bold text-gray-900 dark:text-gray-100 text-base flex-1 leading-tight pt-0.5">{{ calendar.name }}</h3>
                </div>
                <a :href="calendar.source_url" target="_blank" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 no-underline font-medium transition-colors duration-200 hover:underline text-xs truncate block ml-10 -mt-1">
                  {{ calendar.source_url?.length > 35 ? calendar.source_url.substring(0, 35) + '...' : calendar.source_url }}
                </a>
              </div>
              <div class="flex flex-col gap-2">
                <button @click="viewCalendar(calendar.id)" class="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 text-white border-none px-4 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg">
                  {{ $t('home.viewEvents') }}
                </button>
                <button
                  v-if="calendar.type === 'user'"
                  @click="syncCalendar(calendar.id)"
                  :disabled="appStore.loading"
                  class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 dark:from-green-600 dark:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-4 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg disabled:shadow-sm disabled:transform-none"
                >
                  🔄 Sync Events
                </button>
                <button
                  v-if="calendar.type === 'user' && hasCustomUsername()"
                  @click="deleteCalendar(calendar.id)"
                  class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 dark:from-red-600 dark:to-red-700 dark:hover:from-red-700 dark:hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-4 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg disabled:shadow-sm disabled:transform-none"
                  :disabled="appStore.loading"
                >
                  {{ $t('common.delete') }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Desktop: Table Layout -->
        <div class="hidden sm:block overflow-x-auto rounded-2xl border border-gray-200 dark:border-gray-600 shadow-lg">
          <table class="w-full border-collapse bg-white dark:bg-gray-700">
            <thead>
              <tr class="bg-gradient-to-r from-gray-50 via-gray-100 to-gray-50 dark:from-gray-600 dark:via-gray-700 dark:to-gray-600">
                <th class="px-6 py-5 text-left border-b-2 border-gray-200 dark:border-gray-500 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-xs">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                    </svg>
                    {{ $t('home.name') }}
                  </div>
                </th>
                <th class="px-6 py-5 text-left border-b-2 border-gray-200 dark:border-gray-500 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-xs">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clip-rule="evenodd"/>
                    </svg>
                    {{ $t('home.url') }}
                  </div>
                </th>
                <th class="px-6 py-5 text-left border-b-2 border-gray-200 dark:border-gray-500 font-bold text-gray-800 dark:text-gray-200 tracking-wide uppercase text-xs">{{ $t('home.actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-600">
              <tr v-for="calendar in appStore.calendars" :key="calendar.id" :data-testid="`calendar-item-${calendar.id}`" class="hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-indigo-50/50 dark:hover:from-blue-900/20 dark:hover:to-indigo-900/20 transition-all duration-200 group">
                <td class="px-6 py-5">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-200">
                      <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
                      </svg>
                    </div>
                    <strong class="text-gray-900 dark:text-gray-100 font-bold text-base">{{ calendar.name }}</strong>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <a :href="calendar.source_url" target="_blank" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 no-underline break-all font-medium transition-colors duration-200 hover:underline">
                    {{ calendar.source_url?.length > 60 ? calendar.source_url.substring(0, 60) + '...' : calendar.source_url }}
                  </a>
                </td>
                <td class="px-6 py-4">
                  <div class="flex gap-3">
                    <button @click="viewCalendar(calendar.id)" class="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 dark:from-blue-600 dark:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 text-white border-none px-6 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg whitespace-nowrap">
                      {{ $t('home.viewEvents') }}
                    </button>
                    <button
                      v-if="calendar.type === 'user'"
                      @click="syncCalendar(calendar.id)"
                      :disabled="appStore.loading"
                      class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 dark:from-green-600 dark:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-6 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg disabled:shadow-sm disabled:transform-none whitespace-nowrap"
                    >
                      🔄 Sync
                    </button>
                    <button
                      v-if="calendar.user_id !== 'default' && !String(calendar.id).startsWith('cal_domain_') && hasCustomUsername()"
                      @click="deleteCalendar(calendar.id)"
                      class="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 dark:from-red-600 dark:to-red-700 dark:hover:from-red-700 dark:hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 disabled:cursor-not-allowed text-white border-none px-6 py-2.5 rounded-xl cursor-pointer text-sm font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-md hover:shadow-lg disabled:shadow-sm disabled:transform-none whitespace-nowrap"
                      :disabled="appStore.loading"
                    >
                      {{ $t('common.delete') }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Custom Domain Request Card -->
    <DomainRequestCard v-if="showDomainRequest" />

    <!-- Confirmation Dialog -->
    <ConfirmDialog
      ref="confirmDialog"
      :title="$t('home.deleteCalendar')"
      :message="$t('home.deleteCalendarMessage', { name: calendarToDelete?.name || '' })"
      :confirm-text="$t('home.deleteCalendarConfirm')"
      :cancel-text="$t('home.deleteCalendarCancel')"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import { useRouter } from 'vue-router'
import { onMounted, watch, ref, nextTick, computed } from 'vue'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'
import DomainRequestCard from '../components/home/DomainRequestCard.vue'
import { useDarkMode } from '../composables/useDarkMode'
import { useUsername } from '../composables/useUsername'
import { useNotification } from '../composables/useNotification'

const appStore = useAppStore()
const router = useRouter()
const notify = useNotification()

// Initialize dark mode and username
const { isDarkMode, toggleDarkMode } = useDarkMode()
const { hasCustomUsername } = useUsername()

// Confirmation dialog refs
const confirmDialog = ref(null)
const calendarToDelete = ref(null)

// App settings
const showDomainRequest = ref(true)

// Smart domain sorting: domains with filters first, then alphabetically
const sortedDomains = computed(() => {
  if (!appStore.availableDomains || appStore.availableDomains.length === 0) {
    return []
  }

  // Create map of domain_key → filter_count
  const filterCountMap = new Map()
  if (appStore.domainsWithFilters) {
    appStore.domainsWithFilters.forEach(d => {
      filterCountMap.set(d.domain_key, d.filter_count)
    })
  }

  // Sort: domains with filters first, then alphabetically
  return [...appStore.availableDomains].sort((a, b) => {
    const aFilters = filterCountMap.get(a.domain_key) || 0
    const bFilters = filterCountMap.get(b.domain_key) || 0

    // If one has filters and the other doesn't, prioritize the one with filters
    if (aFilters > 0 && bFilters === 0) return -1
    if (aFilters === 0 && bFilters > 0) return 1

    // Otherwise sort alphabetically by name
    return a.name.localeCompare(b.name)
  })
})

// Helper function to get filter count for a domain
const getFilterCount = (domainKey) => {
  if (!appStore.domainsWithFilters) return 0
  const domainInfo = appStore.domainsWithFilters.find(d => d.domain_key === domainKey)
  return domainInfo ? domainInfo.filter_count : 0
}

onMounted(async () => {
  // Public-first access - always try to initialize and fetch calendars
  appStore.initializeApp()
  appStore.fetchCalendars()

  // Fetch user filters after nextTick to ensure username is initialized from localStorage
  nextTick(() => {
    appStore.fetchUserFilters()
  })

  // Load app settings to check if domain request card should be shown
  try {
    const response = await axios.get(`${API_BASE_URL}/api/app-settings`)
    showDomainRequest.value = response.data.show_domain_request
  } catch (error) {
    console.error('Failed to load app settings:', error)
    // Default to showing the domain request card on error
    showDomainRequest.value = true
  }
})

const handleAddCalendar = async () => {
  const result = await appStore.addCalendar()
  if (!result.success && result.error) {
    notify.error(result.error)
  } else if (result.success && result.warnings && result.warnings.length > 0) {
    // Show warnings to user - calendar created but with issues
    const warningMessage = `Calendar added with issues: ${result.warnings.join(', ')}`
    notify.warning(warningMessage, { duration: 7000 })
  } else if (result.success) {
    notify.success('Calendar added successfully!')
  }
}

const viewCalendar = async (calendarId) => {
  router.push(`/calendar/${calendarId}`)
}

const syncCalendar = async (calendarId) => {
  const result = await appStore.syncCalendar(calendarId)

  if (result.success) {
    notify.success(`Calendar synced! ${result.data.event_count} events processed.`)
  } else {
    notify.error(`Sync failed: ${result.error}`)
  }
}

const deleteCalendar = async (calendarId) => {
  // Find the calendar to show its name in the confirmation
  const calendar = appStore.calendars.find(c => c.id === calendarId)
  if (!calendar) {
    return
  }

  // Store the calendar for the confirmation dialog
  calendarToDelete.value = calendar

  // Open the beautiful confirmation dialog
  confirmDialog.value?.open()
}

// Handle confirmation
const confirmDelete = async () => {
  if (!calendarToDelete.value) return

  const calendarName = calendarToDelete.value.name
  const result = await appStore.deleteCalendar(calendarToDelete.value.id)

  if (result.success) {
    notify.success(`Calendar "${calendarName}" deleted successfully!`)
  } else if (result.error) {
    notify.error(result.error)
  }

  calendarToDelete.value = null
}

// Handle cancellation  
const cancelDelete = () => {
  calendarToDelete.value = null
}

</script>