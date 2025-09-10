# CLAUDE.md - Professional Full-Stack CI/CD Template

This file provides Claude Code (claude.ai/code) with a **reusable template** for professional full-stack web applications with automated CI/CD.

---

## 🎯 REUSABLE CI/CD ARCHITECTURE

This project demonstrates a **production-ready template** that can be replicated for any new website on the same AWS infrastructure.

### Core Architecture Pattern
- **Backend**: Clojure/Ring server (port 3000)
- **Frontend**: ClojureScript SPA or static site
- **Deployment**: Multi-container Docker on AWS EC2
- **Domain**: Custom domain with SSL via Let's Encrypt
- **CI/CD**: GitHub Actions with intelligent change detection

---

## 🚀 QUICK REPLICATION GUIDE

### For New Projects on Same Server

1. **Copy Essential Files**:
   ```
   .github/workflows/deploy.yml    # CI/CD pipeline
   .githooks/pre-commit           # Automated testing
   .pre-commit-config.yaml        # Code quality
   .gitignore                     # Clean workspace
   infrastructure/                # Nginx + Docker configs
   DEVELOPMENT.md                 # Developer workflow
   ```

2. **Update Configuration**:
   - Change ECR repository names in `deploy.yml`
   - Update domain name in nginx config
   - Modify container names in docker-compose

3. **Deploy**: Push to main branch → Automated deployment

---

## 🔧 CURRENT PROJECT - iCal Viewer

### Quick Start Commands
```bash
# Backend Development
cd backend && clj -M:run                # Start server (port 3000)  
cd backend && clj -M:test-runner        # Run tests

# Frontend Development  
cd frontend && npm install              # Install dependencies
cd frontend && npm run dev              # Development with hot reload
cd frontend && npm run build            # Production build

# Full Stack (2 terminals)
cd backend && clj -M:run               # Terminal 1: Backend
cd frontend && npm run dev             # Terminal 2: Frontend
```

### Testing Workflow (Industry Standard)
- **Automated**: Pre-commit hooks run tests before every commit
- **Manual**: Use commands above or run `.githooks/pre-commit`
- **CI**: GitHub Actions runs full test suite on push
- **Deployment**: Only proceeds if ALL tests pass

---

## 🏗️ PROJECT STRUCTURE

```
ical-viewer/                           # Root project
├── .github/workflows/deploy.yml       # 🚀 CI/CD Pipeline
├── .githooks/pre-commit               # 🧪 Automated Testing  
├── .pre-commit-config.yaml           # 🔍 Code Quality
├── .gitignore                        # 🧹 Clean Workspace
├── DEVELOPMENT.md                    # 📋 Developer Guide
│
├── backend/                          # Clojure Backend
│   ├── src/app/                     # Source code
│   ├── test/app/                    # Tests
│   ├── data/                        # EDN data files
│   ├── deps.edn                     # Dependencies + test config
│   └── Dockerfile                   # Container config
│
├── frontend/                         # ClojureScript Frontend
│   ├── src/ical_viewer/             # ClojureScript source
│   ├── resources/public/            # Static assets
│   ├── package.json                 # Node dependencies
│   ├── shadow-cljs.edn             # Build config
│   ├── nginx.conf                   # Container nginx
│   └── Dockerfile                   # Container config
│
└── infrastructure/                   # Production Deployment
    ├── production-nginx.conf         # Main reverse proxy
    ├── production-docker-compose.yml # Container orchestration
    └── aws-setup/                   # AWS resource configs
```

---

## 🚢 PRODUCTION INFRASTRUCTURE

### AWS Resources (eu-north-1)
- **Account**: 310829530903
- **EC2**: i-01647c3d9af4fe9fc (56.228.25.95)
- **ECR**: ical-viewer-backend, ical-viewer-frontend
- **Domain**: filter-ical.de → SSL via Let's Encrypt

