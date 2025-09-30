# Filter-iCal

Web application for filtering and customizing iCalendar feeds. Subscribe to calendars, apply custom filters, and get a personalized iCal feed URL.

**Live Application**: https://filter-ical.de

---

## 🎯 What It Does

Filter-iCal allows users to:
- Subscribe to existing iCalendar feeds
- Apply custom filters to events (by keyword, date range, category, etc.)
- Generate a new filtered iCal feed URL
- Subscribe to the filtered feed in any calendar application

**Use Case**: Remove unwanted events, focus on specific categories, or customize shared calendars without modifying the source.

---

## 🏗️ Tech Stack

**Backend**
- Python 3.11+ with FastAPI
- PostgreSQL 16 (user data, filters, subscriptions)
- Uvicorn ASGI server with hot reload
- Alembic for database migrations

**Frontend**
- Vue 3 with Composition API
- Pinia for state management
- Tailwind CSS v4
- Vite build tool with hot reload
- Vue DevTools integration

**Infrastructure**
- AWS EC2 (eu-north-1)
- Docker containerization
- Nginx reverse proxy with Let's Encrypt SSL
- GitHub Actions CI/CD

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for PostgreSQL)
- WSL2 (if on Windows)

### Local Development

```bash
# Clone repository
git clone https://github.com/duersjefen/filter-ical.git
cd filter-ical

# Start full environment (PostgreSQL + Backend + Frontend)
make dev
```

**Access:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:3000
- API Docs: http://localhost:3000/docs
- PostgreSQL: localhost:5432

**Development Features:**
- ✅ Hot reload for both frontend and backend
- ✅ Vue DevTools automatically available
- ✅ PostgreSQL in Docker (no local install needed)
- ✅ Automatic dependency installation

### Available Commands

```bash
# Development
make dev                   # Start all services
make stop                  # Stop all services
make health                # Check service status
make reset-db              # Reset local database

# Testing
make test                  # Run unit tests
make test-all              # Run complete test suite

# Deployment
make deploy-staging        # Deploy to staging
make deploy-production     # Deploy to production (requires approval)
make status                # Check deployment status

# Database
make reset-db              # Reset local database
make logs-db               # View PostgreSQL logs
```

---

## 📐 Architecture

### Development (Native + Docker Hybrid)

**Why Native?** Maximum performance with instant hot reload.

- **Backend**: Native Python with uvicorn (hot reload on .py changes)
- **Frontend**: Native Node.js with Vite (hot reload on .vue/.js changes)
- **Database**: Docker PostgreSQL (consistent, isolated, disposable)

This hybrid approach combines the speed of native development with the consistency of containerized databases.

### Project Structure

```
filter-ical/
├── backend/
│   ├── app/
│   │   ├── data/          # Pure functions (business logic)
│   │   ├── main.py        # FastAPI app (I/O orchestration)
│   │   └── core/          # Configuration, middleware
│   ├── tests/             # pytest unit + integration tests
│   └── alembic/           # Database migrations
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Vue 3 components
│   │   ├── composables/   # Pure functions (data transformations)
│   │   ├── stores/        # Pinia stores (state + I/O)
│   │   └── views/         # Page-level components
│   └── tests/             # Vitest + Playwright E2E tests
│
└── docker-compose.dev.yml # PostgreSQL only (for local dev)
```

### Design Principles

**1. Functional Core, Imperative Shell**
- Pure functions in `/data/` and `/composables/`
- Side effects isolated in `main.py` and stores
- 100% testable business logic

**2. Contract-Driven Development**
- OpenAPI specifications define API contracts
- Contract tests ensure compliance
- Frontend and backend develop independently

**3. Test-First Development (TDD)**
- Write failing tests first (`@pytest.mark.future`)
- Implement minimum code to pass
- Refactor safely with test coverage

---

## 🚢 Deployment

### Environments

| Environment | URL | Database | Trigger |
|-------------|-----|----------|---------|
| **Local** | http://localhost:8000 | `filterical_development` | `make dev` |
| **Staging** | https://staging.filter-ical.de | `filterical_staging` | Push to `master` |
| **Production** | https://filter-ical.de | `filterical_production` | Manual approval |

### Deployment Workflow

```bash
# 1. Develop locally
make dev

# 2. Run tests
make test

# 3. Commit changes
git add .
git commit -m "Add feature X"

# 4. Push to master (triggers staging deployment)
git push origin master

# 5. Verify on staging
curl https://staging.filter-ical.de/health

# 6. Deploy to production
make deploy-production
# → Opens GitHub Actions for manual approval
```

### Infrastructure

**AWS EC2**: i-01647c3d9af4fe9fc (13.62.136.72)
- **Region**: eu-north-1
- **OS**: Amazon Linux 2
- **Services**: Docker, nginx, certbot

**GitHub Actions CI/CD**:
- Automated builds on push
- Docker image publishing to GHCR
- Zero-downtime deployments
- Automatic health checks and rollback

---

## 🗄️ Database

### Local Development

PostgreSQL runs in Docker (no local installation needed):

```bash
# Connection details
Host: localhost
Port: 5432
Database: filterical_development
User: filterical_dev
Password: dev_password_change_me
```

### Migrations

**ALWAYS use Alembic for schema changes:**

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add user preferences table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 🧪 Testing

### Test Structure

- **Unit Tests**: Pure functions, business logic (`tests/unit/`)
- **Integration Tests**: API endpoints, database interactions (`tests/integration/`)
- **E2E Tests**: Full user workflows with Playwright (headless only)
- **Contract Tests**: OpenAPI specification compliance

### Running Tests

```bash
# Fast unit tests (for commits)
make test

# Complete test suite
make test-all

# Frontend tests
cd frontend && npm test

# E2E tests (headless)
cd frontend && npm run test:e2e
```

---

## 🔧 Development Tips

### Hot Reload

Both servers automatically reload on file changes:
- **Backend**: Changes to `.py` files trigger uvicorn reload
- **Frontend**: Changes to `.vue`/`.js` files trigger Vite HMR

No manual restarts needed!

### Checking Service Health

```bash
make health
```

Shows status of:
- PostgreSQL container
- Backend API
- Frontend dev server

### Debugging

**Frontend**: Vue DevTools available at http://localhost:8000
**Backend**: Interactive API docs at http://localhost:3000/docs

### Common Issues

**Port 5432 already in use:**
```bash
docker ps -a | grep postgres
docker stop <container-name>
```

**Services won't start:**
```bash
make stop
make dev
```

**Database needs reset:**
```bash
make reset-db
cd backend && alembic upgrade head
```

---

## 📚 Additional Documentation

- **[CLAUDE.md](CLAUDE.md)** - AI assistant instructions (architecture principles, TDD workflow)
---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD workflow)
3. Implement feature
4. Run tests: `make test`
5. Commit: `git commit -m "Add feature X"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request

**Code Review Checklist:**
- ✅ Tests pass (`make test-all`)
- ✅ Pure functions have no side effects
- ✅ API changes documented in OpenAPI spec
- ✅ Database migrations included (if schema changed)
- ✅ No console.log statements
- ✅ Follows naming conventions (no "New", "Updated", etc.)

---

## 📄 License

[Your License Here]

---

**Maintained by**: [Your Name/Team]
**Production Status**: ✅ Live at https://filter-ical.de
