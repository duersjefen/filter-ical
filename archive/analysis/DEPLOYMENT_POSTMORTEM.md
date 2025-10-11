# Deployment Post-Mortem: Multi-Environment Docker Compose Issues

**Date:** 2025-10-10
**Status:** ✅ Resolved (both staging & production healthy)
**Impact:** Production downtime during staging deployments

---

## Summary

During deployment of admin features (password reset emails, group count fixes), we encountered a critical issue: **deploying to one environment (staging) would take down the other environment (production)**. Both environments are now stable, but the deployment process needs architectural improvements.

---

## Timeline

1. ✅ Fixed admin panel features (SMTP, email URLs, group counts)
2. ✅ Deployed to staging successfully
3. ❌ Deployed to production - failed due to missing JWT_SECRET_KEY
4. ✅ Fixed production env vars, restarted successfully
5. ❌ Redeployed staging - **production went down**
6. ✅ Restarted production manually
7. ❌ Production went down again when staging redeployed
8. ✅ **Root cause identified**: docker-compose state management
9. ✅ **Workaround**: Manual `docker run` for production containers

---

## Root Causes

### 1. **Shared `docker-compose.yml` + Single `.env` File**

**Problem:**
```bash
# Staging deployment:
cp .env.staging .env
docker-compose up -d  # Uses backend/frontend service names

# Production deployment:
cp .env.production .env
docker-compose up -d  # SAME service names, DIFFERENT .env
```

**What happens:**
- Docker Compose tracks container state by service name
- When `.env` changes, Compose sees containers as "stale"
- Running `docker-compose up -d` after changing `.env` **recreates containers**
- Staging deployment → `.env.staging` → recreates staging containers
- But if production was started with `.env.production`, Compose **doesn't know about those containers anymore**

### 2. **Container Naming Relies on Environment Variables**

```yaml
container_name: filter-ical-backend${ENVIRONMENT:+-}${ENVIRONMENT}
```

**Problem:**
- Container names are dynamic based on `ENVIRONMENT` var
- `docker-compose up` only manages containers defined in current `.env`
- Containers from other environments are "orphaned"

### 3. **No Deployment Isolation**

**Problem:**
- `docker-compose down` stops **ALL** filter-ical containers
- No mechanism to deploy to one environment without affecting the other

---

## Why This Happened

### Architectural Design Flaw
The deployment architecture **assumed we'd only run one environment at a time** on the EC2 instance. The multi-tenant platform supports multiple apps, but we're trying to run multiple **environments of the same app** simultaneously.

### Docker Compose Limitations
Docker Compose is designed for:
- Single-environment deployments
- Development workflows
- Local testing

**NOT designed for:**
- Multi-environment production deployments on same host
- Blue-green deployments
- Zero-downtime updates

---

## Solutions Analysis

### ❌ **Solution 1: Separate Compose Files (Over-engineered)**
```bash
docker-compose -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.production.yml up -d
```

**Pros:** Clean separation
**Cons:**
- Duplicate config files
- Maintenance burden
- Violates DRY principle

### ❌ **Solution 2: Docker Swarm/Kubernetes (Over-engineered)**
**Pros:** Enterprise-grade orchestration
**Cons:**
- Massive complexity increase
- Overkill for 2-environment setup
- Learning curve

### ✅ **Solution 3: Manual Container Management (Current Workaround)**
```bash
# Staging (use docker-compose)
cp .env.staging .env
docker-compose up -d

# Production (manual docker run)
docker run -d --name filter-ical-backend-production \
  --network platform \
  --env-file .env.production \
  --restart unless-stopped \
  filter-ical-backend
```

**Pros:**
- Simple
- Full control
- No interference

**Cons:**
- Inconsistent deployment methods
- Manual health checks
- No auto-restart via compose

### ✅ **Solution 4: Project-based Compose (RECOMMENDED)**
```bash
# Use docker-compose project names
docker-compose -p filter-ical-staging up -d
docker-compose -p filter-ical-production up -d
```

