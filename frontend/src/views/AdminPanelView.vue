<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
    <!-- Password Gate -->
    <div v-if="!isAuthenticated" class="min-h-screen flex items-center justify-center">
      <div class="max-w-md w-full">
        <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <div class="flex items-center justify-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-2xl flex items-center justify-center shadow-lg">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
              </svg>
            </div>
          </div>

          <h1 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
            {{ $t('admin.panel.title') }}
          </h1>
          <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
            {{ $t('admin.panel.subtitle') }}
          </p>

          <!-- Error Message -->
          <div v-if="authError" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-xl mb-4 border border-red-200 dark:border-red-700">
            <div class="flex items-center gap-3 sm:gap-2">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <span class="font-semibold text-sm">{{ authError }}</span>
            </div>
          </div>

          <form @submit.prevent="authenticate" class="space-y-4">
            <div>
              <label for="admin-password" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
                {{ $t('admin.panel.password') }}
              </label>
              <input
                id="admin-password"
                v-model="password"
                type="password"
                class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-purple-500 dark:focus:border-purple-400 focus:ring-4 focus:ring-purple-100 dark:focus:ring-purple-900/50"
                :placeholder="$t('admin.panel.passwordPlaceholder')"
                required
                autofocus
              />
            </div>

            <button
              type="submit"
              :disabled="authenticating || !password"
              class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 dark:from-purple-600 dark:to-purple-700 dark:hover:from-purple-700 dark:hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              {{ authenticating ? $t('admin.panel.authenticating') : $t('admin.panel.login') }}
            </button>

            <button
              type="button"
              @click="showResetRequest = true"
              class="w-full text-sm text-purple-600 dark:text-purple-400 hover:underline mt-2"
            >
              Forgot password?
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Password Reset Request Modal -->
    <div v-if="showResetRequest" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="max-w-md w-full mx-4">
        <div class="bg-gradient-to-br from-white via-white to-purple-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-purple-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-4">
            Reset Admin Password
          </h2>

          <div v-if="!resetRequestSent">
            <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
              A password reset link will be sent to <strong>info@paiss.me</strong>
            </p>

            <div v-if="resetError" class="bg-red-50 dark:bg-red-900/30 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-4">
              {{ resetError }}
            </div>

            <div class="flex gap-3">
              <button
                @click="showResetRequest = false"
                class="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 rounded-lg font-semibold"
              >
                Cancel
              </button>
              <button
                @click="requestReset"
                :disabled="requesting"
                class="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg font-semibold"
              >
                {{ requesting ? 'Sending...' : 'Send Reset Link' }}
              </button>
            </div>
          </div>

          <div v-else>
            <div class="bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg mb-4">
              Reset link sent! Check your email.
            </div>
            <button
              @click="showResetRequest = false; resetRequestSent = false"
              class="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Approval Modal (Full-screen overlay) -->
    <div v-if="showApproveModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="max-w-2xl w-full mx-4">
        <div class="bg-gradient-to-br from-white via-white to-green-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-green-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <!-- Icon -->
          <div class="flex items-center justify-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 rounded-2xl flex items-center justify-center shadow-lg">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
          </div>

          <!-- Title & Description -->
          <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
            Approve Domain Request
          </h2>
          <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
            This will create the domain calendar and make it accessible to the user.
          </p>

          <!-- Info Box -->
          <div class="bg-green-50 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-4 py-3 rounded-xl mb-6 border border-green-200 dark:border-green-700">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              <div>
                <p class="font-semibold text-sm mb-1">What happens next</p>
                <p class="text-sm">The domain will be created immediately and the user will be able to access their calendar.</p>
              </div>
            </div>
          </div>

          <!-- Custom Message (Optional) -->
          <div class="mb-4">
            <label for="approval-message" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
              Custom Message (Optional)
            </label>
            <textarea
              id="approval-message"
              v-model="approvalMessage"
              rows="3"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-green-500 dark:focus:border-green-400 focus:ring-4 focus:ring-green-100 dark:focus:ring-green-900/50 resize-none"
              placeholder="Add a personal message or instructions for the user (optional)..."
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
              This will be included in the approval email if you choose to send one.
            </p>
          </div>

          <!-- Email Toggle -->
          <div class="mb-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" v-model="sendApprovalEmail" class="w-5 h-5 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" />
              <div class="flex-1">
                <span class="font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                  Send email notification to user
                </span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">User will receive their domain URL and admin panel link</p>
              </div>
            </label>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button
              @click="cancelApproval"
              :disabled="submittingApproval"
              class="flex-1 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              Cancel
            </button>
            <button
              @click="submitApproval"
              :disabled="submittingApproval"
              class="flex-1 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 dark:from-green-600 dark:to-green-700 dark:hover:from-green-700 dark:hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              {{ submittingApproval ? 'Approving...' : 'Confirm Approval' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rejection Modal (Full-screen overlay) -->
    <div v-if="showRejectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="max-w-2xl w-full mx-4">
        <div class="bg-gradient-to-br from-white via-white to-red-50/30 dark:from-gray-800 dark:via-gray-800 dark:to-red-900/10 rounded-2xl shadow-xl border-2 border-gray-200/80 dark:border-gray-700/80 p-8">
          <!-- Icon -->
          <div class="flex items-center justify-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 dark:from-red-600 dark:to-red-700 rounded-2xl flex items-center justify-center shadow-lg">
              <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </div>
          </div>

          <!-- Title & Description -->
          <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
            Reject Domain Request
          </h2>
          <p class="text-center text-gray-600 dark:text-gray-400 mb-6">
            Provide a reason for rejecting this request. The user will receive an email notification with your explanation.
          </p>

          <!-- Warning Box -->
          <div class="bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200 px-4 py-3 rounded-xl mb-6 border border-amber-200 dark:border-amber-700">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <div>
                <p class="font-semibold text-sm mb-1">Email notification will be sent</p>
                <p class="text-sm">The user will receive your rejection reason via email. Please be clear and constructive in your feedback.</p>
              </div>
            </div>
          </div>

          <!-- Rejection Reason Textarea -->
          <div class="mb-4">
            <label for="rejection-reason" class="block mb-2 font-semibold text-gray-700 dark:text-gray-300 text-sm">
              Rejection Reason
            </label>
            <textarea
              id="rejection-reason"
              v-model="rejectionReason"
              rows="6"
              class="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:border-red-500 dark:focus:border-red-400 focus:ring-4 focus:ring-red-100 dark:focus:ring-red-900/50 resize-none"
              placeholder="Example: Your calendar URL is not accessible, or it contains events that don't meet our content guidelines..."
              autofocus
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Be specific and helpful - this helps users understand how to improve their request.
            </p>
          </div>

          <!-- Email Toggle -->
          <div class="mb-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 border border-gray-200 dark:border-gray-600">
            <label class="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" v-model="sendRejectionEmail" class="w-5 h-5 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500 dark:focus:ring-red-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600" />
              <div class="flex-1">
                <span class="font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                  </svg>
                  Send email notification to user
                </span>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">User will receive your rejection reason via email</p>
              </div>
            </label>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button
              @click="cancelRejection"
              :disabled="submittingRejection"
              class="flex-1 bg-gray-500 hover:bg-gray-600 disabled:bg-gray-400 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              Cancel
            </button>
            <button
              @click="submitRejection"
              :disabled="submittingRejection || !rejectionReason.trim()"
              class="flex-1 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 dark:from-red-600 dark:to-red-700 dark:hover:from-red-700 dark:hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 hover:-translate-y-0.5 hover:scale-105 active:scale-100 shadow-lg disabled:shadow-sm disabled:transform-none"
            >
              {{ submittingRejection ? 'Sending...' : 'Confirm Rejection' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Admin Panel Content -->
    <div v-else>
      <AppHeader
        :title="$t('admin.panel.domainRequests')"
        :subtitle="$t('admin.panel.manageRequests')"
        :back-button-text="$t('navigation.home')"
        :show-back-button="true"
        page-context="admin"
        @navigate-back="$router.push('/')"
      />

      <div class="space-y-8">
      <!-- Create New Domain (admin shortcut) -->
      <div class="">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <!-- Header - Clickable -->
          <div
            @click="showCreateDomainForm = !showCreateDomainForm"
            class="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 px-6 py-4 cursor-pointer hover:from-blue-600 hover:to-blue-700 dark:hover:from-blue-700 dark:hover:to-blue-800 transition-all"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                  </svg>
                </div>
                <div>
                  <h2 class="text-lg font-bold text-white">Create New Domain</h2>
                  <p class="text-xs text-blue-100">Click to {{ showCreateDomainForm ? 'hide' : 'show' }} form</p>
                </div>
              </div>
              <svg
                class="w-5 h-5 text-white transition-transform"
                :class="showCreateDomainForm ? 'rotate-180' : ''"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </div>
          </div>

          <!-- Form -->
          <div v-if="showCreateDomainForm" class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <!-- Domain Key -->
              <div>
                <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Domain Key *</label>
                <input
                  v-model="newDomain.domain_key"
                  @input="autoFillDisplayName"
                  type="text"
                  placeholder="company-events"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Lowercase, hyphens allowed</p>
              </div>

              <!-- Calendar URL -->
              <div>
                <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Calendar URL *</label>
                <input
                  v-model="newDomain.calendar_url"
                  @paste="handleCalendarUrlPaste"
                  @blur="handleCalendarUrlBlur"
                  type="url"
                  placeholder="https://example.com/calendar.ics"
                  class="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">iCal feed URL (auto-previews on paste)</p>
              </div>

              <!-- Admin Password -->
              <div>
                <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Admin Password *</label>
                <div class="relative">
                  <input
                    v-model="newDomain.admin_password"
                    :type="showNewDomainAdminPassword ? 'text' : 'password'"
                    placeholder="Min 4 characters"
                    class="w-full px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  />
                  <button
                    v-if="newDomain.admin_password"
                    type="button"
                    @click="showNewDomainAdminPassword = !showNewDomainAdminPassword"
                    class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                    :title="showNewDomainAdminPassword ? 'Hide' : 'Show'"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="showNewDomainAdminPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- User Password -->
              <div>
                <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">User Password (Optional)</label>
                <div class="relative">
                  <input
                    v-model="newDomain.user_password"
                    :type="showNewDomainUserPassword ? 'text' : 'password'"
                    placeholder="Leave blank if none"
                    class="w-full px-3 py-2.5 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  />
                  <button
                    v-if="newDomain.user_password"
                    type="button"
                    @click="showNewDomainUserPassword = !showNewDomainUserPassword"
                    class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                    :title="showNewDomainUserPassword ? 'Hide' : 'Show'"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path v-if="showNewDomainUserPassword" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                      <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Preview Button -->
            <button
              v-if="newDomain.calendar_url"
              @click="previewNewDomainCalendar"
              :disabled="newDomainPreview.loading"
              class="w-full bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-2.5 rounded-lg font-medium transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2 mb-3"
            >
              <svg v-if="!newDomainPreview.loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ newDomainPreview.loading ? 'Loading Preview...' : 'Preview Calendar' }}
            </button>

            <!-- Preview Display -->
            <div v-if="newDomainPreview.data" class="mb-4">
              <!-- Error State -->
              <div v-if="newDomainPreview.data.error" class="bg-red-50 dark:bg-red-900/30 rounded-lg p-4 border-2 border-red-200 dark:border-red-700">
                <div class="flex items-start gap-3">
                  <svg class="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div>
                    <p class="font-semibold text-red-800 dark:text-red-200 mb-1">Calendar Error</p>
                    <p class="text-sm text-red-700 dark:text-red-300">{{ newDomainPreview.data.error }}</p>
                    <p class="text-xs text-red-600 dark:text-red-400 mt-2">This URL cannot be used to create a domain.</p>
                  </div>
                </div>
              </div>

              <!-- Success State -->
              <div v-else class="bg-green-50 dark:bg-green-900/30 rounded-lg p-4 border-2 border-green-200 dark:border-green-700">
                <div class="flex items-start gap-3 mb-3">
                  <svg class="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div class="flex-1">
                    <p class="font-semibold text-green-800 dark:text-green-200 mb-1">Valid Calendar</p>
                    <p class="text-sm text-green-700 dark:text-green-300">Found {{ newDomainPreview.data.event_count }} event{{ newDomainPreview.data.event_count !== 1 ? 's' : '' }}</p>
                  </div>
                </div>

                <!-- Event Preview -->
                <div class="space-y-2">
                  <p class="text-xs font-semibold text-green-700 dark:text-green-300 mb-2">Preview (first {{ Math.min(5, newDomainPreview.data.events.length) }} events):</p>
                  <div v-for="(event, index) in newDomainPreview.data.events.slice(0, 5)" :key="index" class="bg-white dark:bg-gray-800 rounded p-2 text-sm sm:text-xs">
                    <p class="font-semibold text-gray-900 dark:text-gray-100">{{ event.title }}</p>
                    <p class="text-gray-600 dark:text-gray-400" v-if="event.start_time">{{ event.start_time }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Create Button -->
            <button
              @click="createDomain"
              :disabled="creatingDomain || !newDomain.domain_key || !newDomain.calendar_url || !newDomain.admin_password || newDomain.admin_password.length < 4"
              class="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
            >
              <svg v-if="!creatingDomain" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ creatingDomain ? 'Creating Domain...' : 'Create Domain' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Domains Overview (at top) -->
      <div class="">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
              <span>All Domains</span>
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Manage all domain calendars and their settings
            </p>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 text-sm font-semibold">
            {{ domains.length }} {{ domains.length !== 1 ? 'domains' : 'domain' }}
          </span>
        </div>

        <div v-if="domainsLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="i in 6" :key="i" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 overflow-hidden animate-pulse">
            <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-b-2 border-gray-100 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-xl"></div>
                <div class="flex-1 space-y-2">
                  <div class="h-4 bg-gray-200 dark:bg-gray-600 rounded w-3/4"></div>
                  <div class="h-3 bg-gray-200 dark:bg-gray-600 rounded w-1/2"></div>
                </div>
              </div>
            </div>
            <div class="p-6 space-y-4">
              <div class="h-20 bg-gray-200 dark:bg-gray-600 rounded"></div>
              <div class="h-20 bg-gray-200 dark:bg-gray-600 rounded"></div>
            </div>
          </div>
        </div>

        <div v-else-if="domains.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-12 text-center shadow-sm">
          <div class="max-w-md mx-auto">
            <div class="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
            </div>
            <h3 class="text-2xl sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
              No domains yet
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
              Create your first domain using the "Create New Domain" button above to get started.
            </p>
            <button
              @click="showCreateDomainForm = true"
              class="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <span>Create Domain</span>
            </button>
          </div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <!-- Domain Card - Better Spacing & Readability -->
          <div v-for="domain in domains" :key="domain.domain_key" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all shadow-sm hover:shadow-md">

            <!-- Header with Domain Name & Actions -->
            <div class="px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
              <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 truncate">{{ domain.domain_key }}</h3>
              <div class="flex items-center gap-3 sm:gap-2">
                <a :href="`/${domain.domain_key}`" target="_blank" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors flex items-center justify-center" title="View Calendar">
                  <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                  </svg>
                </a>
                <a :href="`/${domain.domain_key}/admin`" target="_blank" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation bg-purple-50 hover:bg-purple-100 dark:bg-purple-900/30 dark:hover:bg-purple-800/50 rounded-lg transition-colors flex items-center justify-center" title="Manage Domain">
                  <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                </a>
                <button @click="deleteDomain(domain.domain_key)" :disabled="processing" class="p-3 sm:p-2 min-w-[44px] min-h-[44px] touch-manipulation bg-red-50 hover:bg-red-100 dark:bg-red-900/30 dark:hover:bg-red-800/50 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center" title="Delete Domain">
                  <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Password Management: Side by Side -->
            <div class="p-4 sm:p-6 grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">

              <!-- Admin Password -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                    Admin
                  </span>
                  <span v-if="domain.admin_password_set" class="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded">Protected</span>
                  <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">None</span>
                </div>

                <div v-if="editingDomain !== domain.domain_key || editingType !== 'admin'">
                  <div class="flex flex-col gap-1.5">
                    <button @click="startEditing(domain.domain_key, 'admin')" class="px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all">
                      {{ domain.admin_password_set ? 'Change' : 'Set Password' }}
                    </button>
                    <button v-if="domain.admin_password_set" @click="removePassword(domain.domain_key, 'admin')" class="px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all">
                      Remove
                    </button>
                  </div>
                </div>

                <div v-else class="space-y-2">
                  <div class="relative">
                    <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" placeholder="Enter password" class="w-full px-3 py-2 pr-12 text-sm border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 dark:focus:ring-purple-800" />
                    <button
                      v-if="newPassword"
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                      :title="showPassword ? 'Hide password' : 'Show password'"
                    >
                      <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                    </button>
                  </div>
                  <div class="flex gap-1.5">
                    <button @click="savePassword(domain.domain_key, 'admin')" class="flex-1 px-3 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">Save</button>
                    <button @click="cancelEditing" class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all">Cancel</button>
                  </div>
                </div>
              </div>

              <!-- User Password -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    User
                  </span>
                  <span v-if="domain.user_password_set" class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded">Protected</span>
                  <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">None</span>
                </div>

                <div v-if="editingDomain !== domain.domain_key || editingType !== 'user'">
                  <div class="flex flex-col gap-1.5">
                    <button @click="startEditing(domain.domain_key, 'user')" class="px-3 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all">
                      {{ domain.user_password_set ? 'Change' : 'Set Password' }}
                    </button>
                    <button v-if="domain.user_password_set" @click="removePassword(domain.domain_key, 'user')" class="px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all">
                      Remove
                    </button>
                  </div>
                </div>

                <div v-else class="space-y-2">
                  <div class="relative">
                    <input v-model="newPassword" :type="showPassword ? 'text' : 'password'" placeholder="Enter password" class="w-full px-3 py-2 pr-12 text-sm border-2 border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800" />
                    <button
                      v-if="newPassword"
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                      :title="showPassword ? 'Hide password' : 'Show password'"
                    >
                      <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                    </button>
                  </div>
                  <div class="flex gap-1.5">
                    <button @click="savePassword(domain.domain_key, 'user')" class="flex-1 px-3 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">Save</button>
                    <button @click="cancelEditing" class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all">Cancel</button>
                  </div>
                </div>
              </div>

            </div>

            <!-- Owner Management -->
            <div class="px-4 pb-4 border-t-2 border-gray-100 dark:border-gray-700 pt-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Owner
                </span>
                <span v-if="domain.owner_username" class="px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400 text-xs font-medium rounded">
                  {{ domain.owner_username }}
                </span>
                <span v-else class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs font-medium rounded">
                  No owner
                </span>
              </div>

              <!-- Owner Search & Assign -->
              <div v-if="assigningOwner === domain.domain_key" class="space-y-2">
                <div class="relative">
                  <input
                    v-model="ownerSearchQuery"
                    @input="searchUsers"
                    type="text"
                    placeholder="Search users..."
                    class="w-full px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                  <svg v-if="searchingUsers" class="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>

                <!-- Search Results -->
                <div v-if="userSearchResults.length > 0" class="max-h-40 overflow-y-auto bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-600">
                  <button
                    v-for="user in userSearchResults"
                    :key="user.id"
                    @click="assignOwner(domain.domain_key, user.id, user.username)"
                    class="w-full px-3 py-2 text-left hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition text-sm"
                  >
                    <div class="font-semibold text-gray-900 dark:text-gray-100">{{ user.username }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ user.email || 'No email' }}</div>
                  </button>
                </div>

                <div class="flex gap-2">
                  <button
                    @click="cancelOwnerAssignment"
                    class="flex-1 px-3 py-2 text-sm font-medium bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>

              <!-- Owner Actions -->
              <div v-else class="flex gap-2">
                <button
                  @click="startOwnerAssignment(domain.domain_key)"
                  class="flex-1 px-3 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition"
                >
                  {{ domain.owner_username ? 'Change' : 'Assign' }}
                </button>
                <button
                  v-if="domain.owner_username"
                  @click="removeOwner(domain.domain_key)"
                  class="flex-1 px-3 py-2 text-sm font-medium bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Requests List -->
      <div class="">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
              </svg>
              <span>Pending Domain Requests</span>
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Review and approve user requests for new domains
            </p>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 text-sm font-semibold">
            {{ pendingRequests.length }} {{ pendingRequests.length !== 1 ? 'requests' : 'request' }}
          </span>
        </div>

        <div v-if="loading" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-12 text-center">
          <div class="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">{{ $t('common.loading') }}</p>
        </div>

        <div v-else-if="pendingRequests.length === 0" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 p-12 text-center shadow-sm">
          <div class="max-w-md mx-auto">
            <div class="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <h3 class="text-2xl sm:text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
              All caught up!
            </h3>
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
              No pending domain requests at the moment. New requests will appear here for approval.
            </p>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div v-for="request in pendingRequests" :key="request.id" class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-400 dark:hover:border-purple-500 transition-all shadow-sm hover:shadow-md">

            <!-- Request Header -->
            <div class="px-5 py-4 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800 border-b-2 border-gray-100 dark:border-gray-700">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 dark:from-purple-600 dark:to-purple-700 rounded-lg flex items-center justify-center shadow-md">
                  <span class="text-white font-bold text-lg">{{ request.username.charAt(0).toUpperCase() }}</span>
                </div>
                <div>
                  <h3 class="font-bold text-gray-900 dark:text-gray-100">{{ request.username }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ request.email }}</p>
                </div>
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(request.created_at) }}
              </div>
            </div>

            <!-- Request Details -->
            <div class="p-5">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <!-- Requested Domain -->
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-700">
                  <p class="text-xs font-semibold text-purple-700 dark:text-purple-300 mb-1">REQUESTED DOMAIN</p>
                  <p class="font-mono font-bold text-purple-900 dark:text-purple-100">{{ request.requested_domain_key }}</p>
                </div>

                <!-- Calendar URL -->
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                  <p class="text-xs font-semibold text-blue-700 dark:text-blue-300 mb-1">CALENDAR URL</p>
                  <a :href="request.calendar_url" target="_blank" class="text-sm text-blue-600 dark:text-blue-400 hover:underline break-all">
                    {{ request.calendar_url }}
                  </a>
                </div>
              </div>

              <!-- Description -->
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                <p class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">DESCRIPTION</p>
                <p class="text-sm text-gray-700 dark:text-gray-300">{{ request.description }}</p>
              </div>

              <!-- iCal Preview -->
              <div class="mb-4">
                <button
                  @click="togglePreview(request.id)"
                  class="text-sm font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 flex items-center gap-2 transition-colors"
                >
                  <svg class="w-4 h-4" :class="{ 'rotate-90': icalPreviews[request.id]?.expanded }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                  <span>{{ icalPreviews[request.id]?.expanded ? 'Hide' : 'Show' }} Calendar Preview</span>
                </button>

                <div v-if="icalPreviews[request.id]?.expanded" class="mt-3">
                  <!-- Loading State -->
                  <div v-if="icalPreviews[request.id]?.loading" class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border-2 border-blue-200 dark:border-blue-700">
                    <div class="flex items-center gap-3 sm:gap-2">
                      <div class="inline-block w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                      <span class="text-sm font-medium text-blue-700 dark:text-blue-300">Loading events...</span>
                    </div>
                  </div>

                  <!-- Error State -->
                  <div v-else-if="icalPreviews[request.id]?.data?.error" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-2 border-red-200 dark:border-red-700">
                    <div class="flex items-center gap-2 mb-2">
                      <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                      </svg>
                      <span class="font-bold text-red-800 dark:text-red-200">Calendar Error</span>
                    </div>
                    <p class="text-sm text-red-700 dark:text-red-300">{{ icalPreviews[request.id].data.error }}</p>
                  </div>

                  <!-- Success State -->
                  <div v-else-if="icalPreviews[request.id]?.data" class="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border-2 border-green-200 dark:border-green-700">
                    <div class="flex items-center gap-2 mb-3">
                      <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>
                      <span class="font-bold text-green-800 dark:text-green-200">Found {{ icalPreviews[request.id].data.event_count }} event{{ icalPreviews[request.id].data.event_count !== 1 ? 's' : '' }}</span>
                    </div>
                    <div v-if="icalPreviews[request.id].data.events.length > 0" class="space-y-2">
                      <p class="text-xs font-bold text-green-700 dark:text-green-300 mb-2">PREVIEW (first {{ Math.min(5, icalPreviews[request.id].data.events.length) }} events)</p>
                      <div v-for="(event, idx) in icalPreviews[request.id].data.events.slice(0, 5)" :key="idx" class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-green-200 dark:border-green-700">
                        <p class="font-semibold text-gray-900 dark:text-gray-100 mb-1">{{ event.title }}</p>
                        <p v-if="event.start_time" class="text-xs text-gray-600 dark:text-gray-400">📅 {{ new Date(event.start_time).toLocaleDateString() }} {{ new Date(event.start_time).toLocaleTimeString() }}</p>
                        <p v-if="event.location" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">📍 {{ event.location }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex gap-3 pt-4 border-t-2 border-gray-100 dark:border-gray-700">
                <button
                  @click="approveRequest(request.id)"
                  :disabled="processing || !canApproveRequest(request.id)"
                  :title="getApprovalDisabledReason(request.id)"
                  class="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  <span>{{ $t('admin.panel.approve') || 'Approve' }}</span>
                </button>
                <button
                  @click="rejectRequest(request.id)"
                  :disabled="processing"
                  class="flex-1 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-4 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  <span>{{ $t('admin.panel.reject') || 'Reject' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- App Settings - Clean & Spacious -->
      <div class="bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="px-5 py-4 border-b-2 border-gray-100 dark:border-gray-700 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-800">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1 flex items-center gap-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <span>App Settings</span>
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Configure global application behavior</p>
        </div>

        <div class="p-5">
          <!-- Settings Grid: Side by Side -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">

            <!-- Footer Visibility -->
            <div>
              <label class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 block">Footer Visibility</label>
              <div class="inline-flex rounded-lg border-2 border-gray-300 dark:border-gray-600 overflow-hidden shadow-sm">
                <button
                  @click="appSettings.footer_visibility = 'everywhere'"
                  class="px-4 py-2.5 text-sm font-medium transition-all border-r-2 border-gray-300 dark:border-gray-600"
                  :class="appSettings.footer_visibility === 'everywhere'
                    ? 'bg-purple-600 text-white shadow-inner'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
                >
                  Everywhere
                </button>
                <button
                  @click="appSettings.footer_visibility = 'admin_only'"
                  class="px-4 py-2.5 text-sm font-medium transition-all border-r-2 border-gray-300 dark:border-gray-600"
                  :class="appSettings.footer_visibility === 'admin_only'
                    ? 'bg-purple-600 text-white shadow-inner'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
                >
                  Admin
                </button>
                <button
                  @click="appSettings.footer_visibility = 'nowhere'"
                  class="px-4 py-2.5 text-sm font-medium transition-all"
                  :class="appSettings.footer_visibility === 'nowhere'
                    ? 'bg-purple-600 text-white shadow-inner'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
                >
                  Hidden
                </button>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Control where the PayPal donation footer appears</p>
            </div>

            <!-- Domain Request Card -->
            <div>
              <label class="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3 block">Domain Request Card</label>
              <div class="flex items-center gap-3">
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="appSettings.show_domain_request" class="sr-only peer" />
                  <div class="w-14 h-7 bg-gray-300 dark:bg-gray-600 rounded-full peer-checked:bg-purple-600 dark:peer-checked:bg-purple-500 transition-all shadow-inner"></div>
                  <div class="absolute left-1 top-1 w-5 h-5 bg-white rounded-full transition-transform peer-checked:translate-x-7 shadow-md"></div>
                </label>
                <span class="text-sm font-semibold" :class="appSettings.show_domain_request ? 'text-purple-600 dark:text-purple-400' : 'text-gray-500 dark:text-gray-400'">
                  {{ appSettings.show_domain_request ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">Allow users to request their own custom domains</p>
            </div>

          </div>

          <!-- Save Button -->
          <div class="pt-4 border-t-2 border-gray-100 dark:border-gray-700">
            <button
              @click="saveAppSettings"
              :disabled="settingsSaving"
              class="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-lg font-bold transition-all disabled:cursor-not-allowed shadow-md hover:shadow-lg disabled:shadow-none"
            >
              {{ settingsSaving ? 'Saving...' : 'Save Settings' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Domain YAML Configuration Management -->
      <div class="">
        <DomainConfigManager />
      </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <ConfirmDialog
      ref="confirmDialog"
      :title="confirmDialogData.title"
      :message="confirmDialogData.message"
      :confirmText="confirmDialogData.confirmText"
      @confirm="confirmDialogData.onConfirm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { API_BASE_URL } from '../constants/api'
import AppHeader from '../components/shared/AppHeader.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'
import DomainConfigManager from '../components/admin/DomainConfigManager.vue'
import FormInput from '../components/shared/FormInput.vue'
import FormTextarea from '../components/shared/FormTextarea.vue'
import BaseButton from '../components/shared/BaseButton.vue'
import { useNotification } from '../composables/useNotification'

const { t } = useI18n()
const notify = useNotification()

// Authentication
const isAuthenticated = ref(false)
const password = ref('')
const authenticating = ref(false)
const authError = ref(null)

// Password reset
const showResetRequest = ref(false)
const resetRequestSent = ref(false)
const requesting = ref(false)
const resetError = ref(null)

// Requests data
const requests = ref([])
const loading = ref(false)
const processing = ref(false)

// Domains data
const domains = ref([])
const domainsLoading = ref(false)

// Password editing state
const editingDomain = ref(null)
const editingType = ref(null)  // 'admin' or 'user'
const newPassword = ref('')

// App settings state
const appSettings = ref({
  footer_visibility: 'everywhere',
  show_domain_request: true
})
const settingsSaving = ref(false)

// iCal preview state
const icalPreviews = ref({})  // { [requestId]: { expanded: boolean, loading: boolean, data: {...} } }

// Rejection modal state
const showRejectModal = ref(false)
const rejectingRequestId = ref(null)
const rejectionReason = ref('')
const submittingRejection = ref(false)

// Approval modal state
const showApproveModal = ref(false)
const approvingRequestId = ref(null)
const approvalMessage = ref('')
const sendApprovalEmail = ref(true)
const sendRejectionEmail = ref(true)
const submittingApproval = ref(false)

// Confirm dialog state
const confirmDialog = ref(null)
const confirmDialogData = ref({
  title: '',
  message: '',
  confirmText: '',
  onConfirm: null
})

// Create domain state
const showCreateDomainForm = ref(false)
const creatingDomain = ref(false)
const newDomain = ref({
  domain_key: '',
  name: '',
  calendar_url: '',
  admin_password: '',
  user_password: ''
})

// Preview state for new domain creation
const newDomainPreview = ref({
  loading: false,
  data: null
})

// Owner assignment state
const assigningOwner = ref(null)  // domain_key being edited
const ownerSearchQuery = ref('')
const userSearchResults = ref([])
const searchingUsers = ref(false)
let searchTimeout = null

// Computed stats
// Only show pending requests (approved ones become domains, rejected ones are hidden)
const pendingRequests = computed(() => requests.value.filter(r => r.status === 'pending'))

const authenticate = async () => {
  authenticating.value = true
  authError.value = null

  try {
    // Login to get JWT token
    const response = await axios.post(`${API_BASE_URL}/api/admin/login`, {
      password: password.value
    })

    // Store token in localStorage (30-day expiry)
    const token = response.data.token
    localStorage.setItem('admin_token', token)
    localStorage.setItem('admin_token_expires', Date.now() + (30 * 24 * 60 * 60 * 1000))

    isAuthenticated.value = true

    // Load data after successful authentication
    await Promise.all([loadRequests(), loadDomains()])
  } catch (error) {
    authError.value = t('admin.panel.invalidPassword')
  } finally {
    authenticating.value = false
  }
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('admin_token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const requestReset = async () => {
  requesting.value = true
  resetError.value = null

  try {
    await axios.post(`${API_BASE_URL}/api/admin/request-password-reset`)
    resetRequestSent.value = true
  } catch (error) {
    resetError.value = error.response?.data?.detail || 'Failed to send reset email'
  } finally {
    requesting.value = false
  }
}

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domain-requests`, {
      headers: getAuthHeaders()
    })
    requests.value = response.data

    // Auto-expand previews for all pending requests
    await autoExpandPreviews()
  } catch (error) {
    console.error('Failed to load requests:', error)
    // Token might be expired, logout
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_token_expires')
      isAuthenticated.value = false
    }
  } finally {
    loading.value = false
  }
}

const loadDomains = async () => {
  domainsLoading.value = true
  try {
    const response = await axios.get(`${API_BASE_URL}/api/admin/domains-auth`, {
      headers: getAuthHeaders()
    })
    domains.value = response.data
  } catch (error) {
    console.error('Failed to load domains:', error)
  } finally {
    domainsLoading.value = false
  }
}

const startEditing = (domainKey, type) => {
  editingDomain.value = domainKey
  editingType.value = type
  newPassword.value = ''
  showPassword.value = false
}

const cancelEditing = () => {
  editingDomain.value = null
  editingType.value = null
  newPassword.value = ''
  showPassword.value = false
}

const savePassword = async (domainKey, type) => {
  if (!newPassword.value || newPassword.value.length < 4) {
    notify.error(t('admin.domainAuth.passwordSettings.error.minLength') || 'Password must be at least 4 characters')
    return
  }

  try {
    const endpoint = type === 'admin'
      ? `/api/admin/domains/${domainKey}/passwords`
      : `/api/admin/domains/${domainKey}/passwords`

    const payload = type === 'admin'
      ? { admin_password: newPassword.value }
      : { user_password: newPassword.value }

    await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
      headers: getAuthHeaders()
    })

    notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Set`) || `${type === 'admin' ? 'Admin' : 'User'} password updated successfully`)
    cancelEditing()
    await loadDomains()  // Refresh the list
  } catch (error) {
    notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Set`) || `Failed to set password: ${error.message}`)
  }
}

const removePassword = (domainKey, type) => {
  const passwordType = type === 'admin' ? 'Admin' : 'User'

  confirmDialogData.value = {
    title: `Remove ${passwordType} Password`,
    message: t('admin.domainAuth.passwordSettings.confirm.remove' + (type === 'admin' ? 'Admin' : 'User')) || `Are you sure you want to remove the ${type} password for domain "${domainKey}"? Users will no longer need a password to access this domain.`,
    confirmText: 'Remove Password',
    onConfirm: async () => {
      processing.value = true
      try {
        const endpoint = `/api/admin/domains/${domainKey}/passwords`

        const payload = type === 'admin'
          ? { remove_admin_password: true }
          : { remove_user_password: true }

        await axios.patch(`${API_BASE_URL}${endpoint}`, payload, {
          headers: getAuthHeaders()
        })

        notify.success(t(`admin.domainAuth.passwordSettings.success.${type}Removed`) || `${passwordType} password removed successfully`)
        await loadDomains()  // Refresh the list
      } catch (error) {
        notify.error(t(`admin.domainAuth.passwordSettings.error.${type}Removed`) || `Failed to remove password: ${error.message}`)
      } finally {
        processing.value = false
      }
    }
  }
  confirmDialog.value.open()
}

const approveRequest = (requestId) => {
  // Open approval modal
  approvingRequestId.value = requestId
  approvalMessage.value = ''
  sendApprovalEmail.value = true
  showApproveModal.value = true
}

const cancelApproval = () => {
  showApproveModal.value = false
  approvingRequestId.value = null
  approvalMessage.value = ''
}

const submitApproval = async () => {
  submittingApproval.value = true
  try {
    const requestBody = {
      send_email: sendApprovalEmail.value
    }

    // Only include message if it's not empty
    if (approvalMessage.value.trim()) {
      requestBody.message = approvalMessage.value.trim()
    }

    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${approvingRequestId.value}/approve`,
      requestBody,
      {
        headers: getAuthHeaders()
      }
    )
    // Reload both requests and domains to show the new domain
    await Promise.all([loadRequests(), loadDomains()])
    notify.success(t('admin.panel.approvalSuccess') || 'Request approved successfully')
    cancelApproval()
  } catch (error) {
    notify.error(t('admin.panel.approvalFailed'))
  } finally {
    submittingApproval.value = false
  }
}

