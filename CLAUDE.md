# CLAUDE.md - Professional CI/CD Template with Full Automation

This file instructs Claude Code on how to **automatically set up** professional full-stack web applications with zero-downtime CI/CD pipelines.

---

## 🎯 CLAUDE CODE AUTOMATION INSTRUCTIONS

When the user asks Claude Code to "set up a new website" or "replicate this architecture", Claude should **automatically execute** the following steps without asking for confirmation:

### 1. AUTOMATIC PROJECT SETUP

**Copy Essential Template Files:**
```bash
# Claude should automatically run these commands:
cp .github/workflows/deploy.yml NEW_PROJECT/.github/workflows/
cp .githooks/pre-commit NEW_PROJECT/.githooks/
cp .pre-commit-config.yaml NEW_PROJECT/
cp .gitignore NEW_PROJECT/
cp -r docs/ NEW_PROJECT/
cp -r infrastructure/ NEW_PROJECT/
chmod +x NEW_PROJECT/.githooks/pre-commit
cd NEW_PROJECT && git config core.hooksPath .githooks
```

### 2. AUTOMATIC CONFIGURATION UPDATES

**Claude should automatically update these files with new project details:**

**In `deploy.yml`:**
- Replace `ical-viewer-backend` → `NEW_PROJECT-backend`
- Replace `ical-viewer-frontend` → `NEW_PROJECT-frontend` 
- Replace `filter-ical.de` → `NEW_DOMAIN.com`

**In `production-nginx.conf`:**
- Replace all instances of `filter-ical.de` → `NEW_DOMAIN.com`
- Update SSL certificate paths to use new domain

**In `production-docker-compose.yml`:**
- Replace container names to use new project name

### 3. AUTOMATIC AWS SETUP

**Claude should provide these exact commands for the user to run:**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name NEW_PROJECT-backend --region eu-north-1
aws ecr create-repository --repository-name NEW_PROJECT-frontend --region eu-north-1

# Test deployment (after DNS is configured)
git add . && git commit -m "Initial deployment" && git push origin main
```

### 4. USER REQUIREMENTS (Claude should ask for these only)

Claude should ask the user for ONLY these 3 inputs:
1. **Project name** (for container/repository names)
2. **Domain name** (for nginx and SSL config)
3. **Project type** (Clojure/ClojureScript, Node.js, Python, etc.)

Everything else should be automated.

---

## 📁 PROJECT ARCHITECTURE

### Current Project - iCal Viewer
- **Type**: Full-stack Clojure/ClojureScript
- **Backend**: Ring server (port 3000)
- **Frontend**: ClojureScript SPA with shadow-cljs
- **Domain**: https://filter-ical.de
- **Status**: ✅ Production-ready template

### Quick Start Commands
```bash
# Development
cd backend && clj -M:run                # Backend server
cd frontend && npm run dev              # Frontend development
cd backend && clj -M:test-runner        # Run tests

# Production
git push origin main                    # Triggers automatic deployment
```

---

## 🚢 PRODUCTION INFRASTRUCTURE

### AWS Resources (eu-north-1)
- **Account**: 310829530903
- **EC2**: i-01647c3d9af4fe9fc (56.228.25.95)
- **ECR**: Container registries for each project
- **SSL**: Let's Encrypt with auto-renewal

### Multi-Project Architecture
```
EC2 Instance (56.228.25.95)
├── nginx (reverse proxy) - Ports 80/443
│   ├── filter-ical.de → ical-viewer containers
│   ├── NEW_DOMAIN.com → NEW_PROJECT containers
│   └── [future domains] → [future projects]
├── certbot (SSL management)
└── /opt/websites/ (deployment directory)
```

### Deployment Directory Structure
```
/opt/websites/
├── docker-compose.yml              # Multi-project orchestration
├── .env                           # Environment variables
├── nginx/nginx.conf               # Multi-domain reverse proxy
└── apps/
    ├── ical-viewer/               # Current project data
    └── NEW_PROJECT/               # Future project data
