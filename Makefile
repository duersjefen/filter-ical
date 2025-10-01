# =============================================================================
# Filter-iCal Development Makefile
# =============================================================================
# Fast native development with PostgreSQL in Docker
# See DEV_WORKFLOW.md for complete guide
# =============================================================================

.PHONY: help setup dev dev-db dev-backend dev-frontend stop test deploy-staging deploy-production approve-production deploy-production-auto status clean migrate-create migrate-up migrate-down migrate-history migrate-current migrate-stamp

.DEFAULT_GOAL := help

##
## 🚀 Development Commands
##

setup: ## Install all dependencies (run this first!)
	@echo "📦 Setting up development environment..."
	@echo ""
	@echo "🐍 Installing backend dependencies..."
	@cd backend && \
		(test -d venv || python3 -m venv venv) && \
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
	@echo "📍 http://localhost:8000"
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
	@gh workflow run "Deploy to Production" -f confirm=deploy 2>/dev/null || \
		(echo "❌ Failed to trigger workflow" && exit 1)
	@echo "✅ Workflow triggered"
	@echo ""
	@echo "👉 Use 'make approve-production' to approve"
	@echo "   or use 'make deploy-production-auto' to trigger + auto-approve"

approve-production: ## Approve pending production deployment
	@echo "🔍 Looking for pending production deployment..."
	@PENDING=$$(gh run list -w "Deploy to Production" -L 5 --json status,databaseId,conclusion \
		--jq '.[] | select(.status == "waiting" or .status == "in_progress") | .databaseId' | head -1); \
	if [ -z "$$PENDING" ]; then \
		echo "❌ No pending production deployment found"; \
		echo "💡 Run 'make deploy-production' first"; \
		exit 1; \
	fi; \
	echo "✅ Found pending deployment: $$PENDING"; \
	echo ""; \
	echo "⏳ Reviewing pending environments..."; \
	gh run view $$PENDING --json name,status,createdAt,url \
		--jq '"📋 Workflow: " + .name, "🕒 Started: " + .createdAt, "🔗 URL: " + .url'; \
	echo ""; \
	read -p "🤔 Approve production deployment? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "✅ Approving deployment..."; \
		ENV_ID=$$(gh api repos/duersjefen/filter-ical/actions/runs/$$PENDING/pending_deployments --jq '.[0].environment.id'); \
		gh api repos/duersjefen/filter-ical/actions/runs/$$PENDING/pending_deployments -X POST --input - <<< "{\"environment_ids\":[$$ENV_ID],\"state\":\"approved\",\"comment\":\"Approved via make approve-production\"}"; \
		echo ""; \
		echo "👀 Watching deployment progress..."; \
		gh run watch $$PENDING; \
	else \
		echo "❌ Approval cancelled"; \
		exit 1; \
	fi

deploy-production-auto: ## Deploy to production and auto-approve (use with caution!)
	@echo "🚀 Starting automated production deployment..."
	@echo "⚠️  This will deploy AND approve automatically!"
	@echo ""
	@read -p "🤔 Continue? (yes/no): " confirm; \
	if [ "$$confirm" != "yes" ]; then \
		echo "❌ Cancelled"; \
		exit 1; \
	fi
	@echo ""
	@echo "📤 Triggering workflow..."
	@gh workflow run "Deploy to Production" -f confirm=deploy
	@echo "⏳ Waiting for workflow to start..."
	@sleep 5
	@echo ""
	@echo "🔍 Finding workflow run..."
	@RUN_ID=$$(gh run list -w "Deploy to Production" -L 1 --json databaseId --jq '.[0].databaseId'); \
	if [ -z "$$RUN_ID" ]; then \
		echo "❌ Could not find workflow run"; \
		exit 1; \
	fi; \
	echo "✅ Found deployment: $$RUN_ID"; \
	echo ""; \
	echo "⏳ Waiting for approval gate..."; \
	sleep 3; \
	echo "✅ Auto-approving..."; \
	ENV_ID=$$(gh api repos/duersjefen/filter-ical/actions/runs/$$RUN_ID/pending_deployments --jq '.[0].environment.id'); \
	gh api repos/duersjefen/filter-ical/actions/runs/$$RUN_ID/pending_deployments -X POST --input - <<< "{\"environment_ids\":[$$ENV_ID],\"state\":\"approved\",\"comment\":\"Auto-approved via make deploy-production-auto\"}"; \
	echo ""; \
	echo "👀 Watching deployment progress..."; \
	gh run watch $$RUN_ID

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
