# 🏗️ Infrastructure Directory

**Automation-first infrastructure organization. Everything is automated - no manual setup required.**

## 📂 Directory Structure

```
.github/                 # GitHub CI/CD (REQUIRED by GitHub)
├── workflows/           # Three-tier deployment pipeline (automated)
└── actions/             # Composite deployment actions (automated)

.infra/                  # Infrastructure automation
├── terraform/           # Infrastructure as Code (automated via Terraform)
│   ├── github-environments/  # GitHub environments with protection rules
│   └── aws-oidc/            # AWS OIDC authentication (secure, no keys)
└── docker/              # Production container configurations
```

## 🎯 Why This Organization?

### ✅ **Automation Over Documentation**
- **Zero Manual Setup** - Everything provisioned automatically
- **Infrastructure as Code** - All changes version controlled and automated
- **Self-Documenting** - Code is the documentation
- **No README Pollution** - Automation eliminates need for setup guides

### ✅ **Production-Ready Patterns**
- **GitHub Environments** - Automated via Terraform with protection rules
- **AWS OIDC** - Secure authentication without stored secrets
- **Three-Tier Pipeline** - Dev → Staging → Production (automated)
- **Container Orchestration** - Production Docker Compose with nginx

## 🚀 **How It Works**

### Fully Automated Deployment
```bash
git push origin master  # Triggers complete three-tier deployment
```

### Infrastructure Changes
```bash
cd .infra/terraform/github-environments
terraform apply  # Updates GitHub environments automatically
```

### Production Stack
- **Containers**: Frontend + Backend + nginx + SSL automation
- **Environments**: Development, Staging, Production with protection rules
- **Security**: AWS OIDC authentication, no long-lived secrets
- **Monitoring**: Health checks and automatic rollback capabilities

---

*Zero documentation needed because everything is automated. The infrastructure provisions itself.*