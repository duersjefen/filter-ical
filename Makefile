# =============================================================================
# Project Makefile - Docker-First Development
# =============================================================================
# This project uses Docker containers for development to eliminate environment
# conflicts and ensure consistent behavior across all development machines.

.PHONY: dev test test-unit test-integration test-future test-all build clean help deploy deploy-staging deploy-force status status-detailed health dev-docker stop-docker logs-docker shell-backend shell-frontend reset-docker
.DEFAULT_GOAL := help

## Docker Development Commands (Primary Workflow)

dev: dev-docker ## Start development environment (Docker)

dev-docker: ## Start full development environment with Docker
	@echo "🐳 Starting Docker development environment..."
	@echo "✨ Zero conflicts, fresh environment every time"
	@echo "📝 Backend: http://localhost:3000 | Frontend: http://localhost:8000"
	@docker-compose -f docker-compose.dev.yml up --build

stop: stop-docker ## Stop development environment

stop-docker: ## Stop Docker development environment
	@echo "🛑 Stopping Docker development environment..."
	@docker-compose -f docker-compose.dev.yml down

logs: logs-docker ## View development logs

logs-docker: ## View logs from Docker development environment
	@echo "📋 Viewing Docker development logs..."
	@docker-compose -f docker-compose.dev.yml logs -f

shell-backend: ## Open shell in backend development container
	@echo "🐍 Opening shell in backend container..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev /bin/bash

shell-frontend: ## Open shell in frontend development container
	@echo "🎨 Opening shell in frontend container..."
	@docker-compose -f docker-compose.dev.yml exec frontend-dev /bin/sh

reset: reset-docker ## Reset development environment (clean slate)

reset-docker: ## Reset Docker development environment (clean slate)
	@echo "🧹 Resetting Docker development environment..."
	@docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	@docker-compose -f docker-compose.dev.yml build --no-cache
	@echo "✅ Docker environment reset complete"

## Legacy Support (for compatibility)

setup: ## Setup environment for development
	@echo "🐳 This project uses Docker for development"
	@echo "💡 Use 'make dev' to start the development environment"

## Testing Commands (TDD Workflow - Universal Pattern)

test: test-unit ## Run unit tests (for commits)

test-unit: ## Run unit tests only - must pass for commits
	@echo "🧪 Running unit tests (must pass for commits)..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python3 -m pytest tests/ -m unit -v

test-integration: ## Run integration tests - for deployment readiness
	@echo "🔧 Running integration tests..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python3 -m pytest tests/ -m integration -v

test-future: ## Run TDD future tests - shows what to build next
	@echo "🔮 Running TDD future tests (can fail - guides development)..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python3 -m pytest tests/ -m future -v || echo "✨ Future tests show features to implement"

test-all: ## Run ALL tests (unit + integration + future + E2E)
	@echo "🎯 Running complete test suite..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python3 -m pytest tests/ -v
	@echo ""
	@echo "🎭 Running E2E tests..."
	@docker-compose -f docker-compose.dev.yml exec frontend-dev npx playwright test

test-e2e: ## Run end-to-end tests (catches UI issues)
	@echo "🎭 Running E2E tests..."
	@docker-compose -f docker-compose.dev.yml exec frontend-dev npx playwright test

test-api: ## Run OpenAPI contract tests (validates API against spec)
	@echo "📋 Running OpenAPI contract tests..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python -m pytest tests/test_api_contract.py -v

test-backend: ## Run backend unit tests in Docker
	@echo "🧪 Running backend tests..."
	@docker-compose -f docker-compose.dev.yml exec backend-dev python -m pytest tests/ -v --tb=short

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

deploy-staging: ## Deploy to staging environment for testing
	@echo "🎭 Deploying to staging environment..."
	@echo "💡 Use staging to test features before production!"
	@echo "📋 Current status:"
	@git status --porcelain
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  You have uncommitted changes. Commit them first:"; \
		echo "   git add . && git commit -m 'Your commit message'"; \
		exit 1; \
	fi
	@echo "📤 Pushing to remote repository..."
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring staging deployment with GitHub CLI..."
	@echo "   Use Ctrl+C to stop monitoring (deployment continues)"
	@sleep 3
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown") && \
	 if [ "$$latest_run" != "unknown" ]; then \
		 gh run watch $$latest_run --exit-status 2>/dev/null || echo "📊 Monitoring failed - check status with 'make status'"; \
	 else \
		 echo "📊 Could not get run ID - check status with 'make status'"; \
	 fi

