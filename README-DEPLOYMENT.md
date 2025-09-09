# 🚀 AWS Deployment Guide - Complete Infrastructure as Code

This repository is configured for secure, automated deployment to AWS using **IAM Roles + OIDC** (no stored credentials!).

## 🏗️ Architecture Overview

**Deployment Setup:**
- ✅ **Region**: Stockholm (`eu-north-1`) - optimal for European users
- ✅ **EC2 Instance**: Running with IAM role for secure access
- ✅ **ECR Repositories**: Container registry in same region
- ✅ **GitHub OIDC**: Secure deployments without stored AWS keys

## 🔐 Security Features

### EC2 Instance (Production)
- ✅ **Uses IAM role** - no credentials stored on server
- ✅ **ECR access** - can pull/push images automatically
- ✅ **SSM enabled** - secure remote management

### GitHub Actions (CI/CD)
- ✅ **OIDC Provider** - temporary credentials only
- ✅ **Role-based access** - GitHub Actions role with minimal permissions
- ✅ **No stored AWS keys** - much more secure than access keys

## 📋 GitHub Secrets Configuration

Set these **3 secrets** in GitHub repo → Settings → Secrets:

```bash
EC2_HOST = your-ec2-public-ip
EC2_USER = ec2-user
EC2_SSH_KEY = [your-private-key-content]
```

**Note**: Get your actual values from the `.env` file (not committed to git).

**No AWS keys needed** - uses OIDC! 🎉

## 🛠️ Local Development

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific AWS values
   ```

2. **Run locally:**
   ```bash
   clj -M -m app.server
   ```

## 🚢 Deployment Process

### Automatic (Recommended)
Push to `main` or `master` branch → GitHub Actions automatically:
1. Runs tests
2. Builds Docker image
3. Pushes to ECR
4. Deploys to EC2
5. Runs health checks

### Manual Deployment
```bash
# Build and push to ECR (use your values from .env)
docker build -t $ECR_BACKEND_URI:latest .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_BACKEND_URI
docker push $ECR_BACKEND_URI:latest

# Deploy on EC2 (use your EC2_HOST from .env)
ssh -i $EC2_SSH_KEY_PATH $EC2_USER@$EC2_HOST
cd /opt/ical-viewer
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing Deployment

After deployment, test your application:

```bash
# Test the application (use your EC2_HOST from .env)
curl -I http://$EC2_HOST:3000
curl http://$EC2_HOST:3000/health
```

## 📁 Infrastructure Files

- ✅ `infrastructure/docker-compose.prod.yml` - Production container setup
- ✅ `infrastructure/aws-setup.sh` - ECR repository setup
- ✅ `infrastructure/github-oidc-*.json` - IAM role definitions
- ✅ `.github/workflows/deploy.yml` - Secure CI/CD pipeline
- ✅ `.env.example` - Template with all required variables

## 🔄 GitHub CLI Workflow

Authenticate GitHub CLI for command-line operations:

```bash
# Login to GitHub
gh auth login

# View repository
gh repo view

# Create pull request
gh pr create --title "Your changes" --body "Description"

# View deployment status
gh run list

# View workflow logs
gh run view [run-id] --log
```

## 🛡️ Security Best Practices Implemented

1. **✅ No AWS credentials in code** - Uses IAM roles
2. **✅ .env excluded from git** - Local secrets stay local
3. **✅ OIDC instead of access keys** - Temporary credentials
4. **✅ Minimal permissions** - Roles have only needed permissions
5. **✅ No hardcoded IPs/accounts** - All in .env file
6. **✅ Example files provided** - Easy setup without exposing secrets

## 🐳 Docker Configuration

The application runs in Docker with:
- **Port 3000** - Clojure backend
- **Volume mount** - `/opt/ical-viewer/data` for persistence
- **Health checks** - Automatic restart on failure
- **Resource limits** - Configured for production

## 🌍 Region Configuration

**Region**: Stockholm (`eu-north-1`)
- ✅ Optimal for European users
- ✅ All resources in same region
- ✅ Lower latency

## 📊 Monitoring & Logs

```bash
# View container logs (use your EC2_HOST)
ssh $EC2_USER@$EC2_HOST
docker-compose -f /opt/ical-viewer/docker-compose.prod.yml logs -f

# Check container status
docker ps

# View resource usage
docker stats
```

## 🔧 Environment Setup

**Required Environment Variables** (see `.env.example`):
- `AWS_ACCOUNT_ID` - Your AWS account ID
- `AWS_REGION` - Deployment region
- `ECR_BACKEND_URI` - Container registry URL
- `EC2_HOST` - Your EC2 instance public IP
- `EC2_SSH_KEY_PATH` - Path to your SSH key

**For GitHub Secrets**:
- `EC2_HOST` - Your EC2 public IP
- `EC2_USER` - SSH username (usually `ec2-user`)
- `EC2_SSH_KEY` - Content of your private key file

---

🎉 **Your infrastructure follows security best practices with Infrastructure as Code principles!** 

All sensitive information is properly managed through environment variables and GitHub secrets.