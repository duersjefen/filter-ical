<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
      <div class="bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 px-6 py-4 border-b-2 border-gray-100 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
              My Profile
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
              Manage your account and domains
            </p>
          </div>
          <div class="text-right">
            <div class="text-xs text-gray-500 dark:text-gray-400">Username</div>
            <div class="font-bold text-gray-900 dark:text-gray-100">{{ user?.username || 'Not logged in' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Not Logged In -->
    <div v-if="!isLoggedIn" class="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-6 text-center">
      <p class="text-yellow-900 dark:text-yellow-200 font-semibold">
        You must be logged in to view your profile
      </p>
      <button
        @click="$router.push('/login')"
        class="mt-4 bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-2 rounded-xl font-semibold transition"
      >
        Go to Login
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
              <h2 class="text-lg font-bold text-white">Account Settings</h2>
              <p class="text-xs text-purple-100">Manage your email and password</p>
            </div>
          </div>
        </div>

        <div class="p-6">

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {{ user?.email ? 'Update Email' : 'Add Email' }}
              </label>
              <input
                v-model="accountForm.email"
                type="email"
                class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg"
                :placeholder="user?.email || 'Add email address'"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ user?.email ? `Current: ${user.email}` : 'Required for password reset and domain requests' }}
              </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  {{ user?.has_password ? 'Change Password' : 'Add Password' }}
                </label>
                <input
                  v-model="accountForm.newPassword"
                  type="password"
                  class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg"
                  :placeholder="user?.has_password ? 'Leave blank to keep current' : 'Optional: Add password for account security'"
                />
                <p v-if="!user?.email && accountForm.newPassword" class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  ⚠️ Add email first - required for password reset
                </p>
              </div>

              <div v-if="user?.has_password && accountForm.newPassword">
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Current Password</label>
                <input
                  v-model="accountForm.currentPassword"
                  type="password"
                  class="w-full px-4 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg"
                  placeholder="Required to change password"
                />
              </div>
            </div>

          <div class="flex gap-2">
            <button
              @click="updateAccount"
              :disabled="updatingAccount"
              class="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold transition"
            >
              {{ updatingAccount ? 'Saving...' : (user?.email || user?.has_password ? 'Update Account' : 'Save Account Info') }}
            </button>
          </div>
        </div>
      </div>
    </div>

      <!-- Active Domains (Filters + Password Access) -->
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
                Active Domains ({{ activeDomains.length }})
              </h2>
              <p class="text-xs text-indigo-100">
                Domains you're actively using with filters or password access
              </p>
            </div>
          </div>
        </div>

        <div class="p-6">

        <div v-if="activeDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>You haven't interacted with any domains yet.</p>
          <p class="text-sm mt-2">Create filters or unlock password-protected domains to get started.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="domain in activeDomains"
            :key="domain.domain_key"
            class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-indigo-400 dark:hover:border-indigo-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
          >
            <!-- Header -->
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
                :title="domain.access_level === 'admin' ? 'Manage Domain' : 'View Domain'"
              >
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
              </button>
            </div>

            <!-- Content -->
            <div class="p-4">
              <!-- Activity Badges -->
              <div class="flex flex-wrap gap-2">
                <span
                  v-if="domain.filter_count"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300 font-semibold"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                  </svg>
                  {{ domain.filter_count }} filter{{ domain.filter_count !== 1 ? 's' : '' }}
                </span>

                <span
                  v-if="domain.access_level === 'admin'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 font-semibold"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                  </svg>
                  Admin Access
                </span>

                <span
                  v-else-if="domain.access_level === 'user'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 font-semibold"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                  </svg>
                  User Access
                </span>

                <span
                  v-if="domain.unlocked_at"
                  class="text-xs text-gray-500 dark:text-gray-400"
                >
                  Unlocked {{ new Date(domain.unlocked_at).toLocaleDateString() }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

      <!-- Admin Domains -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden mb-6">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 px-6 py-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white">
                Admin Access ({{ adminDomains.length }})
              </h2>
              <p class="text-xs text-blue-100">Domains where you have admin privileges</p>
            </div>
          </div>
        </div>

        <div class="p-6">

        <div v-if="adminDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>You don't have admin access to any domains.</p>
          <p class="text-sm mt-2">Domain owners can grant you admin access.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="domain in adminDomains"
            :key="domain.domain_key"
            class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
          >
            <!-- Header -->
            <div class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
              <div class="flex-1">
                <h3 class="font-bold text-lg text-gray-900 dark:text-gray-100 truncate">
                  {{ domain.name || domain.domain_key }}
                </h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  <span class="font-mono">{{ domain.domain_key }}</span> • Admin Role
                </p>
              </div>
              <button
                @click="goToDomainAdmin(domain.domain_key)"
                class="p-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/30 dark:hover:bg-blue-800/50 rounded-lg transition-colors"
                title="Manage Domain"
              >
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

      <!-- Owned Domains -->
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
                My Domains ({{ ownedDomains.length }})
              </h2>
              <p class="text-xs text-green-100">Domains you own and manage</p>
            </div>
          </div>
        </div>

        <div class="p-6">

          <div v-if="loading" class="text-center py-8 text-gray-500 dark:text-gray-400">
            Loading...
          </div>

          <div v-else-if="ownedDomains.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>You don't own any domains yet.</p>
            <p class="text-sm mt-2">Request a domain to get started!</p>
          </div>

        <div v-else class="space-y-3">
          <div
            v-for="domain in ownedDomains"
            :key="domain.domain_key"
            class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-green-400 dark:hover:border-green-500 transition-all shadow-sm hover:shadow-md overflow-hidden"
          >
            <!-- Header -->
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
                  :title="(showingPasswords === domain.domain_key ? 'Hide' : 'Manage') + ' Passwords'"
                >
                  <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                  </svg>
                </button>
                <button
                  @click="toggleAdminManagement(domain.domain_key)"
                  class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  :title="(showingAdmins === domain.domain_key ? 'Hide' : 'Manage') + ' Admins'"
                >
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
                  </svg>
                </button>
                <button
                  @click="goToDomain(domain.domain_key)"
                  class="p-2 bg-green-50 hover:bg-green-100 dark:bg-green-900/30 dark:hover:bg-green-800/50 rounded-lg transition-colors"
                  title="View Domain"
                >
                  <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Password Management -->
            <div v-if="showingPasswords === domain.domain_key" class="p-4">
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">Domain Passwords</h4>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <!-- Admin Password -->
                  <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border-2 border-purple-200 dark:border-purple-700">
                    <h5 class="font-semibold text-purple-900 dark:text-purple-100 mb-2">Admin Password</h5>
                    <div class="relative mb-2">
                      <input
                        v-model="passwordForms[domain.domain_key].adminPassword"
                        :type="showAdminPassword ? 'text' : 'password'"
                        placeholder="Enter admin password (min 4 chars)"
                        class="w-full px-3 py-2 pr-12 border-2 border-purple-300 dark:border-purple-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                      />
                      <button
                        v-if="passwordForms[domain.domain_key]?.adminPassword"
                        type="button"
                        @click="showAdminPassword = !showAdminPassword"
                        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        :title="showAdminPassword ? 'Hide password' : 'Show password'"
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
                      {{ settingPassword ? 'Setting...' : 'Set Admin Password' }}
                    </button>
                  </div>

                  <!-- User Password -->
                  <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border-2 border-blue-200 dark:border-blue-700">
                    <h5 class="font-semibold text-blue-900 dark:text-blue-100 mb-2">User Password</h5>
                    <div class="relative mb-2">
                      <input
                        v-model="passwordForms[domain.domain_key].userPassword"
                        :type="showUserPassword ? 'text' : 'password'"
                        placeholder="Enter user password (min 4 chars)"
                        class="w-full px-3 py-2 pr-12 border-2 border-blue-300 dark:border-blue-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                      />
                      <button
                        v-if="passwordForms[domain.domain_key]?.userPassword"
                        type="button"
                        @click="showUserPassword = !showUserPassword"
                        class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        :title="showUserPassword ? 'Hide password' : 'Show password'"
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
                      {{ settingPassword ? 'Setting...' : 'Set User Password' }}
                    </button>
                  </div>
                </div>
            </div>

            <!-- Admin Management -->
            <div v-if="showingAdmins === domain.domain_key" class="p-4 border-t-2 border-gray-200 dark:border-gray-700">
              <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">Domain Admins</h4>

              <div v-if="loadingAdmins" class="text-sm text-gray-500 dark:text-gray-400">
                Loading admins...
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
                    Remove
                  </button>
                </div>

                <div v-if="domainAdmins[domain.domain_key].length === 0" class="text-sm text-gray-500 dark:text-gray-400 py-2">
                  No admins yet
                </div>
              </div>

              <div class="mt-4 flex gap-2">
                <input
                  v-model="newAdminUsername"
                  type="text"
                  placeholder="Username to add as admin"
                  class="flex-1 px-3 py-2 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm"
                  @keyup.enter="addAdmin(domain.domain_key)"
                />
                <button
                  @click="addAdmin(domain.domain_key)"
                  :disabled="!newAdminUsername || addingAdmin"
                  class="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                >
                  Add Admin
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useHTTP } from '../composables/useHTTP'
import { useNotification } from '../composables/useNotification'

