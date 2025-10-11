# Component Prop Validation Testing

This directory contains prop validation tests that catch type mismatches BEFORE they reach the browser.

## Problem Statement

**The Gap:**
- ✅ 664+ unit tests passing
- ❌ Browser shows prop type warnings
- ❌ Tests don't mount components with real data

**Solution:**
Mount components with realistic API data and validate prop types.

## How It Works

### 1. Prop Validation Utilities (`tests/utils/propValidator.js`)

```javascript
import { validatePropTypes, assertNoPropWarnings, fixtures } from '../../utils/propValidator'

// Check for warnings
const warnings = validatePropTypes(GroupCard, {
  domainId: 123,  // Wrong type - number instead of string
  group: fixtures.group
})
// warnings = ["Invalid prop: type check failed for prop 'domainId'..."]

// Assert no warnings (throws if warnings found)
assertNoPropWarnings(GroupCard, {
  domainId: "123",  // Correct type - string
  group: fixtures.group
})
```

### 2. Realistic Test Fixtures

```javascript
import { fixtures } from '../../utils/propValidator'

// Domain context as returned by API (id is number)
fixtures.domainContext
// { id: 1, domain_key: 'exter', name: 'Exter Calendar' }

// Group with recurring events
fixtures.group
// { id: 1, name: 'Test Group', recurring_events: [...] }

// Group with detailed event data
fixtures.groupWithEvents
// { id: 2, name: 'Detailed Group', recurring_events: [{ events: [...] }] }
```

### 3. Test Pattern

```javascript
describe('Component - Prop Validation', () => {
  describe('propName type validation', () => {
    it('accepts correct type', () => {
      assertNoPropWarnings(Component, {
        propName: 'correct-value',
        // ... other required props
      })
    })

    it('FAILS with wrong type (catches bug)', () => {
      const warnings = validatePropTypes(Component, {
        propName: 123,  // Wrong type
        // ... other required props
      })

      expect(warnings.length).toBeGreaterThan(0)
      expect(warnings.some(w => w.includes('propName'))).toBe(true)
    })

    it('works with realistic API data', () => {
      const apiData = fixtures.domainContext

      // Demonstrate the bug
      const warnings = validatePropTypes(Component, {
        propName: apiData.id,  // API returns number
        // ...
      })

      expect(warnings.length).toBeGreaterThan(0)
    })
  })
})
```

## Example: GroupCard domainId Bug

### The Bug

**CalendarView.vue** (before fix):
```vue
<EventGroupsSection
  :domain-id="props.domainContext?.id || 'default'"
  <!-- API returns id as Number, but GroupCard expects String -->
/>
```

**GroupCard.vue**:
```javascript
defineProps({
  domainId: { type: String, required: true }  // Expects String
})
```

**Result:** Browser console shows type mismatch warning.

### How Tests Catch It

```javascript
it('FAILS with domainId as number (catches type mismatch bug)', () => {
  assertPropWarnings(
    GroupCard,
    {
      domainId: 1,  // Number - WRONG TYPE
      group: fixtures.group,
    },
    ['domainId', 'type']  // Warning should mention domainId and type
  )
})

it('works with realistic domain context from API (demonstrates the bug)', () => {
  const domainContext = fixtures.domainContext

  // API returns id as number
  expect(typeof domainContext.id).toBe('number')

  // But GroupCard expects string - this produces a warning
  const warnings = validatePropTypes(GroupCard, {
    domainId: domainContext.id,  // Number from API
    group: fixtures.group,
  })

  // Should have at least one warning about type mismatch
  expect(warnings.length).toBeGreaterThan(0)
  expect(warnings.some(w => w.includes('domainId'))).toBe(true)
})
```

### The Fix

**CalendarView.vue** (after fix):
```vue
<EventGroupsSection
  :domain-id="props.domainContext?.id ? String(props.domainContext.id) : 'default'"
  <!-- Convert number to string -->
/>
```

### Verify Fix Works

```javascript
it('works correctly when domainId is converted to string', () => {
  const domainContext = fixtures.domainContext
  const domainIdValue = String(domainContext?.id || 'default')

  // Now it's a string
  expect(typeof domainIdValue).toBe('string')

  // Should not produce warnings
  assertNoPropWarnings(GroupCard, {
    domainId: domainIdValue,
    group: fixtures.group,
  })
})
```

## Running Tests

```bash
# Run all prop validation tests
npm test -- tests/components/calendar/GroupCard.test.js

# Run specific test suite
npm test -- tests/components/calendar/GroupCard.test.js -t "domainId prop type validation"

# Watch mode for development
npm test -- tests/components/calendar/GroupCard.test.js --watch
```

## CI/CD Integration

**vitest.config.js** is configured to fail CI builds on prop warnings:

```javascript
test: {
  onConsoleLog(log, type) {
    // Only fail in CI to avoid disrupting local development
    if (process.env.CI && type === 'warn') {
      if (typeof log === 'string' &&
          (log.includes('Invalid prop') ||
           log.includes('type check failed'))) {
        throw new Error(`Prop validation failed in CI: ${log}`)
      }
    }
    return true
  }
}
```

**Benefits:**
- ✅ Local development: warnings shown but don't fail tests
- ✅ CI/CD: warnings fail the build
- ✅ Catches prop bugs before deployment

## Adding Prop Tests for New Components

1. **Create test file**: `tests/components/[path]/Component.test.js`

2. **Import utilities**:
   ```javascript
   import { validatePropTypes, assertNoPropWarnings, assertPropWarnings, fixtures } from '../../utils/propValidator'
   import Component from '@/components/path/Component.vue'
   ```

3. **Add fixtures** (if needed):
   Edit `tests/utils/propValidator.js` to add realistic test data

4. **Write tests** for each prop:
   - ✅ Correct type test
   - ❌ Wrong type test (to catch bugs)
   - 🔄 Real API data test (to demonstrate bugs)

5. **Run tests**:
   ```bash
   npm test -- tests/components/path/Component.test.js
   ```

## Key Benefits

1. **Catch bugs early**: Type mismatches found in tests, not production
2. **Real data validation**: Tests use actual API response patterns
3. **Documentation**: Tests document expected prop types
4. **CI/CD safety**: Automated checks prevent prop bugs from reaching production
5. **Easy to write**: Utilities make prop tests simple and consistent

## Success Metrics

**Before prop validation tests:**
- 664 unit tests passing ✅
- Browser prop warnings ❌
- No prop type validation ❌

**After prop validation tests:**
- 681+ tests passing ✅
- Prop type bugs caught ✅
- CI/CD enforcement ✅
- Real API data tested ✅
