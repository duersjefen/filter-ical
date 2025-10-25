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
make preview               # Build and preview production frontend locally (port 4173)
                          # CRITICAL: Test production builds before deploying
                          # Catches Vite optimization issues that don't appear in dev mode

# Deployment (auto-pushes to GitHub before deploying)
make deploy-staging        # Push → test → deploy to staging (auto health check)
make deploy-production     # Push → test → deploy to production (auto health check)
SKIP_PUSH=1 make deploy-staging    # Deploy without pushing to GitHub
SKIP_TESTS=1 make deploy-staging   # Emergency deploy (skip tests, still pushes)
make logs-staging          # View staging logs (if deployment fails)
make logs-production       # View production logs (if deployment fails)
make status                # Check deployment status

# Environment Management (EC2 only)
make edit-env-staging      # SSH to EC2 to edit staging .env files
make edit-env-production   # SSH to EC2 to edit production .env files
make restart-staging       # Restart staging containers (after .env changes)
make restart-production    # Restart production containers (after .env changes)

# Local Development URLs
# Frontend:  http://localhost:8000
# Backend:   http://localhost:3000
# API Docs:  http://localhost:3000/docs
# Database:  localhost:5432 (PostgreSQL in Docker)

# NEVER use manual server commands - always use Makefile
# NOTE: Servers have hot-reloading - no restart needed for code changes
# IMPORTANT: make dev is usually already running in a separate terminal
#            Do NOT run make dev unless explicitly requested by user
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

### Production Stack (SST Hybrid Deployment)
- **Backend:** Python FastAPI + Uvicorn on EC2 (filter-ical AWS account)
  - EC2: `i-041f562bf5f9642e1` (t4g.micro ARM, 13.50.144.0)
  - Staging: port 3001, Production: port 3000
  - PostgreSQL + Redis in Docker
- **Frontend:** Vue 3 SPA on S3 (temporary, will migrate to CloudFront)
  - Staging: http://filter-ical-staging.paiss.me → S3 static website
  - Production: Not deployed yet
- **AWS Account:** filter-ical (165046687980)
- **Region:** eu-north-1 (Stockholm)

**NEXT TASK:** Migrate frontend to CloudFront + SST once account verification completes
- CloudFront verification is pending (received email, API access not yet propagated)
- `sst.config.ts` already configured for CloudFront deployment
- Run `npx sst deploy --stage staging` when CloudFront access is enabled
- Will replace S3-only deployment with CloudFront CDN (same domain)

**Legacy (filter-ical.de):**
- Domain: https://filter-ical.de (not yet migrated to paiss.me)
- AWS: EC2 i-01647c3d9af4fe9fc (13.62.136.72) - OLD, needs migration

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

### Environment Configuration (Per-Component Pattern)

**Structure:**
```
backend/.env.development    # Local: DB, SMTP, secrets (backend only)
frontend/.env.development   # Local: VITE_API_BASE_URL (frontend only)
backend/.env.staging        # EC2: Backend config (created manually)
frontend/.env.staging       # EC2: Frontend config (created manually)
backend/.env.production     # EC2: Backend config (created manually)
frontend/.env.production    # EC2: Frontend config (created manually)
```

**Security:** Frontend never receives backend secrets (DB, SMTP, JWT keys).

**Changing .env on EC2:**
1. Backend config: `make edit-env-staging` → edit `backend/.env.staging` → `make restart-staging`
2. Frontend config: Edit `frontend/.env.staging` → **MUST REBUILD**: `docker-compose build frontend && docker-compose up -d`
   - VITE_* vars are baked into the build, restart alone won't work

**Initial setup:** Run `./scripts/setup-remote-env.sh` once, then SSH to update placeholders.

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