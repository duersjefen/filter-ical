# Test Coverage Gap Analysis Report

**Investigation Date:** 2025-10-11
**Application:** Filter iCal Frontend (Vue 3 + Vite + Vitest)
**Test Framework:** Vitest 3.2.4 + Vue Test Utils 2.4.6

---

## Executive Summary

The test suite has **critical gaps** that allowed 3 production errors to reach deployment:

1. ✅ **v-model on props error** (GroupFilterBar.vue) - NOT using v-model on props (false alarm)
2. ❌ **i18n missing key warnings** - Test setup lacks proper i18n mocking
3. ❌ **window.URL.createObjectURL missing mock** - jsdom environment incomplete

**Test Coverage Statistics:**
- **Total Vue Components:** 45
- **Component Tests:** 3 (6.7% coverage)
- **Total Test Files:** 25
- **Test Categories:** 23 unit tests, 2 E2E tests (both failing)

---

## Root Cause Analysis

### 1. V-Model on Props Error (FALSE ALARM)

**Status:** ✅ NOT AN ACTUAL ERROR

**Investigation:**
```vue
<!-- GroupFilterBar.vue lines 62 and 86 -->
<input
  :value="editingGroupName"
  @input="$emit('update:editingGroupName', $event.target.value)"
/>
<input
  :value="newGroupName"
  @input="$emit('update:newGroupName', $event.target.value)"
/>
```

**Finding:** This is **NOT** v-model on props. This is the **correct manual implementation** of v-model pattern using `:value` binding and `@input` emit. Vue only warns when you use `v-model="propName"` directly.

**Why Tests Didn't Catch:** No error exists to catch.

---

### 2. i18n Missing Key Warnings ⚠️ CRITICAL

**Root Cause:** Test environment has **ZERO i18n configuration**

**Evidence:**
```javascript
// tests/setup.js - NO i18n configuration
import { vi } from 'vitest';

// Mock global objects...
Object.defineProperty(window, 'matchMedia', { ... });
Object.defineProperty(window, 'localStorage', { ... });
global.fetch = vi.fn();

// ❌ NO i18n mock
// ❌ NO vue-i18n import
// ❌ NO $t function mock
```

**Component Under Test:**
```vue
<!-- GroupFilterBar.vue uses i18n extensively -->
<span>{{ t('domainAdmin.filterByGroup') }}</span>
<span>{{ $t('messages.holdCtrlMultipleGroups') }}</span>
<span>{{ $t('controls.addGroup') }}</span>
```

**Why Tests Didn't Catch:**
1. **NO component tests exist for GroupFilterBar.vue** (or 42 other components)
2. **Test setup has NO i18n mock** - components can't be tested
3. **App.test.js stubs out everything** - doesn't actually test real components:

```javascript
// tests/App.test.js
stubs: {
  RouterView: {
    template: '<div data-testid="router-view"><h1>iCal Viewer</h1></div>'
  }
}
```

**Actual Production Setup:**
```javascript
// src/main.js
import i18n from './i18n'
const app = createApp(App).use(pinia).use(i18n)

// src/i18n/locales/en.json has 854 lines of translations
```

**Impact:** ANY component using i18n will fail in tests.

---

### 3. window.URL.createObjectURL Missing Mock ⚠️ CRITICAL

**Root Cause:** jsdom doesn't implement browser file APIs

**Code Locations:**
```javascript
// 4 locations using window.URL.createObjectURL:
src/composables/useCalendar.js:159
src/stores/admin.js:102
src/views/AdminView.vue:323
src/views/AdminView.vue:466
```

**Example:**
```javascript
// src/composables/useCalendar.js
const blob = new Blob([icsContent], { type: 'text/calendar' })
const url = window.URL.createObjectURL(blob)  // ❌ undefined in jsdom
```

**Why Tests Didn't Catch:**
1. **NO tests exist for these components/composables**
2. **tests/setup.js doesn't mock URL.createObjectURL**
3. **E2E tests are excluded from Vitest:**

```javascript
// vitest.config.js
exclude: [
  '**/tests/e2e/**',  // Playwright E2E excluded from Vitest
]
```

**jsdom Limitation:** jsdom only implements ~80% of browser APIs. File/Blob/URL APIs are often missing.