const router = useRouter()
const { user, isLoggedIn, fetchUser } = useAuth()
const { get, post, del, patch } = useHTTP()
const notify = useNotification()

const loading = ref(false)
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

const accountForm = ref({
  email: '',
  newPassword: '',
  currentPassword: ''
})
const updatingAccount = ref(false)

// Merge filter domains and password access domains
const activeDomains = computed(() => {
  const domainMap = new Map()

  // Add filter domains
  filterDomains.value.forEach(domain => {
    domainMap.set(domain.domain_key, {
      ...domain,
      filter_count: domain.filter_count
    })
  })

  // Merge password access domains
  passwordAccessDomains.value.forEach(domain => {
    const existing = domainMap.get(domain.domain_key)
    if (existing) {
      // Merge with existing
      domainMap.set(domain.domain_key, {
        ...existing,
        access_level: domain.access_level,
        unlocked_at: domain.unlocked_at
      })
    } else {
      // Add new
      domainMap.set(domain.domain_key, domain)
    }
  })

  return Array.from(domainMap.values())
})

// Fetch user's domains
const fetchDomains = async () => {
  if (!isLoggedIn.value) return

  loading.value = true
  try {
    const result = await get('/api/users/me/domains')
    if (result.success) {
      ownedDomains.value = result.data.owned_domains || []
      adminDomains.value = result.data.admin_domains || []
      passwordAccessDomains.value = result.data.password_access_domains || []
      filterDomains.value = result.data.filter_domains || []

      // Initialize password forms for owned domains
      ownedDomains.value.forEach(domain => {
        if (!passwordForms.value[domain.domain_key]) {
          passwordForms.value[domain.domain_key] = {
            adminPassword: '',
            userPassword: ''
          }
        }
      })
    }
  } catch (error) {
    console.error('Failed to fetch domains:', error)
  } finally {
    loading.value = false
  }
}


