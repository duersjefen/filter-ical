#!/bin/bash
# AWS infrastructure setup script for iCal Viewer

set -e

# Configuration
REGION="us-east-1"
BACKEND_REPO="ical-viewer-backend"
FRONTEND_REPO="ical-viewer-frontend"

echo "Setting up AWS infrastructure for iCal Viewer..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "Error: AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $ACCOUNT_ID"

# Create ECR repositories
echo "Creating ECR repositories..."

echo "Creating backend repository..."
aws ecr create-repository --repository-name $BACKEND_REPO --region $REGION || echo "Backend repository may already exist"

echo "Creating frontend repository..."
aws ecr create-repository --repository-name $FRONTEND_REPO --region $REGION || echo "Frontend repository may already exist"

# Get ECR login token
echo "Getting ECR login token..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "AWS infrastructure setup completed!"
echo ""
echo "ECR Repository URIs:"
echo "Backend:  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$BACKEND_REPO"
echo "Frontend: $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$FRONTEND_REPO"
echo ""
echo "Next steps:"
echo "1. Update docker-compose.prod.yml with your actual AWS account ID"
echo "2. Update GitHub Actions workflow with your AWS account ID"
echo "3. Set up GitHub secrets for AWS credentials and EC2 access"
echo "4. Launch an EC2 instance and run infrastructure/ec2-setup.sh"