---

## Component Test Coverage Gap Analysis

### Current State

**Components WITH Tests (3/45 = 6.7%):**
- ✅ BaseButton.vue (15 tests)
- ✅ BaseCard.vue (20 tests)
- ✅ FormInput.vue (18 tests)

**Components WITHOUT Tests (42/45 = 93.3%):**
- ❌ GroupFilterBar.vue (THE ERROR COMPONENT)
- ❌ AdminView.vue (uses createObjectURL)
- ❌ EventCardGrid.vue
- ❌ GroupCard.vue
- ❌ PreviewEventsSection.vue
- ❌ AppFooter.vue (i18n warnings in production)
- ❌ FilteredCalendarSection.vue
- ❌ ... 35 more components

### Test Strategy Analysis

**What IS Being Tested:**
1. ✅ **Composables** - 9 test files, comprehensive coverage
2. ✅ **Stores** - 5 test files, good coverage
3. ✅ **Utils** - 4 test files, 253 tests total
4. ✅ **Shared Components** - 3 basic components only

**What is NOT Being Tested:**
1. ❌ **Business Components** - 0 tests for calendar, admin, filtered-calendar components
2. ❌ **Views** - 0 tests for any view component
3. ❌ **i18n Integration** - Not configured in test environment
4. ❌ **Browser APIs** - No mocks for File/Blob/URL APIs
5. ❌ **Component Integration** - Components tested in isolation only

---

## Test Quality Assessment

### Unit Tests (23 files) ✅ GOOD QUALITY
```
✓ Pure function testing (composables, stores, utils)
✓ Comprehensive edge cases
✓ 664 tests passing
✓ Fast execution (< 3 seconds)
```

### Component Tests (3 files) ⚠️ LIMITED SCOPE
```
✓ Tests basic props/events/rendering
⚠️ Only tests simple shared components
❌ No business logic components tested
❌ No i18n integration
❌ No API integration
```

### Integration Tests (0 files) ❌ NONE
```
❌ No multi-component integration tests
❌ No store + component tests
❌ No router integration tests
```

### E2E Tests (3 files) ❌ BROKEN
```
❌ 2 tests failing in src/test/
❌ 3 Playwright tests in tests/e2e/ (excluded from Vitest)
⚠️ Mixing test frameworks (Vitest + Playwright)
```

---

## Why These Specific Errors Weren't Caught

### Error 1: V-Model on Props (FALSE ALARM)
**Not an error.** Code correctly implements v-model pattern.

### Error 2: i18n Warnings in Footer
**Missing Test Infrastructure:**
1. No i18n mock in tests/setup.js
2. No AppFooter.vue tests
3. App.test.js stubs out all real components
4. Test would look like this (doesn't exist):

```javascript
// ❌ This test file doesn't exist
// tests/components/shared/AppFooter.test.js
import { mount } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'
import AppFooter from '@/components/shared/AppFooter.vue'
import en from '@/i18n/locales/en.json'

describe('AppFooter', () => {
  it('renders all footer text without i18n errors', () => {
    const i18n = createI18n({
      locale: 'en',
      messages: { en }
    })
    const wrapper = mount(AppFooter, {
      global: { plugins: [i18n] }
    })

    // This would fail if i18n keys are missing
    expect(wrapper.html()).toContain('Support Server')
  })
})
```

### Error 3: createObjectURL Not Mocked
**Missing Browser API Mocks:**
1. tests/setup.js doesn't mock URL.createObjectURL
2. No tests for components using it
3. Should have this in setup.js:

```javascript
// ❌ This mock doesn't exist in tests/setup.js
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()
```

---

## Missing Test Infrastructure

### 1. i18n Configuration
```javascript
// ❌ Missing from tests/setup.js
import { createI18n } from 'vue-i18n'
import en from '../src/i18n/locales/en.json'

global.i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: { en }
})
```

### 2. Browser API Mocks
```javascript
// ❌ Missing from tests/setup.js
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
global.URL.revokeObjectURL = vi.fn()
```

### 3. Test Utilities
```javascript
// ❌ Missing: tests/test-utils.js
export function mountWithPlugins(component, options = {}) {
  return mount(component, {
    global: {
      plugins: [createPinia(), i18n, router],
      ...options.global
    },
    ...options
  })
}
```

### 4. Component Test Templates
No systematic approach to testing components. Should have:
- Template for testing business components
- Template for testing views
- Template for integration tests

---

## Configuration Issues

### 1. Test Environment Setup (vitest.config.js)
```javascript
test: {
  environment: 'jsdom',
  setupFiles: ['./tests/setup.js'],  // ✅ Has setup file
  globals: true,
  exclude: [
    '**/tests/e2e/**',  // ⚠️ E2E tests excluded
  ]
}
```

**Issues:**
- ✅ jsdom environment configured
- ❌ Setup file incomplete (missing i18n, URL mocks)
- ⚠️ E2E tests excluded (using Playwright separately)

### 2. No ESLint Configuration
```bash
$ npm list eslint
└── (empty)
```

**Impact:** No static analysis to catch:
- v-model on props (would be caught by `vue/no-mutating-props`)
- Missing i18n keys
- Unused variables/imports

### 3. Vue SFC Compilation
```javascript
// vitest.config.js
plugins: [vue()],  // ✅ SFC compiler configured
```

**Status:** ✅ Vue SFCs compile correctly in tests

---

## Production vs Test Environment Comparison

### Production (src/main.js)
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter } from 'vue-router'
import i18n from './i18n'  // ✅ Full i18n
import App from './App.vue'