const rejectRequest = (requestId) => {
  // Open rejection modal
  rejectingRequestId.value = requestId
  rejectionReason.value = ''
  sendRejectionEmail.value = true
  showRejectModal.value = true
}

const cancelRejection = () => {
  showRejectModal.value = false
  rejectingRequestId.value = null
  rejectionReason.value = ''
}

const submitRejection = async () => {
  if (!rejectionReason.value.trim()) {
    notify.error('Please provide a rejection reason')
    return
  }

  submittingRejection.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/domain-requests/${rejectingRequestId.value}/reject`,
      {
        reason: rejectionReason.value.trim(),
        send_email: sendRejectionEmail.value
      },
      {
        headers: getAuthHeaders()
      }
    )
    await loadRequests()
    notify.success(t('admin.panel.rejectionSuccess') || 'Request rejected successfully')
    cancelRejection()
  } catch (error) {
    notify.error(t('admin.panel.rejectionFailed'))
  } finally {
    submittingRejection.value = false
  }
}

const deleteDomain = (domainKey) => {
  confirmDialogData.value = {
    title: 'Delete Domain',
    message: `Are you sure you want to delete domain "${domainKey}"? This will delete all associated data (calendar, filters, groups). This action cannot be undone.`,
    confirmText: 'Delete Domain',
    onConfirm: async () => {
      processing.value = true
      try {
        await axios.delete(
          `${API_BASE_URL}/api/admin/domains/${domainKey}`,
          {
            headers: getAuthHeaders()
          }
        )
        await loadDomains()
        notify.success(`Domain "${domainKey}" deleted successfully`)
      } catch (error) {
        notify.error(`Failed to delete domain: ${error.response?.data?.detail || error.message}`)
      } finally {
        processing.value = false
      }
    }
  }
  confirmDialog.value.open()
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const loadAppSettings = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/app-settings`)
    appSettings.value = response.data
  } catch (error) {
    console.error('Failed to load app settings:', error)
  }
}