// Update account
const updateAccount = async () => {
  updatingAccount.value = true

  try {
    const payload = {}

    // Only send email if it's different from current
    const emailValue = accountForm.value.email.trim()
    if (emailValue && emailValue !== user.value?.email) {
      payload.email = emailValue
    }

    // Send password if provided
    if (accountForm.value.newPassword) {
      payload.password = accountForm.value.newPassword
      // Only send current_password if user ALREADY HAS a password
      if (user.value?.has_password) {
        payload.current_password = accountForm.value.currentPassword
      }
    }

    if (Object.keys(payload).length === 0) {
      notify.warning('No changes to save')
      return
    }

    const result = await patch('/api/users/me', payload)

    if (result.success) {
      notify.success('Account updated successfully')
      accountForm.value.email = ''
      accountForm.value.newPassword = ''
      accountForm.value.currentPassword = ''
      await fetchUser()
    } else {
      notify.error(result.error || 'Failed to update account')
    }
  } catch (error) {
    console.error('Account update error:', error)
    notify.error('Failed to update account')
  } finally {
    updatingAccount.value = false
  }
}

// Toggle admin management panel
const toggleAdminManagement = async (domainKey) => {
  if (showingAdmins.value === domainKey) {
    showingAdmins.value = null
    return
  }

  showingAdmins.value = domainKey
  await fetchAdmins(domainKey)
}

