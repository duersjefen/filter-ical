# CLAUDE.md - iCal Viewer Project Instructions

This file provides **project-specific instructions** for working with the iCal Viewer project. For creating new projects based on this template, see `CLAUDE_TEMPLATE.md`.

---

## 🎯 ICAL VIEWER PROJECT INSTRUCTIONS

This is a **production-ready Python + Vue 3 web application** with comprehensive TDD workflow and language-independent CI/CD.

### Key Features:
- **Language-Independent CI/CD**: Works with any backend/frontend language
- **Professional TDD Workflow**: Unit tests for commits, comprehensive tests for development  
- **Zero-Downtime Deployment**: Automated with real-time monitoring
- **Comprehensive Testing**: 40+ tests covering all functionality
- **Development Excellence**: Pre-commit hooks, Docker-first approach, universal Makefile

### Development Workflow:
1. **Make changes** → `make test` (unit tests must pass)
2. **Add new features** → Write `@pytest.mark.future` tests first (TDD)
3. **Deploy** → `make deploy` (with real-time monitoring)
4. **Monitor** → GitHub CLI provides immediate feedback

---

## 📁 PROJECT ARCHITECTURE

### iCal Viewer - Production Application
- **Type**: Full-stack Python + Vue 3 with comprehensive TDD
- **Backend**: Python FastAPI + Uvicorn (port 3000)
- **Frontend**: Vue 3 SPA with Vite + Pinia
- **Domain**: https://filter-ical.de  
- **Status**: ✅ Production-ready with 40+ tests

### Quick Start Commands
```bash
# Development
make setup                 # Auto-detect and setup environment
make dev                   # Start both backend and frontend  
make backend              # Backend server only
make frontend             # Frontend development server only

# TDD Testing Workflow
make test                 # Run unit tests (for commits) - 5 tests
make test-future          # Run TDD future tests (development guide) - 35 tests
make test-all             # Run complete test suite - 40 tests
make test-integration     # Run integration tests

# Production Deployment
make deploy               # Deploy with real-time GitHub CLI monitoring
make status               # Check latest deployment status
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

### Future-Proof CI/CD Safeguards
- **Dependency sync validation**: Prevents package-lock.json issues automatically
- **Requirements.txt validation**: Catches malformed Python dependencies
- **Docker environment validation**: Comprehensive pre-build checks
- **Build failure diagnostics**: Detailed troubleshooting guidance
- **Container metadata**: Full build traceability and debugging info

### Automatic Deployment Monitoring
- **Real-time feedback**: `make deploy` automatically monitors deployment progress
- **Zero manual intervention**: Automatically gets latest run ID and watches deployment
- **Immediate failure notification**: Exit status reflects deployment success/failure
- **GitHub CLI integration**: Uses native GitHub tools for reliable monitoring
- **No email notifications**: Feedback provided directly in terminal where deployment initiated

```bash
# The deploy command automatically:
# 1. Pushes changes to repository
# 2. Waits 3 seconds for GitHub Actions to start
# 3. Gets the latest workflow run ID
# 4. Monitors deployment progress with gh run watch
# 5. Exits with proper status code (0=success, 1=failure)
make deploy
```

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

## 🎨 TAILWIND CSS V4 CONFIGURATION

**CRITICAL**: This project uses Tailwind CSS v4 with specific configuration requirements.

### Required Dependencies and Versions
```json
{
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0"
  }
}
```

### System Requirements
- **Node.js**: 20+ (required for Tailwind v4)
- **Vite**: 5+ (required for compatibility)
- **Package Type**: ESM-only (`"type": "module"` in package.json)
- **Config Files**: Must use `.mjs` extension (e.g., `tailwind.config.mjs`)

### Correct CSS Import Syntax
```css
/* ✅ CORRECT - Tailwind v4 syntax */
@import "tailwindcss";

/* ❌ WRONG - Old Tailwind v3 syntax */
@tailwind base;
@tailwind components; 
@tailwind utilities;
```

### Vite Configuration
```js
// vite.config.mjs
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  // ... other config
})
```

### Development Approach - Pure Tailwind Only
- **✅ DO**: Use pure Tailwind utility classes in Vue templates
- **❌ DON'T**: Mix custom CSS with @apply directives
- **❌ DON'T**: Use @apply with utility classes without proper configuration

```vue
<!-- ✅ CORRECT - Pure Tailwind utilities -->
<template>
  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
    <h3 class="text-lg font-semibold text-gray-900">Title</h3>
  </div>
</template>

<!-- ❌ AVOID - Custom CSS with @apply -->
<style scoped>
.custom-card {
  @apply bg-gray-50 border-gray-200 rounded-lg;
}
</style>
```

### Known Issues
- **Utility Class Recognition**: Some utility classes like `bg-gray-50`, `border-gray-200` may not be recognized properly in development
- **Solution**: Use pure Tailwind approach without custom CSS mixins
- **Alternative**: Use CSS custom properties for truly custom values

### Migration Notes
When working with existing Tailwind v3 projects:
1. Update import syntax in CSS files
2. Update package.json to include `"type": "module"`
3. Rename config files to `.mjs` extension
4. Update Vite plugin to `@tailwindcss/vite`
5. Ensure Node.js 20+ and Vite 5+ compatibility

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
read -p "Project type (python-vue/node/python-react): " PROJECT_TYPE

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

*Last Updated: September 12, 2025*  
*Status: Production-ready automation template with Tailwind v4 configuration*