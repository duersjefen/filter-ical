#!/bin/bash
# Validate environment configuration before deployment
# Run: ./scripts/validate-env.sh staging|production

set -e

ENV="${1:-staging}"

if [ "$ENV" != "staging" ] && [ "$ENV" != "production" ]; then
    echo "❌ Usage: $0 <staging|production>"
    exit 1
fi

# Load EC2 instance ID
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_ENV="$SCRIPT_DIR/../../multi-tenant-platform/.env.ec2"

if [ -f "$PLATFORM_ENV" ]; then
    source "$PLATFORM_ENV"
elif [ -f ".env.ec2" ]; then
    source .env.ec2
else
    echo "❌ EC2 instance ID not found"
    exit 1
fi

if [ -z "$EC2_INSTANCE_ID" ]; then
    echo "❌ EC2_INSTANCE_ID not set"
    exit 1
fi

REGION="eu-north-1"

echo "🔍 Validating $ENV environment configuration..."
echo "Instance: $EC2_INSTANCE_ID"
echo ""

# Check if .env file exists and has required variables
VALIDATION_OUTPUT=$(aws ssm send-command \
    --instance-ids "$EC2_INSTANCE_ID" \
    --region "$REGION" \
    --document-name "AWS-RunShellScript" \
    --parameters "commands=[
        'cd /opt/apps/filter-ical',
        'echo \"Checking .env.$ENV...\"',
        'if [ ! -f .env.$ENV ]; then',
        '  echo \"❌ ERROR: .env.$ENV not found\"',
        '  echo \"Run: ./scripts/setup-remote-env.sh\"',
        '  exit 1',
        'fi',
        'echo \"✅ File exists\"',
        'echo \"\"',
        'echo \"Checking required variables...\"',
        'source .env.$ENV',
        'MISSING=0',
        'check_var() {',
        '  if [ -z \"\${!1}\" ]; then',
        '    echo \"❌ MISSING: \$1\"',
        '    MISSING=1',
        '  else',
        '    echo \"✅ SET: \$1\"',
        '  fi',
        '}',
        'check_var ENVIRONMENT',
        'check_var DATABASE_URL',
        'check_var JWT_SECRET_KEY',
        'check_var ADMIN_PASSWORD',
        'check_var ADMIN_EMAIL',
        'check_var SMTP_HOST',
        'check_var SMTP_PORT',
        'check_var SMTP_USERNAME',
        'check_var SMTP_PASSWORD',
        'check_var SMTP_FROM_EMAIL',
        'echo \"\"',
        'if [ \$MISSING -eq 0 ]; then',
        '  echo \"✅ All required variables are set\"',
        '  exit 0',
        'else',
        '  echo \"❌ Some variables are missing\"',
        '  echo \"Edit: sudo nano /opt/apps/filter-ical/.env.$ENV\"',
        '  exit 1',
        'fi'
    ]" \
    --output text \
    --query 'Command.CommandId')

echo "Command ID: $VALIDATION_OUTPUT"
echo "Waiting for results..."
sleep 3

# Get command output
aws ssm get-command-invocation \
    --command-id "$VALIDATION_OUTPUT" \
    --instance-id "$EC2_INSTANCE_ID" \
    --region "$REGION" \
    --query 'StandardOutputContent' \
    --output text

echo ""
echo "✅ Validation complete"