**Pros:**
- Uses compose for both
- Clean isolation
- Minimal changes
- Keeps all compose benefits (health checks, networks, volumes)

**Cons:**
- Requires updating deploy script
- Need to be careful with shared resources (networks, volumes)

---

## Recommended Fix (Not Over-Engineered)

### **Use Docker Compose Projects**

**Update `deploy.sh`:**
```bash
# Instead of:
cp .env.$ENVIRONMENT .env
docker-compose up -d

# Use:
docker-compose -p filter-ical-$ENVIRONMENT \
  --env-file .env.$ENVIRONMENT \
  up -d
```

**Benefits:**
1. ✅ Each environment is isolated by project name
2. ✅ Both use docker-compose (consistency)
3. ✅ No manual container management
4. ✅ Compose handles health checks, restarts, networks
5. ✅ Simple one-line change to deploy script

**Update `docker-compose.yml`:**
```yaml
services:
  backend:
    # Remove dynamic container names
    # Let compose auto-generate: filter-ical-staging-backend-1
    container_name: ${CONTAINER_NAME_BACKEND}
```

**Set in `.env` files:**
```bash
# .env.staging
CONTAINER_NAME_BACKEND=filter-ical-backend-staging
CONTAINER_NAME_FRONTEND=filter-ical-frontend-staging

# .env.production
CONTAINER_NAME_BACKEND=filter-ical-backend-production
CONTAINER_NAME_FRONTEND=filter-ical-frontend-production
```

---

## Additional Improvements (Future)

### 1. **Health Check Automation**
```bash
# deploy.sh addition
wait_for_healthy() {
  local url=$1
  local max_attempts=30
  for i in $(seq 1 $max_attempts); do
    if curl -f -s "$url/health" > /dev/null 2>&1; then
      echo "✅ Healthy after $i attempts"
      return 0
    fi
    sleep 2
  done
  echo "❌ Health check failed after $max_attempts attempts"
  return 1
}
```

### 2. **Rollback Capability**
```bash
# Tag images with timestamp
docker tag filter-ical-backend filter-ical-backend:$(date +%Y%m%d-%H%M%S)

# Rollback command
docker-compose -p filter-ical-production down
docker tag filter-ical-backend:20251010-153000 filter-ical-backend:latest
docker-compose -p filter-ical-production up -d
```

### 3. **Blue-Green Deployments** (Future consideration)
- Run new version on `:8001`, `:8002` ports
- Nginx switch upstream when healthy
- Zero-downtime deployments

---

## Immediate Action Items

- [ ] Update `deploy.sh` to use compose projects (`-p` flag)
- [ ] Remove dynamic container naming in `docker-compose.yml`
- [ ] Set explicit container names in `.env` files
- [ ] Test deployment to staging without affecting production
- [ ] Document new deployment process in CLAUDE.md
- [ ] Add automated rollback script

---

## Lessons Learned

### ✅ What Worked
1. Test-first workflow caught issues early
2. SSM-based deployment allows quick iteration
3. Separate databases prevented data corruption
4. Health checks caught failures immediately

### ❌ What Didn't Work
1. Shared `.env` file caused environment interference
2. `docker-compose down` too aggressive (stops everything)
3. Lack of deployment isolation testing
4. No rollback plan

### 🔧 Improvements
1. **Always test multi-environment scenarios** before production
2. **Use compose projects** for isolation
3. **Never use `docker-compose down`** in multi-environment setups
4. **Implement health check loops** instead of fixed sleep
5. **Tag images with versions** for quick rollback

---

## Conclusion

The root issue was **architectural**: using a single-environment deployment tool (docker-compose) for multi-environment deployments. The recommended fix is simple and maintainable: **use compose projects**. This provides isolation without over-engineering the solution.

**Current Status:** Both environments healthy via manual workaround
**Next Step:** Implement compose projects for long-term stability
**Complexity:** Low (one-line change to deploy script)