const saveAppSettings = async () => {
  settingsSaving.value = true
  try {
    await axios.patch(
      `${API_BASE_URL}/api/admin/app-settings`,
      appSettings.value,
      {
        headers: getAuthHeaders()
      }
    )
    notify.success('App settings updated successfully')
  } catch (error) {
    notify.error(`Failed to update settings: ${error.response?.data?.detail || error.message}`)
  } finally {
    settingsSaving.value = false
  }
}

const togglePreview = async (requestId) => {
  // Initialize preview state if not exists
  if (!icalPreviews.value[requestId]) {
    icalPreviews.value[requestId] = { expanded: false, loading: false, data: null }
  }

  // Toggle expansion
  icalPreviews.value[requestId].expanded = !icalPreviews.value[requestId].expanded

  // If expanding and no data loaded yet, fetch it
  if (icalPreviews.value[requestId].expanded && !icalPreviews.value[requestId].data) {
    icalPreviews.value[requestId].loading = true

    try {
      const request = requests.value.find(r => r.id === requestId)
      if (!request) return

      const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
        calendar_url: request.calendar_url
      })

      icalPreviews.value[requestId].data = response.data
    } catch (error) {
      icalPreviews.value[requestId].data = {
        event_count: 0,
        events: [],
        error: `Failed to load preview: ${error.response?.data?.detail || error.message}`
      }
    } finally {
      icalPreviews.value[requestId].loading = false
    }
  }
}