// Fetch domain admins
const fetchAdmins = async (domainKey) => {
  loadingAdmins.value = true
  try {
    const result = await get(`/api/domains/${domainKey}/admins`)
    if (result.success) {
      domainAdmins.value[domainKey] = result.data.admins || []
    } else {
      notify.error('Failed to load admins')
    }
  } catch (error) {
    console.error('Failed to fetch admins:', error)
    notify.error('Failed to load admins')
  } finally {
    loadingAdmins.value = false
  }
}

// Add admin
const addAdmin = async (domainKey) => {
  if (!newAdminUsername.value.trim()) return

  addingAdmin.value = true

  try {
    const result = await post(`/api/domains/${domainKey}/admins`, {
      username: newAdminUsername.value.trim()
    })

    if (result.success) {
      notify.success(`Successfully added ${newAdminUsername.value} as admin`)
      newAdminUsername.value = ''
      await fetchAdmins(domainKey)
    } else {
      notify.error(result.error || 'Failed to add admin')
    }
  } catch (error) {
    notify.error('Failed to add admin')
  } finally {
    addingAdmin.value = false
  }
}

// Remove admin
const removeAdmin = async (domainKey, username) => {
  if (!confirm(`Remove ${username} from admins?`)) return

  removingAdmin.value = true

  try {
    const result = await del(`/api/domains/${domainKey}/admins/${username}`)

    if (result.success) {
      notify.success(`Successfully removed ${username} from admins`)
      await fetchAdmins(domainKey)
    } else {
      notify.error(result.error || 'Failed to remove admin')
    }
  } catch (error) {
    notify.error('Failed to remove admin')
  } finally {
    removingAdmin.value = false
  }
}

// Toggle password management panel
const togglePasswordManagement = (domainKey) => {
  if (showingPasswords.value === domainKey) {
    showingPasswords.value = null
    return
  }

  showingPasswords.value = domainKey

  // Initialize password form for this domain if not exists
  if (!passwordForms.value[domainKey]) {
    passwordForms.value[domainKey] = {
      adminPassword: '',
      userPassword: ''
    }
  }
}

// Set admin password for domain
const setAdminPasswordForDomain = async (domainKey) => {
  const password = passwordForms.value[domainKey]?.adminPassword
  if (!password || password.length < 4) {
    notify.error('Password must be at least 4 characters')
    return
  }

  settingPassword.value = true

  try {
    const result = await patch(`/api/users/me/domains/${domainKey}/passwords`, {
      admin_password: password
    })

    if (result.success) {
      notify.success('Admin password set successfully')
      passwordForms.value[domainKey].adminPassword = ''
    } else {
      notify.error(result.error || 'Failed to set admin password')
    }
  } catch (error) {
    notify.error('Failed to set admin password')
  } finally {
    settingPassword.value = false
  }
}

// Set user password for domain
const setUserPasswordForDomain = async (domainKey) => {
  const password = passwordForms.value[domainKey]?.userPassword
  if (!password || password.length < 4) {
    notify.error('Password must be at least 4 characters')
    return
  }

  settingPassword.value = true

  try {
    const result = await patch(`/api/users/me/domains/${domainKey}/passwords`, {
      user_password: password
    })

    if (result.success) {
      notify.success('User password set successfully')
      passwordForms.value[domainKey].userPassword = ''
    } else {
      notify.error(result.error || 'Failed to set user password')
    }
  } catch (error) {
    notify.error('Failed to set user password')
  } finally {
    settingPassword.value = false
  }
}

// Navigation
const goToDomain = (domainKey) => {
  router.push(`/${domainKey}`)
}

const goToDomainAdmin = (domainKey) => {
  router.push(`/${domainKey}/admin`)
}

// Initialize
onMounted(() => {
  fetchDomains()
})
</script>
