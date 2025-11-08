# CLAUDE.md - Filter iCal Project Instructions

Production-ready Python + Vue 3 **full serverless** web application with AWS Lambda + RDS PostgreSQL.

**Architecture:** CloudFront + S3 (frontend) + AWS Lambda (backend) + RDS PostgreSQL (database)
**Deployment:** Via SST (`npx sst deploy --stage staging/production`)
**Cost:** ~$14/month (Lambda $0 + RDS $12 + CloudFront $2) - 42% savings vs ECS
**Updated:** 2025-11-07

---

## 🔗 DOCUMENTATION HIERARCHY

**Global principles (TDD, architecture, critical behaviors):**
→ `~/.claude/CLAUDE.md`

**This file:** Filter-iCal specific configuration and deployment details only

---

## 🏗️ ARCHITECTURE OVERVIEW

### Full Serverless Stack (Current)

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Vue 3 SPA)                                       │
│  CloudFront + S3                                            │
│  filter-ical.de                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI + Mangum)                                 │
│  AWS Lambda (Python 3.13, 512 MB)                           │
│  api.filter-ical.de                                         │
│  Auto-scaling: 0-1000 concurrent executions                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL 16)                                   │
│  RDS t4g.micro (Single-AZ)                                  │
│  Private VPC subnet                                         │
│  Automated backups (7-day retention)                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Scheduled Sync Task (EventBridge)                          │
│  AWS Lambda (Python 3.13, 512 MB, 5 min timeout)            │
│  Runs every 30 minutes                                      │
│  Syncs calendars, applies rules, warms cache                │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**
- ✅ Zero server maintenance (no Docker, no containers to manage)
- ✅ Automated database backups (daily, point-in-time recovery)
- ✅ True auto-scaling (0 to 1000 concurrent executions)
- ✅ Pay-per-use pricing (within free tier for typical usage)
- ✅ CloudWatch logs & monitoring (built-in)
- ✅ Private VPC networking (secure database access)
- ✅ 42% cost reduction vs ECS Fargate

**What Happened to Redis?**
- Removed! App has graceful degradation built-in (`backend/app/core/redis.py`)
- Caching is optional (performance optimization only)
- App works perfectly without Redis (slightly slower repeated queries)

---

## ⚙️ FILTER-ICAL CONFIGURATION

### Quick Reference
```bash
##
## 🚀 Local Development
##

# Start development (connects to staging RDS)
npm run dev  # Runs "sst dev --stage staging"

# This automatically:
# - Connects to staging RDS database (real data!)
# - Loads secrets from AWS Secrets Manager
# - Hot-reloads backend + frontend on code changes
# - Simulates CloudFront + S3 locally

# URLs:
# Frontend: http://localhost:8000
# Backend:  http://localhost:3000
# API Docs: http://localhost:3000/docs
# Database: Staging RDS (auto-connected)

##
## 🧪 Testing
##

# Backend tests
cd backend && . venv/bin/activate && pytest tests/ -m unit -v

# Frontend build test (catches Vue compilation errors)
cd frontend && npm run build

# Frontend preview (test production build)
cd frontend && npm run preview  # http://localhost:4173

##
## 🚀 Deployment (Use deploy-kit "dk" command)
##

# One-time setup (before first deployment):
npx sst secret set JwtSecretKey "$(openssl rand -base64 32)" --stage staging
npx sst secret set SmtpHost "mail.privateemail.com" --stage staging
npx sst secret set SmtpPort "587" --stage staging
npx sst secret set SmtpUsername "info@paiss.me" --stage staging
npx sst secret set SmtpPassword "your-password" --stage staging

# Deploy (runs tests, builds, deploys, health checks)
npx sst deploy --stage staging          # Deploy to staging.filter-ical.de
npx sst deploy --stage production       # Deploy to filter-ical.de

# After deployment, run database migrations:
npx sst shell --stage staging --command "cd backend && alembic upgrade head"
npx sst shell --stage production --command "cd backend && alembic upgrade head"

# Verify deployment:
curl https://api-staging.filter-ical.de/health    # Should return 200
curl https://api.filter-ical.de/health            # Should return 200

# Monitor & Debug:
npx sst console            # Open SST console (resources, logs, metrics)
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalBackendApi-staging --follow
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalBackendApi-production --follow
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalSyncTask-staging --follow
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalSyncTask-production --follow

# Database access:
npx sst shell --stage staging      # Shell with staging DATABASE_URL
npx sst shell --stage production   # Shell with production DATABASE_URL
# Inside shell: psql $DATABASE_URL

# Cleanup (DESTRUCTIVE!):
npx sst remove --stage staging      # Delete staging CloudFormation stack
npx sst remove --stage production   # Delete production stack

##
## 📊 Deployment URLs
##

# Staging:
#   Frontend: https://staging.filter-ical.de
#   Backend:  https://api-staging.filter-ical.de
#   Docs:     https://api-staging.filter-ical.de/docs

# Production:
#   Frontend: https://filter-ical.de
#   Backend:  https://api.filter-ical.de
#   Docs:     https://api.filter-ical.de/docs

##
## 💰 Infrastructure Cost
##

# Monthly (eu-north-1):
#   Lambda API:    $0.00   (within free tier: 1M requests, 400K GB-seconds)
#   Lambda Sync:   $0.00   (1,440 invocations/month, within free tier)
#   EventBridge:   $0.00   (1,440 schedule invocations, negligible)
#   RDS t4g.micro: $12.41  (Single-AZ, 20 GB GP3)
#   CloudFront+S3: $2.00   (frontend hosting)
#   Secrets:       $2.40   (6 secrets × $0.40)
#   ─────────────────────
#   Total:         ~$17/month (26% savings vs ECS)
#
# Note: Lambda free tier = 400,000 GB-seconds/month
#   API Lambda (512 MB): ~1,000 requests at 200ms = 100 GB-seconds ✅ Free
#   Sync Lambda (512 MB): 1,440 × 30s = 21,600 GB-seconds ✅ Free

##
## 🔐 AWS Configuration
##

# AWS Profile: filter-ical
# AWS Region:  eu-north-1 (Stockholm)
# AWS Account: 165046687980

##
## 🌐 DNS (Route53)
##

# After first deployment, SST outputs Route53 nameservers
# Update domain registrar (Namecheap) to use these nameservers:
dk deploy staging  # See output: dnsNameservers = ["ns-xxx.awsdns-xx.com", ...]

# Update Namecheap:
node ~/.scripts/namecheap.js list filter-ical.de  # See current NS records
# Then update nameservers at Namecheap dashboard or via script
```