const canApproveRequest = (requestId) => {
  const preview = icalPreviews.value[requestId]

  // If preview was checked and has error or 0 events, block approval
  if (preview?.data) {
    if (preview.data.error || preview.data.event_count === 0) {
      return false
    }
  }

  return true
}

const getApprovalDisabledReason = (requestId) => {
  const preview = icalPreviews.value[requestId]

  if (preview?.data?.error) {
    return `Cannot approve: ${preview.data.error}`
  }

  if (preview?.data?.event_count === 0) {
    return 'Cannot approve: Calendar has no events'
  }

  return ''
}

const autoFillDisplayName = () => {
  // Auto-generate display name from domain key (capitalize first letter)
  const key = newDomain.value.domain_key.trim()
  if (key) {
    // Replace hyphens with spaces and capitalize first letter of each word
    newDomain.value.name = key
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  } else {
    newDomain.value.name = ''
  }
}

const previewNewDomainCalendar = async () => {
  // Don't preview if URL is empty or invalid
  if (!newDomain.value.calendar_url || !newDomain.value.calendar_url.startsWith('http')) {
    return
  }

  newDomainPreview.value.loading = true
  newDomainPreview.value.data = null

  try {
    const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
      calendar_url: newDomain.value.calendar_url
    })
    newDomainPreview.value.data = response.data
  } catch (error) {
    console.error('Failed to preview calendar:', error)
    newDomainPreview.value.data = {
      event_count: 0,
      events: [],
      error: error.response?.data?.detail || error.message || 'Failed to load preview'
    }
  } finally {
    newDomainPreview.value.loading = false
  }
}

