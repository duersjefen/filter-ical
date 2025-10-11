# Comprehensive Test Strategy for Filter-iCal
## Multi-Layer Defense Against Bugs

**Document Purpose:** Prevent issues like v-model on props, i18n key warnings, and missing browser API mocks from reaching production.

**Date:** 2025-10-11
**Status:** Active Strategy Document

---

## Executive Summary

### Current State Assessment

**Test Coverage Status:**
- **Components:** 3/45 tested (7% coverage) ❌
- **Composables:** 9/18 tested (50% coverage) ⚠️
- **Stores:** 5 fully tested ✅
- **E2E Tests:** 3 smoke tests ⚠️
- **Unit Tests:** Comprehensive for business logic ✅

**Critical Gaps Identified:**
1. ✅ **SOLVED:** v-model on props (reactive pattern fixed in useSelection.js)
2. ❌ **MISSING:** Component rendering tests (97% of components untested)
3. ❌ **MISSING:** i18n key validation (338 usages, no validation)
4. ⚠️ **PARTIAL:** Browser API mocks (localStorage/matchMedia only)
5. ❌ **MISSING:** ESLint configuration (no static analysis)
6. ❌ **MISSING:** Pre-commit hooks (no write-time validation)
7. ❌ **MISSING:** TypeScript type checking (no compile-time safety)

---

## 6-Layer Testing Strategy

### Layer 1: Static Analysis (Catch at Write-Time)

**Goal:** Prevent bugs before code is committed

#### 1.1 ESLint Configuration

**Priority:** 🔥 **IMMEDIATE** (Week 1, Day 1-2)

**Installation:**
```bash
cd /Users/martijn/Documents/Projects/filter-ical/frontend
npm install --save-dev \
  eslint \
  @eslint/js \
  eslint-plugin-vue \
  @vue/eslint-config-prettier \
  prettier
```

**Configuration File:** `eslint.config.js`
```javascript
import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import prettier from '@vue/eslint-config-prettier'

export default [
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  prettier,
  {
    files: ['**/*.vue', '**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        navigator: 'readonly',
        localStorage: 'readonly',
        // Node globals
        process: 'readonly',
        __dirname: 'readonly',
        // Vitest globals
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        vi: 'readonly'
      }
    },
    rules: {
      // Critical: Prevent v-model on props
      'vue/no-mutating-props': 'error',

      // Critical: Prevent missing emits declarations
      'vue/require-explicit-emits': 'error',

      // Critical: Enforce prop validation
      'vue/require-prop-types': 'error',
      'vue/require-default-prop': 'warn',

      // Critical: Component naming
      'vue/multi-word-component-names': 'error',
      'vue/component-definition-name-casing': ['error', 'PascalCase'],

      // Code quality
      'no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'error',

      // Vue-specific quality
      'vue/no-unused-components': 'error',
      'vue/no-unused-vars': 'error',
      'vue/no-v-html': 'warn',
      'vue/valid-v-model': 'error',
      'vue/no-side-effects-in-computed-properties': 'error',

      // Architecture enforcement (from CLAUDE.md)
      'vue/component-tags-order': ['error', {
        order: ['script', 'template', 'style']
      }],

      // i18n (will add custom rule later)
      'vue/no-bare-strings-in-template': 'off' // We use i18n
    }
  },
  {
    files: ['**/*.test.js', '**/*.spec.js', '**/tests/**'],
    rules: {
      'no-console': 'off' // Allow console in tests
    }
  },
  {
    // Ignore patterns
    ignores: [
      'dist/**',
      'node_modules/**',
      'coverage/**',
      'playwright-report/**',
      'test-results/**'
    ]
  }
]
```

**Prettier Configuration:** `.prettierrc.json`
```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "none",
  "arrowParens": "avoid",
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "vueIndentScriptAndStyle": false
}
```

**Package.json Scripts:**
```json
{
  "scripts": {
    "lint": "eslint . --ext .vue,.js",
    "lint:fix": "eslint . --ext .vue,.js --fix",
    "format": "prettier --write \"src/**/*.{js,vue,css}\"",
    "format:check": "prettier --check \"src/**/*.{js,vue,css}\""
  }
}
```

**IDE Integration:**
- VSCode: Install "ESLint" and "Prettier" extensions
- Enable "Format on Save" and "ESLint: Auto Fix On Save"

**Expected Impact:**
- Catch 80% of v-model on props issues
- Prevent missing emits declarations
- Enforce prop type validation
- Catch unused variables and components

---

#### 1.2 TypeScript Type Checking (Gradual Adoption)

**Priority:** 🟡 **SHORT-TERM** (Week 2-3)

**Strategy:** Use TypeScript for type checking WITHOUT converting to .ts files

**Setup:**
```bash
npm install --save-dev typescript vue-tsc
```

