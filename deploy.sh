#!/bin/bash
# =============================================================================
# Filter-iCal - SSM Deployment Script
# =============================================================================
# Deploys filter-ical to EC2 via AWS Systems Manager (SSM)
# Builds Docker images on server (no registry needed)
# Usage: ./deploy.sh [staging|production]
# =============================================================================

set -e

ENVIRONMENT="${1:-staging}"
REGION="eu-north-1"

# Load EC2 instance ID from .env file
if [ -f ".env.ec2" ]; then
    source .env.ec2
fi

INSTANCE_ID="${EC2_INSTANCE_ID}"

# Validation
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "❌ Invalid environment. Use: staging or production"
    echo "   Usage: ./deploy.sh [staging|production]"
    exit 1
fi

if [ -z "$INSTANCE_ID" ]; then
    echo "❌ EC2_INSTANCE_ID not set"
    echo "   Create .env.ec2 with: EC2_INSTANCE_ID=i-xxxxxxxxxxxxx"
    exit 1
fi

echo "🚀 Deploying Filter-iCal to $ENVIRONMENT"
echo "===================================="
echo "Instance: $INSTANCE_ID"
echo "Region: $REGION"
echo ""

# Determine container names based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    BACKEND_CONTAINER="filter-ical-backend"
    FRONTEND_CONTAINER="filter-ical-frontend"
else
    BACKEND_CONTAINER="filter-ical-backend-staging"
    FRONTEND_CONTAINER="filter-ical-frontend-staging"
fi

echo "📤 Sending deployment command via SSM..."
echo ""

# Deploy via SSM - build on server
aws ssm send-command \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --comment "Deploy filter-ical $ENVIRONMENT" \
    --parameters "commands=[
        'set -e',
        'echo \"🚀 Deploying filter-ical ($ENVIRONMENT)...\"',
        'cd /opt/apps/filter-ical || exit 1',
        'if [ ! -d .git ]; then',
        '  echo \"📥 Cloning repository...\"',
        '  cd /opt/apps',
        '  git clone https://github.com/duersjefen/filter-ical.git',
        '  cd filter-ical',
        'fi',
        'echo \"📥 Pulling latest code...\"',
        'git fetch origin',
        'git reset --hard origin/main',
        'git pull origin main',
        'echo \"📝 Copying environment-specific .env file...\"',
        'cp .env.$ENVIRONMENT .env',
        'echo \"🔨 Building Docker images...\"',
        'BACKEND_CONTAINER=$BACKEND_CONTAINER FRONTEND_CONTAINER=$FRONTEND_CONTAINER ENVIRONMENT=$ENVIRONMENT docker-compose build',
        'echo \"🚀 Starting containers...\"',
        'BACKEND_CONTAINER=$BACKEND_CONTAINER FRONTEND_CONTAINER=$FRONTEND_CONTAINER ENVIRONMENT=$ENVIRONMENT docker-compose up -d',
        'echo \"⏳ Waiting for containers to start...\"',
        'sleep 5',
        'echo \"🔍 Running database migrations...\"',
        'docker exec $BACKEND_CONTAINER alembic upgrade head || echo \"⚠️  Migration failed or already up to date\"',
        'echo \"🔍 Checking container status...\"',
        'docker ps | grep filter-ical || echo \"⚠️  Containers not found\"',
        'echo \"✅ Deployment complete!\"',
        'echo \"\"',
        'echo \"📋 Container Info:\"',
        'docker inspect $BACKEND_CONTAINER --format=\"{{.State.Status}}: {{.Name}}\" 2>/dev/null || echo \"Backend: $BACKEND_CONTAINER\"',
        'docker inspect $FRONTEND_CONTAINER --format=\"{{.State.Status}}: {{.Name}}\" 2>/dev/null || echo \"Frontend: $FRONTEND_CONTAINER\"'
    ]" \
    --output text

echo ""
echo "✅ Deployment command sent successfully!"
echo ""
echo "⏳ Waiting for deployment to complete (60s)..."
sleep 60

# Perform health check
echo "🔍 Checking health..."
if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="https://filter-ical.de/health"
else
    HEALTH_URL="https://staging.filter-ical.de/health"
fi

if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Deployment successful - health check passed"
    echo ""
    echo "🌐 Application is live:"
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  https://filter-ical.de"
    else
        echo "  https://staging.filter-ical.de"
    fi
else
    echo "❌ Health check failed - deployment may have issues"
    echo ""
    echo "🔍 Debug with:"
    echo "  make logs-$ENVIRONMENT"
    echo ""
    echo "Or connect interactively:"
    echo "  aws ssm start-session --target $INSTANCE_ID --region $REGION"
    exit 1
fi
echo ""
