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
make dev                   # Start PostgreSQL + backend + frontend (dev stage)
make stop                  # Stop database (ports auto-increment if in use)
make health                # Check service status
make reset-db              # Reset local database

# Testing
make test                  # Run unit tests
make test-all              # Run complete test suite (unit + integration + E2E)
make preview               # Build and preview production frontend locally (port 4173)
                          # CRITICAL: Test production builds before deploying
                          # Catches Vite optimization issues that don't appear in dev mode

# SST Deployment (CloudFront + S3)
make sst-deploy-staging        # Deploy frontend to staging.filter-ical.de
make sst-deploy-production     # Deploy frontend to filter-ical.de
make sst-remove-dev            # Remove dev stage resources
make sst-remove-staging        # Remove staging stage resources
make sst-console               # Open SST console (monitoring, logs)

# Legacy EC2 Deployment (SSM-Based)
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

# Local Development URLs (auto-increments if ports in use)
# Frontend:  http://localhost:8000 (or 8001, 8002 if port in use)
# Backend:   http://localhost:3000 (or 3001, 3002 if port in use)
# API Docs:  http://localhost:3000/docs
# Database:  localhost:5432 (PostgreSQL in Docker)

# NEVER use manual server commands - always use Makefile
# NOTE: Servers have hot-reloading - no restart needed for code changes
# NOTE: Multiple dev instances can run simultaneously (auto port increment)
# IMPORTANT: make dev is usually already running in a separate terminal
#            Do NOT run make dev unless explicitly requested by user
```

---

## 🚢 INFRASTRUCTURE

### Environment Stages

**Three isolated AWS environments:**

1. **Dev (local + AWS):**
   - Local backend/frontend with isolated AWS resources
   - Stage: `dev` (SST creates separate CloudFormation stacks)
   - Purpose: Individual developer testing with real AWS services
   - Domain: None (CloudFront distribution created but not domain-mapped)
   - Cleanup: `make sst-remove-dev` (deletes all dev AWS resources)

2. **Staging:**
   - Pre-production testing environment
   - Stage: `staging`
   - Domain: `staging.filter-ical.de`
   - Purpose: Integration testing before production

3. **Production:**
   - Live production environment
   - Stage: `production`
   - Domain: `filter-ical.de`
   - Purpose: Live application serving users

**Port Auto-Detection:**
- SST/Vite automatically increment ports if default ports are in use
- Multiple dev instances can run simultaneously (3000→3001→3002, 8000→8001→8002)
- No need to kill existing processes - just start another instance

### Local Development (macOS)
- **Backend:** Uvicorn on `localhost:3000` (hot reload, auto-increments if port in use)
- **Frontend:** Vite on `localhost:8000` (hot reload, auto-increments if port in use)
- **Database:** PostgreSQL in Docker on `localhost:5432`
  - Container: `filter-ical-postgres-dev`
  - Database: `filterical_development`
  - Managed by: `docker-compose.dev.yml`

### Production Stack (SST CloudFront Deployment)
- **Backend:** Python FastAPI + Uvicorn on EC2 (filter-ical AWS account)
  - EC2: `i-041f562bf5f9642e1` (t4g.micro ARM, 13.50.144.0)
  - Staging: port 3001, Production: port 3000
  - PostgreSQL + Redis in Docker
- **Frontend:** Vue 3 SPA on CloudFront + S3
  - Staging: `staging.filter-ical.de` (pending CloudFront verification)
  - Production: `filter-ical.de` (pending CloudFront verification)
- **AWS Account:** filter-ical (165046687980)
- **Region:** eu-north-1 (Stockholm)

**CloudFront Status:**
- ✅ CloudFront API verified and accessible
- ⏳ Account verification pending for distribution creation
- 📋 AWS Support ticket submitted
- 🚀 Ready to deploy once verification completes: `AWS_PROFILE=filter-ical npx sst deploy --stage staging`

### Email Service (SMTP → SES Migration Plan)

**⚠️ IMPORTANT: Current SMTP setup is TEMPORARY**

**Current State (Temporary):**
- Using PrivateEmail SMTP (mail.privateemail.com:587)
- Credentials: `info@paiss.me` / stored in `/opt/secrets/` on EC2
- **Why temporary:** External dependency, not AWS-native, less scalable

**Migration Plan (After AWS Account Verification):**
1. **Request SES Production Access:**
   - AWS Console → SES → Request production access
   - Current state: Sandbox mode (only verified emails)
   - Production: Send to any email address

2. **Verify Sender Domain:**
   ```bash
   # Generate DKIM records
   aws ses verify-domain-identity --domain filter-ical.de --region eu-north-1

   # Add DNS records (via Namecheap script or Route53)
   # - TXT record for domain verification
   # - CNAME records for DKIM signing
   ```

3. **Update Backend Configuration:**
   ```bash
   # On EC2, edit backend/.env.staging and backend/.env.production
   # Replace SMTP_* variables with SES configuration:

   # Remove:
   SMTP_HOST=mail.privateemail.com
   SMTP_PORT=587
   SMTP_USERNAME=info@paiss.me
   SMTP_PASSWORD=***

   # Add:
   AWS_SES_REGION=eu-north-1
   AWS_SES_FROM_EMAIL=noreply@filter-ical.de
   # No credentials needed - uses EC2 IAM role
   ```

4. **Update IAM Role:**
   ```bash
   # Add SES permissions to FilterIcalEC2SSMRole
   aws iam attach-role-policy \
     --role-name FilterIcalEC2SSMRole \
     --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess
   ```

5. **Update Backend Code:**
   - Modify `backend/app/services/email.py` to use boto3 SES client
   - Keep SMTP as fallback for local development

6. **Test & Deploy:**
   ```bash
   # Test in staging first
   make deploy-staging

   # Verify emails are sent
   # Check SES console for delivery metrics

   # Deploy to production
   make deploy-production
   ```

**SES Benefits:**
- ✅ Native AWS integration (IAM-based auth, no passwords)
- ✅ Better deliverability (AWS IP reputation)
- ✅ Scalable (50,000 emails/day free tier)
- ✅ Built-in bounce/complaint handling
- ✅ Email analytics and monitoring
- ✅ Cost-effective ($0.10 per 1,000 emails after free tier)

**Timeline:**
- **Now:** SMTP working (production ready)
- **After AWS verification:** Request SES production access (~24-48 hours)
- **After SES approval:** Migrate to SES (~1 hour implementation)

**References:**
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [SES Python SDK (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html)

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

---

## 🚀 DEPLOYMENT READINESS CHECKLIST

### Current Status (2025-10-27)

**✅ Ready & Working:**
- [x] EC2 instance configured (t4g.micro ARM64, 13.50.144.0)
- [x] Docker Buildx v0.17.1 installed (ARM64 compatible)
- [x] GitHub deploy key configured
- [x] Environment files created and configured
- [x] SMTP credentials configured (temporary)
- [x] PostgreSQL + Redis running (both staging & production)
- [x] Backend APIs deployed and healthy:
  - Production: http://api.filter-ical.de/health (port 3000)
  - Staging: http://api-staging.filter-ical.de/health (port 3001)
- [x] DNS records configured in Route53:
  - filter-ical.de → 13.50.144.0
  - api.filter-ical.de → 13.50.144.0
  - staging.filter-ical.de → S3 (will become CloudFront)
  - api-staging.filter-ical.de → 13.50.144.0
- [x] SST configuration complete
- [x] Docker Compose project isolation (staging/production can coexist)

**⏳ Blocked by AWS Account Verification:**
- [ ] CloudFront distribution creation
- [ ] API Gateway deployment
- [ ] ACM SSL certificates
- [ ] Frontend deployment (staging & production)
- [ ] HTTPS for APIs

**🔜 Post-Verification Tasks:**
1. Deploy staging frontend: `AWS_PROFILE=filter-ical npx sst deploy --stage staging`
2. Deploy production frontend: `AWS_PROFILE=filter-ical npx sst deploy --stage production`
3. Request SES production access
4. Migrate SMTP → SES
5. Enable Brotli compression (optional, after CloudFront)

### Post-Verification Deployment Commands

Once AWS account verification completes, run these commands in order:

```bash
# 1. Deploy staging (test first)
cd /Users/martijn/Documents/Projects/filter-ical
export AWS_PROFILE=filter-ical
npx sst deploy --stage staging

