#!/bin/bash
# Production Infrastructure Setup Script
# This script configures infrastructure files with your specific AWS account details

set -e

echo "🚀 Setting up production infrastructure..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and fill in your values."
    exit 1
fi

# Source environment variables
source .env

# Validate required variables
if [ -z "$AWS_ACCOUNT_ID" ] || [ -z "$AWS_REGION" ]; then
    echo "❌ AWS_ACCOUNT_ID and AWS_REGION must be set in .env file"
    exit 1
fi

echo "✅ Using AWS Account ID: $AWS_ACCOUNT_ID"
echo "✅ Using AWS Region: $AWS_REGION"

# Generate docker-compose.prod.yml from template
echo "📝 Generating docker-compose.prod.yml..."
envsubst < infrastructure/docker-compose.prod.yml.template > infrastructure/docker-compose.prod.yml

# Generate GitHub OIDC role with correct account ID
echo "📝 Updating GitHub OIDC role configuration..."
sed "s/YOUR_ACCOUNT_ID/$AWS_ACCOUNT_ID/g" infrastructure/github-oidc-role.json.template > infrastructure/github-oidc-role.json 2>/dev/null || echo "Template not found, using existing file"

echo "✅ Production infrastructure files configured!"
echo ""
echo "Next steps:"
echo "1. Commit the generated infrastructure/docker-compose.prod.yml"
echo "2. Set up GitHub secrets with your EC2 details"
echo "3. Deploy via GitHub Actions or manually"
echo ""
echo "Files updated:"
echo "- infrastructure/docker-compose.prod.yml"
echo "- infrastructure/github-oidc-role.json (if template exists)"