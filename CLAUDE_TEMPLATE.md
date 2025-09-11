# CLAUDE_TEMPLATE.md - Universal Project Template

This file provides **language-independent CI/CD automation** for any project. Copy this to `CLAUDE.md` in your new project and customize the marked sections.

---

## 🎯 CLAUDE CODE AUTOMATION INSTRUCTIONS

When the user asks Claude Code to "set up a new project based on this template", Claude should **automatically execute** the following steps:

### 1. AUTOMATIC PROJECT SETUP

**Copy Essential Template Files:**
```bash
# Claude should automatically run these commands:
cp .github/workflows/deploy.yml NEW_PROJECT/.github/workflows/
cp .githooks/pre-commit NEW_PROJECT/.githooks/
cp .gitignore NEW_PROJECT/
cp Makefile NEW_PROJECT/
cp -r docs/ NEW_PROJECT/ (if exists)
cp -r infrastructure/ NEW_PROJECT/ (if exists)
chmod +x NEW_PROJECT/.githooks/pre-commit
cd NEW_PROJECT && git config core.hooksPath .githooks
```

### 2. AUTOMATIC CONFIGURATION UPDATES

**Claude should automatically update these values:**

**In `deploy.yml`:**
- Replace `[PROJECT_NAME]` → `NEW_PROJECT_NAME` 
- Replace `[DOMAIN_NAME]` → `NEW_DOMAIN.com`
- Replace `[ECR_REPOSITORY_BACKEND]` → `NEW_PROJECT-backend`
- Replace `[ECR_REPOSITORY_FRONTEND]` → `NEW_PROJECT-frontend`

**In production configs:**
- Update all domain references
- Update container names
- Update SSL certificate paths

### 3. USER REQUIREMENTS (Claude should ask for these only)

Claude should ask the user for ONLY these inputs:
1. **Project name** (for container/repository names)
2. **Domain name** (for nginx and SSL config)  
3. **Project type** (Python + Vue 3, Node.js + React, etc.)

Everything else should be automated.

---

## 📁 PROJECT ARCHITECTURE TEMPLATE

### Your Project - [PROJECT_NAME]
- **Type**: [PROJECT_TYPE] (e.g., Python + Vue 3, Node.js + React)
- **Backend**: [BACKEND_TECH] (port 3000)
- **Frontend**: [FRONTEND_TECH] 
- **Domain**: https://[DOMAIN_NAME]
- **Status**: ✅ Production-ready template

### Quick Start Commands
```bash
# Development  
make dev                    # Start both backend and frontend
make backend               # Backend server only
make frontend              # Frontend development server only

# Testing (TDD Workflow)
make test                  # Run unit tests (for commits)
make test-future           # Run TDD future tests (development guide)
make test-all              # Run complete test suite

# Production
make deploy                # Deploy with real-time monitoring
```

---

## 🧪 TDD TESTING FRAMEWORK

### Test Categories:
- **`@pytest.mark.unit`** - Core functionality, must pass for commits
- **`@pytest.mark.integration`** - Full system tests, must pass for deployment
- **`@pytest.mark.future`** - TDD tests for planned features, can fail

### Workflow:
1. **Write failing tests** → `@pytest.mark.future`
2. **Implement feature** → Tests pass
3. **Promote to unit tests** → `@pytest.mark.unit`
4. **Commit** → Only unit tests must pass

---

## 🚀 DEPLOYMENT INFRASTRUCTURE

### AWS Resources ([AWS_REGION])
- **Account**: [AWS_ACCOUNT_ID]
- **EC2**: [EC2_INSTANCE_ID] ([DOMAIN_IP])
- **ECR**: Container registries for each project
- **SSL**: Let's Encrypt with auto-renewal

### Multi-Project Architecture
```
EC2 Instance ([DOMAIN_IP])
├── nginx (reverse proxy) - Ports 80/443
│   ├── [DOMAIN_NAME] → [PROJECT_NAME] containers
│   └── [future domains] → [future projects]
├── certbot (SSL management)
└── /opt/websites/ (deployment directory)
```

---

## 🔄 LANGUAGE-INDEPENDENT CI/CD

### Features:
- **Docker-first**: Prioritizes containerized testing
- **Smart fallbacks**: Detects Python, Node.js, Clojure, or any language
- **Universal interface**: Same commands work with any language
- **TDD workflow**: Unit tests for commits, comprehensive tests for development

### Commands Work With Any Language:
```bash
make test      # Language auto-detected
make deploy    # Works with any backend/frontend
make dev       # Universal development environment
```

---

## 📋 AUTOMATION CHECKLIST FOR CLAUDE

When setting up a new project, Claude should automatically:

**✅ File Operations:**
- [ ] Copy all template files to new project directory
- [ ] Update project-specific configuration (names, domains, regions)
- [ ] Set executable permissions on git hooks
- [ ] Configure git hooks path

**✅ Configuration:**
- [ ] Replace all placeholder values with project specifics
- [ ] Update AWS resource names and regions
- [ ] Configure domain and SSL settings

**✅ Testing:**
- [ ] Verify configuration file syntax
- [ ] Test language detection in Makefile
- [ ] Validate CI/CD pipeline configuration

**✅ Documentation:**
- [ ] Create project-specific CLAUDE.md (not CLAUDE_TEMPLATE.md)
- [ ] Update README with project specifics
- [ ] Generate deployment documentation

---

## 🎯 SUCCESS CRITERIA

**A successful automated setup includes:**
1. ✅ All template files copied and configured
2. ✅ Project builds without errors  
3. ✅ TDD workflow established (unit + future tests)
4. ✅ Language-independent CI/CD working
5. ✅ Pre-commit hooks preventing broken commits
6. ✅ Deployment monitoring with `make deploy`

**After DNS configuration and first deployment:**
1. ✅ HTTPS website accessible
2. ✅ SSL certificate valid
3. ✅ Health endpoints responding
4. ✅ Zero-downtime updates working

---

## 🛠️ CUSTOMIZATION GUIDE

### For Python + Vue 3 Projects:
```bash
# Backend setup
cd backend && python3 -m venv venv && pip install -r requirements.txt

# Frontend setup  
cd frontend && npm install
```

### For Node.js + React Projects:
```bash
# Backend setup
cd backend && npm install

# Frontend setup
cd frontend && npm install  
```

### For Any Docker Project:
```bash
# Universal setup
make setup    # Auto-detects language and sets up environment
```

---

**This template eliminates manual configuration and ensures perfect replication of professional CI/CD practices for any language stack.**

---

*Template Version: 2.0*  
*Status: Production-ready universal automation*