## 🚢 INFRASTRUCTURE

### Local Development

**SST Dev Mode (connects to staging RDS)**
- **Command:** `npm run dev` (runs `sst dev --stage staging`)
- **Backend:** Uvicorn on `localhost:3000` (hot reload)
- **Frontend:** Vite on `localhost:8000` (hot reload)
- **Database:** Staging RDS (auto-connected via SST)
- **Secrets:** AWS Secrets Manager (auto-loaded)
- **Benefits:** Test with real data, no local database setup, faster iteration

### Production Stack (Lambda + RDS + Route53)

**Architecture:**
```
Frontend (Vue 3 SPA)           Backend (FastAPI + Mangum)  Database (PostgreSQL 16)
CloudFront + S3                AWS Lambda                  RDS t4g.micro
filter-ical.de          →      api.filter-ical.de    →     Private VPC
                               Python 3.13, 512 MB         Single-AZ, 20GB
                               Auto-scaling: 0-1000         Automated backups
```

**Domains:**
- Production Frontend: https://filter-ical.de
- Production Backend: https://api.filter-ical.de
- Staging Frontend: https://staging.filter-ical.de
- Staging Backend: https://api-staging.filter-ical.de

**AWS Resources:**
- Region: eu-north-1 (Stockholm)
- Profile: filter-ical
- DNS: FilterIcalDns (Route53 hosted zone for filter-ical.de)
- VPC: FilterIcalVpc (required for RDS access)
- Database: FilterIcalDB (PostgreSQL 16.10, RDS)
- Backend API: FilterIcalBackendApi (Lambda Function)
- Sync Task: FilterIcalSyncTask (Lambda Function, EventBridge scheduled)
- Frontend: FilterIcalFrontend (CloudFront + S3)

**Cost Breakdown:**
- Lambda: ~$0/month (within free tier)
- RDS: ~$12/month (t4g.micro Single-AZ)
- CloudFront + S3: ~$2/month
- Secrets: ~$2.40/month
- **Total: ~$17/month (26% savings vs ECS)**

### Deployment Verification

**After deployment, verify:**
```bash
# 1. Check health endpoints
curl https://api.filter-ical.de/health      # Should return 200
curl https://api-staging.filter-ical.de/health

# 2. Test frontend loads
curl -I https://filter-ical.de              # Should return 200
curl -I https://staging.filter-ical.de

# 3. Check CloudWatch logs if issues
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalBackendApi-production --follow
AWS_PROFILE=filter-ical aws logs tail /aws/lambda/filter-ical-FilterIcalSyncTask-production --follow
```

