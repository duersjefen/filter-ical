#!/bin/bash
# Complete environment setup for EC2 deployments
# Creates full .env.staging and .env.production files with all required variables
# Run: ./scripts/setup-remote-env.sh

set -e

# Load EC2 instance ID from platform config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ENV="$SCRIPT_DIR/../../multi-tenant-platform/.env.ec2"

if [ -f "$PLATFORM_ENV" ]; then
    source "$PLATFORM_ENV"
elif [ -f ".env.ec2" ]; then
    source .env.ec2
else
    echo "❌ EC2 instance ID not found"
    echo "Expected: $PLATFORM_ENV or .env.ec2"
    exit 1
fi

if [ -z "$EC2_INSTANCE_ID" ]; then
    echo "❌ EC2_INSTANCE_ID not set in .env.ec2"
    exit 1
fi

REGION="eu-north-1"
APP_DIR="/opt/apps/filter-ical"

echo "🔐 Setting up complete environment files on EC2..."
echo "Instance: $EC2_INSTANCE_ID"
echo "App directory: $APP_DIR"
echo ""

# =============================================================================
# Create backend/.env.staging
# =============================================================================
echo "📝 Creating backend/.env.staging..."
aws ssm send-command \
    --instance-ids "$EC2_INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /opt/apps/filter-ical",
        "cat > backend/.env.staging << '\''EOF'\''
# Backend Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=false

# Database - TODO: Update with actual staging database credentials
DATABASE_URL=postgresql://filterical_staging:CHANGE_ME@postgres-platform:5432/filterical_staging

# Security - CRITICAL: These keys must be unique and strong
SECRET_KEY=staging-secret-key-CHANGE-ME
JWT_SECRET_KEY=staging-jwt-secret-CHANGE-ME-64-chars-minimum

# Admin (will be reset via admin panel after deployment)
ADMIN_PASSWORD=temporary-will-reset-after-deployment
ADMIN_EMAIL=info@paiss.me

# SMTP Email Configuration
SMTP_HOST=mail.privateemail.com
SMTP_PORT=587
SMTP_USERNAME=info@paiss.me
SMTP_PASSWORD=CHANGE-ME-get-from-1password
SMTP_FROM_EMAIL=info@paiss.me

# Backend Configuration
PYTHONPATH=/app
LOG_LEVEL=INFO
DISABLE_BACKGROUND_TASKS=false
HTTP_TIMEOUT=30
DEV_MODE=false
EOF",
        "chmod 600 backend/.env.staging",
        "ls -la backend/.env.staging",
        "echo \"✅ backend/.env.staging created\""
    ]' \
    --region "$REGION"

sleep 2

# =============================================================================
# Create frontend/.env.staging
# =============================================================================
echo "📝 Creating frontend/.env.staging..."
aws ssm send-command \
    --instance-ids "$EC2_INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /opt/apps/filter-ical",
        "cat > frontend/.env.staging << '\''EOF'\''
# Frontend Staging Environment Configuration
VITE_API_BASE_URL=https://staging.filter-ical.de
EOF",
        "chmod 600 frontend/.env.staging",
        "ls -la frontend/.env.staging",
        "echo \"✅ frontend/.env.staging created\""
    ]' \
    --region "$REGION"

sleep 2

# =============================================================================
# Create backend/.env.production
# =============================================================================
echo "📝 Creating backend/.env.production..."
aws ssm send-command \
    --instance-ids "$EC2_INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /opt/apps/filter-ical",
        "cat > backend/.env.production << '\''EOF'\''
# Backend Production Environment Configuration
ENVIRONMENT=production
DEBUG=false

# Database - TODO: Update with actual production database credentials
DATABASE_URL=postgresql://filterical_prod:CHANGE_ME@postgres-platform:5432/filterical_production

# Security - CRITICAL: These keys must be unique and strong
SECRET_KEY=production-secret-key-CHANGE-ME
JWT_SECRET_KEY=production-jwt-secret-CHANGE-ME-64-chars-minimum

# Admin (will be reset via admin panel after deployment)
ADMIN_PASSWORD=temporary-will-reset-after-deployment
ADMIN_EMAIL=info@paiss.me

# SMTP Email Configuration
SMTP_HOST=mail.privateemail.com
SMTP_PORT=587
SMTP_USERNAME=info@paiss.me
SMTP_PASSWORD=CHANGE-ME-get-from-1password
SMTP_FROM_EMAIL=info@paiss.me

# Backend Configuration
PYTHONPATH=/app
LOG_LEVEL=WARNING
DISABLE_BACKGROUND_TASKS=false
HTTP_TIMEOUT=30
DEV_MODE=false
EOF",
        "chmod 600 backend/.env.production",
        "ls -la backend/.env.production",
        "echo \"✅ backend/.env.production created\""
    ]' \
    --region "$REGION"

sleep 2

# =============================================================================
# Create frontend/.env.production
# =============================================================================
echo "📝 Creating frontend/.env.production..."
aws ssm send-command \
    --instance-ids "$EC2_INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /opt/apps/filter-ical",
        "cat > frontend/.env.production << '\''EOF'\''
# Frontend Production Environment Configuration
VITE_API_BASE_URL=https://filter-ical.de
EOF",
        "chmod 600 frontend/.env.production",
        "ls -la frontend/.env.production",
        "echo \"✅ frontend/.env.production created\""
    ]' \
    --region "$REGION"

echo ""
echo "✅ Environment files created!"
echo ""
echo "⚠️  CRITICAL NEXT STEPS:"
echo "1. SSH into EC2 and update placeholder values:"
echo "   aws ssm start-session --target $EC2_INSTANCE_ID --region $REGION"
echo "   cd /opt/apps/filter-ical"
echo "   nano backend/.env.staging    # Update DATABASE_URL, JWT_SECRET_KEY, SMTP_PASSWORD"
echo "   nano backend/.env.production # Update DATABASE_URL, JWT_SECRET_KEY, SMTP_PASSWORD"
echo ""
echo "2. Generate strong keys:"
echo "   JWT_SECRET_KEY:  python3 -c \"import secrets; print(secrets.token_urlsafe(64))\""
echo ""
echo "3. After updating, verify files:"
echo "   cat backend/.env.staging | grep -E 'DATABASE_URL|JWT_SECRET_KEY'"
echo "   cat frontend/.env.staging"
echo ""
echo "4. Deploy:"
echo "   make deploy-staging"
echo "   make deploy-production"
echo ""
echo "5. After deployment, reset admin password:"
echo "   Visit: https://staging.filter-ical.de/admin (or production URL)"
echo "   Use 'reset password' feature to set your admin password"