createApp(App)
  .use(createPinia())
  .use(i18n)  // ✅ i18n available
  .use(router)
  .mount('#app')
```

### Tests (tests/setup.js)
```javascript
import { vi } from 'vitest'

// ✅ Mock window.matchMedia
// ✅ Mock localStorage
// ✅ Mock fetch
// ❌ NO i18n
// ❌ NO URL.createObjectURL
// ❌ NO Pinia
// ❌ NO Router
```

**Gap:** Tests run in a vastly different environment than production.

---

## Recommendations

### Immediate Fixes (P0 - Deploy Today)

1. **Add i18n Mock to tests/setup.js**
```javascript
import { createI18n } from 'vue-i18n'
import en from '../src/i18n/locales/en.json'
import de from '../src/i18n/locales/de.json'

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en, de },
  globalInjection: true,
  silentTranslationWarn: false,  // Fail on missing keys
  missingWarn: true
})

// Make available globally for tests
global.i18n = i18n
```

2. **Add Browser API Mocks to tests/setup.js**
```javascript
// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn((blob) => {
  return `blob:mock-${Math.random().toString(36).substring(7)}`
})
global.URL.revokeObjectURL = vi.fn()
```

3. **Create Test Utility Helper**
```javascript
// tests/test-utils.js
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import i18n from './setup'  // Use the i18n from setup

export function mountComponent(component, options = {}) {
  const pinia = createPinia()

  return mount(component, {
    global: {
      plugins: [pinia, i18n],
      ...options.global
    },
    ...options
  })
}
```

### Short-term Improvements (P1 - This Week)

4. **Add ESLint + Vue Plugin**
```bash
npm install --save-dev eslint eslint-plugin-vue
```

Create eslint.config.js:
```javascript
import pluginVue from 'eslint-plugin-vue'

export default [
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'vue/no-mutating-props': 'error',  // Catch v-model on props
      'vue/require-v-for-key': 'error',
      'vue/no-unused-components': 'warn'
    }
  }
]
```

5. **Test GroupFilterBar.vue**
```javascript
// tests/components/admin/event-management/GroupFilterBar.test.js
import { describe, it, expect } from 'vitest'
import { mountComponent } from '../../../test-utils'
import GroupFilterBar from '@/components/admin/event-management/GroupFilterBar.vue'

