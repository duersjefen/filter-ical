# Complete GitHub Environments Setup Guide

This is a **reusable template** you can copy to any project. Follow these steps exactly.

## Step 1: Create GitHub Environments

Go to your repository → **Settings** → **Environments** → **New Environment**

Create these three environments:

### 1. `development` Environment
```yaml
Name: development
Description: "Fast feedback development environment"

Protection Rules:
- Required reviewers: None
- Wait timer: 0 minutes  
- Deployment branches: Any branch

Environment Variables:
- DOMAIN_NAME_VAR: "dev.your-domain.com"
- AWS_REGION: "eu-north-1"

Environment Secrets:
- None (uses defaults or temporary resources)
```

### 2. `staging` Environment  
```yaml
Name: staging
Description: "Production-identical staging environment"

Protection Rules:
- Required reviewers: None
- Wait timer: 0 minutes
- Deployment branches: main, master only

Environment Variables:
- STAGING_DOMAIN_NAME: "staging.your-domain.com"
- AWS_REGION: "eu-north-1"

Environment Secrets:
- STAGING_EC2_HOST: "your-staging-server.com"
- STAGING_EC2_USER: "ec2-user"
- STAGING_EC2_SSH_KEY: "your-staging-ssh-key"
```

### 3. `production` Environment
```yaml
Name: production
Description: "Live production environment"

Protection Rules:
- ✅ Required reviewers: 1 person minimum
- ✅ Wait timer: 5 minutes (cooling-off period)
- ✅ Deployment branches: main, master only

Environment Variables:
- DOMAIN_NAME_VAR: "your-domain.com"
- AWS_REGION: "eu-north-1"

Environment Secrets:
- EC2_HOST: "your-production-server.com"
- EC2_USER: "ec2-user"
- EC2_SSH_KEY: "your-production-ssh-key"
```

## Step 2: Replace the Existing Deploy Workflow

**IMPORTANT**: Rename your existing `deploy.yml` to `deploy-legacy.yml`, then copy the new `environments.yml` workflow.

```bash
# In your repository
mv .github/workflows/deploy.yml .github/workflows/deploy-legacy.yml
cp .github/workflows/environments.yml .github/workflows/deploy.yml
```

## Step 3: Update Domain and Project Names

Find and replace these values in `environments.yml`:

```yaml
# Replace these with your values:
ECR_REGISTRY: "YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com"
container names: "your-backend your-frontend"
domain references: "your-domain.com"
```

## Step 4: Test the Pipeline

### Development Test
```bash
git checkout -b feature/test-environments
git push origin feature/test-environments
# Should trigger development deployment
```

### Staging Test  
```bash
git checkout main
git push origin main
# Should trigger staging deployment after tests pass
```

### Production Test
```bash
# After staging succeeds, production will require manual approval
# Go to Actions → Running workflow → Review deployments → Approve
```

## Benefits You Get

### 🔒 **Safety & Quality Control**
- **Manual approval gate** for production
- **5-minute cooling-off period** prevents rushed deployments
- **Staging validation** before production release
- **Automatic rollback** on production failures

### 🚀 **Development Velocity**
- **Feature branches** deploy to development automatically
- **Fast feedback loops** for developers
- **Parallel testing** across environments

### 📊 **Operational Excellence**
- **Clear deployment history** per environment
- **Environment-specific configurations**
- **Audit trail** for all production changes
- **Zero-downtime deployments**

### 🔄 **Reusability**
- **Copy this entire setup** to any new project
- **Standardized patterns** across all repositories
- **Industry best practices** out of the box

## Environment Flow

```
Feature Branch → Development (automatic)
       ↓
Master/Main → Staging (automatic)
       ↓
   Production (manual approval required)
```

## Secrets Management Strategy

### Development
- Uses temporary/mock resources
- No real secrets needed
- Fast iteration

### Staging
- **Production-identical infrastructure**
- Separate secrets from production
- Full integration testing

### Production
- **Locked-down security**
- Manual approval required
- Comprehensive validation

## Troubleshooting

### Common Issues

1. **"Environment doesn't exist"**
   - Ensure you created all three environments in Settings
   - Check spelling: `development`, `staging`, `production`

2. **"Required reviewers not set"**
   - Production environment must have ≥1 required reviewer
   - Add yourself or team members as reviewers

3. **"Branch protection rules"**
   - Staging/Production should only allow main/master
   - Development can allow any branch

4. **"Missing secrets"**
   - Each environment needs its own set of secrets
   - Don't share production secrets with staging

### Validation Commands

```bash
# Check environments exist
gh api repos/OWNER/REPO/environments

# View environment protection rules  
gh api repos/OWNER/REPO/environments/production

# List environment secrets
gh api repos/OWNER/REPO/environments/production/secrets
```

## Copy This Template

This entire setup is designed to be copied to any project:

1. Copy `.github/workflows/environments.yml`
2. Copy `.github/environments/` directory
3. Follow this setup guide
4. Customize domain names and container names
5. Set up your three GitHub environments

**Result**: Industry-standard, production-ready CI/CD pipeline that scales to any project size.