### Environment Configuration

**SST manages environment-specific secrets:**
```bash
# Set secrets per stage (one-time setup)
npx sst secret set JwtSecretKey "your-secret" --stage staging
npx sst secret set SmtpHost "mail.privateemail.com" --stage staging
npx sst secret set SmtpPort "587" --stage staging
npx sst secret set SmtpUsername "info@paiss.me" --stage staging
npx sst secret set SmtpPassword "your-password" --stage staging

# List secrets
npx sst secret list --stage staging

# Remove secret (if needed)
npx sst secret remove JwtSecretKey --stage staging
```

**Security:**
- Secrets stored in AWS Secrets Manager (encrypted at rest)
- SST automatically injects secrets into Fargate containers
- Frontend NEVER receives backend secrets (DB, SMTP, JWT)
- Database credentials auto-generated by RDS (no manual setup)
- Frontend config (VITE_API_BASE_URL) injected at build time by SST

**No Manual Configuration Needed:**
- RDS connection: SST auto-links database to backend
- Backend URL: SST auto-injects into frontend build
- All secrets: Managed via `npx sst secret` commands

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
- Write OpenAPI specs before implementation
- Pure functions in `/data/` and `/composables/` directories
- Contract tests for API validation
- Headless E2E tests only
- Alembic for database changes
- Run tests before committing

**❌ NEVER:**
- Implementation before OpenAPI specification
- Classes for business logic (functions only)
- Side effects in pure function directories
- Browser pop-ups during automated testing
- Manual database schema changes

**PURPOSE:** This architecture ensures 100% testability, zero frontend coupling, fearless refactoring, and production reliability.

## 🚀 DEPLOYMENT WORKFLOW

### First-Time Setup (One-Time Only)

**1. Set AWS Secrets:**
```bash
# Set secrets for staging
npx sst secret set JwtSecretKey "$(openssl rand -base64 32)" --stage staging
npx sst secret set SmtpHost "mail.privateemail.com" --stage staging
npx sst secret set SmtpPort "587" --stage staging
npx sst secret set SmtpUsername "info@paiss.me" --stage staging
npx sst secret set SmtpPassword "your-password" --stage staging

# Repeat for production with DIFFERENT secrets
npx sst secret set JwtSecretKey "$(openssl rand -base64 32)" --stage production
npx sst secret set SmtpHost "mail.privateemail.com" --stage production
npx sst secret set SmtpPort "587" --stage production
npx sst secret set SmtpUsername "info@paiss.me" --stage production
npx sst secret set SmtpPassword "your-password" --stage production
```

### Deployment Commands

**Deploy to staging:**
```bash
dk deploy staging            # Run tests → Deploy → Health check
# Output: https://staging.filter-ical.de
#         https://api-staging.filter-ical.de
#         dnsNameservers: ["ns-xxx.awsdns-xx.com", ...]
```

**Update DNS (first deployment only):**
- Copy nameservers from SST output
- Update domain registrar (Namecheap) to use Route53 nameservers
- DNS propagation: 5-60 minutes

**Run database migrations:**
```bash
npx sst shell --stage staging --command "cd backend && alembic upgrade head"
```

**Deploy to production:**
```bash
dk deploy production         # Requires "yes" confirmation
# Output: https://filter-ical.de
#         https://api.filter-ical.de
```

### Monitoring & Debugging

```bash
# Check health
dk health                    # Run all health checks
dk status                    # Check deployment status

# View logs
AWS_PROFILE=filter-ical aws logs tail /aws/ecs/filter-ical-backend-staging --follow
AWS_PROFILE=filter-ical aws logs tail /aws/ecs/filter-ical-backend-production --follow

# SST console (resources, metrics, logs)
npx sst console

# Database access
npx sst shell --stage staging       # Shell with DATABASE_URL set
npx sst shell --stage production
# Inside shell: psql $DATABASE_URL
```

### Rollback

```bash
# Code rollback
git revert HEAD
dk deploy staging

# Full teardown (DESTRUCTIVE!)
npx sst remove --stage staging      # Deletes CloudFormation stack
npx sst remove --stage production   # Deletes all AWS resources
```

---

# Deploy-Kit - Claude Code for Web (CCW) Environment

**IMPORTANT:** This file is loaded in CCW environments (when `CLAUDE_CODE_REMOTE=true`).

---

## Environment Detection

You are in **Claude Code for Web (CCW)** when:
- `CLAUDE_CODE_REMOTE=true` environment variable is set
- Running in cloud-based development environment

---

