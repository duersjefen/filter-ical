#!/bin/bash
set -e

ENVIRONMENT="${1:-staging}"

# Load EC2 instance ID from local .env.ec2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env.ec2" ]; then
    source "$SCRIPT_DIR/.env.ec2"
fi

INSTANCE_ID="${EC2_INSTANCE_ID}"
REGION="${EC2_REGION:-eu-north-1}"

# Set backend port based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    BACKEND_PORT=3000
else
    BACKEND_PORT=3001
fi

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

echo "🚀 Deploying filter-ical to $ENVIRONMENT"
echo "Instance: $INSTANCE_ID"
echo "Region: $REGION"
echo ""

# Deploy via SSM
COMMAND_ID=$(aws ssm send-command \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --comment "Deploy filter-ical $ENVIRONMENT" \
    --parameters "commands=[
        'set -e',
        'echo \"🚀 Deploying filter-ical to $ENVIRONMENT\"',
        'cd /opt/apps/filter-ical || exit 1',
        'if [ ! -d .git ]; then',
        '  echo \"📦 Initial setup...\"',
        '  cd /opt/apps',
        '  git clone https://github.com/duersjefen/filter-ical.git',
        '  cd filter-ical',
        'fi',
        'echo \"📥 Fetching latest code...\"',
        'git fetch origin',
        'git reset --hard origin/main',
        'echo \"🐳 Building containers...\"',
        'export ENVIRONMENT=$ENVIRONMENT',
        'export BACKEND_PORT=$BACKEND_PORT',
        'export POSTGRES_PASSWORD=\$(cat /opt/secrets/postgres_password)',
        'export DOCKER_BUILDKIT=1',
        'export GIT_COMMIT=\$(git rev-parse --short HEAD)',
        'docker-compose build',
        'echo \"🚀 Starting services...\"',
        'docker-compose up -d',
        'echo \"⏳ Waiting for database...\"',
        'sleep 15',
        'echo \"📊 Running migrations...\"',
        'docker-compose exec -T backend alembic upgrade head || echo \"⚠️  Migrations may have failed\"',
        'echo \"✅ $ENVIRONMENT is live on port $BACKEND_PORT!\"',
        'docker-compose ps'
    ]" \
    --output text \
    --query 'Command.CommandId')

echo ""
echo "✅ Deployment command sent!"
echo "Command ID: $COMMAND_ID"
echo "⏳ Waiting for deployment to complete..."

# Wait for command to finish (no arbitrary timeout)
aws ssm wait command-executed \
    --region "$REGION" \
    --command-id "$COMMAND_ID" \
    --instance-id "$INSTANCE_ID"

echo "✅ Deployment finished!"

# Health check (direct to EC2)
echo "🔍 Checking backend health..."
EC2_IP="13.50.144.0"
HEALTH_URL="http://${EC2_IP}:${BACKEND_PORT}/health"

sleep 5
if curl -f -s -m 10 "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Backend deployment successful!"
    echo ""
    echo "📍 Backend: ${HEALTH_URL}"
    echo "🌐 Frontend: Will be available after SST deployment"
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "   - Production: https://filter-ical.de (pending SST deploy)"
        echo "   - API: https://api.filter-ical.de (pending SST deploy)"
    else
        echo "   - Staging: https://staging.filter-ical.de (pending SST deploy)"
        echo "   - API: https://api-staging.filter-ical.de (pending SST deploy)"
    fi
else
    echo "❌ Health check failed"
    echo "🔍 Debug with: make logs-$ENVIRONMENT"
    exit 1
fi
echo ""
