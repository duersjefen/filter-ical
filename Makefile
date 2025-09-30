# =============================================================================
# Filter-iCal Development Makefile
# =============================================================================
# Fast native development with PostgreSQL in Docker
# See DEV_WORKFLOW.md for complete guide
# =============================================================================

.PHONY: help dev dev-db dev-backend dev-frontend stop test deploy-staging deploy-production status clean

.DEFAULT_GOAL := help

##
## 🚀 Development Commands
##

dev: ## Start full development environment (recommended)
	@echo "🚀 Starting full development environment..."
	@echo ""
	@$(MAKE) dev-db
	@echo ""
	@echo "✅ PostgreSQL running on localhost:5432"
	@echo ""
	@echo "Starting backend and frontend in parallel..."
	@bash -c "trap 'kill 0' EXIT; \
		(cd backend && (test -d venv || python3 -m venv venv) && . venv/bin/activate && pip install -q -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000) & \
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
		(test -d venv || python3 -m venv venv) && \
		. venv/bin/activate && \
		pip install -q -r requirements.txt && \
		uvicorn app.main:app --reload --host 0.0.0.0 --port 3000

dev-frontend: ## Run frontend natively (hot reload)
	@echo "🎨 Starting frontend with hot reload..."
	@echo "📍 http://localhost:5173"
	@cd frontend && \
		(test -d node_modules || npm install) && \
		npm run dev

stop: ## Stop all development services
	@echo "🛑 Stopping services..."
	@docker-compose -f docker-compose.dev.yml down
	@-pkill -f "uvicorn app.main:app"
	@-pkill -f "vite"
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
## 🚀 Deployment Commands
##

deploy-staging: ## Deploy to staging (push to master)
	@echo "🎭 Deploying to staging..."
	@echo ""
	@echo "📋 Checking git status..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  You have uncommitted changes. Commit first:"; \
		echo "   git add . && git commit -m 'Your message'"; \
		exit 1; \
	fi
	@echo "📤 Pushing to master (triggers auto-deploy)..."
	@git push origin master
	@echo ""
	@echo "👀 Monitoring deployment..."
	@sleep 3
	@gh run list --limit 1 2>/dev/null || echo "💡 Check GitHub Actions: https://github.com/duersjefen/filter-ical/actions"
	@echo ""
	@echo "🔍 Verify at: https://staging.filter-ical.de/health"

deploy-production: ## Deploy to production (manual workflow)
	@echo "🚀 Triggering production deployment..."
	@echo ""
	@echo "⚠️  Production requires manual approval!"
	@echo "📍 Opening GitHub Actions..."
	@gh workflow run deploy-production.yml 2>/dev/null || \
		(echo "💡 Manually trigger: https://github.com/duersjefen/filter-ical/actions" && exit 1)
	@echo ""
	@echo "👉 Go to GitHub Actions to approve the deployment"
	@echo "🔗 https://github.com/duersjefen/filter-ical/actions"

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
	@curl -sf http://localhost:5173 >/dev/null 2>&1 && echo "✅ http://localhost:5173" || echo "❌"

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
