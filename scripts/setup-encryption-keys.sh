#!/bin/bash
# Setup encryption keys on EC2 via SSM
# Run: ./scripts/setup-encryption-keys.sh

set -e

# Load EC2 instance ID
if [ ! -f .env.ec2 ]; then
    echo "Error: .env.ec2 not found"
    echo "Create it with: echo 'INSTANCE_ID=i-01647c3d9af4fe9fc' > .env.ec2"
    exit 1
fi

source .env.ec2

echo "🔐 Setting up encryption keys on EC2..."

# Production key
echo "Setting production encryption key..."
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /app/filter-ical",
        "echo \"PASSWORD_ENCRYPTION_KEY=IXcnyFN65lorghxsYz_Dd_X-eX3mMS94tOfnNzz5Jmc=\" >> backend/.env.production"
    ]' \
    --region eu-north-1

# Staging key
echo "Setting staging encryption key..."
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "cd /app/filter-ical",
        "echo \"PASSWORD_ENCRYPTION_KEY=RBB6nbzfUieauhDQIxzNfEtxOXFP7zkACTKgZ7iVF-E=\" >> backend/.env.staging"
    ]' \
    --region eu-north-1

echo "✅ Encryption keys configured!"
echo ""
echo "Next: Restart containers to pick up new keys"
echo "Run: make deploy-staging && make deploy-production"