```

---

## 🔄 AUTOMATED CI/CD FEATURES

### Zero-Configuration Deployment
- **Smart change detection**: Only rebuilds changed components
- **Automated testing**: Pre-commit hooks + CI validation
- **Zero-downtime updates**: Rolling container deployments
- **Health validation**: 6-point verification system
- **SSL management**: Automatic certificate generation/renewal

### Professional Development Workflow
- **Pre-commit hooks**: Block broken commits automatically
- **Code quality**: Automated linting and formatting
- **Test automation**: Backend + frontend validation
- **Deployment validation**: Health checks before going live

---

## 📋 AUTOMATION CHECKLIST FOR CLAUDE

When setting up a new project, Claude should automatically:

**✅ File Operations:**
- [ ] Copy all template files to new project directory
- [ ] Update project-specific configuration (names, domains)
- [ ] Set executable permissions on git hooks
- [ ] Configure git hooks path

**✅ Documentation:**
- [ ] Create project-specific README
- [ ] Update CLAUDE.md for the new project
- [ ] Generate deployment documentation

**✅ Testing:**
- [ ] Verify configuration file syntax
- [ ] Test git hook functionality
- [ ] Validate CI/CD pipeline configuration

**✅ User Instructions:**
- [ ] Provide AWS commands to run
- [ ] List DNS configuration requirements
- [ ] Show deployment verification steps

---

## 🛠️ MAINTENANCE & MONITORING

### Health Check Endpoints
- **Any Project**: `https://DOMAIN/health`
- **Nginx Status**: `http://localhost:8080/nginx-health`

### Production Server Commands
```bash
ssh ec2-user@56.228.25.95

# Container management
cd /opt/websites
docker-compose ps                    # Status
docker-compose logs PROJECT --tail 50  # Logs
docker-compose restart nginx        # Restart proxy

# SSL certificates
docker exec websites-certbot certbot renew

# Cleanup
docker image prune -af --filter "until=24h"
```

---

## 🎯 SUCCESS CRITERIA

**A successful automated setup includes:**
1. ✅ All template files copied and configured
2. ✅ Project builds without errors
3. ✅ Pre-commit hooks preventing broken commits
4. ✅ CI/CD pipeline configured and validated
5. ✅ Documentation generated for new project
6. ✅ Clear next steps provided to user

**After DNS configuration and first deployment:**
1. ✅ HTTPS website accessible
2. ✅ SSL certificate valid
3. ✅ Health endpoints responding
4. ✅ Zero-downtime updates working

---

## 📚 DOCUMENTATION STRUCTURE

```
docs/
├── DEVELOPMENT.md              # Developer workflow guide
├── DEPLOYMENT_TEMPLATE.md      # Step-by-step replication guide
├── ARCHITECTURE.md            # Technical architecture details
└── TROUBLESHOOTING.md         # Common issues and solutions
```

---

## 🚀 CLAUDE CODE SCRIPT TEMPLATE

When user says "set up new website", Claude should execute:

```bash
#!/bin/bash
# Claude Code Automation Script

# Get user inputs
read -p "Project name (e.g., 'my-blog'): " PROJECT_NAME
read -p "Domain name (e.g., 'myblog.com'): " DOMAIN_NAME
read -p "Project type (clojure/node/python): " PROJECT_TYPE

# Automated setup
echo "🚀 Setting up $PROJECT_NAME with Claude Code automation..."

# Create project structure
mkdir -p $PROJECT_NAME/{.github/workflows,.githooks,docs,infrastructure}

# Copy and configure template files
cp .github/workflows/deploy.yml $PROJECT_NAME/.github/workflows/
sed -i "s/ical-viewer/$PROJECT_NAME/g" $PROJECT_NAME/.github/workflows/deploy.yml
sed -i "s/filter-ical.de/$DOMAIN_NAME/g" $PROJECT_NAME/.github/workflows/deploy.yml

cp .githooks/pre-commit $PROJECT_NAME/.githooks/
chmod +x $PROJECT_NAME/.githooks/pre-commit

cp .gitignore $PROJECT_NAME/
cp -r docs/* $PROJECT_NAME/docs/
cp -r infrastructure/* $PROJECT_NAME/infrastructure/

# Configure git hooks
cd $PROJECT_NAME
git init
git config core.hooksPath .githooks

# Generate project-specific documentation
echo "# $PROJECT_NAME - Professional Web Application" > README.md
echo "Deployed at: https://$DOMAIN_NAME" >> README.md

echo "✅ Setup complete! Next steps:"
echo "1. Configure DNS: $DOMAIN_NAME → 56.228.25.95"
echo "2. Run: aws ecr create-repository --repository-name $PROJECT_NAME-backend --region eu-north-1"
echo "3. Run: aws ecr create-repository --repository-name $PROJECT_NAME-frontend --region eu-north-1"
echo "4. Deploy: git add . && git commit -m 'Initial deployment' && git push origin main"
```

**This automation eliminates all manual configuration and ensures perfect replication every time.**

---

*Last Updated: September 10, 2025*  
*Status: Production-ready automation template*