// Auto-preview handlers
let previewTimeout = null

const handleCalendarUrlPaste = () => {
  // Wait a moment for paste to complete, then preview
  setTimeout(() => {
    previewNewDomainCalendar()
  }, 100)
}

const handleCalendarUrlBlur = () => {
  // Debounce preview on blur
  clearTimeout(previewTimeout)
  previewTimeout = setTimeout(() => {
    if (newDomain.value.calendar_url && !newDomainPreview.value.data) {
      previewNewDomainCalendar()
    }
  }, 300)
}

const createDomain = async () => {
  // If preview hasn't been run yet, or if URL changed since last preview, run it first
  if (!newDomainPreview.value.data || newDomainPreview.value.loading) {
    await previewNewDomainCalendar()

    // If preview shows an error, don't proceed
    if (newDomainPreview.value.data?.error) {
      notify.error('Cannot create domain: ' + newDomainPreview.value.data.error)
      return
    }
  }

  creatingDomain.value = true

  try {
    const token = localStorage.getItem('admin_token')

    // Auto-generate display name if not set
    if (!newDomain.value.name) {
      autoFillDisplayName()
    }

    const payload = {
      domain_key: newDomain.value.domain_key.trim().toLowerCase(),
      name: newDomain.value.name.trim(),
      calendar_url: newDomain.value.calendar_url.trim(),
      admin_password: newDomain.value.admin_password  // Required
    }

    // Add optional user password if provided
    if (newDomain.value.user_password) {
      payload.user_password = newDomain.value.user_password
    }

    const response = await axios.post(
      `${API_BASE_URL}/api/admin/domains`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    // Success - reset form and reload domains
    notify.success(t('admin.domains.createSuccess', { domainKey: response.data.domain_key }))

    // Reset form and preview
    newDomain.value = {
      domain_key: '',
      name: '',
      calendar_url: '',
      admin_password: '',
      user_password: ''
    }
    newDomainPreview.value = {
      loading: false,
      data: null
    }

    // Reload domains list
    await loadDomains()

  } catch (error) {
    console.error('Failed to create domain:', error)

    if (error.response?.status === 409) {
      notify.error(t('admin.domains.createErrorDuplicate', { domainKey: newDomain.value.domain_key }))
    } else if (error.response?.status === 404) {
      notify.error(t('admin.domains.createErrorUserNotFound', { username: newDomain.value.owner_username }))
    } else if (error.response?.status === 422) {
      notify.error(t('admin.domains.createErrorValidation', { detail: error.response?.data?.detail || t('admin.domains.invalidFormat') }))
    } else {
      notify.error(t('admin.domains.createError', { detail: error.response?.data?.detail || error.message }))
    }
  } finally {
    creatingDomain.value = false
  }
}

const startOwnerAssignment = (domainKey) => {
  assigningOwner.value = domainKey
  ownerSearchQuery.value = ''
  userSearchResults.value = []
}

const cancelOwnerAssignment = () => {
  assigningOwner.value = null
  ownerSearchQuery.value = ''
  userSearchResults.value = []
}

const searchUsers = async () => {
  const query = ownerSearchQuery.value.trim()

  if (!query || query.length < 1) {
    userSearchResults.value = []
    return
  }

  // Debounce search
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    searchingUsers.value = true
    try {
      const token = localStorage.getItem('admin_token')
      const response = await axios.get(
        `${API_BASE_URL}/api/admin/users/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      userSearchResults.value = response.data.users
    } catch (error) {
      console.error('Failed to search users:', error)
      userSearchResults.value = []
    } finally {
      searchingUsers.value = false
    }
  }, 300)
}

const assignOwner = async (domainKey, userId, username) => {
  try {
    const token = localStorage.getItem('admin_token')
    await axios.patch(
      `${API_BASE_URL}/api/admin/domains/${domainKey}/owner`,
      { user_id: userId },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    notify.success(t('admin.domains.assignOwnerSuccess', { domainKey, username }))

    // Update local domain list
    const domain = domains.value.find(d => d.domain_key === domainKey)
    if (domain) {
      domain.owner_username = username
      domain.owner_id = userId
    }

    cancelOwnerAssignment()
  } catch (error) {
    console.error('Failed to assign owner:', error)
    notify.error(t('admin.domains.assignOwnerError', { detail: error.response?.data?.detail || error.message }))
  }
}

const removeOwner = (domainKey) => {
  confirmDialogData.value = {
    title: t('admin.domains.removeOwnerTitle'),
    message: t('admin.domains.removeOwnerConfirm', { domainKey }),
    confirmText: t('common.remove'),
    onConfirm: async () => {
      try {
        const token = localStorage.getItem('admin_token')
        await axios.patch(
          `${API_BASE_URL}/api/admin/domains/${domainKey}/owner`,
          { user_id: null },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )

        notify.success(t('admin.domains.removeOwnerSuccess', { domainKey }))

        // Update local domain list
        const domain = domains.value.find(d => d.domain_key === domainKey)
        if (domain) {
          domain.owner_username = null
          domain.owner_id = null
        }
      } catch (error) {
        console.error('Failed to remove owner:', error)
        notify.error(t('admin.domains.removeOwnerError', { detail: error.response?.data?.detail || error.message }))
      }
    }
  }
  confirmDialog.value?.open()
}

const autoExpandPreviews = async () => {
  // Auto-load previews for all pending requests
  for (const request of pendingRequests.value) {
    // Initialize and expand
    icalPreviews.value[request.id] = { expanded: true, loading: true, data: null }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/ical/preview`, {
        calendar_url: request.calendar_url
      })

      icalPreviews.value[request.id].data = response.data

      // Auto-collapse if successful (no errors, has events)
      if (!response.data.error && response.data.event_count > 0) {
        icalPreviews.value[request.id].expanded = false
      }
      // Keep expanded if there's an error or no events (so admin sees it immediately)
    } catch (error) {
      icalPreviews.value[request.id].data = {
        event_count: 0,
        events: [],
        error: `Failed to load preview: ${error.response?.data?.detail || error.message}`
      }
      // Keep expanded to show error
    } finally {
      icalPreviews.value[request.id].loading = false
    }
  }
}

