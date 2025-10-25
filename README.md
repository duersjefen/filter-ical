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
- SSM-based deployment (builds on server)

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
- Frontend: http://localhost:8000 (auto-increments to 8001, 8002 if port in use)
- Backend API: http://localhost:3000 (auto-increments to 3001, 3002 if port in use)
- API Docs: http://localhost:3000/docs
- PostgreSQL: localhost:5432

**Development Features:**
- ✅ Hot reload for both frontend and backend
- ✅ Vue DevTools automatically available
- ✅ PostgreSQL in Docker (no local install needed)
- ✅ Automatic dependency installation
- ✅ Multiple dev instances can run simultaneously (auto port increment)
- ✅ Isolated dev AWS resources (separate CloudFormation stacks)

### Available Commands

```bash
# Development
make dev                   # Start all services (dev stage)
make stop                  # Stop database (ports auto-increment if in use)
make health                # Check service status
make reset-db              # Reset local database

# Testing
make test                  # Run unit tests
make test-all              # Run complete test suite
make preview               # Build and test production frontend locally

# SST Deployment (CloudFront + S3)
make sst-deploy-staging        # Deploy frontend to staging.filter-ical.de
make sst-deploy-production     # Deploy frontend to filter-ical.de
make sst-remove-dev            # Remove dev stage AWS resources
make sst-console               # Open SST console (monitoring, logs)

# Legacy Deployment (SSM-based EC2)
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

| Environment | URL | Database | AWS Resources | Trigger |
|-------------|-----|----------|---------------|---------|
| **Dev** | http://localhost:8000 | `filterical_development` | Isolated CloudFormation stacks | `make dev` |
| **Staging** | https://staging.filter-ical.de | `filterical_staging` | Staging CloudFront distribution | `make sst-deploy-staging` |
| **Production** | https://filter-ical.de | `filterical_production` | Production CloudFront distribution | `make sst-deploy-production` |

**Note**: Each stage has completely isolated AWS resources (separate CloudFormation stacks, S3 buckets, CloudFront distributions).

### Deployment Workflow

```bash
# 1. Develop locally
make dev

# 2. Run tests
make test

# 3. Commit changes
git add .
git commit -m "Add feature X"
git push origin main  # Optional: backup to GitHub

# 4. Deploy to staging via SSM (builds on server)
make deploy-staging

# 5. Verify on staging
curl https://staging.filter-ical.de/health

# 6. Deploy to production via SSM
make deploy-production
```

### Prerequisites for Deployment

1. **EC2 Instance**: Running Amazon Linux 2023 in eu-north-1
2. **AWS CLI**: Configured with SSM permissions
3. **Instance ID**: Set in `.env.ec2` (copy from `.env.ec2.example`)

```bash
# Create .env.ec2 file
cp .env.ec2.example .env.ec2
# Edit and add your EC2_INSTANCE_ID
```

### Infrastructure

**AWS EC2**: eu-north-1
- **OS**: Amazon Linux 2023
- **Services**: Docker, nginx, certbot
- **Deployment**: SSM (AWS Systems Manager)

**SSM-Based Deployment**:
- Builds Docker images on server (no registry needed)
- Connects via AWS Systems Manager (no SSH)
- Automatic database migrations
- Zero-downtime container updates

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

**Port 3000 or 8000 already in use:**
- No action needed! SST/Vite automatically increment to next available port
- Multiple dev instances can run simultaneously

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

**Clean up dev stage AWS resources:**
```bash
make sst-remove-dev
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
