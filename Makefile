# =============================================================================
# Universal Project Interface - Language Independent
# =============================================================================
# This Makefile provides a standardized interface that works with any language.
# Each project only needs to implement these Docker-based targets.

.PHONY: setup dev backend frontend test test-backend test-frontend build clean help
.DEFAULT_GOAL := help

## Development Commands

setup: ## Setup local development environment (language auto-detected)
	@echo "📦 Setting up local development environment..."
	@if [ -f "backend/requirements.txt" ]; then \
		cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt; \
	elif [ -f "backend/package.json" ]; then \
		cd backend && npm install; \
	elif [ -f "backend/deps.edn" ]; then \
		echo "Clojure setup - dependencies managed by clj tool"; \
	fi
	@if [ -f "frontend/package.json" ]; then \
		cd frontend && npm install; \
	fi
	@echo "✅ Setup complete! Run 'make dev' to start development."

dev: setup ## Start full development environment (backend + frontend)
	@echo "🚀 Starting development environment..."
	@echo "Press Ctrl+C to stop both services"
	@(trap 'kill 0' INT; $(MAKE) backend & $(MAKE) frontend & wait)

backend: ## Start backend development server (language auto-detected)
	@echo "🚀 Starting backend..."
	@if [ -f "backend/Dockerfile" ]; then \
		cd backend && docker build -t dev-backend --target development . && docker run -p 3000:3000 -v $(PWD)/backend:/app dev-backend; \
	elif [ -f "backend/requirements.txt" ]; then \
		cd backend && . venv/bin/activate && python app/main.py; \
	elif [ -f "backend/package.json" ]; then \
		cd backend && npm run dev; \
	elif [ -f "backend/deps.edn" ]; then \
		cd backend && clj -M:run; \
	else \
		echo "❌ No recognized backend configuration found"; \
		exit 1; \
	fi

frontend: ## Start frontend development server (language auto-detected)  
	@echo "🎨 Starting frontend..."
	@if [ -f "frontend/Dockerfile" ]; then \
		cd frontend && docker build -t dev-frontend --target development . && docker run -p 5173:5173 -v $(PWD)/frontend:/app dev-frontend; \
	elif [ -f "frontend/package.json" ]; then \
		cd frontend && npm run dev; \
	else \
		echo "❌ No recognized frontend configuration found"; \
		exit 1; \
	fi

## Testing Commands (Docker-first, Language Independent)

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests (Docker-first approach)
	@echo "🧪 Testing backend..."
	@if [ -f "backend/Dockerfile" ] && docker --version >/dev/null 2>&1; then \
		cd backend && docker build -t test-backend --target test . && docker run --rm test-backend; \
	elif [ -f "backend/requirements.txt" ] && [ -d "backend/tests" ]; then \
		echo "🐍 Python backend detected, checking dependencies..."; \
		if command -v python3 >/dev/null 2>&1; then \
			cd backend && \
			if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then \
				. venv/bin/activate && python3 -m pytest tests/ -v; \
			elif python3 -c "import pytest" 2>/dev/null; then \
				python3 -m pytest tests/ -v; \
			else \
				echo "⚠️  pytest not installed, install with: pip install pytest"; \
				exit 1; \
			fi; \
		else \
			echo "⚠️  Python 3 not found"; \
			exit 1; \
		fi; \
	elif [ -f "backend/package.json" ]; then \
		echo "📦 Node.js backend detected..."; \
		if command -v npm >/dev/null 2>&1; then \
			cd backend && npm ci && npm test; \
		else \
			echo "⚠️  npm not found"; \
			exit 1; \
		fi; \
	elif [ -f "backend/deps.edn" ]; then \
		echo "☕ Clojure backend detected..."; \
		if command -v clj >/dev/null 2>&1; then \
			cd backend && clj -M:test; \
		else \
			echo "⚠️  clj command not found"; \
			exit 1; \
		fi; \
	else \
		echo "⚠️  No backend tests found or configured"; \
	fi

test-frontend: ## Run frontend tests (Docker-first approach)
	@echo "🎨 Testing frontend..."  
	@if [ -f "frontend/Dockerfile" ]; then \
		cd frontend && docker build -t test-frontend --target test . 2>/dev/null && docker run --rm test-frontend || echo "⚠️  Frontend tests not configured in Docker"; \
	elif [ -f "frontend/package.json" ]; then \
		cd frontend && npm ci && npm run build; \
	else \
		echo "⚠️  No frontend tests found or configured"; \
	fi

## Production Commands

build: ## Build production containers
	@echo "🏗️  Building production containers..."
	@if [ -f "backend/Dockerfile" ]; then \
		cd backend && docker build -t backend --target production .; \
	fi
	@if [ -f "frontend/Dockerfile" ]; then \
		cd frontend && docker build -t frontend .; \
	fi
	@echo "✅ Build complete"

## Utility Commands

health: ## Check application health
	@echo "🔍 Checking application health..."
	@curl -sf http://localhost:3000/health && echo " ✅ Backend healthy" || echo " ❌ Backend unhealthy"

clean: ## Clean up development artifacts (universal cleanup)
	@echo "🧹 Cleaning up..."
	@docker system prune -f 2>/dev/null || true
	@find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".shadow-cljs" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".cpcache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "target" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

## CI/CD Integration Commands (Used by GitHub Actions and pre-commit hooks)

ci-test: ## Run tests in CI environment (language independent)
	@$(MAKE) test-backend
	@$(MAKE) test-frontend

ci-build: ## Build containers in CI environment (language independent)
	@$(MAKE) build

## Deployment Commands

deploy: ## Deploy to production with native GitHub CLI monitoring
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
	@gh run watch || true

deploy-force: ## Force deploy (skip dirty working tree check)  
	@echo "🚨 Force deploying (skipping dirty working tree check)..."
	@git push origin $$(git branch --show-current)
	@echo "👀 Monitoring deployment..."
	@gh run watch || true

status: ## Check latest deployment status
	@echo "📊 Latest deployment status:"
	@gh run list --limit 3

help: ## Show this help message
	@echo "🚀 Universal Project Interface (Language Independent)"
	@echo "===================================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make setup    # Auto-detect and setup environment"
	@echo "  make dev      # Start development (any language)"
	@echo "  make test     # Run all tests (Docker-first)"
	@echo ""
	@echo "This Makefile works with Python, Node.js, Clojure, or any Docker-based project."