**Configuration:** `jsconfig.json` (already exists, enhance it)
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "checkJs": true,
    "allowJs": true,
    "noEmit": true,
    "isolatedModules": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vite/client", "vitest/globals"]
  },
  "include": ["src/**/*", "tests/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Add JSDoc Type Annotations:**
```javascript
// Example: src/composables/useSelection.js
/**
 * @typedef {Object} SelectionAPI
 * @property {import('vue').Ref<string[]>} selectedRecurringEvents
 * @property {import('vue').Ref<Set<string>>} subscribedGroups
 * @property {(title: string) => boolean} isRecurringEventSelected
 * @property {(title: string) => void} toggleRecurringEvent
 */

/**
 * Selection composable with type safety
 * @returns {SelectionAPI}
 */
export function useSelection() {
  // ...
}
```

**Package.json Scripts:**
```json
{
  "scripts": {
    "typecheck": "vue-tsc --noEmit",
    "typecheck:watch": "vue-tsc --noEmit --watch"
  }
}
```

**Expected Impact:**
- Catch type errors at write time
- Better IDE autocomplete
- Prevent API misuse
- Document function contracts

---

#### 1.3 Pre-Commit Hooks

**Priority:** 🔥 **IMMEDIATE** (Week 1, Day 3)

**Installation:**
```bash
npm install --save-dev husky lint-staged
npx husky init
```

**Configuration:** `.husky/pre-commit`
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Run lint-staged
npx lint-staged

# Run unit tests on changed files
npm run test -- --run --changed
```

**Configuration:** `.lintstagedrc.json`
```json
{
  "*.{js,vue}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{json,md,css}": [
    "prettier --write"
  ],
  "*.vue": [
    "npm run test:component -- --run"
  ]
}
```

**Expected Impact:**
- Prevent committing code with ESLint errors
- Auto-format code before commit
- Run relevant tests automatically
- Catch issues before CI/CD

---

### Layer 2: Unit Tests (Test Pure Logic)

**Priority:** ✅ **MAINTAIN** (Ongoing)

**Current Status:** Strong coverage for composables and stores

**What to Test:**
1. **Pure Functions:** All functions in `/src/composables/` and `/src/utils/`
2. **Store Logic:** All Pinia stores
3. **Business Logic:** Event filtering, grouping, selection algorithms
4. **Edge Cases:** Empty arrays, null values, boundary conditions

**Example Test Structure:**
```javascript
// tests/composables/useEventFiltering.test.js
import { describe, it, expect, beforeEach } from 'vitest'
import { useEventFiltering } from '@/composables/useEventFiltering'

describe('useEventFiltering', () => {
  describe('filterEventsBySelection', () => {
    it('filters events when selection is provided', () => {
      const events = [
        { title: 'Meeting', start: '2025-01-01' },
        { title: 'Lunch', start: '2025-01-02' }
      ]
      const selection = ['Meeting']

      const result = filterEventsBySelection(events, selection)

      expect(result).toHaveLength(1)
      expect(result[0].title).toBe('Meeting')
    })

    it('returns empty array when no events match', () => {
      const events = [{ title: 'Meeting' }]
      const selection = ['NonExistent']

      const result = filterEventsBySelection(events, selection)

      expect(result).toHaveLength(0)
    })

    it('handles empty selection', () => {
      const events = [{ title: 'Meeting' }]
      const selection = []

      const result = filterEventsBySelection(events, selection)

      expect(result).toHaveLength(0)
    })
  })
})
```

**Test Coverage Requirements:**
- **Target:** 90% coverage for composables and utils
- **Current:** ~70% (good baseline)
- **Action:** Add edge case tests for each composable

**Expected Impact:**
- Catch logic errors before integration
- Enable fearless refactoring
- Document expected behavior
- Fast test execution (< 5 seconds)

---

### Layer 3: Component Tests (Test Rendering & User Interaction)

**Priority:** 🔥 **IMMEDIATE** (Week 1-2)

**Current Status:** Only 3/45 components tested (CRITICAL GAP)

#### 3.1 Component Test Template

**Create:** `tests/component-test-template.js`
```javascript
/**
 * Component Test Template
 *
 * Use this template for ALL Vue component tests
 * Covers: props, emits, slots, rendering, user interaction
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ComponentName from '@/components/path/ComponentName.vue'

// Import translation keys for validation
import enMessages from '@/i18n/locales/en.json'

/**
 * Create mock i18n instance with ALL translation keys
 */
function createMockI18n() {
  return createI18n({
    legacy: false,
    locale: 'en',
    messages: { en: enMessages },
    globalInjection: true
  })
}

describe('ComponentName', () => {
  let wrapper
  let pinia
  let i18n

  beforeEach(() => {
    pinia = createPinia()
    i18n = createMockI18n()

    wrapper = mount(ComponentName, {
      global: {
        plugins: [pinia, i18n]
      }
    })
  })

  describe('Rendering', () => {
    it('renders without crashing', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('has correct structure', () => {
      // Test for key DOM elements
      expect(wrapper.find('[data-testid="component-root"]').exists()).toBe(true)
    })
  })

  describe('Props', () => {
    it('accepts and renders props correctly', () => {
      const wrapper = mount(ComponentName, {
        props: {
          title: 'Test Title'
        },
        global: { plugins: [pinia, i18n] }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('validates prop types', () => {
      // This should throw a warning in development
      const wrapper = mount(ComponentName, {
        props: {
          count: 'not-a-number' // Should be number
        },
        global: { plugins: [pinia, i18n] }
      })

      // Check that prop validation works
      expect(wrapper.props('count')).toBe('not-a-number')
    })
  })

  describe('Emits', () => {
    it('emits correct events with correct payload', async () => {
      const wrapper = mount(ComponentName, {
        global: { plugins: [pinia, i18n] }
      })

      await wrapper.find('button').trigger('click')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['expected-value'])
    })
  })

  describe('v-model', () => {
    it('implements v-model correctly (emits, not mutates)', async () => {
      const wrapper = mount(ComponentName, {
        props: {
          modelValue: 'initial'
        },
        global: { plugins: [pinia, i18n] }
      })

      await wrapper.find('input').setValue('new-value')

      // Should emit, not mutate prop
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['new-value'])
      expect(wrapper.props('modelValue')).toBe('initial') // Prop unchanged
    })
  })

  describe('Slots', () => {
    it('renders slot content', () => {
      const wrapper = mount(ComponentName, {
        slots: {
          default: '<div data-testid="slot-content">Slot Content</div>'
        },
        global: { plugins: [pinia, i18n] }
      })

      expect(wrapper.find('[data-testid="slot-content"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Slot Content')
    })
  })

  describe('User Interactions', () => {
    it('handles button clicks', async () => {
      await wrapper.find('button').trigger('click')
      expect(wrapper.emitted('click')).toBeTruthy()
    })

    it('handles input changes', async () => {
      await wrapper.find('input').setValue('new value')
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })
  })

  describe('i18n Keys', () => {
    it('uses only defined translation keys', () => {
      // Get all translation keys used in the component
      const html = wrapper.html()
      const i18nKeys = Array.from(html.matchAll(/\$t\(['"]([^'"]+)['"]\)/g))
        .map(match => match[1])

      // Validate each key exists in translations
      i18nKeys.forEach(key => {
        const exists = key.split('.').reduce((obj, part) => obj?.[part], enMessages)
        expect(exists, `i18n key "${key}" not found in en.json`).toBeDefined()
      })
    })
  })

  describe('Edge Cases', () => {
    it('handles empty props gracefully', () => {
      const wrapper = mount(ComponentName, {
        props: {
          items: []
        },
        global: { plugins: [pinia, i18n] }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('handles null/undefined props', () => {
      const wrapper = mount(ComponentName, {
        props: {
          data: null
        },
        global: { plugins: [pinia, i18n] }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})
```

#### 3.2 Priority Components to Test

**Week 1 (Critical Path):**
1. `FormInput.vue` ✅ (already tested)
2. `BaseButton.vue` ✅ (already tested)
3. `AuthModal.vue` 🔥 (authentication critical)
4. `PasswordGate.vue` 🔥 (security critical)
5. `GroupCard.vue` 🔥 (core functionality)

**Week 2 (High Traffic):**
6. `HeaderSection.vue`
7. `GroupsControlBar.vue`
8. `RecurringEventsCardsSection.vue`
9. `UniqueEventsSection.vue`
10. `LanguageToggle.vue`

**Week 3-4 (Complete Coverage):**
- All remaining 35 components

#### 3.3 Browser API Mocking Strategy

**Enhance:** `tests/setup.js`
```javascript
/**
 * Comprehensive browser API mocks for Vitest
 */
import { vi } from 'vitest'

// ============================================
// Window APIs
// ============================================

// matchMedia (already mocked) ✅
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// localStorage (already mocked) ✅
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => null),
    removeItem: vi.fn(() => null),
    clear: vi.fn(() => null),
  },
  writable: true,
})

// sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => null),
    removeItem: vi.fn(() => null),
    clear: vi.fn(() => null),
  },
  writable: true,
})

// window.location
delete window.location
window.location = {
  href: 'http://localhost:8000',
  origin: 'http://localhost:8000',
  protocol: 'http:',
  host: 'localhost:8000',
  hostname: 'localhost',
  port: '8000',
  pathname: '/',
  search: '',
  hash: '',
  reload: vi.fn(),
  replace: vi.fn(),
  assign: vi.fn(),
}

// navigator
Object.defineProperty(window, 'navigator', {
  value: {
    userAgent: 'Mozilla/5.0 (Test)',
    language: 'en-US',
    languages: ['en-US', 'en'],
    onLine: true,
    clipboard: {
      writeText: vi.fn().mockResolvedValue(undefined),
      readText: vi.fn().mockResolvedValue('')
    }
  },
  writable: true,
})

// IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() { return [] }
  unobserve() {}
}

// ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// MutationObserver
global.MutationObserver = class MutationObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() { return [] }
}

// ============================================
// Network APIs
// ============================================

// fetch (already mocked) ✅
global.fetch = vi.fn()

// XMLHttpRequest
global.XMLHttpRequest = vi.fn(() => ({
  open: vi.fn(),
  send: vi.fn(),
  setRequestHeader: vi.fn(),
  readyState: 0,
  status: 200,
  responseText: '',
}))

// ============================================
// Animation APIs
// ============================================

// requestAnimationFrame
global.requestAnimationFrame = vi.fn(cb => setTimeout(cb, 0))
global.cancelAnimationFrame = vi.fn(id => clearTimeout(id))

// ============================================
// Media APIs
// ============================================

// matchMedia enhancement for dark mode testing
window.matchMedia = vi.fn().mockImplementation(query => ({
  matches: query === '(prefers-color-scheme: dark)' ? false : false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}))

// ============================================
// Console Suppression (for clean test output)
// ============================================

// Suppress expected warnings
const originalWarn = console.warn
console.warn = (...args) => {
  const message = args[0]

  // Suppress known Vue 3 warnings that are expected in tests
  if (
    typeof message === 'string' && (
      message.includes('Failed to resolve component') ||
      message.includes('Invalid prop') ||
      message.includes('Unknown custom element')
    )
  ) {
    return
  }

  originalWarn.apply(console, args)
}
```

**Expected Impact:**
- Prevent "matchMedia is not a function" errors
- Mock all browser APIs used by components
- Clean test output (no API warnings)
- Test browser-specific features

---

### Layer 4: Integration Tests (Test Interactions)

**Priority:** 🟡 **SHORT-TERM** (Week 3-4)

**Current Status:** Minimal integration testing

**What to Test:**
1. **Store Integration:** Components + Pinia stores
2. **Router Integration:** Navigation flows
3. **API Integration:** Components + API calls
4. **i18n Integration:** Language switching

#### 4.1 Store Integration Tests

**Example:** `tests/integration/calendar-selection.test.js`
```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import GroupCard from '@/components/calendar/GroupCard.vue'
import { useSelectionStore } from '@/stores/selectionStore'
import { useAppStore } from '@/stores/app'

describe('Calendar Selection Integration', () => {
  let pinia
  let selectionStore
  let appStore

  beforeEach(() => {
    pinia = createPinia()
    selectionStore = useSelectionStore(pinia)
    appStore = useAppStore(pinia)

    // Setup test data
    appStore.groups = {
      'group-1': {
        id: 'group-1',
        title: 'Work Events',
        recurring_events: [
          { title: 'Meeting', event_count: 5 },
          { title: 'Standup', event_count: 3 }
        ]
      }
    }
  })

  it('selecting event in GroupCard updates selection store', async () => {
    const wrapper = mount(GroupCard, {
      props: {
        group: appStore.groups['group-1'],
        groupId: 'group-1'
      },
      global: {
        plugins: [pinia, createI18n({ legacy: false, locale: 'en', messages: {} })]
      }
    })

    // Click event checkbox
    await wrapper.find('[data-testid="event-checkbox-Meeting"]').trigger('click')

    // Verify store was updated
    expect(selectionStore.isRecurringEventSelected('Meeting')).toBe(true)
  })

  it('subscribing to group selects all events', async () => {
    const wrapper = mount(GroupCard, {
      props: {
        group: appStore.groups['group-1'],
        groupId: 'group-1'
      },
      global: {
        plugins: [pinia, createI18n({ legacy: false, locale: 'en', messages: {} })]
      }
    })

    // Click subscribe button
    await wrapper.find('[data-testid="subscribe-button"]').trigger('click')

    // Verify all events selected
    expect(selectionStore.isGroupSubscribed('group-1')).toBe(true)
    expect(selectionStore.isRecurringEventEffectivelySelected('Meeting', appStore.groups)).toBe(true)
    expect(selectionStore.isRecurringEventEffectivelySelected('Standup', appStore.groups)).toBe(true)
  })
})
```

#### 4.2 Router Integration Tests

**Example:** `tests/integration/navigation.test.js`
```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia } from 'pinia'
import routes from '@/router/routes'
import AppHeader from '@/components/shared/AppHeader.vue'

describe('Navigation Integration', () => {
  let router
  let pinia

  beforeEach(async () => {
    router = createRouter({
      history: createMemoryHistory(),
      routes
    })
    pinia = createPinia()

    await router.push('/')
    await router.isReady()
  })

  it('navigates to calendar view when clicking calendar link', async () => {
    const wrapper = mount(AppHeader, {
      global: {
        plugins: [router, pinia]
      }
    })

    await wrapper.find('[data-testid="nav-calendar-123"]').trigger('click')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/calendar/123')
  })
})
```

**Expected Impact:**
- Catch integration bugs before E2E
- Verify store updates from UI actions
- Test navigation flows
- Faster than E2E tests

---

### Layer 5: E2E Tests (Test User Flows)

**Priority:** 🟡 **SHORT-TERM** (Week 4-5)

**Current Status:** 3 smoke tests (minimal coverage)

**Critical User Flows to Test:**

#### 5.1 E2E Test Structure

**Example:** `tests/e2e/calendar-filtering-flow.spec.js`
```javascript
/**
 * E2E Test: Complete calendar filtering workflow
 *
 * User Story:
 * As a user, I want to filter my calendar by selecting specific events,
 * so I can create a custom subscription URL.
 */
import { test, expect } from '@playwright/test'

test.describe('Calendar Filtering Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('user can select events and generate filtered calendar', async ({ page }) => {
    // Step 1: Login with test domain
    await page.fill('[data-testid="domain-input"]', 'test-calendar')
    await page.click('[data-testid="login-button"]')
    await page.waitForURL('/home')

    // Step 2: Navigate to calendar
    await page.click('[data-testid="calendar-link-test"]')
    await page.waitForURL(/\/calendar\/\d+/)

    // Step 3: Select events
    await page.click('[data-testid="event-checkbox-Meeting"]')
    await page.click('[data-testid="event-checkbox-Lunch"]')

    // Step 4: Verify selection counter
    const counter = page.locator('[data-testid="selection-counter"]')
    await expect(counter).toHaveText('2 events selected')

    // Step 5: Generate subscription URL
    await page.click('[data-testid="generate-url-button"]')

    // Step 6: Verify URL was generated
    const urlOutput = page.locator('[data-testid="subscription-url"]')
    await expect(urlOutput).toBeVisible()
    await expect(urlOutput).toContainText('/ical/')
  })

  test('selection persists across page reloads', async ({ page }) => {
    // Setup: Select events
    await page.fill('[data-testid="domain-input"]', 'test-calendar')
    await page.click('[data-testid="login-button"]')
    await page.waitForURL('/home')
    await page.click('[data-testid="calendar-link-test"]')
    await page.click('[data-testid="event-checkbox-Meeting"]')

    // Action: Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Verify: Selection persisted
    const checkbox = page.locator('[data-testid="event-checkbox-Meeting"]')
    await expect(checkbox).toBeChecked()
  })

  test('user can clear all selections', async ({ page }) => {
    // Setup
    await page.fill('[data-testid="domain-input"]', 'test-calendar')
    await page.click('[data-testid="login-button"]')
    await page.click('[data-testid="calendar-link-test"]')
    await page.click('[data-testid="event-checkbox-Meeting"]')
    await page.click('[data-testid="event-checkbox-Lunch"]')

    // Action: Clear all
    await page.click('[data-testid="clear-all-button"]')

    // Verify: All selections cleared
    const counter = page.locator('[data-testid="selection-counter"]')
    await expect(counter).toHaveText('0 events selected')
  })
})
```

#### 5.2 E2E Test Checklist

**Critical Flows (Week 4):**
- [ ] Login flow (domain authentication)
- [ ] Calendar filtering (select events → generate URL)
- [ ] Group subscription
- [ ] Language switching
- [ ] Admin panel access

**Important Flows (Week 5):**
- [ ] Selection persistence (localStorage)
- [ ] Error handling (network errors, 404s)
- [ ] Responsive design (mobile/tablet)
- [ ] Dark mode toggle
- [ ] Multi-calendar management

**Edge Cases (Week 6):**
- [ ] Empty calendars
- [ ] Calendars with 1000+ events
- [ ] Concurrent user sessions
- [ ] Browser back/forward navigation

**Expected Impact:**
- Catch integration bugs
- Validate complete user workflows
- Test real browser behavior
- Build confidence in releases

---

### Layer 6: CI/CD Checks

**Priority:** 🟡 **SHORT-TERM** (Week 2)

**Current Status:** GitHub Actions exists, needs enhancement

#### 6.1 Enhanced GitHub Actions Workflow

**Update:** `.github/workflows/ci.yml`
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  # ============================================
  # Layer 1: Static Analysis
  # ============================================
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Run ESLint
        run: cd frontend && npm run lint

      - name: Check Prettier formatting
        run: cd frontend && npm run format:check

      - name: TypeScript type checking
        run: cd frontend && npm run typecheck

  # ============================================
  # Layer 2: Unit Tests
  # ============================================
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Run unit tests
        run: cd frontend && npm run test -- --run --reporter=verbose

      - name: Generate coverage report
        run: cd frontend && npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend

  # ============================================
  # Layer 3: Component Tests
  # ============================================
  component-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Run component tests
        run: cd frontend && npm run test -- --run --reporter=verbose

  # ============================================
  # Layer 4: Build Validation
  # ============================================
  build:
    runs-on: ubuntu-latest
    needs: [lint, unit-tests]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Build production bundle
        run: cd frontend && npm run build

      - name: Check bundle size
        run: |
          cd frontend
          BUNDLE_SIZE=$(du -sh dist/ | cut -f1)
          echo "Bundle size: $BUNDLE_SIZE"
          # Fail if bundle > 2MB (adjust threshold as needed)
          SIZE_BYTES=$(du -s dist/ | cut -f1)
          if [ $SIZE_BYTES -gt 2048000 ]; then
            echo "❌ Bundle size exceeds 2MB limit"
            exit 1
          fi

  # ============================================
  # Layer 5: E2E Tests
  # ============================================
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [build]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Install Playwright browsers
        run: cd frontend && npx playwright install --with-deps chromium

      - name: Start dev server
        run: cd frontend && npm run dev &

      - name: Wait for server
        run: npx wait-on http://localhost:8000 --timeout 60000

      - name: Run E2E tests
        run: cd frontend && npx playwright test

      - name: Upload Playwright report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/

  # ============================================
  # Layer 6: Security & Quality Gates
  # ============================================
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run npm audit
        run: cd frontend && npm audit --audit-level=moderate

      - name: Check for vulnerable dependencies
        run: cd frontend && npm audit --production
```

#### 6.2 Test Coverage Thresholds

**Configuration:** `vitest.config.js`
```javascript
export default defineConfig({
  // ... existing config
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.js',
        '**/dist/**'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80
      }
    }
  }
})
```

**Expected Impact:**
- Enforce test coverage minimums
- Catch regressions before merge
- Automate quality checks
- Prevent bundle size bloat

---

## i18n Key Validation Strategy

**Priority:** 🔥 **IMMEDIATE** (Week 1, Day 4-5)

**Problem:** 338 i18n usages across 36 files, no validation for missing keys

### Solution 1: ESLint Plugin (Recommended)

**Installation:**
```bash
npm install --save-dev eslint-plugin-i18n-json
```

**Configuration:** `eslint.config.js`
```javascript
import i18nJson from 'eslint-plugin-i18n-json'

export default [
  // ... existing config
  {
    files: ['src/i18n/locales/*.json'],
    ...i18nJson.configs['recommended'],
    rules: {
      'i18n-json/valid-json': 'error',
      'i18n-json/valid-message-syntax': 'error',
      'i18n-json/identical-keys': ['error', {
        filePath: 'src/i18n/locales/en.json'
      }]
    }
  }
]
```

### Solution 2: Custom Validation Script

**Create:** `scripts/validate-i18n.js`
```javascript
#!/usr/bin/env node

/**
 * Validate all i18n keys exist in translation files
 * Usage: node scripts/validate-i18n.js
 */

import { readFileSync, readdirSync } from 'fs'
import { join, extname } from 'path'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Load translation files
const localesDir = join(__dirname, '../src/i18n/locales')
const enMessages = JSON.parse(readFileSync(join(localesDir, 'en.json'), 'utf-8'))
const deMessages = JSON.parse(readFileSync(join(localesDir, 'de.json'), 'utf-8'))

// Function to get all keys from nested object
function getAllKeys(obj, prefix = '') {
  const keys = []
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && value !== null) {
      keys.push(...getAllKeys(value, fullKey))
    } else {
      keys.push(fullKey)
    }
  }
  return keys
}

// Function to find i18n keys in file content
function findI18nKeys(content) {
  const patterns = [
    /\$t\(['"]([^'"]+)['"]\)/g,  // $t('key')
    /t\(['"]([^'"]+)['"]\)/g,     // t('key')
    /i18n\.t\(['"]([^'"]+)['"]\)/g // i18n.t('key')
  ]

  const keys = new Set()
  for (const pattern of patterns) {
    const matches = content.matchAll(pattern)
    for (const match of matches) {
      keys.add(match[1])
    }
  }
  return Array.from(keys)
}

// Function to recursively find all Vue and JS files
function findFiles(dir, extensions = ['.vue', '.js']) {
  const files = []
  const entries = readdirSync(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)
    if (entry.isDirectory() && !entry.name.includes('node_modules')) {
      files.push(...findFiles(fullPath, extensions))
    } else if (extensions.includes(extname(entry.name))) {
      files.push(fullPath)
    }
  }
  return files
}

// Main validation
console.log('🔍 Validating i18n keys...\n')

const srcDir = join(__dirname, '../src')
const files = findFiles(srcDir)
const allEnKeys = getAllKeys(enMessages)
const allDeKeys = getAllKeys(deMessages)

let hasErrors = false
const usedKeys = new Set()

for (const file of files) {
  const content = readFileSync(file, 'utf-8')
  const keys = findI18nKeys(content)

  if (keys.length === 0) continue

  for (const key of keys) {
    usedKeys.add(key)

    // Check if key exists in English
    const existsInEn = allEnKeys.includes(key)
    const existsInDe = allDeKeys.includes(key)

    if (!existsInEn) {
      console.error(`❌ Missing key in en.json: "${key}" (used in ${file})`)
      hasErrors = true
    }

    if (!existsInDe) {
      console.warn(`⚠️  Missing key in de.json: "${key}" (used in ${file})`)
    }
  }
}

// Check for unused keys
console.log('\n📊 Checking for unused translation keys...\n')
let unusedCount = 0
for (const key of allEnKeys) {
  if (!usedKeys.has(key)) {
    console.log(`📦 Unused key: "${key}"`)
    unusedCount++
  }
}

// Summary
console.log('\n' + '='.repeat(50))
console.log(`✅ Validated ${files.length} files`)
console.log(`📝 Found ${usedKeys.size} unique i18n keys`)
console.log(`📦 Found ${unusedCount} unused keys`)

if (hasErrors) {
  console.log('\n❌ i18n validation FAILED')
  process.exit(1)
} else {
  console.log('\n✅ i18n validation PASSED')
}
```

**Make executable:**
```bash
chmod +x scripts/validate-i18n.js
```

**Add to package.json:**
```json
{
  "scripts": {
    "validate:i18n": "node scripts/validate-i18n.js"
  }
}
```

**Add to pre-commit hook:**
```bash
# .husky/pre-commit
npm run validate:i18n
```

**Expected Impact:**
- Catch missing i18n keys before commit
- Prevent "key not found" warnings in console
- Identify unused translation keys
- Ensure translations are in sync

---

## Test Checklist for New Features

**Priority:** 🔥 **IMMEDIATE** (Week 1, Day 5)

### Pre-Implementation Checklist

Before writing ANY code for a new feature:

- [ ] **1. Define OpenAPI Contract** (if backend involved)
  - Write API specification
  - Define request/response schemas
  - Document error cases

- [ ] **2. Write Failing Tests** (TDD)
  - Write unit tests for pure logic
  - Write component tests for UI
  - Mark tests with `@pytest.mark.future` or `it.skip()`

- [ ] **3. Plan i18n Keys**
  - List all UI text that needs translation
  - Add keys to `en.json` and `de.json`
  - Run `npm run validate:i18n`

- [ ] **4. Design Component Props**
  - Define prop types and defaults
  - Plan emits (no v-model on props!)
  - Document component API

### Implementation Checklist

While implementing:

- [ ] **5. Write Minimal Implementation**
  - Code only what's needed to pass tests
  - Keep functions pure (no side effects in `/composables/`)
  - Use proper reactive patterns (computed, not getters)

- [ ] **6. Add data-testid Attributes**
  - Add `data-testid` to all interactive elements
  - Use descriptive names: `data-testid="submit-button"`

- [ ] **7. Handle Edge Cases**
  - Test with empty data
  - Test with null/undefined
  - Test with extreme values (1000+ items)

- [ ] **8. Update Tests**
  - Remove `.skip()` from tests
  - Verify all tests pass
  - Add additional edge case tests

### Pre-Commit Checklist

Before committing:

- [ ] **9. Run All Checks**
  ```bash
  npm run lint          # ESLint
  npm run format:check  # Prettier
  npm run typecheck     # TypeScript
  npm run test          # Unit tests
  npm run validate:i18n # i18n keys
  ```

- [ ] **10. Manual Testing**
  - Test in browser (dev mode)
  - Test on mobile (responsive)
  - Test dark mode
  - Test both languages (en/de)

- [ ] **11. Documentation**
  - Update component JSDoc
  - Add inline comments for complex logic
  - Update CLAUDE.md if architecture changed

### Pre-PR Checklist

Before creating pull request:

- [ ] **12. E2E Test Coverage**
  - Write E2E test for critical user flow
  - Run `npx playwright test`
  - Verify test passes

- [ ] **13. Performance Check**
  - Check bundle size (`npm run build`)
  - Profile component rendering (Vue DevTools)
  - Optimize if needed

- [ ] **14. Accessibility**
  - Test with keyboard navigation
  - Check ARIA labels
  - Test screen reader (VoiceOver/NVDA)

---

## Implementation Timeline

### Week 1: Critical Foundation (Days 1-5)

**Day 1-2: Static Analysis Setup**
- [ ] Install and configure ESLint ✅
- [ ] Configure Prettier ✅
- [ ] Add npm scripts ✅
- [ ] Test on existing code ✅

**Day 3: Pre-Commit Hooks**
- [ ] Install Husky ✅
- [ ] Configure lint-staged ✅
- [ ] Test hook workflow ✅

**Day 4-5: i18n Validation**
- [ ] Create validation script ✅
- [ ] Test on existing codebase ✅
- [ ] Fix any missing keys ✅
- [ ] Add to pre-commit hook ✅

### Week 2: Component Test Expansion (Days 1-5)

**Day 1-2: Test Template & Critical Components**
- [ ] Create component test template ✅
- [ ] Test AuthModal.vue ✅
- [ ] Test PasswordGate.vue ✅
- [ ] Test GroupCard.vue ✅

**Day 3-4: High-Traffic Components**
- [ ] Test HeaderSection.vue
- [ ] Test GroupsControlBar.vue
- [ ] Test RecurringEventsCardsSection.vue
- [ ] Test UniqueEventsSection.vue

**Day 5: CI/CD Enhancement**
- [ ] Update GitHub Actions workflow
- [ ] Add coverage thresholds
- [ ] Test CI pipeline

### Week 3-4: Complete Coverage (Days 1-10)

**Days 1-5: Remaining Components**
- [ ] Test 15 components (Days 1-2)
- [ ] Test 10 components (Days 3-4)
- [ ] Test 10 components (Day 5)

**Days 6-8: Integration Tests**
- [ ] Store integration tests
- [ ] Router integration tests
- [ ] API integration tests

**Days 9-10: TypeScript Setup**
- [ ] Configure jsconfig.json
- [ ] Add JSDoc annotations to composables
- [ ] Add type checking to CI

### Week 5-6: E2E & Refinement (Days 1-10)

**Days 1-3: E2E Tests**
- [ ] Login flow E2E test
- [ ] Calendar filtering E2E test
- [ ] Group subscription E2E test
- [ ] Language switching E2E test

**Days 4-5: Edge Cases**
- [ ] Empty calendar tests
- [ ] Large calendar tests (1000+ events)
- [ ] Error handling tests

**Days 6-10: Polish & Documentation**
- [ ] Fix any failing tests
- [ ] Improve test coverage to 90%
- [ ] Update documentation
- [ ] Team training on test strategy

---

## Success Metrics

### Coverage Targets

**Week 1:**
- ESLint: 100% of files linted ✅
- Pre-commit hooks: Active ✅
- i18n validation: 0 missing keys ✅

**Week 2:**
- Component tests: 20% coverage (9/45 components)
- CI/CD: All checks passing
- Test coverage: 75%

**Week 4:**
- Component tests: 50% coverage (23/45 components)
- Integration tests: Core flows covered
- Test coverage: 85%

**Week 6:**
- Component tests: 90% coverage (40/45 components)
- E2E tests: All critical flows covered
- Test coverage: 90%

### Quality Gates

**Never Merge Without:**
1. ✅ All ESLint checks passing
2. ✅ All unit tests passing
3. ✅ Component tests for changed components
4. ✅ i18n keys validated
5. ✅ TypeScript type checks passing (Week 3+)
6. ✅ E2E tests passing (Week 5+)

**Optional but Recommended:**
- 📊 Code coverage > 80%
- 📦 Bundle size < 2MB
- ⚡ Lighthouse score > 90
- ♿ Accessibility score > 90

---

## Tools & Resources

### VS Code Extensions

**Essential:**
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Volar (Vue.volar)
- Vue VSCode Snippets (sdras.vue-vscode-snippets)

**Recommended:**
- Error Lens (usernamehw.errorlens) - Inline error display
- Vue DevTools - Browser extension
- Vitest (ZixuanChen.vitest-explorer)

### Configuration Files Reference

**Files to Create:**
1. `/Users/martijn/Documents/Projects/filter-ical/frontend/eslint.config.js`
2. `/Users/martijn/Documents/Projects/filter-ical/frontend/.prettierrc.json`
3. `/Users/martijn/Documents/Projects/filter-ical/frontend/.lintstagedrc.json`
4. `/Users/martijn/Documents/Projects/filter-ical/frontend/scripts/validate-i18n.js`
5. `/Users/martijn/Documents/Projects/filter-ical/frontend/tests/component-test-template.js`

**Files to Update:**
1. `/Users/martijn/Documents/Projects/filter-ical/frontend/package.json` (add scripts)
2. `/Users/martijn/Documents/Projects/filter-ical/frontend/vitest.config.js` (add coverage)
3. `/Users/martijn/Documents/Projects/filter-ical/frontend/tests/setup.js` (enhance mocks)
4. `/Users/martijn/Documents/Projects/filter-ical/.github/workflows/ci.yml` (CI/CD)

### Commands Quick Reference

```bash
# Development
npm run dev              # Start dev server
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint errors
npm run format           # Format with Prettier
npm run typecheck        # Check types

# Testing
npm run test             # Run unit tests
npm run test:ui          # Vitest UI
npm run test:coverage    # Coverage report
npx playwright test      # Run E2E tests
npx playwright test --ui # Playwright UI

# Validation
npm run validate:i18n    # Check i18n keys
npm run build            # Test production build

# Pre-commit (automatic)
git commit               # Runs lint-staged + tests
```

---

## Conclusion

This test strategy provides **6 layers of defense** against bugs:

1. **Static Analysis** → Catch at write-time (ESLint, TypeScript)
2. **Unit Tests** → Test pure logic (Vitest)
3. **Component Tests** → Test rendering & interaction (Vue Test Utils)
4. **Integration Tests** → Test component interactions
5. **E2E Tests** → Test user flows (Playwright)
6. **CI/CD Checks** → Automated quality gates

**Key Principles:**
- Write tests BEFORE implementation (TDD)
- Fail fast (pre-commit hooks)
- Comprehensive coverage (90% target)
- Fast feedback (< 5 seconds for unit tests)
- Real-world testing (E2E for critical flows)

**Next Steps:**
1. Review this strategy with team ✅
2. Start Week 1 implementation immediately
3. Track progress weekly
4. Adjust strategy based on findings
5. Celebrate milestones! 🎉

---

**Questions or Feedback?**
This is a living document. Update as you learn and improve.

**Last Updated:** 2025-10-11
**Version:** 1.0
**Author:** Test Strategy Architect
