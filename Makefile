# =============================================================================
# Filter-iCal Development Makefile
# =============================================================================
# Fast native development with PostgreSQL in Docker
# See DEV_WORKFLOW.md for complete guide
# =============================================================================

.PHONY: help setup dev dev-db dev-backend dev-frontend stop test test-build test-all deploy-staging deploy-production status clean migrate-create migrate-up migrate-down migrate-history migrate-current migrate-stamp

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
		(cd backend && unset PASSWORD_ENCRYPTION_KEY && (test -d venv || python3.13 -m venv venv) && . venv/bin/activate && pip install -q -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000) & \
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
		unset PASSWORD_ENCRYPTION_KEY && \
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

stop: ## Stop database (ports auto-increment if in use)
	@echo "🛑 Stopping database..."
	@docker-compose -f docker-compose.dev.yml down
	@echo "✅ Database stopped"
	@echo "💡 Note: SST/Vite auto-detect available ports if 3000/8000 are in use"

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

test-build: ## Test frontend builds without errors (catches Vue compilation errors)
	@echo "🏗️  Testing frontend build..."
	@cd frontend && npm run build
	@echo "✅ Frontend builds successfully!"

test-all: ## Run all tests (unit + integration + E2E + build)
	@echo "🎯 Running complete test suite (excluding future/unimplemented features)..."
	@cd backend && \
		. venv/bin/activate && \
		python -m pytest tests/ -v -m "not future"
	@cd frontend && npm run test
	@echo ""
	@$(MAKE) test-build

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
## 🚀 Deployment Commands (Hybrid SST)
##

# SST Frontend Deployments (CloudFront + S3)
sst-deploy-dev: ## Deploy frontend to SST dev environment
	@echo "🚀 Deploying frontend to SST dev..."
	@npm run dev

sst-deploy-staging: ## Deploy frontend to SST staging (staging.filter-ical.de)
	@echo "🚀 Deploying frontend to SST staging..."
	@npm run deploy:staging

sst-deploy-production: ## Deploy frontend to SST production (filter-ical.de)
	@echo "🚀 Deploying frontend to SST production..."
	@npm run deploy:prod

sst-remove-dev: ## Remove SST dev deployment
	@echo "🗑️  Removing SST dev deployment..."
	@npm run remove:dev

sst-remove-staging: ## Remove SST staging deployment
	@echo "🗑️  Removing SST staging deployment..."
	@npm run remove:staging

sst-console: ## Open SST console (monitoring, logs)
	@npm run console

# Legacy EC2 Deployments (SSM-Based - for reference)
deploy-staging: ## Deploy to staging via SSM (builds on server) - LEGACY
	@$(MAKE) deploy ENV=staging

deploy-production: ## Deploy to production via SSM (builds on server) - LEGACY
	@$(MAKE) deploy ENV=production

deploy: ## Internal: Test, push, then deploy (use SKIP_TESTS=1 or SKIP_PUSH=1 to skip)
ifndef SKIP_TESTS
	@echo "🧪 Running pre-deployment checks..."
	@echo ""
	@echo "1️⃣  Testing frontend build (catches Vue compilation errors)..."
	@$(MAKE) test-build
	@echo ""
	@echo "2️⃣  Running backend unit tests..."
	@$(MAKE) test
	@echo ""
	@echo "✅ All pre-deployment checks passed!"
	@echo ""
endif
ifndef SKIP_PUSH
	@echo "📤 Pushing to GitHub..."
	@git push origin main || (echo "❌ Push failed. Use SKIP_PUSH=1 to deploy without pushing." && exit 1)
	@echo ""
endif
	@./deploy.sh $(ENV)

logs-staging: ## View staging backend logs (Ctrl+C to exit)
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔍 Connecting to staging logs (Ctrl+C to exit)..." && \
		aws ssm start-session --target $$EC2_INSTANCE_ID --region eu-north-1 \
			--document-name AWS-StartInteractiveCommand \
			--parameters command="docker logs -f filter-ical-backend-staging"

logs-production: ## View production backend logs (Ctrl+C to exit)
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔍 Connecting to production logs (Ctrl+C to exit)..." && \
		aws ssm start-session --target $$EC2_INSTANCE_ID --region eu-north-1 \
			--document-name AWS-StartInteractiveCommand \
			--parameters command="docker logs -f filter-ical-backend"

status: ## Check deployment status
	@echo "📊 Recent deployments:"
	@gh run list --limit 5 2>/dev/null || \
		echo "💡 Check manually: https://github.com/duersjefen/filter-ical/actions"

##
## 🔐 Remote Environment Management
##

edit-env-staging: ## SSH to EC2 to edit staging .env files
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔐 Opening SSH session to edit staging environment..." && \
		echo "📝 Edit: backend/.env.staging and frontend/.env.staging" && \
		echo "💡 After editing, restart containers with: make restart-staging" && \
		aws ssm start-session --target $$EC2_INSTANCE_ID --region eu-north-1

edit-env-production: ## SSH to EC2 to edit production .env files
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔐 Opening SSH session to edit production environment..." && \
		echo "📝 Edit: backend/.env.production and frontend/.env.production" && \
		echo "⚠️  CRITICAL: Changing VITE_* vars requires rebuild!" && \
		echo "💡 After editing, restart containers with: make restart-production" && \
		aws ssm start-session --target $$EC2_INSTANCE_ID --region eu-north-1

restart-staging: ## Restart staging containers (after .env changes)
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔄 Restarting staging containers..." && \
		aws ssm send-command --region eu-north-1 \
			--instance-ids $$EC2_INSTANCE_ID \
			--document-name "AWS-RunShellScript" \
			--parameters 'commands=["cd /opt/apps/filter-ical && docker-compose -p filter-ical-staging restart"]' \
			--output text --query 'Command.CommandId'
	@echo "✅ Restart command sent"
	@echo "💡 Check logs with: make logs-staging"

restart-production: ## Restart production containers (after .env changes)
	@if [ ! -f .env.ec2 ]; then \
		echo "❌ .env.ec2 not found"; \
		exit 1; \
	fi
	@. .env.ec2 && \
		echo "🔄 Restarting production containers..." && \
		aws ssm send-command --region eu-north-1 \
			--instance-ids $$EC2_INSTANCE_ID \
			--document-name "AWS-RunShellScript" \
			--parameters 'commands=["cd /opt/apps/filter-ical && docker-compose -p filter-ical-production restart"]' \
			--output text --query 'Command.CommandId'
	@echo "✅ Restart command sent"
	@echo "💡 Check logs with: make logs-production"

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