### Container Architecture
```
nginx (reverse proxy) - Port 80/443
├── ical-viewer (backend) - Port 3000
├── ical-viewer-frontend - Port 80  
└── certbot (SSL management)
```

### Deployment Directory: `/opt/websites/`
```
/opt/websites/
├── docker-compose.yml              # Container orchestration
├── .env                           # Environment variables
├── nginx/nginx.conf               # Reverse proxy config
└── apps/ical-viewer/              # Application data
```

---

## 🔄 CI/CD PIPELINE FEATURES

### Intelligent Change Detection
- Only builds changed components (backend/frontend)
- Robust fallback strategies for Git edge cases
- Fail-safe approach: forces updates when uncertain

### Automated Testing
- **Pre-commit hooks**: Block broken commits locally
- **CI testing**: Backend tests + frontend compilation
- **Deployment validation**: 6-point health check system

### Zero-Downtime Deployment
- Rolling container updates
- Health validation before declaring success
- Automatic rollback on failure

### Professional Logging
- Structured output with emojis for readability
- Comprehensive error reporting
- Clear troubleshooting guidance

---

## 📋 REPLICATION CHECKLIST

### For New Project Setup

**1. Repository Setup**
- [ ] Copy `.github/workflows/deploy.yml`
- [ ] Copy `.githooks/pre-commit` + `chmod +x`
- [ ] Copy `.pre-commit-config.yaml`
- [ ] Copy `.gitignore`
- [ ] Run `git config core.hooksPath .githooks`

**2. AWS Configuration**
- [ ] Create ECR repositories for new project
- [ ] Update ECR names in `deploy.yml`
- [ ] Configure GitHub secrets (EC2_HOST, EC2_USER, EC2_SSH_KEY)
- [ ] Verify OIDC role permissions

**3. Infrastructure Updates**
- [ ] Update domain name in nginx config
- [ ] Update container names in docker-compose
- [ ] Configure SSL certificates for new domain
- [ ] Test nginx configuration syntax

**4. Application Customization**
- [ ] Update project-specific code
- [ ] Configure database/storage as needed
- [ ] Set up monitoring and logging
- [ ] Test deployment pipeline

---

## 🛠️ MAINTENANCE COMMANDS

### On Production Server (EC2)
```bash
ssh ec2-user@56.228.25.95

# Container Management
cd /opt/websites
docker-compose ps                    # Check status
docker-compose logs --tail 50       # View logs
docker-compose restart nginx        # Restart reverse proxy

# SSL Certificate Renewal
docker exec websites-certbot certbot renew

# Cleanup
docker image prune -af --filter "until=24h"
```

### Health Check Endpoints
- **Frontend**: https://filter-ical.de/
- **Backend Health**: https://filter-ical.de/health
- **Nginx Health**: http://localhost:8080/nginx-health (internal)

---

## 🎯 KEY SUCCESS PRINCIPLES

### 1. Fail-Fast Philosophy
- Tests run automatically before commits
- Deployment blocks on any test failure
- Comprehensive health validation

### 2. Zero-Downtime Operations
- Rolling updates with health checks
- Automatic rollback on failure
- Previous version remains active during failures

### 3. Professional Development Standards
- Code quality enforced through automation
- Comprehensive documentation
- Reusable, maintainable architecture

### 4. Monitoring & Observability
- Structured logging throughout pipeline
- Clear error messages and troubleshooting guides
- Health endpoints for monitoring integration

---

## 🚀 PROVEN DEPLOYMENT RECORD

**Status**: ✅ Production-ready template
- ✅ Zero-downtime deployments working
- ✅ Automated testing preventing broken deployments  
- ✅ SSL certificates auto-renewing
- ✅ Multi-container architecture stable
- ✅ Change detection optimizing deployment speed
- ✅ Professional development workflow established

**Last Updated**: September 10, 2025
**Next Maintenance**: Review SSL certificate renewal (auto-managed)