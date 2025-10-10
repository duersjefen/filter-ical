# =============================================================================
# Filter-iCal Development Makefile
# =============================================================================
# Fast native development with PostgreSQL in Docker
# See DEV_WORKFLOW.md for complete guide
# =============================================================================

.PHONY: help setup dev dev-db dev-backend dev-frontend stop test deploy-staging deploy-production status clean migrate-create migrate-up migrate-down migrate-history migrate-current migrate-stamp

.DEFAULT_GOAL := help

##
## 🚀 Development Commands
##

setup: ## Install all dependencies (run this first!)
	@echo "📦 Setting up development environment..."
	@echo ""
	@echo "🐍 Installing backend dependencies..."
	@cd backend && \
		(test -d venv || python3.13 -m venv venv) && \
		. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	@echo "✅ Backend dependencies installed"
	@echo ""
	@echo "🎨 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ Frontend dependencies installed"
	@echo ""
	@echo "🐘 Starting PostgreSQL database..."
	@$(MAKE) dev-db
	@echo ""
	@echo "✅ Setup complete! Use 'make dev' to start development"

##
## 🚀 Development Commands
##

dev: ## Start full development environment (recommended)
	@echo "🚀 Starting full development environment..."
	@$(MAKE) stop
	@echo ""
	@$(MAKE) dev-db
	@echo ""
	@echo "✅ PostgreSQL running on localhost:5432"
	@echo ""
	@echo "⬆️  Applying database migrations..."
	@cd backend && \
		(test -d venv || python3.13 -m venv venv) && \
		. venv/bin/activate && \
		pip install -q -r requirements.txt && \
		alembic upgrade head 2>&1 | grep -E "(Running upgrade|Already at head|ERROR)" || true
	@echo "✅ Migrations applied"
	@echo ""
	@echo "🐍 Starting backend..."
	@bash -c "trap 'kill 0' EXIT; \
		(cd backend && (test -d venv || python3.13 -m venv venv) && . venv/bin/activate && pip install -q -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000) & \
		BACKEND_PID=$$!; \
		echo '⏳ Waiting for backend to be ready...'; \
		for i in {1..30}; do \
			if curl -sf http://localhost:3000/health >/dev/null 2>&1; then \
				echo '✅ Backend ready on http://localhost:3000'; \
				break; \
			fi; \
			sleep 1; \
		done; \
		echo '🎨 Starting frontend...'; \
		(cd frontend && (test -d node_modules || npm install) && npm run dev) & \
		wait"

dev-db: ## Start PostgreSQL database only
	@echo "🐘 Starting PostgreSQL database..."
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ PostgreSQL running on localhost:5432"

dev-backend: ## Run backend natively (hot reload)
	@echo "🐍 Starting backend with hot reload..."
	@echo "📍 http://localhost:3000"
	@echo "📖 http://localhost:3000/docs"
	@cd backend && \
		(test -d venv || python3.13 -m venv venv) && \
		. venv/bin/activate && \
		pip install -q -r requirements.txt && \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

dev-frontend: ## Run frontend natively (hot reload)
	@echo "🎨 Starting frontend with hot reload..."
	@echo "📍 http://localhost:8000"
	@cd frontend && \
		(test -d node_modules || npm install) && \
		npm run dev

preview: ## Build and preview production frontend
	@echo "📦 Building production bundle..."
	@cd frontend && npm run build
	@echo "✅ Build complete!"
	@echo ""
	@echo "🔍 Starting production preview..."
	@echo "📍 http://localhost:4173"
	@echo ""
	@echo "💡 Test performance with Lighthouse on localhost:4173"
	@cd frontend && npm run preview

stop: ## Stop all development services
	@echo "🛑 Stopping services..."
	@docker-compose -f docker-compose.dev.yml down
	@-lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@echo "✅ All services stopped"

clean: ## Clean development artifacts and containers
	@echo "🧹 Cleaning up..."
	@docker-compose -f docker-compose.dev.yml down -v
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

reset-db: ## Reset local development database
	@echo "🗄️  Resetting development database..."
	@docker-compose -f docker-compose.dev.yml down -v
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Database reset. Run migrations if needed."

##
## 🧪 Testing Commands
##

test: ## Run unit tests
	@echo "🧪 Running unit tests..."
	@cd backend && \
		. venv/bin/activate && \
		python -m pytest tests/ -m unit -v

test-all: ## Run all tests (unit + integration + E2E)
	@echo "🎯 Running complete test suite..."
	@cd backend && \
		. venv/bin/activate && \
		python -m pytest tests/ -v
	@cd frontend && npm run test

##
## 🗄️  Database Migration Commands
##

migrate-create: ## Create a new migration (usage: make migrate-create name="add_user_table")
	@echo "📝 Creating new migration..."
	@if [ -z "$(name)" ]; then \
		echo "❌ Error: Please provide a name"; \
		echo "   Usage: make migrate-create name=\"add_user_table\""; \
		exit 1; \
	fi
	@cd backend && \
		. venv/bin/activate && \
		alembic revision --autogenerate -m "$(name)"
	@echo "✅ Migration created! Review it in backend/alembic/versions/"

migrate-up: ## Apply all pending migrations
	@echo "⬆️  Applying database migrations..."
	@cd backend && \
		. venv/bin/activate && \
		alembic upgrade head
	@echo "✅ Migrations applied"

migrate-down: ## Revert last migration
	@echo "⬇️  Reverting last migration..."
	@cd backend && \
		. venv/bin/activate && \
		alembic downgrade -1
	@echo "✅ Migration reverted"

migrate-history: ## Show migration history
	@echo "📚 Migration history:"
	@cd backend && \
		. venv/bin/activate && \
		alembic history --verbose

migrate-current: ## Show current migration version
	@echo "📍 Current migration:"
	@cd backend && \
		. venv/bin/activate && \
		alembic current --verbose

migrate-stamp: ## Mark database as being at specific version (usage: make migrate-stamp version="head")
	@echo "🏷️  Stamping database to $(version)..."
	@cd backend && \
		. venv/bin/activate && \
		alembic stamp $(version)
	@echo "✅ Database stamped to $(version)"

##
## 🚀 Deployment Commands (SSM-Based)
##

deploy-staging: ## Deploy to staging via SSM (builds on server)
	@./deploy.sh staging

deploy-production: ## Deploy to production via SSM (builds on server)
	@./deploy.sh production

status: ## Check deployment status
	@echo "📊 Recent deployments:"
	@gh run list --limit 5 2>/dev/null || \
		echo "💡 Check manually: https://github.com/duersjefen/filter-ical/actions"

##
## 🛠️ Utility Commands
##

health: ## Check application health
	@echo "🔍 Checking health..."
	@echo -n "🐘 PostgreSQL: "
	@docker exec filter-ical-postgres-dev pg_isready -U filterical_dev >/dev/null 2>&1 && echo "✅" || echo "❌"
	@echo -n "🐍 Backend:    "
	@curl -sf http://localhost:3000/health >/dev/null 2>&1 && echo "✅ http://localhost:3000" || echo "❌"
	@echo -n "🎨 Frontend:   "
	@curl -sf http://localhost:8000 >/dev/null 2>&1 && echo "✅ http://localhost:8000" || echo "❌"

logs-db: ## View PostgreSQL logs
	@docker logs filter-ical-postgres-dev -f

##
## 📚 Help
##

help: ## Show this help message
	@echo ""
	@echo "🌐 Filter-iCal Development"
	@echo "═══════════════════════════════════════════"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📖 Full guide: cat DEV_WORKFLOW.md"
	@echo ""
