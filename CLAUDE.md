# CLAUDE.md - Filter iCal Project Instructions

Production-ready Python + Vue 3 web application with comprehensive TDD workflow and language-independent CI/CD.

---

## 🔗 PLATFORM INFRASTRUCTURE

**This app is deployed on the multi-tenant platform.**

For platform-level changes (nginx routing, SSL certificates, database, shared infrastructure):
→ **See:** `/Users/martijn/Documents/Projects/multi-tenant-platform/CLAUDE.md`

For app-specific development and deployment, see below.

---

## 🎯 CORE PROJECT PRINCIPLES

### Development Workflow (TDD-First)
1. **Write failing test FIRST** → `@pytest.mark.future` tests drive implementation
2. **Make minimum implementation** → Code only what's needed to pass tests
3. **Refactor safely** → `make test` ensures no regression
4. **Test & Commit** → Always run `make test` and commit after completing features/fixes
5. **Deploy** → `make test` → `make deploy-staging` or `make deploy-production`
   - Tests catch code issues before deployment
   - Automatic health check catches deployment issues
   - Use `make logs-staging` or `make logs-production` if health check fails

### Quick Reference
```bash
# Development
make dev                   # Start PostgreSQL + backend + frontend
make stop                  # Stop all development services
make health                # Check service status
make reset-db              # Reset local database

# Testing
make test                  # Run unit tests
make test-all              # Run complete test suite (unit + integration + E2E)

# Deployment (auto-pushes to GitHub before deploying)
make deploy-staging        # Push → test → deploy to staging (auto health check)
make deploy-production     # Push → test → deploy to production (auto health check)
SKIP_PUSH=1 make deploy-staging    # Deploy without pushing to GitHub
SKIP_TESTS=1 make deploy-staging   # Emergency deploy (skip tests, still pushes)
make logs-staging          # View staging logs (if deployment fails)
make logs-production       # View production logs (if deployment fails)
make status                # Check deployment status

# Local Development URLs
# Frontend:  http://localhost:8000
# Backend:   http://localhost:3000
# API Docs:  http://localhost:3000/docs
# Database:  localhost:5432 (PostgreSQL in Docker)

# NEVER use manual server commands - always use Makefile
# NOTE: Servers have hot-reloading - no restart needed for code changes
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
**Notify user when Claude can't continue (finished or needs input):**
```bash
~/bin/claude-notify "message" "type"
```

**Types:** `success`, `task_complete`, `milestone`, `error`, `question`, `approval_needed`, `input_needed`

**When to notify:**
- ✅ All tasks complete - nothing left to do
- ✅ Waiting for input - need decision/approval/clarification
- ✅ Blocked/error - can't proceed without help
- ❌ Don't notify on routine mid-task updates

### Systematic Debugging
**2-Failure Rule:** After 2 failed attempts, IMMEDIATELY find root cause
- Stop micro-debugging → Address system-level issues
- Frontend: Use Vue DevTools (available in Vite dev server) for reactive debugging
- AI-accessible debugging → Unit tests, E2E tests, HTML debug panels (NOT console.log)

### Professional Guidance
**Must challenge:** Architectural shortcuts, security issues, performance anti-patterns
**Template:** *"This approach will cause [problems] because [reasons]. Instead, [better solution] which [benefits]."*

### Parallel Agent Orchestration
**For complex tasks, use 6 agents in parallel (Task tool):**
1. **Research** - Analyze existing patterns (Read, Grep, Glob)
2. **Backend** - FastAPI implementation (pure functions + routers)
3. **Frontend** - Vue 3 components + composables
4. **Tests** - pytest + Vitest (TDD-first with @pytest.mark.future)
5. **Security** - SQL injection, XSS, auth validation
6. **Architecture** - Validate filter-ical principles compliance

**Trigger:** User says "ultrathink" or requests comprehensive implementation

**Workflow:** Spawn all 6 agents → run in parallel → synthesize results → present unified plan

**Speed:** 60% faster than sequential (9 min vs 25 min for features)

---

## 🚢 INFRASTRUCTURE

### Local Development (macOS)
- **Backend:** Uvicorn on `localhost:3000` (hot reload)
- **Frontend:** Vite on `localhost:8000` (hot reload)
- **Database:** PostgreSQL in Docker on `localhost:5432`
  - Container: `filter-ical-postgres-dev`
  - Database: `filterical_development`
  - Managed by: `docker-compose.dev.yml`

### Production Stack
- **Backend:** Python FastAPI + Uvicorn (port 3000)
- **Frontend:** Vue 3 SPA with Vite + Pinia (port 8000)
- **Domain:** https://filter-ical.de
- **Staging:** https://staging.filter-ical.de
- **AWS:** EC2 i-01647c3d9af4fe9fc (13.62.136.72)

### SSM-Based Deployment Architecture
**CRITICAL:** filter-ical uses SSM (AWS Systems Manager) for deployment.

**How It Works:**
1. `make deploy-staging` → Tests pass → Push to GitHub → SSM connects to EC2
2. EC2 pulls code, builds Docker images, starts containers (2-5 min)
3. Containers join `platform` Docker network with DNS resolution

**Key Files:**
- Application: `backend/`, `frontend/`
- Deployment: `deploy.sh`, `docker-compose.yml`, `Makefile`
- Platform nginx: `../multi-tenant-platform/platform/nginx/sites/filter-ical.conf`
- EC2 instance ID: `.env.ec2` (gitignored)

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
- Run `make test` and commit after completing features/fixes

**❌ NEVER:**
- Manual server startup or non-standard ports
- Implementation before OpenAPI specification
- Classes for business logic (functions only)
- Side effects in pure function directories
- Browser pop-ups during automated testing
- Manual database schema changes

**PURPOSE:** This architecture ensures 100% testability, zero frontend coupling, fearless refactoring, and production reliability.