# Expected output:
# ✓ Complete
#   Frontend: https://staging.filter-ical.de
#   API: https://api-staging.filter-ical.de

# 2. Test staging
curl https://staging.filter-ical.de
curl https://api-staging.filter-ical.de/health

# 3. Deploy production (if staging works)
npx sst deploy --stage production

# Expected output:
# ✓ Complete
#   Frontend: https://filter-ical.de
#   API: https://api.filter-ical.de

# 4. Test production
curl https://filter-ical.de
curl https://api.filter-ical.de/health

# 5. Verify DNS propagation (may take 5-10 minutes)
dig filter-ical.de CNAME
dig api.filter-ical.de CNAME
```

### Monitoring After Deployment

```bash
# Open SST console for monitoring
npx sst console

# Check CloudFront distribution status
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName,Status]' --output table

# Check backend health
curl https://api.filter-ical.de/health
curl https://api-staging.filter-ical.de/health

# Check CloudWatch logs (if issues)
aws logs tail /aws/lambda/filter-ical --follow
```

### Rollback Plan (If Needed)

```bash
# Remove staging deployment
npx sst remove --stage staging

# Remove production deployment (DANGEROUS - only if critical issue)
npx sst remove --stage production

# Backend rollback (revert to previous git commit)
git revert HEAD
make deploy-production
```