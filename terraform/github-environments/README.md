# Infrastructure as Code: GitHub Environments

**Industry Best Practice**: Terraform for managing GitHub Environments, protection rules, and variables.

## 🎯 **What This Creates**

```
Development Environment (dev.filter-ical.de)
├── No protection rules (fast iteration)
└── Any branch can deploy

Staging Environment (staging.filter-ical.de)  
├── Protected branches only (main/master)
└── Automatic deployment

Production Environment (filter-ical.de)
├── Protected branches only (main/master)
├── Manual approval (GitHub Pro required)
└── 5-minute wait timer (GitHub Pro required)
```

## 🚀 **Setup Instructions**

### 1. Install Terraform
```bash
# macOS
brew install terraform

# Windows
choco install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
```

### 2. Get GitHub Token
```bash
# Create token at: https://github.com/settings/tokens/new
# Required scopes: repo, admin:repo_hook, admin:org_hook
export GITHUB_TOKEN="your_github_token_here"
```

### 3. Run Terraform
```bash
cd terraform/github-environments
terraform init
terraform plan
terraform apply
```

### 4. Verify Setup
```bash
# View created environments
terraform output repository_environments_url

# List environments
terraform output environments_created
```

## 🔧 **Free Tier vs Pro Tier**

### GitHub Free Tier (Current)
- ✅ Creates environments
- ✅ Sets environment variables
- ✅ Branch protection rules
- ❌ Manual approval reviewers
- ❌ Wait timers

### GitHub Pro Tier (Upgrade)
- ✅ All free tier features
- ✅ Manual approval reviewers
- ✅ Wait timers (cooling-off periods)
- ✅ Full environment protection

## 📊 **Benefits of Terraform**

### ✅ **Infrastructure as Code**
- Version controlled environment configuration
- Reproducible across repositories
- No manual clicking in GitHub UI

### ✅ **Team Collaboration**  
- Peer review of environment changes
- Consistent setup across projects
- Documentation in code

### ✅ **Scalability**
- Copy to any repository instantly
- Standardized environment patterns
- Automated environment management

## 🔄 **Workflow Integration**

After running Terraform, uncomment environment lines in `.github/workflows/deploy.yml`:

```yaml
# Before Terraform
# environment: development

# After Terraform  
environment: development
```

## 🎯 **Copy to New Projects**

```bash
# Copy this entire directory to any new project
cp -r terraform/github-environments ../new-project/terraform/

# Update variables in main.tf
# Run terraform apply
```

## 🛠️ **Customization**

Edit `main.tf` variables:
- `repository_name`: Your repo name
- `repository_owner`: Your GitHub username
- `production_domain`: Your domain
- `staging_domain`: Your staging domain

## 📋 **State Management**

**Important**: This uses local Terraform state. For production, consider:
- Terraform Cloud
- AWS S3 + DynamoDB
- Azure Storage
- Google Cloud Storage