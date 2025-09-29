# GitHub Environments Configuration

This directory contains reusable environment configurations that can be copied to any project.

## Industry Best Practice: Three-Environment Pipeline

```
Development → Staging → Production
```

### Environment Setup Instructions

1. **Create GitHub Environments** (in repository settings):
   - Go to repository → Settings → Environments
   - Create: `development`, `staging`, `production`

2. **Configure Environment Protection Rules**:

#### Development Environment
- No protection rules (auto-deploy)
- Deployment branches: Any branch
- Environment secrets: None (uses defaults)

#### Staging Environment  
- No protection rules (auto-deploy from main/master)
- Deployment branches: `main` and `master` only
- Required reviewers: None
- Wait timer: 0 minutes
- Environment secrets: Staging-specific configs

#### Production Environment
- ✅ **Required reviewers**: 1 reviewer minimum
- ✅ **Wait timer**: 5 minutes (cooling-off period)
- ✅ **Deployment branches**: `main` and `master` only
- Environment secrets: Production configs

3. **Environment Variables & Secrets**:
   
   Copy these to each environment with appropriate values:

```yaml
# Staging Environment Variables
DOMAIN_NAME_VAR: "staging-filter-ical.de"
AWS_REGION: "eu-north-1"

# Staging Environment Secrets
EC2_HOST: "staging-server-address"
EC2_USER: "ec2-user" 
EC2_SSH_KEY: "staging-ssh-private-key"

# Production Environment Variables  
DOMAIN_NAME_VAR: "filter-ical.de"
AWS_REGION: "eu-north-1"

# Production Environment Secrets
EC2_HOST: "ec2-56-228-25-95.eu-north-1.compute.amazonaws.com"
EC2_USER: "ec2-user"
EC2_SSH_KEY: "production-ssh-private-key"
```

## Benefits of This Setup

### 🔒 **Safety & Quality Control**
- Production requires manual approval
- Staging tests the exact deployment process
- 5-minute cooling-off period prevents hasty deployments

### 🚀 **Development Velocity** 
- Feature branches deploy to development automatically
- Master/main deploys to staging automatically
- Fast feedback loops for developers

### 📊 **Deployment Tracking**
- Clear deployment history per environment
- Ability to see what's deployed where
- Easy rollback capabilities

### 🔄 **Reusability**
- Copy this entire setup to any new project
- Standardized across all your repositories
- Industry-standard patterns

## Usage in Workflow

```yaml
jobs:
  deploy-staging:
    environment: staging
    if: github.ref == 'refs/heads/main'
    
  deploy-production:
    environment: production
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
```

The `environment:` key automatically:
- Requires configured approvals
- Uses environment-specific secrets/variables
- Enforces branch protection rules
- Provides deployment tracking