## Key Principle: Use APIs with curl

In CCW, we use **HTTP APIs with curl** instead of CLI tools:

**GitHub Operations:**
- Use **GitHub REST API** with curl instead of `gh` CLI
- Requires: `GITHUB_TOKEN` environment variable
- Base URL: `https://api.github.com`

**Linear Operations:**
- Use **Linear GraphQL API** with curl
- Requires: `LINEAR_API_KEY` environment variable
- Base URL: `https://api.linear.app/graphql`
- **CRITICAL:** ALWAYS use `curl -k` (skip SSL verification)

---

## Extracting Repo Information

```bash
# Get repo owner/name (handles proxy URLs correctly)
REPO=$(git config --get remote.origin.url | sed -E 's|.*[:/]([^/]+/[^/]+)(\.git)?$|\1|' | sed 's|^local_proxy@[^/]*/git/||')
# Output: "duersjefen/deploy-kit"

# Get current branch
BRANCH=$(git branch --show-current)

# Get default branch
DEFAULT_BRANCH=$(git remote show origin | grep "HEAD branch" | sed 's/.*: //')
```

**Why the double sed?**
- First sed: Extracts `owner/repo` from git URLs
- Second sed: Removes `local_proxy@127.0.0.1:19541/git/` prefix (CCW specific)

---

## GitHub API Examples

### Create PR

```bash
REPO=$(git config --get remote.origin.url | sed -E 's|.*[:/]([^/]+/[^/]+)(\.git)?$|\1|' | sed 's|^local_proxy@[^/]*/git/||')
BRANCH=$(git branch --show-current)

curl -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/pulls" \
  -d "{
    \"title\": \"feat: Your feature description (DEP-X)\",
    \"body\": \"## Summary\n\nWhat changed\n\n## Changes\n- Item 1\n- Item 2\n\nLinear: DEP-X\n🤖 Generated with Claude Code\",
    \"head\": \"${BRANCH}\",
    \"base\": \"main\"
  }"
```

**Response contains:** PR number, URL, merge status

### Merge PR (Squash)

```bash
curl -X PUT \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}/merge" \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: Description (#${PR_NUMBER})\",
    \"commit_message\": \"Summary of changes\"
  }"
```

**Response:** `{"sha": "...", "merged": true, "message": "Pull Request successfully merged"}`

### Extract PR Number from Response

```bash
PR_RESPONSE=$(curl -s -X POST ... )
PR_NUMBER=$(echo "$PR_RESPONSE" | grep -o '"number": *[0-9]*' | head -1 | grep -o '[0-9]*')
```

### Check PR Status

```bash
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}"
```

---

## Linear API Examples

### Get Issue Details

```bash
# By identifier (DEP-31)
curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d '{"query": "query { issue(id: \"DEP-31\") { id identifier title description state { name } priority priorityLabel labels { nodes { name } } assignee { name email } } }"}'
```

**Note:** Linear uses identifiers (DEP-31) in queries, but UUIDs in mutations

### Update Issue to Done (Complete Workflow)

**Step 1:** Get issue UUID and team's Done state UUID
```bash
curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d '{"query": "query { issue(id: \"DEP-31\") { id team { states(filter: { type: { eq: \"completed\" } }) { nodes { id name } } } } }"}'
```

**Response:**
```json
{
  "data": {
    "issue": {
      "id": "7c4ab083-19be-4f5a-96f6-5c3237def046",
      "team": {
        "states": {
          "nodes": [{"id": "b9a89684-c517-4906-bb09-b5ff6608fb2d", "name": "Done"}]
        }
      }
    }
  }
}
```

**Step 2:** Update issue with UUIDs
```bash
ISSUE_UUID="7c4ab083-19be-4f5a-96f6-5c3237def046"
STATE_UUID="b9a89684-c517-4906-bb09-b5ff6608fb2d"

curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d "{\"query\": \"mutation { issueUpdate(id: \\\"${ISSUE_UUID}\\\", input: { stateId: \\\"${STATE_UUID}\\\" }) { success issue { identifier state { name } } } }\"}"
```

**Response:** `{"data": {"issueUpdate": {"success": true, "issue": {"identifier": "DEP-31", "state": {"name": "Done"}}}}}`

### List Team Issues (Backlog)

```bash
curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d '{"query": "query { team(id: \"DEP\") { issues(first: 20, filter: { state: { type: { eq: \"backlog\" } } }) { nodes { id identifier title state { name } priority assignee { name } } } } }"}'
```

### Add Comment to Issue

