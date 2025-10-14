#!/bin/bash
set -e

ENVIRONMENT="${1:-staging}"
REGION="eu-north-1"

# Load EC2 instance ID from shared platform config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../multi-tenant-platform/.env.ec2" ]; then
    source "$SCRIPT_DIR/../multi-tenant-platform/.env.ec2"
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

echo "🚀 Deploying filter-ical to $ENVIRONMENT"
echo "Instance: $INSTANCE_ID"
echo "Region: $REGION"
echo ""

# Deploy via SSM with compose project isolation
COMMAND_ID=$(aws ssm send-command \
    --region "$REGION" \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --comment "Deploy filter-ical $ENVIRONMENT" \
    --parameters "commands=[
        'set -e',
        'PROJECT_NAME=filter-ical-$ENVIRONMENT',
        'echo \"🚀 Deploying filter-ical to $ENVIRONMENT\"',
        'echo \"Project: \$PROJECT_NAME\"',
        'cd /opt/apps/filter-ical || exit 1',
        'if [ ! -d .git ]; then',
        '  cd /opt/apps',
        '  git clone https://github.com/duersjefen/filter-ical.git',
        '  cd filter-ical',
        'fi',
        'git fetch origin',
        'git reset --hard origin/main',
        'export ENVIRONMENT=$ENVIRONMENT',
        'export DOCKER_BUILDKIT=1',
        'export GIT_COMMIT=\$(git rev-parse --short HEAD)',
        'docker-compose -p \$PROJECT_NAME build --no-cache --build-arg GIT_COMMIT=\$GIT_COMMIT',
        'docker-compose -p \$PROJECT_NAME up -d --force-recreate',
        'echo \"⏳ Waiting for backend...\"',
        'sleep 10',
        'echo \"📊 Running migrations...\"',
        'docker-compose -p \$PROJECT_NAME exec -T backend alembic upgrade head',
        'echo \"✅ $ENVIRONMENT is live!\"'
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

# Health check
echo "🔍 Checking health..."
if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="https://filter-ical.de/health"
else
    HEALTH_URL="https://staging.filter-ical.de/health"
fi

if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo ""
    if [ "$ENVIRONMENT" = "production" ]; then
        echo "🌐 https://filter-ical.de"
    else
        echo "🌐 https://staging.filter-ical.de"
    fi
else
    echo "❌ Health check failed"
    echo "🔍 Debug with: make logs-$ENVIRONMENT"
    exit 1
fi
echo ""
