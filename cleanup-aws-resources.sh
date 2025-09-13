#!/bin/bash
# AWS Resource Cleanup Script
# Run this after successful deployment to clean up unused resources

set -euo pipefail

echo "🧹 AWS Resource Cleanup"
echo "======================"

# Remove unused ECR repository
echo "1. Removing unused ECR repository: ical-viewer"
aws ecr delete-repository --repository-name ical-viewer --region eu-north-1 --force 2>/dev/null || echo "   Already deleted or doesn't exist"

# List remaining repositories
echo "2. Remaining ECR repositories:"
aws ecr describe-repositories --region eu-north-1 --query 'repositories[].repositoryName' --output table

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "To also remove the old Clojure project repository:"
echo "aws ecr delete-repository --repository-name duersjefen/clj-app --region eu-north-1 --force"
