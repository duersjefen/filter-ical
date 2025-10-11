# CLAUDE.md - Filter iCal Project Instructions

Production-ready Python + Vue 3 web application with comprehensive TDD workflow and language-independent CI/CD.

---

## 🔗 DOCUMENTATION HIERARCHY

**Global principles (TDD, architecture, critical behaviors):**
→ `/Users/martijn/Documents/Projects/CLAUDE.md`

**Platform infrastructure (nginx, SSL, deployment):**
→ `/Users/martijn/Documents/Projects/multi-tenant-platform/CLAUDE.md`

**This file:** Filter-iCal specific configuration and deployment details only.

---

## ⚙️ FILTER-ICAL CONFIGURATION

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