deploy: ## Deploy to production with automatic monitoring  
	@echo "🚀 Deploying to production..."
	@echo "⚠️  This deploys to the LIVE website at https://filter-ical.de"
	@echo "💡 Consider using 'make deploy-staging' first to test!"
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
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown") && \
	 if [ "$$latest_run" != "unknown" ]; then \
		 gh run watch $$latest_run --exit-status 2>/dev/null || echo "📊 Monitoring failed - check status with 'make status'"; \
	 else \
		 echo "📊 Could not get run ID - check status with 'make status'"; \
	 fi

deploy-clean: ## Deploy with fresh database (no users yet - destroys all data) [FORCE_CLEAN_DEPLOY=true to skip confirmation]
	@echo "🚀 Clean deployment (⚠️  DESTROYS ALL DATA)"
	@echo "⚠️  This will reset the production database!"
	@echo "💡 Only use this when NO USERS exist yet"
	@if [ "$$FORCE_CLEAN_DEPLOY" = "true" ]; then \
		echo "🤖 Force mode enabled via FORCE_CLEAN_DEPLOY=true"; \
	elif [ -t 0 ]; then \
		read -p "Are you sure? Type 'RESET' to continue: " confirm && [ "$$confirm" = "RESET" ] || exit 1; \
	else \
		echo "🤖 Non-interactive mode detected - proceeding with clean deployment"; \
		echo "💡 To skip this in future: FORCE_CLEAN_DEPLOY=true make deploy-clean"; \
	fi
	@echo "📋 Current status:"
	@git status --porcelain
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "⚠️  You have uncommitted changes. Commit them first:"; \
		echo "   git add . && git commit -m 'Your commit message'"; \
		exit 1; \
	fi
	@echo "📤 Pushing to remote repository with clean deployment signal..."
	@git commit --allow-empty -m "🧹 CLEAN_DEPLOY: Force database reset and fresh startup" \
		-m "" \
		-m "This is a clean deployment that should:" \
		-m "- Remove all database volumes" \
		-m "- Start with fresh containers" \
		-m "- Trigger domain calendar creation" \
		-m "- Run demo data seeding" \
		-m "" \
		-m "🎭 Generated with [Claude Code](https://claude.ai/code)" \
		-m "" \
		-m "Co-Authored-By: Claude <noreply@anthropic.com>"
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring deployment with GitHub CLI..."
	@echo "   Use Ctrl+C to stop monitoring (deployment continues)"
	@sleep 3
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown") && \
	 if [ "$$latest_run" != "unknown" ]; then \
		 gh run watch $$latest_run --exit-status 2>/dev/null || echo "📊 Monitoring failed - check status with 'make status'"; \
	 else \
		 echo "📊 Could not get run ID - check status with 'make status'"; \
	 fi

deploy-force: ## Force deploy (skip dirty working tree check)  
	@echo "🚨 Force deploying (skipping dirty working tree check)..."
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring deployment with GitHub CLI..."
	@echo "   Use Ctrl+C to stop monitoring (deployment continues)"
	@sleep 3
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown") && \
	 if [ "$$latest_run" != "unknown" ]; then \
		 gh run watch $$latest_run --exit-status 2>/dev/null || echo "📊 Monitoring failed - check status with 'make status'"; \
	 else \
		 echo "📊 Could not get run ID - check status with 'make status'"; \
	 fi

status: ## Check latest deployment status
	@echo "📊 Latest deployment status:"
	@gh run list --limit 3 2>/dev/null || echo "❌ Could not fetch status - GitHub CLI may have connectivity issues"

status-detailed: ## Check detailed deployment status with logs
	@echo "📊 Detailed deployment status:"
	@latest_run=$$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "unknown") && \
	 if [ "$$latest_run" != "unknown" ]; then \
		 echo "🔍 Latest run ID: $$latest_run"; \
		 gh run view $$latest_run 2>/dev/null || echo "❌ Could not view run details"; \
	 else \
		 echo "❌ Could not get latest run ID"; \
	 fi

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
	@echo "🚀 iCal Viewer - Docker-First Development"
	@echo "=========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-18s\\033[0m %s\\n", $$1, $$2}'
	@echo ""
	@echo "🐳 Primary Development Workflow:"
	@echo "  make dev          # Start development environment (Docker)"
	@echo "  make stop         # Stop development environment"
	@echo "  make logs         # View development logs"
	@echo "  make reset        # Reset environment (clean slate)"
	@echo ""
	@echo "🔧 Development Tools:"
	@echo "  make shell-backend   # Access backend container"
	@echo "  make shell-frontend  # Access frontend container"
	@echo ""
	@echo "🧪 Testing & Deployment:"
	@echo "  make test         # Run tests"
	@echo "  make deploy-staging  # Deploy to staging for testing"
	@echo "  make deploy       # Deploy to production"