#!/bin/bash
# Local Clean Deployment Script
# Mirrors the production clean deployment logic using same containers
# Provides perfect parity with GitHub Actions clean deployment

set -e  # Exit on any error

echo "🚀 Local Clean Deployment (GitHub Actions Parity)"
echo "=================================================="
echo ""
echo "⚠️  WARNING: This will DESTROY ALL local data!"
echo "💡 This mirrors production clean deployment logic"
echo "🎯 Same containers and logic as GitHub Actions"
echo ""

# Safety check
read -p "Destroy local data and deploy fresh? Type 'YES' to continue: " -r
echo
if [[ ! $REPLY == "YES" ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo "🏗️  Starting clean deployment (mirrors production)..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop and remove existing containers (clean state)
echo "🛑 Stopping and removing existing containers..."
docker-compose down -v || true
docker system prune -f || true

# Remove old database files
echo "🗄️  Removing old database files..."
rm -f backend/data/*.db || true
rm -rf backend/data/ || true
mkdir -p backend/data

# Pull latest code (mirrors GitHub Actions)
echo "📥 Pulling latest code..."
git pull origin master || echo "⚠️  Git pull failed (working on changes?)"

# Build applications first (mirrors GitHub Actions)
echo "🔨 Building applications..."
make ci-build || echo "⚠️  Make build failed, using docker-compose build"

# Build containers with production-like settings
echo "🏗️  Building containers (production parity)..."
docker-compose build --no-cache

# Start services with fresh database
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready (same as GitHub Actions)
echo "⏳ Waiting for services to start..."
sleep 15

# Health check (same endpoints as GitHub Actions)
echo "🔍 Health check (mirrors GitHub Actions validation)..."
BACKEND_HEALTHY=false
FRONTEND_HEALTHY=false

# Backend health check
for i in {1..5}; do
    if curl -sf http://localhost:3000/health > /dev/null; then
        echo "✅ Backend healthy"
        BACKEND_HEALTHY=true
        break
    else
        echo "⏳ Backend not ready, attempt $i/5..."
        sleep 3
    fi
done

# Frontend health check
for i in {1..5}; do
    if curl -sf http://localhost:8000/ > /dev/null; then
        echo "✅ Frontend healthy"
        FRONTEND_HEALTHY=true
        break
    else
        echo "⏳ Frontend not ready, attempt $i/5..."
        sleep 3
    fi
done

# Validate both services are healthy
if [[ "$BACKEND_HEALTHY" != "true" ]]; then
    echo "❌ Backend health check failed"
    docker-compose logs backend
    exit 1
fi

if [[ "$FRONTEND_HEALTHY" != "true" ]]; then
    echo "❌ Frontend health check failed"
    docker-compose logs frontend
    exit 1
fi

# Test domain endpoints (mirrors production validation)
echo "🧪 Testing domain endpoints..."
if curl -sf http://localhost:3000/domains/exter/groups > /dev/null; then
    echo "✅ Domain endpoints working"
else
    echo "⚠️  Domain endpoints not responding (may be expected for fresh deployment)"
fi

echo ""
echo "🎉 Local clean deployment complete!"
echo "💡 Fresh database created with latest schema"
echo "🎯 This deployment mirrors production clean deployment exactly"
echo ""
echo "🌐 Application running at:"
echo "   Frontend: http://localhost:8000"
echo "   Backend:  http://localhost:3000"
echo "   Health:   http://localhost:3000/health"
echo ""
echo "📊 Next steps:"
echo "   1. Validate application works locally"
echo "   2. Run ./scripts/validate-contracts.sh"
echo "   3. Push to trigger GitHub Actions deployment"
echo ""