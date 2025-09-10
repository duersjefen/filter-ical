# iCal Viewer - Professional CI/CD Template

A production-ready full-stack web application template with automated CI/CD pipeline, designed for zero-downtime deployment.

## 🚀 Live Application

**Production**: https://filter-ical.de

## 📋 Template Features

This project serves as a **reusable template** for professional web applications:

- ✅ **Zero-downtime CI/CD** with GitHub Actions
- ✅ **Automated testing** with pre-commit hooks  
- ✅ **Multi-domain SSL** with Let's Encrypt auto-renewal
- ✅ **Docker containerization** with optimized builds
- ✅ **AWS infrastructure** with intelligent change detection
- ✅ **Professional monitoring** with health checks

## 🎯 Quick Replication

### For Claude Code Users
Simply ask: *"Set up a new website using this template"*

Claude Code will automatically:
1. Copy all template files
2. Configure project-specific settings
3. Set up automated testing and deployment
4. Provide AWS setup commands

### Manual Setup
```bash
./scripts/setup-new-project.sh
```

## 📚 Documentation

- **[Development Guide](docs/DEVELOPMENT.md)** - Local development workflow
- **[Deployment Template](docs/DEPLOYMENT_TEMPLATE.md)** - Step-by-step replication
- **[Architecture](docs/ARCHITECTURE.md)** - Technical architecture details
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🏗️ Current Project - iCal Viewer

### Tech Stack
- **Backend**: Clojure + Ring + Jetty
- **Frontend**: ClojureScript + Reagent + Re-frame
- **Build**: shadow-cljs for optimized compilation
- **Infrastructure**: Docker + nginx + AWS EC2

### Quick Start
```bash
# Backend development
cd backend && clj -M:run

# Frontend development  
cd frontend && npm run dev

# Run tests
cd backend && clj -M:test-runner

# Deploy to production
git push origin main  # Automated pipeline
```

## 🚢 Production Infrastructure

### AWS Resources
- **Account**: 310829530903 (eu-north-1)
- **EC2**: i-01647c3d9af4fe9fc (56.228.25.95)
- **Domain**: filter-ical.de with auto-renewing SSL

### Multi-Project Architecture
The infrastructure supports multiple projects on the same server:
```
nginx (reverse proxy) → Multiple domains → Individual containers
├── filter-ical.de → ical-viewer
├── example.com → future-project-1
└── [your-domain] → your-new-project
```

## 🎯 Template Success Record

**Proven Production Template**:
- ✅ Zero-downtime deployments working
- ✅ Automated testing preventing broken code
- ✅ SSL certificates auto-renewing
- ✅ Multi-container architecture stable
- ✅ Change detection optimizing deployment speed
- ✅ Professional development workflow

## 🤖 Claude Code Integration

This project includes comprehensive instructions for Claude Code to automatically replicate the architecture to new projects without any debugging or configuration.

**Result**: Professional web applications deployable in minutes instead of days.

---

*Template last updated: September 10, 2025*  
*Status: Production-ready for replication*
