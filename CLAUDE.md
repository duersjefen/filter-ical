# CLAUDE.md - iCal Viewer Project Instructions

Production-ready Python + Vue 3 web application with comprehensive TDD workflow and language-independent CI/CD.

---

## 🎯 CORE PROJECT PRINCIPLES

### Development Workflow (TDD-First)
1. **Write failing test FIRST** → `@pytest.mark.future` tests drive implementation
2. **Make minimum implementation** → Code only what's needed to pass tests
3. **Refactor safely** → `make test` ensures no regression
4. **Test & Commit** → Always run `make test` and commit after completing features/fixes
5. **Deploy** → `make deploy-staging` (auto) or `make deploy-production` (manual approval)

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

# Deployment
make deploy-staging        # Deploy to staging (auto-deploy on push to master)
make deploy-production     # Deploy to production (requires manual approval)
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
**Required notifications using:**
```bash
/home/martijn/.claude-notifications/claude_notify "message" "type"
```

**Types:** `task_complete`, `error`, `milestone`, `approval_needed`

### Systematic Debugging
**2-Failure Rule:** After 2 failed attempts, IMMEDIATELY find root cause
- Stop micro-debugging → Address system-level issues
- Frontend: Use Vue DevTools (available in Vite dev server) for reactive debugging
- AI-accessible debugging → Unit tests, E2E tests, HTML debug panels (NOT console.log)

### Professional Guidance
**Must challenge:** Architectural shortcuts, security issues, performance anti-patterns
**Template:** *"This approach will cause [problems] because [reasons]. Instead, [better solution] which [benefits]."*

---

## 🚢 INFRASTRUCTURE

### Local Development (WSL2)
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

### Multi-Tenant Platform Architecture
**CRITICAL:** filter-ical is deployed via the [multi-tenant-platform](../multi-tenant-platform) system.

**Repository Structure:**
```
~/Desktop/
├── filter-ical/              # This repository (application code)
│   ├── backend/              # FastAPI application
│   ├── frontend/             # Vue 3 application
│   └── CLAUDE.md            # This file
└── multi-tenant-platform/    # Platform repository (deployment configs)
    └── configs/filter-ical/  # filter-ical deployment configuration
        ├── docker-compose.yml    # Container orchestration
        ├── .env.staging          # Staging environment variables
        ├── .env.production       # Production environment variables
        └── nginx.conf            # Reverse proxy configuration
```

**How Deployment Works:**
1. **Code Changes** → Pushed to `filter-ical` GitHub repo
2. **GitHub Actions** → Builds Docker images and pushes to ghcr.io
3. **Deployment Script** → Pulls configs from `multi-tenant-platform` repo
4. **Docker Compose** → Orchestrates container deployment on EC2

**Container Networking:**
- Both frontend and backend join the `platform` Docker network
- Backend has network alias `backend` for DNS resolution
- Frontend connects to backend via `BACKEND_HOST` environment variable (defaults to `backend`)
- This allows frontend nginx to proxy `/api/*` requests to backend

**Environment Variables:**
- **Backend:** Configured via `.env.{environment}` files in platform repo
- **Frontend:** `BACKEND_HOST=backend` (set in platform .env files)
- Frontend's nginx.conf uses `${BACKEND_HOST}` for dynamic backend hostname

**Key Files to Update:**
- Application code: `filter-ical` repository
- Deployment config: `multi-tenant-platform/configs/filter-ical/`
- Never commit environment secrets to `filter-ical` repo

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

### Development Tips
- Dev servers usually already running - check with `make health` before starting
- Don't rerun `make dev` when servers are still running
- Use `make stop` to cleanly stop all services
- Always use `make deploy-staging` / `make deploy-production` instead of manual GitHub Actions commands