```bash
curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d "{\"query\": \"mutation { commentCreate(input: { issueId: \\\"${ISSUE_UUID}\\\", body: \\\"Completed in PR #172\\\" }) { success comment { id } } }\"}"
```

---

## Error Handling

### Linear SSL Certificate Errors

**Problem:**
```
TLS_error:|268435581:SSL routines:OPENSSL_internal:CERTIFICATE_VERIFY_FAILED
```

**Solution:** ALWAYS use `curl -k` for Linear API
- The `-k` flag skips SSL certificate verification
- Required in CCW environment due to certificate validation issues

### GitHub 403 Errors on Push

**Problem:**
```
error: RPC failed; HTTP 403
fatal: the remote end hung up unexpectedly
```

**Cause:** Branch name doesn't match session ID pattern

**Solution:** Branch must start with `claude/` and end with matching session ID
- Example: `claude/fix-npm-release-dep-31-011CUr8sDfqqr2699pjyjKcK`

### Extracting Data from API Responses

**Without jq (use grep):**
```bash
# Extract PR number
echo "$PR_RESPONSE" | grep -o '"number": *[0-9]*' | head -1 | grep -o '[0-9]*'

# Extract URL
echo "$PR_RESPONSE" | grep -o '"html_url": *"[^"]*"' | head -1 | sed 's/"html_url": *"\(.*\)"/\1/'

# Extract merge status
echo "$MERGE_RESPONSE" | grep -o '"merged": *[^,]*' | head -1
```

---

## Complete PR + Linear Workflow

```bash
# 1. Get repo info
REPO=$(git config --get remote.origin.url | sed -E 's|.*[:/]([^/]+/[^/]+)(\.git)?$|\1|' | sed 's|^local_proxy@[^/]*/git/||')
BRANCH=$(git branch --show-current)

# 2. Push branch
git push -u origin $BRANCH

# 3. Create PR
PR_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${REPO}/pulls" \
  -d "{\"title\": \"fix: Issue (DEP-31)\", \"body\": \"Linear: DEP-31\", \"head\": \"${BRANCH}\", \"base\": \"main\"}")

PR_NUMBER=$(echo "$PR_RESPONSE" | grep -o '"number": *[0-9]*' | head -1 | grep -o '[0-9]*')

# 4. Merge PR
curl -X PUT \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}/merge" \
  -d '{"merge_method": "squash"}'

# 5. Get Linear issue and Done state
LINEAR_RESPONSE=$(curl -sk -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d '{"query": "query { issue(id: \"DEP-31\") { id team { states(filter: { type: { eq: \"completed\" } }) { nodes { id } } } } }"}')

# Extract UUIDs (requires manual inspection of LINEAR_RESPONSE)
ISSUE_UUID=$(echo "$LINEAR_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

# 6. Update Linear issue
curl -k -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: ${LINEAR_API_KEY}" \
  -d "{\"query\": \"mutation { issueUpdate(id: \\\"${ISSUE_UUID}\\\", input: { stateId: \\\"${STATE_UUID}\\\" }) { success } }\"}"
```

---

## Cheat Sheet

| Task | Command Pattern | Key Flags |
|------|----------------|-----------|
| Create GitHub PR | `curl -X POST .../pulls` | `-H "Authorization: token ${GITHUB_TOKEN}"` |
| Merge GitHub PR | `curl -X PUT .../pulls/N/merge` | `merge_method: "squash"` |
| Get Linear issue | `curl -k -X POST .../graphql` | `-k` (skip SSL), use identifier in query |
| Update Linear issue | `curl -k -X POST .../graphql` | `-k`, use UUID in mutation |
| Extract repo name | `git config ... \| sed ... \| sed ...` | Double sed for proxy URLs |

---

## Limitations in CCW

**Cannot:**
- Publish to npm (no npm auth token)
- Deploy to AWS (no AWS credentials)
- Use `gh` CLI (blocked/unavailable)
- Use `linear` CLI (blocked/unavailable)

**Can:**
- All git operations (push, pull, commit, branch)
- Build and test code (npm, pnpm, node)
- GitHub operations via REST API
- Linear operations via GraphQL API
- All development tasks (read, write, edit files)

---

## Tips for Efficiency

1. **Store REPO variable early** - Avoids repeating the sed chain
2. **Use `-s` flag with curl** - Silent mode, cleaner output when piping to grep
3. **Always use curl -k for Linear** - Prevents SSL errors 100% of the time
4. **Extract PR number immediately** - Needed for merge operation
5. **Query Linear with identifier, mutate with UUID** - Different formats for different operations
6. **Get Done state dynamically** - Each team has different state UUIDs

---