describe('GroupFilterBar', () => {
  const defaultProps = {
    groups: [],
    activeGroupFilters: [],
    totalEventsCount: 0,
    unassignedEventsCount: 0,
    getGroupEventCount: () => 0
  }

  it('renders without i18n errors', () => {
    const wrapper = mountComponent(GroupFilterBar, {
      props: defaultProps
    })

    // Would catch missing i18n keys
    expect(wrapper.find('h3').text()).toContain('Filter')
  })

  it('emits update:newGroupName when input changes', async () => {
    const wrapper = mountComponent(GroupFilterBar, {
      props: { ...defaultProps, showAddGroupForm: true }
    })

    const input = wrapper.find('input')
    await input.setValue('New Group')

    expect(wrapper.emitted('update:newGroupName')).toBeTruthy()
    expect(wrapper.emitted('update:newGroupName')[0]).toEqual(['New Group'])
  })
})
```

6. **Test AppFooter.vue**
```javascript
// tests/components/shared/AppFooter.test.js
import { describe, it, expect } from 'vitest'
import { mountComponent } from '../../test-utils'
import AppFooter from '@/components/shared/AppFooter.vue'

describe('AppFooter', () => {
  it('renders all footer translations without errors', () => {
    const wrapper = mountComponent(AppFooter)

    // These are the keys that were missing warnings in production
    expect(wrapper.text()).toContain('Support')
    expect(wrapper.text()).toContain('2025')
    expect(wrapper.text()).toContain('community')
  })
})
```

### Long-term Strategy (P2 - Next Sprint)

7. **Systematic Component Testing Strategy**
   - Test ALL 45 components (not just 3)
   - Priority: Admin components → Calendar components → Preview components
   - Target: 80% component coverage

8. **Integration Test Suite**
   - Store + Component integration
   - Router navigation flows
   - Multi-component interactions

9. **CI/CD Gate Improvements**
   - Add ESLint to CI pipeline
   - Fail on i18n missing keys
   - Coverage thresholds (min 70%)

10. **Test Organization Restructure**
```
tests/
├── unit/           # Pure functions
├── components/     # Component tests (expand to 45)
├── integration/    # Multi-component tests
├── e2e/           # Playwright E2E
├── setup.js       # Global test setup
└── test-utils.js  # Test helpers
```

---

## Success Criteria

### Phase 1: Immediate (Complete by EOD)
- ✅ i18n mock in tests/setup.js
- ✅ URL.createObjectURL mock in tests/setup.js
- ✅ Test utility helper created
- ✅ AppFooter.vue test added
- ✅ GroupFilterBar.vue test added

### Phase 2: Short-term (Complete this week)
- ✅ ESLint + vue plugin installed
- ✅ 10 critical component tests added
- ✅ All i18n keys validated in tests

### Phase 3: Long-term (Next sprint)
- ✅ 80% component test coverage
- ✅ Integration test suite
- ✅ CI/CD gates for code quality

---

## Test Execution Evidence

```bash
$ npm run test
 Test Files  2 failed | 23 passed (25)
      Tests  664 passed | 8 skipped (672)
   Duration  2.69s
```

**Breakdown:**
- ✅ 23 test files passing (composables, stores, utils)
- ❌ 2 E2E test files failing (expected - need backend running)
- ⚠️ 664 tests but only 3 component files

**Coverage by Type:**
- Composables: 54 + 46 + 36 + 19 + 53 + 17 + 8 + 6 = 239 tests
- Stores: 23 + 20 + 15 + 10 = 68 tests
- Utils: 90 + 56 + 65 + 42 = 253 tests
- Components: 15 + 20 + 18 = 53 tests
- Other: 51 tests

**Red Flag:** Only 7.9% of tests are component tests (53/664).

---

## Conclusion

The test suite is **well-designed for pure functions** (composables, stores, utils) but has **critical gaps in component testing** and **test environment setup**.

**Primary Failure Modes:**
1. ❌ **93.3% of components have ZERO tests**
2. ❌ **Test environment missing i18n** - can't test real components
3. ❌ **Test environment missing browser APIs** - can't test file operations
4. ⚠️ **No ESLint** - static analysis would catch many issues

**Why Errors Reached Production:**
- GroupFilterBar.vue: No component test exists
- i18n warnings: No i18n in test environment + no AppFooter test
- createObjectURL: No URL API mock + no tests for those components

**Immediate Action Required:**
1. Fix tests/setup.js (add i18n + URL mocks)
2. Add ESLint with Vue plugin
3. Write tests for 10 critical components
4. Make "no component changes without tests" a CI gate

---

**Report Generated:** 2025-10-11
**Confidence Level:** HIGH (based on complete codebase analysis)
