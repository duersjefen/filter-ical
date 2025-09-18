#!/bin/bash
# Clean Production Deployment Script
# For use when NO USERS exist yet - destroys all data and recreates fresh schema

set -e  # Exit on any error

echo "🚀 Clean Production Deployment"
echo "================================"
echo ""
echo "⚠️  WARNING: This will DESTROY ALL production data!"
echo "💡 Only use this when NO USERS exist yet"
echo ""

# Safety check
read -p "Are you absolutely sure? Type 'DESTROY_DATA' to continue: " -r
echo
if [[ ! $REPLY == "DESTROY_DATA" ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo "🏗️  Starting clean deployment..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Stop services
echo "🛑 Stopping services..."
docker-compose down || true

# Remove old database
echo "🗄️  Removing old database..."
rm -f backend/data/icalviewer.db || true

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin master

# Build containers
echo "🔨 Building containers..."
docker-compose build

# Start services (database will be created automatically)
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo "🔍 Health check..."
if curl -sf http://localhost:3000/health > /dev/null; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

if curl -sf http://localhost:8000/ > /dev/null; then
    echo "✅ Frontend healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo ""
echo "🎉 Clean deployment complete!"
echo "💡 Fresh database created with latest schema"
echo "🌐 Application running at:"
echo "   Frontend: http://localhost:8000"
echo "   Backend:  http://localhost:3000"
echo ""