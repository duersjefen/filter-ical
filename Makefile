.PHONY: setup dev backend frontend docker-dev docker-clean test health help

# Default target
.DEFAULT_GOAL := help

## Development Commands

setup: ## Setup local development environment
	@echo "📦 Setting up local development environment..."
	@cd frontend && npm install
	@cd backend && mkdir -p resources data && ln -sf ../../frontend/resources/public resources/public
	@echo "✅ Setup complete! Run 'make dev' to start development."

dev: setup ## Start full development environment (backend + frontend)
	@echo "🚀 Starting iCal Viewer development environment..."
	@echo ""
	@echo "Starting backend (port 3000) and frontend (port 8001) in parallel..."
	@echo "Access your app at: http://localhost:3000/app"
	@echo ""
	@echo "Press Ctrl+C to stop both services"
	@echo ""
	@(trap 'kill 0' INT; make backend & make frontend & wait)

backend: ## Start backend server only
	@echo "🚀 Starting backend server on http://localhost:3000"
	@cd backend && clj -M:run

frontend: ## Start frontend development server only
	@echo "🚀 Starting frontend development server on http://localhost:8001"
	@cd frontend && npm run dev

## Docker Development (Production Parity)

docker-dev: ## Start Docker development environment (mirrors production exactly)
	@echo "🐳 Starting Docker development environment..."
	@echo "   • Perfect production parity"
	@echo "   • Backend: http://localhost:3000/app"
	@echo "   • API: http://localhost:3000/api/"
	@docker-compose -f docker-compose.dev.yml up --build -d

docker-clean: ## Clean Docker development environment
	@echo "🧹 Cleaning Docker development environment..."
	@docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	@docker system prune -f

## Testing & Utility Commands

test: ## Run all tests
	@echo "🧪 Running backend tests..."
	@cd backend && clj -M:test

health: ## Check application health
	@echo "🔍 Checking application health..."
	@curl -sf http://localhost:3000/health && echo " ✅ Backend healthy" || echo " ❌ Backend unhealthy"

clean: ## Clean development artifacts
	@echo "🧹 Cleaning development artifacts..."
	@rm -rf frontend/node_modules frontend/.shadow-cljs
	@rm -rf backend/.cpcache backend/target
	@rm -f backend/resources/public backend/data/user-*.edn
	@echo "✅ Cleaned"

help: ## Show this help message
	@echo "iCal Viewer Development Commands"
	@echo "================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  make setup    # First time setup"
	@echo "  make dev      # Start development environment"