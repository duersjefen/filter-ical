# Development Workflow Guide

## 🚀 Quick Start (Local Development in WSL2)

### 1. Start PostgreSQL
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### 2. Run Backend (Native - Hot Reload)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

### 3. Run Frontend (Native - Hot Reload)
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:3000
- API Docs: http://localhost:3000/docs

---

## 📋 Development Process

### Branch Strategy

```
master (protected)
  ↓
  └─ Auto-deploys to STAGING on push
  └─ Manual deploy to PRODUCTION (requires approval)

feature/* branches
  ↓
  └─ Develop locally
  └─ Create PR to master
  └─ PR merge triggers staging deployment
```

### Typical Development Flow

```bash
# 1. Create feature branch
git checkout -b feature/new-calendar-filter

# 2. Start local environment
docker-compose -f docker-compose.dev.yml up -d
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &

# 3. Make changes with instant hot reload
# Backend: Uvicorn auto-reloads on .py file changes
# Frontend: Vite auto-reloads on .vue/.js file changes

# 4. Test locally
curl http://localhost:3000/health
# Open http://localhost:5173 in browser

# 5. Commit and push
git add .
git commit -m "Add calendar filter feature"
git push origin feature/new-calendar-filter

# 6. Create Pull Request on GitHub
# → Merge to master → Auto-deploys to staging

# 7. Verify on staging
curl https://staging.filter-ical.de/health

# 8. Deploy to production (manual)
# → Go to GitHub Actions
# → Run "Deploy to Production" workflow
# → Requires manual approval
```

---

## 🗄️ Database Management

### Local Development Database

PostgreSQL runs in Docker, exposed on `localhost:5432`:
- **Database**: `filterical_development`
- **User**: `filterical_dev`
- **Password**: `dev_password_change_me`

### Run Migrations Locally

```bash
cd backend
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

### Reset Local Database

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
# Wait for PostgreSQL to start, then run migrations
cd backend && alembic upgrade head
```

---

## 🌍 Environments

### Development (Local WSL2)
- **URL**: http://localhost:5173
- **Database**: Local PostgreSQL in Docker
- **Hot Reload**: ✅ Instant
- **Purpose**: Fast iteration, debugging

### Staging (EC2)
- **URL**: https://staging.filter-ical.de
- **Database**: `filterical_staging` on shared PostgreSQL
- **Deployment**: Auto on push to `master`
- **Purpose**: Testing in production-like environment

### Production (EC2)
- **URL**: https://filter-ical.de
- **Database**: `filterical_production` on shared PostgreSQL
- **Deployment**: Manual with approval
- **Purpose**: Live user traffic

---

## 📦 Deployment Pipeline

### Automatic Staging Deployment

**Trigger**: Push to `master` branch

**Process**:
1. GitHub Actions builds Docker images
2. Pushes to GHCR (ghcr.io/duersjefen/filter-ical-*)
3. SSHs to EC2
4. Pulls new images
5. Creates `.env.staging` with GitHub Secrets
6. Runs `docker-compose up -d`
7. Health check verification
8. Auto-rollback on failure

**Workflows**:
- `.github/workflows/build-and-push-images.yml`
- `.github/workflows/deploy-staging.yml`

### Manual Production Deployment

**Trigger**: GitHub Actions → "Deploy to Production" → "Run workflow"

**Process**:
1. Requires manual confirmation
2. Requires environment approval (set in GitHub repo settings)
3. Same process as staging but uses production database
4. Health check verification
5. Manual rollback if needed

**Workflow**:
- `.github/workflows/deploy-production.yml`

---

## 🛠️ Common Tasks

### Install New Python Package

```bash
cd backend
source venv/bin/activate
pip install package-name
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add package-name dependency"
```

### Install New NPM Package

```bash
cd frontend
npm install package-name
git add package.json package-lock.json
git commit -m "Add package-name dependency"
```

### View Backend Logs (Local)

```bash
# Uvicorn outputs to terminal where you ran it
# Or check Docker logs if using docker-compose
docker logs filter-ical-postgres-dev
```

### View Logs (Staging/Production)

```bash
ssh ec2-user@13.62.136.72
docker logs filter-ical-backend-staging --tail 100 -f
docker logs filter-ical-frontend-staging --tail 100 -f
```

### Database Backup (Production)

```bash
ssh ec2-user@13.62.136.72
docker exec postgres-test pg_dump -U admin filterical_production > backup.sql
```

---

## 🔧 Troubleshooting

### Backend Won't Start

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check DATABASE_URL
cat .env.development | grep DATABASE_URL

# Check if database exists
docker exec filter-ical-postgres-dev psql -U filterical_dev -l
```

### Frontend Can't Connect to Backend

```bash
# Check VITE_API_BASE_URL
cat .env.development | grep VITE

# Check if backend is running
curl http://localhost:3000/health

# Check network
docker network inspect bridge
```

### Staging Deployment Failed

```bash
# Check GitHub Actions logs
gh run list --repo duersjefen/filter-ical
gh run view <run-id> --log-failed

# SSH to EC2 and check
ssh ec2-user@13.62.136.72
docker ps -a | grep filter-ical
docker logs filter-ical-backend-staging --tail 50
```

---

## 📊 Monitoring

### Local Development
- **Health Check**: http://localhost:3000/health
- **API Docs**: http://localhost:3000/docs
- **Database**: Connect with any PostgreSQL client to `localhost:5432`

### Staging/Production
- **Grafana**: https://monitoring.filter-ical.de (if configured)
- **Health Checks**: https://staging.filter-ical.de/health
- **Logs**: SSH to EC2 → `docker logs <container>`

---

## 🎯 Best Practices

1. **Always develop on feature branches**, never directly on `master`
2. **Test locally first** before pushing
3. **Run migrations locally** before pushing schema changes
4. **Verify on staging** before deploying to production
5. **Use meaningful commit messages**: "Add feature X" not "Update file"
6. **Keep PRs small**: Easier to review and rollback
7. **Document breaking changes** in PR description

---

## 🚨 Emergency Procedures

### Rollback Staging

```bash
ssh ec2-user@13.62.136.72
cd /opt/multi-tenant-platform
./lib/rollback.sh filter-ical staging
```

### Rollback Production

```bash
# Use GitHub Actions "Deploy to Production" with previous commit
# Or manual SSH:
ssh ec2-user@13.62.136.72
cd /opt/multi-tenant-platform
./lib/rollback.sh filter-ical production
```

### Database Recovery

```bash
# Restore from backup
ssh ec2-user@13.62.136.72
docker exec -i postgres-test psql -U admin filterical_production < backup.sql
```

---

**Questions?** Check the GitHub Actions logs or SSH to EC2 for detailed information.
