<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <!-- Header with Language & Dark Mode -->
    <AppHeader
      :title="t('profile.title')"
      :subtitle="t('profile.subtitle')"
      page-context="profile"
      :show-back-button="true"
      :back-button-text="t('navigation.backToHome')"
      @navigate-back="$router.push('/home')"
    />

    <!-- Not Logged In -->
    <div v-if="!isLoggedIn" class="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-6 text-center">
      <p class="text-yellow-900 dark:text-yellow-200 font-semibold">
        {{ t('profile.notLoggedIn.warning') }}
      </p>
      <button
        @click="$router.push('/login')"
        class="mt-4 bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-xl font-semibold transition"
      >
        {{ t('profile.notLoggedIn.loginButton') }}
      </button>
    </div>

    <!-- Profile Content -->
    <template v-else>
      <!-- Account Settings -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 px-6 py-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white">{{ t('profile.account.title') }}</h2>
              <p class="text-xs text-purple-100">{{ t('profile.account.subtitle') }}</p>
            </div>
          </div>
        </div>

        <div class="p-6 space-y-4">
          <!-- Email -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ user?.email ? t('profile.account.email.labelUpdate') : t('profile.account.email.labelAdd') }}
            </label>
            <input
              v-model="form.email"
              type="email"
              class="w-full px-4 py-2 border-2 rounded-lg"
              :class="emailError ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'"
              :placeholder="user?.email || t('profile.account.email.placeholder')"
            />
            <p v-if="emailError" class="text-xs text-red-600 dark:text-red-400 font-semibold mt-1">
              {{ emailError }}
            </p>
            <p v-else class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ user?.email ? `${t('profile.account.email.currentPrefix')} ${user.email}` : t('profile.account.email.helpText') }}
            </p>
          </div>

          <!-- Password Fields -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- New Password -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {{ user?.has_password ? t('profile.account.password.labelChange') : t('profile.account.password.labelAdd') }}
                <span v-if="form.email && !user?.email" class="text-red-600 dark:text-red-400">*</span>
              </label>
              <input
                v-model="form.newPassword"
                type="password"
                class="w-full px-4 py-2 border-2 rounded-lg"
                :class="passwordError ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'"
                :placeholder="passwordPlaceholder"
              />
              <p v-if="passwordError" class="text-xs text-red-600 dark:text-red-400 font-semibold mt-1">
                {{ passwordError }}
              </p>
              <p v-else-if="passwordEmailError" class="text-xs text-red-600 dark:text-red-400 mt-1">
                {{ passwordEmailError }}
              </p>
            </div>

            <!-- Confirm Password (only show when setting new password) -->
            <div v-if="form.newPassword">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {{ t('profile.account.password.confirmLabel') }}
                <span class="text-red-600 dark:text-red-400">*</span>
              </label>
              <input
                v-model="form.confirmPassword"
                type="password"
                class="w-full px-4 py-2 border-2 rounded-lg"
                :class="confirmPasswordError ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'"
                :placeholder="t('profile.account.password.confirmPlaceholder')"
              />
              <p v-if="confirmPasswordError" class="text-xs text-red-600 dark:text-red-400 font-semibold mt-1">
                {{ confirmPasswordError }}
              </p>
            </div>

            <!-- Current Password (only show when changing existing password) -->
            <div v-if="user?.has_password && form.newPassword">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {{ t('profile.account.password.currentLabel') }}
                <span class="text-red-600 dark:text-red-400">*</span>
              </label>
              <input
                v-model="form.currentPassword"
                type="password"
                class="w-full px-4 py-2 border-2 rounded-lg"
                :class="currentPasswordError ? 'border-red-500 dark:border-red-400' : 'border-gray-300 dark:border-gray-600'"
                :placeholder="t('profile.account.password.currentPlaceholder')"
              />
              <p v-if="currentPasswordError" class="text-xs text-red-600 dark:text-red-400 font-semibold mt-1">
                {{ currentPasswordError }}
              </p>
            </div>
          </div>

          <!-- Save Button -->
          <div class="flex gap-2">
            <button
              @click="updateAccount"
              :disabled="!canSaveAccount"
              class="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-semibold transition"
            >
              {{ updatingAccount ? t('profile.account.saveButton.saving') : (user?.email || user?.has_password ? t('profile.account.saveButton.update') : t('profile.account.saveButton.save')) }}
            </button>
          </div>
        </div>
      </div>

      <!-- Active Domains -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 dark:from-indigo-600 dark:to-purple-700 px-6 py-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="flex-1">
              <h2 class="text-lg font-bold text-white">
                {{ t('profile.activeDomains.title', { count: activeDomains.length }) }}
              </h2>
              <p class="text-xs text-indigo-100">
                {{ t('profile.activeDomains.subtitle') }}
              </p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div v-if="activeDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>{{ t('profile.activeDomains.emptyMessage') }}</p>
            <p class="text-sm mt-2">{{ t('profile.activeDomains.emptyHelp') }}</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="domain in activeDomains"
              :key="domain.domain_key"
              class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
            >
              <div class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
                <div class="flex-1">
                  <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100 truncate">
                    {{ domain.name || domain.domain_key }}
                  </h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    <span class="font-mono">{{ domain.domain_key }}</span>
                  </p>
                </div>
                <button
                  @click="domain.access_level === 'admin' ? goToDomainAdmin(domain.domain_key) : goToDomain(domain.domain_key)"
                  class="p-2 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/30 dark:hover:bg-indigo-800/50 rounded-lg transition-colors"
                  :title="domain.access_level === 'admin' ? t('profile.activeDomains.manageButton') : t('profile.activeDomains.viewButton')"
                >
                  <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </button>
              </div>

              <div class="p-4">
                <div class="flex flex-wrap gap-2">
                  <span v-if="domain.filter_count" class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                    </svg>
                    {{ t('profile.activeDomains.filterCount', domain.filter_count) }}
                  </span>
                  <span v-if="domain.access_level === 'admin'" class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 font-semibold">
                    {{ t('profile.activeDomains.adminAccess') }}
                  </span>
                  <span v-else-if="domain.access_level === 'user'" class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 font-semibold">
                    {{ t('profile.activeDomains.userAccess') }}
                  </span>
                  <span v-if="domain.unlocked_at" class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('profile.activeDomains.unlocked', { date: new Date(domain.unlocked_at).toLocaleDateString() }) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Owned Domains (Password & Admin Management) -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 px-6 py-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white">
                {{ t('profile.ownedDomains.title', { count: ownedDomains.length }) }}
              </h2>
              <p class="text-xs text-green-100">{{ t('profile.ownedDomains.subtitle') }}</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">
            {{ t('profile.ownedDomains.loading') }}
          </div>

          <div v-else-if="ownedDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>{{ t('profile.ownedDomains.emptyMessage') }}</p>
            <p class="text-sm mt-2">{{ t('profile.ownedDomains.emptyHelp') }}</p>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="domain in ownedDomains"
              :key="domain.domain_key"
              class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-green-400 dark:hover:border-green-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
            >
              <div class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
                <div class="flex-1">
                  <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100 truncate">
                    {{ domain.name || domain.domain_key }}
                  </h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    <span class="font-mono">{{ domain.domain_key }}</span> • {{ domain.status }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="togglePasswordManagement(domain.domain_key)"
                    class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    :title="showingPasswords === domain.domain_key ? t('profile.ownedDomains.hidePasswords') : t('profile.ownedDomains.managePasswords')"
                  >
                    <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                    </svg>
                  </button>
                  <button
                    @click="toggleAdminManagement(domain.domain_key)"
                    class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    :title="showingAdmins === domain.domain_key ? t('profile.ownedDomains.hideAdmins') : t('profile.ownedDomains.manageAdmins')"
                  >
                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                    </svg>
                  </button>
                  <button
                    @click="goToDomain(domain.domain_key)"
                    class="p-2 bg-green-50 hover:bg-green-100 dark:bg-green-900/30 dark:hover:bg-green-800/50 rounded-lg transition-colors"
                    :title="t('profile.ownedDomains.viewDomain')"
                  >
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Password Management -->
              <div v-if="showingPasswords === domain.domain_key" class="p-4">
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ t('profile.passwords.sectionTitle') }}</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <!-- Admin Password -->
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border-2 border-purple-200 dark:border-purple-700">
                    <h5 class="font-semibold text-purple-900 dark:text-purple-100 mb-2">{{ t('profile.passwords.admin.title') }}</h5>
                    <div class="relative mb-2">
                      <input
                        v-model="passwordForms[domain.domain_key].adminPassword"
                        :type="showAdminPassword ? 'text' : 'password'"
                        :placeholder="t('profile.passwords.admin.placeholder')"
                        class="w-full px-3 py-2 pr-12 border-2 border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                      />
                      <button
                        v-if="passwordForms[domain.domain_key]?.adminPassword"
                        type="button"
                        @click="showAdminPassword = !showAdminPassword"
                        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        :title="showAdminPassword ? t('profile.passwords.admin.hideButton') : t('profile.passwords.admin.showButton')"
                      >
                        <svg v-if="showAdminPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                        </svg>
                        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                        </svg>
                      </button>
                    </div>
                    <button
                      @click="setAdminPasswordForDomain(domain.domain_key)"
                      :disabled="!passwordForms[domain.domain_key]?.adminPassword || passwordForms[domain.domain_key]?.adminPassword.length < 4 || settingPassword"
                      class="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-semibold transition"
                    >
                      {{ settingPassword ? t('profile.passwords.admin.setting') : t('profile.passwords.admin.setButton') }}
                    </button>
                  </div>

                  <!-- User Password -->
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border-2 border-blue-200 dark:border-blue-700">
                    <h5 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">{{ t('profile.passwords.user.title') }}</h5>
                    <div class="relative mb-2">
                      <input
                        v-model="passwordForms[domain.domain_key].userPassword"
                        :type="showUserPassword ? 'text' : 'password'"
                        :placeholder="t('profile.passwords.user.placeholder')"
                        class="w-full px-3 py-2 pr-12 border-2 border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                      />
                      <button
                        v-if="passwordForms[domain.domain_key]?.userPassword"
                        type="button"
                        @click="showUserPassword = !showUserPassword"
                        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        :title="showUserPassword ? t('profile.passwords.user.hideButton') : t('profile.passwords.user.showButton')"
                      >
                        <svg v-if="showUserPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                        </svg>
                        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                        </svg>
                      </button>
                    </div>
                    <button
                      @click="setUserPasswordForDomain(domain.domain_key)"
                      :disabled="!passwordForms[domain.domain_key]?.userPassword || passwordForms[domain.domain_key]?.userPassword.length < 4 || settingPassword"
                      class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm font-semibold transition"
                    >
                      {{ settingPassword ? t('profile.passwords.user.setting') : t('profile.passwords.user.setButton') }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Admin Management -->
              <div v-if="showingAdmins === domain.domain_key" class="p-4 border-t-2 border-gray-200 dark:border-gray-700">
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">{{ t('profile.admins.sectionTitle') }}</h4>

                <div v-if="loadingAdmins" class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('profile.admins.loading') }}
                </div>

                <div v-else-if="domainAdmins[domain.domain_key]" class="space-y-2">
                  <div
                    v-for="admin in domainAdmins[domain.domain_key]"
                    :key="admin.id"
                    class="flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3"
                  >
                    <div>
                      <div class="font-semibold text-gray-900 dark:text-gray-100">{{ admin.username }}</div>
                      <div class="text-xs text-gray-500 dark:text-gray-400">{{ admin.email }}</div>
                    </div>
                    <button
                      @click="removeAdmin(domain.domain_key, admin.username)"
                      :disabled="removingAdmin"
                      class="bg-red-500 hover:bg-red-600 disabled:bg-gray-400 text-white px-3 py-1 rounded-lg text-sm font-semibold transition"
                    >
                      {{ t('profile.admins.removeButton') }}
                    </button>
                  </div>

                  <div v-if="domainAdmins[domain.domain_key].length === 0" class="text-sm text-gray-500 dark:text-gray-400 py-2">
                    {{ t('profile.admins.emptyMessage') }}
                  </div>
                </div>

                <div class="mt-4 flex gap-2">
                  <input
                    v-model="newAdminUsername"
                    type="text"
                    :placeholder="t('profile.admins.addPlaceholder')"
                    class="flex-1 px-3 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                    @keyup.enter="addAdmin(domain.domain_key)"
                  />
                  <button
                    @click="addAdmin(domain.domain_key)"
                    :disabled="!newAdminUsername || addingAdmin"
                    class="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                  >
                    {{ t('profile.admins.addButton') }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../composables/useAuth'
import { useHTTP } from '../composables/useHTTP'
import { useNotification } from '../composables/useNotification'
import { useValidation } from '../composables/useValidation'
import AppHeader from '../components/shared/AppHeader.vue'

const router = useRouter()
const { t } = useI18n()
const { user, isLoggedIn, fetchCurrentUser } = useAuth()
const { get, post, del, patch } = useHTTP()
const notify = useNotification()
const { isValidEmail, isValidPassword } = useValidation()

// Form state
const form = ref({
  email: '',
  newPassword: '',
  confirmPassword: '',
  currentPassword: ''
})

const updatingAccount = ref(false)
const loading = ref(false)

// Domains state
const ownedDomains = ref([])
const adminDomains = ref([])
const passwordAccessDomains = ref([])
const filterDomains = ref([])

const showingAdmins = ref(null)
const loadingAdmins = ref(false)
const domainAdmins = ref({})
const newAdminUsername = ref('')
const addingAdmin = ref(false)
const removingAdmin = ref(false)

const showingPasswords = ref(null)
const passwordForms = ref({})
const settingPassword = ref(false)
const showAdminPassword = ref(false)
const showUserPassword = ref(false)

// Validation computed properties
const emailError = computed(() => {
  const emailValue = form.value.email.trim()
  if (!emailValue) return ''
  if (!isValidEmail(emailValue)) {
    return t('profile.account.email.invalidFormat')
  }
  return ''
})

const passwordError = computed(() => {
  if (!form.value.newPassword) return ''
  if (!isValidPassword(form.value.newPassword, 4)) {
    return t('profile.account.password.minLength')
  }
  return ''
})

const confirmPasswordError = computed(() => {
  if (!form.value.newPassword || !form.value.confirmPassword) return ''
  if (form.value.newPassword !== form.value.confirmPassword) {
    return t('profile.account.password.mismatch')
  }
  return ''
})

const passwordEmailError = computed(() => {
  if (!form.value.newPassword) return ''
  const emailValue = form.value.email.trim()
  const effectiveEmail = emailValue || user.value?.email
  if (!effectiveEmail || !effectiveEmail.trim()) {
    return t('profile.account.password.warningAddEmailFirst')
  }
  return ''
})

const currentPasswordError = computed(() => {
  if (!form.value.newPassword) return ''
  if (!user.value?.has_password) return ''
  if (form.value.currentPassword) return ''
  return t('profile.account.password.currentPlaceholder')
})

const passwordPlaceholder = computed(() => {
  if (form.value.email && !user.value?.email) {
    return t('profile.account.password.placeholderRequired')
  }
  if (user.value?.has_password) {
    return t('profile.account.password.placeholderKeepCurrent')
  }
  return t('profile.account.password.placeholderOptional')
})

// Form validation
const canSaveAccount = computed(() => {
  if (updatingAccount.value) return false

  const emailValue = form.value.email.trim()
  const effectiveEmail = emailValue || user.value?.email
  const isEmailChanged = emailValue && emailValue !== user.value?.email
  const isPasswordChanged = !!form.value.newPassword

  if (!isEmailChanged && !isPasswordChanged) return false
  if (emailValue && !isValidEmail(emailValue)) return false

  // When adding email for first time (no existing email), password is REQUIRED
  if (isEmailChanged && !user.value?.email && !isPasswordChanged) {
    return false
  }

  if (isPasswordChanged) {
    if (!isValidPassword(form.value.newPassword, 4)) return false
    if (form.value.newPassword !== form.value.confirmPassword) return false
    if (!effectiveEmail || !effectiveEmail.trim()) return false
    if (user.value?.has_password && !form.value.currentPassword) return false
  }

  return true
})

// Active domains merged
const activeDomains = computed(() => {
  const domainMap = new Map()

  filterDomains.value.forEach(domain => {
    domainMap.set(domain.domain_key, { ...domain, filter_count: domain.filter_count })
  })

  passwordAccessDomains.value.forEach(domain => {
    const existing = domainMap.get(domain.domain_key)
    if (existing) {
      domainMap.set(domain.domain_key, { ...existing, access_level: domain.access_level, unlocked_at: domain.unlocked_at })
    } else {
      domainMap.set(domain.domain_key, domain)
    }
  })

  adminDomains.value.forEach(domain => {
    const existing = domainMap.get(domain.domain_key)
    if (existing) {
      domainMap.set(domain.domain_key, { ...existing, ...domain, filter_count: existing.filter_count || domain.filter_count })
    } else {
      domainMap.set(domain.domain_key, domain)
    }
  })

  return Array.from(domainMap.values())
})

// Actions
const updateAccount = async () => {
  updatingAccount.value = true

  const payload = {}
  const emailValue = form.value.email.trim()

  if (emailValue && emailValue !== user.value?.email) {
    payload.email = emailValue
  }

  if (form.value.newPassword) {
    payload.password = form.value.newPassword
    if (user.value?.has_password) {
      payload.current_password = form.value.currentPassword
    }
  }

  if (Object.keys(payload).length === 0) {
    notify.warning(t('profile.account.messages.noChanges'))
    updatingAccount.value = false
    return
  }

  const result = await patch('/api/users/me', payload)

  if (result.success) {
    notify.success(t('profile.account.messages.updateSuccess'))
    form.value.email = ''
    form.value.newPassword = ''
    form.value.confirmPassword = ''
    form.value.currentPassword = ''
  } else {
    notify.error(result.error || t('profile.account.messages.updateFailed'))
  }

  updatingAccount.value = false
}

const fetchDomains = async () => {
  if (!isLoggedIn.value) return

  loading.value = true
  const result = await get('/api/users/me/domains')
  if (result.success) {
    ownedDomains.value = result.data.owned_domains || []
    adminDomains.value = result.data.admin_domains || []
    passwordAccessDomains.value = result.data.password_access_domains || []
    filterDomains.value = result.data.filter_domains || []

    ownedDomains.value.forEach(domain => {
      if (!passwordForms.value[domain.domain_key]) {
        passwordForms.value[domain.domain_key] = { adminPassword: '', userPassword: '' }
      }
    })
  }
  loading.value = false
}

const toggleAdminManagement = async (domainKey) => {
  if (showingAdmins.value === domainKey) {
    showingAdmins.value = null
    return
  }
  showingAdmins.value = domainKey
  await fetchAdmins(domainKey)
}

const fetchAdmins = async (domainKey) => {
  loadingAdmins.value = true
  const result = await get(`/api/domains/${domainKey}/admins`)
  if (result.success) {
    domainAdmins.value[domainKey] = result.data.admins || []
  } else {
    notify.error(t('profile.admins.loadFailed'))
  }
  loadingAdmins.value = false
}

const addAdmin = async (domainKey) => {
  if (!newAdminUsername.value.trim()) return

  addingAdmin.value = true
  const result = await post(`/api/domains/${domainKey}/admins`, {
    username: newAdminUsername.value.trim()
  })

  if (result.success) {
    notify.success(t('profile.admins.addSuccess', { username: newAdminUsername.value }))
    newAdminUsername.value = ''
    await fetchAdmins(domainKey)
  } else {
    notify.error(result.error || t('profile.admins.addFailed'))
  }
  addingAdmin.value = false
}

const removeAdmin = async (domainKey, username) => {
  if (!confirm(t('profile.admins.removeConfirm', { username }))) return

  removingAdmin.value = true
  const result = await del(`/api/domains/${domainKey}/admins/${username}`)

  if (result.success) {
    notify.success(t('profile.admins.removeSuccess', { username }))
    await fetchAdmins(domainKey)
  } else {
    notify.error(result.error || t('profile.admins.removeFailed'))
  }
  removingAdmin.value = false
}

const togglePasswordManagement = (domainKey) => {
  if (showingPasswords.value === domainKey) {
    showingPasswords.value = null
    return
  }
  showingPasswords.value = domainKey
  if (!passwordForms.value[domainKey]) {
    passwordForms.value[domainKey] = { adminPassword: '', userPassword: '' }
  }
}

const setAdminPasswordForDomain = async (domainKey) => {
  const password = passwordForms.value[domainKey]?.adminPassword
  if (!password || password.length < 4) {
    notify.error(t('profile.passwords.minLengthError'))
    return
  }

  settingPassword.value = true
  const result = await patch(`/api/users/me/domains/${domainKey}/passwords`, {
    admin_password: password
  })

  if (result.success) {
    notify.success(t('profile.passwords.admin.setSuccess'))
    passwordForms.value[domainKey].adminPassword = ''
  } else {
    notify.error(result.error || t('profile.passwords.admin.setFailed'))
  }
  settingPassword.value = false
}

const setUserPasswordForDomain = async (domainKey) => {
  const password = passwordForms.value[domainKey]?.userPassword
  if (!password || password.length < 4) {
    notify.error(t('profile.passwords.minLengthError'))
    return
  }

  settingPassword.value = true
  const result = await patch(`/api/users/me/domains/${domainKey}/passwords`, {
    user_password: password
  })

  if (result.success) {
    notify.success(t('profile.passwords.user.setSuccess'))
    passwordForms.value[domainKey].userPassword = ''
  } else {
    notify.error(result.error || t('profile.passwords.user.setFailed'))
  }
  settingPassword.value = false
}

const goToDomain = (domainKey) => router.push(`/${domainKey}`)
const goToDomainAdmin = (domainKey) => router.push(`/${domainKey}/admin`)

onMounted(() => {
  fetchDomains()
})
</script>