// Check for existing token on mount
onMounted(async () => {
  const token = localStorage.getItem('admin_token')
  const tokenExpires = localStorage.getItem('admin_token_expires')

  if (token && tokenExpires && Date.now() < parseInt(tokenExpires)) {
    // Token exists and hasn't expired
    isAuthenticated.value = true
    await Promise.all([loadRequests(), loadDomains(), loadAppSettings()])
  } else if (token) {
    // Token exists but has expired
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_token_expires')
  }
})
</script>

<style scoped>
/* Enhanced accessibility styles */

/* Focus visible styles for all interactive elements */
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
a:focus-visible,
[role="button"]:focus-visible,
[role="link"]:focus-visible {
  outline: 2px solid rgb(147 51 234); /* purple-600 */
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgb(243 232 255 / 1); /* purple-100 ring */
}

/* Dark mode focus styles */
.dark button:focus-visible,
.dark input:focus-visible,
.dark textarea:focus-visible,
.dark a:focus-visible,
.dark [role="button"]:focus-visible,
.dark [role="link"]:focus-visible {
  outline: 2px solid rgb(147 51 234); /* purple-600 */
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgb(88 28 135 / 0.5); /* purple-900/50 ring */
}

/* Ensure modals trap focus properly */
[role="dialog"] {
  isolation: isolate;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  button:focus-visible,
  input:focus-visible,
  textarea:focus-visible,
  a:focus-visible {
    outline-width: 3px;
    outline-offset: 3px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
