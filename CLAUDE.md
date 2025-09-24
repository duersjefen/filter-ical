# CLAUDE.md - iCal Viewer Project Instructions

Production-ready Python + Vue 3 web application with comprehensive TDD workflow and language-independent CI/CD.

---

## 🎯 CORE PROJECT PRINCIPLES

### Development Workflow (TDD-First)
1. **Write failing test FIRST** → `@pytest.mark.future` tests drive implementation
2. **Make minimum implementation** → Code only what's needed to pass tests
3. **Refactor safely** → `make test` ensures no regression
4. **Deploy** → `make deploy` (with real-time monitoring)

### Commands
```bash
# Development
make dev                   # Start both backend and frontend  
make test                  # Unit tests (for commits) - 5 tests
make test-future           # TDD development tests - 35 tests  
make test-all             # Complete test suite - 40 tests
make deploy               # Deploy with real-time monitoring

# NEVER use manual server commands - always use Makefile
```

---

## 🏗️ MANDATORY ARCHITECTURE PRINCIPLES

### 1. Clean Code Organization
**✅ NAMING RULES:**
- Name what it IS, not what it WAS → `useAPI.js` not `useUnifiedAPI.js`
- No historical memory → No `New`, `Updated`, `Fixed`, `Unified`, `Merged`
- Present-tense documentation → Describe current functionality only
- Flat structure when possible → `/composables/useAPI.js` not `/composables/api/useAPI.js`

### 2. Contract-Driven Development
**THE MOST IMPORTANT LESSON: OpenAPI specifications are immutable contracts**

```
OpenAPI Contract → Implementation Freedom → Frontend Independence
```

**✅ Workflow:**
1. Write OpenAPI specification → Define exact API behavior
2. Write contract tests → Validate implementation matches spec
3. Implement backend → Code to pass contract tests
4. Frontend uses contracts → Never depends on backend implementation

**Benefits:** Complete backend refactoring freedom without breaking frontend.

### 3. Functional Programming Architecture
**"Functional Core, Imperative Shell" Pattern**

```
app/data/           # PURE FUNCTIONS ONLY (business logic)
app/main.py         # I/O ORCHESTRATION (side effects)
src/composables/    # PURE FUNCTIONS ONLY (data transformations)  
src/stores/         # STATE + I/O (reactive boundaries)
```

**✅ Rules:**
- Pure functions in `/data/` and `/composables/` directories
- NO classes for business logic - functions only
- Explicit data flow - no hidden dependencies
- Immutable data transformations - return new objects

### 4. Test-First Development
**✅ TDD Workflow:**
- Unit tests → Pure functions, business logic
- Integration tests → Component interactions, API endpoints  
- E2E tests → Real user workflows (HEADLESS ONLY)
- Contract tests → API compliance with OpenAPI specs

**Vue 3 + Pinia Reactivity Fix:**
```javascript
// ✅ CORRECT - Use computed for reactive delegation
const user = computed({
  get() { return appStore.user },
  set(value) { appStore.user = value }
})

// ❌ WRONG - Simple getters break reactivity
return { get user() { return appStore.user } }
```

---

## 🔧 CRITICAL BEHAVIORS

### User Notification System
**Required notifications using:**
```bash
/home/martijn/.claude-notifications/claude_notify "message" "type"
```

**Types:** `task_complete`, `error`, `milestone`, `approval_needed`

### Systematic Debugging
**2-Failure Rule:** After 2 failed attempts, IMMEDIATELY find root cause
- Stop micro-debugging → Address system-level issues
- Frontend: Always check browser console FIRST
- AI-accessible debugging → Unit tests, E2E tests, HTML debug panels (NOT console.log)

### Professional Guidance
**Must challenge:** Architectural shortcuts, security issues, performance anti-patterns
**Template:** *"This approach will cause [problems] because [reasons]. Instead, [better solution] which [benefits]."*

---

## 🚢 PRODUCTION INFRASTRUCTURE

### Stack
- **Backend:** Python FastAPI + Uvicorn (port 3000)
- **Frontend:** Vue 3 SPA with Vite + Pinia (port 8000)
- **Domain:** https://filter-ical.de
- **AWS:** EC2 i-01647c3d9af4fe9fc (56.228.25.95)

### Database Migrations
**MANDATORY: Use Alembic for all schema changes**
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Tailwind CSS v4
**Critical configuration:**
```css
/* ✅ CORRECT */
@import "tailwindcss";

/* ❌ WRONG (v3 syntax) */
@tailwind base;
```

**Requirements:** Node.js 20+, ESM-only, `.mjs` config files

---

## 📋 DEVELOPMENT RULES

**✅ ALWAYS:**
- Use Makefile commands for servers (`make dev`, not manual npm/uvicorn)
- Write OpenAPI specs before implementation
- Pure functions in `/data/` and `/composables/` directories  
- Contract tests for API validation
- Headless E2E tests only
- Alembic for database changes

**❌ NEVER:**
- Manual server startup or non-standard ports
- Implementation before OpenAPI specification
- Classes for business logic (functions only)
- Side effects in pure function directories
- Browser pop-ups during automated testing
- Manual database schema changes

**PURPOSE:** This architecture ensures 100% testability, zero frontend coupling, fearless refactoring, and production reliability.