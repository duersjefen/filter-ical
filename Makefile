# =============================================================================
# Project Makefile - Python + Vue 3 (Template for other languages)
# =============================================================================
# This Makefile is optimized for THIS project's stack (Python + Vue 3).
# When copying to a new project, adapt the language-specific commands below.
# The universal commands (deploy, clean, etc.) work with any language.

.PHONY: setup dev backend frontend stop test test-unit test-integration test-future test-all build clean help deploy deploy-force status health
.DEFAULT_GOAL := help

## Development Commands (Language-Specific: Python + Vue 3)

setup: setup-backend setup-frontend ## Setup local development environment
	@echo "✅ Setup complete! Run 'make dev' to start development."

dev: ## Start full development environment (kills existing servers first)
	@echo "🚀 Starting Python + Vue 3 development..."
	@echo "🔍 Checking for existing processes on ports 3000 and 8000..."
	@lsof -ti:3000 | xargs -r kill -9 2>/dev/null || true
	@lsof -ti:8000 | xargs -r kill -9 2>/dev/null || true
	@sleep 1
	@echo "🆕 Starting fresh development servers..."
	@echo "Press Ctrl+C to stop both services"
	@(trap 'kill 0' INT; $(MAKE) backend & $(MAKE) frontend & wait)

backend: setup-backend ## Start backend development server
	@echo "🐍 Starting Python FastAPI backend..."
	@cd backend && . venv/bin/activate && python -m app.main

setup-backend: ## Setup backend virtual environment and dependencies
	@echo "🔧 Setting up Python backend..."
	@cd backend && python3 -m venv venv 2>/dev/null || true
	@cd backend && . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

frontend: setup-frontend ## Start frontend development server
	@echo "🎨 Starting Vue 3 frontend..."
	@cd frontend && npm run dev

setup-frontend: ## Setup frontend dependencies
	@echo "🔧 Setting up frontend dependencies..."
	@cd frontend && npm install

stop: ## Stop all development servers
	@echo "🛑 Stopping development servers..."
	@pkill -f "python.*app.main" 2>/dev/null && echo "🐍 Backend stopped" || echo "🐍 Backend not running"
	@pkill -f "vite.*dev" 2>/dev/null && echo "🎨 Frontend stopped" || echo "🎨 Frontend not running"  
	@pkill -f "npm.*run.*dev" 2>/dev/null || true
	@echo "✅ All development servers stopped"

## Testing Commands (TDD Workflow - Universal Pattern)

test: test-unit ## Run unit tests (for commits)

test-unit: ## Run unit tests only - must pass for commits
	@echo "🧪 Running unit tests (must pass for commits)..."
	@cd backend && . venv/bin/activate && python3 -m pytest tests/ -m unit -v

test-integration: ## Run integration tests - for deployment readiness
	@echo "🔧 Running integration tests..."
	@cd backend && . venv/bin/activate && python3 -m pytest tests/ -m integration -v

test-future: ## Run TDD future tests - shows what to build next
	@echo "🔮 Running TDD future tests (can fail - guides development)..."
	@cd backend && . venv/bin/activate && python3 -m pytest tests/ -m future -v || echo "✨ Future tests show features to implement"

test-all: ## Run ALL tests (unit + integration + future + E2E)
	@echo "🎯 Running complete test suite..."
	@cd backend && . venv/bin/activate && python3 -m pytest tests/ -v
	@echo ""
	@echo "🎭 Running E2E tests..."
	@cd frontend && npx playwright test

test-e2e: ## Run end-to-end tests (catches UI issues)
	@echo "🎭 Running E2E tests..."
	@cd frontend && npx playwright test

test-api: setup-backend ## Run OpenAPI contract tests (validates API against spec)
	@echo "📋 Running OpenAPI contract tests..."
	@cd backend && . venv/bin/activate && python -m pytest tests/test_api_contract.py -v

test-backend: setup-backend ## Run backend unit tests
	@echo "🧪 Running backend tests..."
	@cd backend && . venv/bin/activate && python -m pytest tests/ -v --tb=short

## Production Commands (Docker-First - Universal)

build: ## Build production containers
	@echo "🏗️  Building production containers..."
	@cd backend && docker build -t backend --target production .
	@cd frontend && docker build -t frontend .
	@echo "✅ Build complete"

## CI/CD Integration Commands (Universal)

ci-test: ## Run tests in CI environment (Docker-first)
	@cd backend && docker build -t test-backend --target test . && docker run --rm test-backend python3 -m pytest tests/ -m unit -v

ci-build: ## Build containers in CI environment
	@$(MAKE) build

## Deployment Commands (Universal - Work with any language)

deploy: ## Deploy to production with automatic monitoring
	@echo "🚀 Deploying to production..."
	@echo "📋 Current status:"
	@git status --porcelain
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  You have uncommitted changes. Commit them first:"; \
		echo "   git add . && git commit -m 'Your commit message'"; \
		exit 1; \
	fi
	@echo "📤 Pushing to remote repository..."
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring deployment with GitHub CLI..."
	@echo "   Use Ctrl+C to stop monitoring (deployment continues)"
	@sleep 3
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId') && \
	 gh run watch $$latest_run --exit-status || true

deploy-force: ## Force deploy (skip dirty working tree check)  
	@echo "🚨 Force deploying (skipping dirty working tree check)..."
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring deployment with GitHub CLI..."
	@echo "   Use Ctrl+C to stop monitoring (deployment continues)"
	@sleep 3
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId') && \
	 gh run watch $$latest_run --exit-status || true

status: ## Check latest deployment status
	@echo "📊 Latest deployment status:"
	@gh run list --limit 3

todos: ## Show current TODOs and project status
	@echo "📋 Current TODOs:"
	@if [ -f TODO.md ]; then \
		echo ""; \
		grep -n "^- \[ \]" TODO.md | head -10 | sed 's/^/   /' || echo "   ✅ No pending todos!"; \
		echo ""; \
		echo "📊 Progress:"; \
		total=$$(grep -c "^- \[" TODO.md 2>/dev/null || echo "0"); \
		done=$$(grep -c "^- \[x\]" TODO.md 2>/dev/null || echo "0"); \
		if [ $$total -gt 0 ]; then \
			echo "   $$done/$$total tasks completed"; \
		fi; \
		echo ""; \
		echo "📄 View all: cat TODO.md"; \
	else \
		echo "   📝 Create TODO.md to track features"; \
	fi

## Utility Commands (Universal)

health: ## Check application health
	@echo "🔍 Checking application health..."
	@echo "🐍 Backend health check:"
	@curl -sf http://localhost:3000/health && echo " ✅ Backend healthy" || echo " ❌ Backend unhealthy"
	@echo "🎨 Frontend health check:"
	@curl -sf http://localhost:8000/ >/dev/null 2>&1 && echo " ✅ Frontend healthy" || echo " ❌ Frontend unhealthy"

clean: ## Clean up development artifacts
	@echo "🧹 Cleaning up..."
	@docker system prune -f 2>/dev/null || true
	@find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

help: ## Show this help message
	@echo "🚀 Python + Vue 3 Project Interface"
	@echo "==================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make setup    # Setup Python + Vue 3 environment"
	@echo "  make dev      # Start development servers"
	@echo "  make test     # Run tests"
	@echo ""
	@echo "🎯 To adapt for other languages:"
	@echo "   Modify the 'Language-Specific' commands above"
	@echo "   Keep the 'Universal' commands unchanged"