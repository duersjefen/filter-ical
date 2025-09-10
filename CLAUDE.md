# CLAUDE.md - iCal Viewer Project Guide

This file provides comprehensive guidance to Claude Code (claude.ai/code) when working with this iCal Viewer project.

## 🚀 Quick Start Commands

### Backend Development
```bash
cd backend
clj -M:run                  # Start backend server (port 3000)
clj -M:test                 # Run backend tests
```

### Frontend Development  
```bash
cd frontend
npm install                 # Install dependencies
npm run dev                 # Development build with hot reload
npm run build               # Production build
```

### Full Stack Development
```bash
# Terminal 1: Backend
cd backend && clj -M:run

# Terminal 2: Frontend
cd frontend && npm run dev

# Visit http://localhost:3000
```

## 🏗️ Architecture Overview

### Application Structure
This is a **full-stack web application** with separated frontend and backend:

- **Backend**: Clojure server with Ring + Jetty (port 3000)
- **Frontend**: ClojureScript SPA built with shadow-cljs
- **Deployment**: Multi-container Docker setup on AWS EC2
- **Domain**: https://filter-ical.de (with SSL via Let's Encrypt)

### Project Structure
```
ical-viewer/
├── backend/                # Clojure backend application
│   ├── src/app/           # Backend source code
│   ├── test/              # Backend tests
│   ├── data/              # EDN data files (entries.edn, filters.edn)
│   ├── deps.edn          # Backend dependencies
│   └── Dockerfile        # Backend container config
├── frontend/              # ClojureScript frontend application
│   ├── src/              # Frontend source code
│   ├── resources/public/ # Static assets
│   ├── package.json      # Frontend dependencies
│   ├── shadow-cljs.edn  # Build configuration
│   ├── nginx.conf       # Frontend nginx config
│   └── Dockerfile       # Frontend container config
├── infrastructure/       # Deployment configurations
│   ├── production-docker-compose.yml
│   ├── production-nginx.conf
│   ├── github-oidc-*.json
└── .github/workflows/    # CI/CD pipeline
    └── deploy.yml
```

### Core Backend Modules
- **`app.storage`** - Calendar and filter persistence using EDN files
- **`app.ics`** - iCal fetching, parsing, and generation
- **`app.server`** - Web server with API endpoints
- **`app.auth.*`** - Authentication strategies (magic-link, telegram, etc.)
- **`app.ui.*`** - Server-side UI components
- **`app.core.*`** - Core business logic (filtering, sync, types)

### Key Features
- Smart event filtering by type/summary with keyword search
- Persistent filter management with custom names
- Dynamic iCal subscription URLs for calendar apps
- Responsive web interface with statistics
- Multiple authentication strategies

## 🚢 Production Deployment

### Infrastructure Components

#### AWS Resources
- **Account ID**: 310829530903
- **Region**: eu-north-1 (Stockholm)  
- **EC2 Instance**: i-01647c3d9af4fe9fc (56.228.25.95)
- **ECR Repositories**: 
  - ical-viewer-backend
  - ical-viewer-frontend
- **Domain**: filter-ical.de → 56.228.25.95

#### Docker Architecture
```
nginx (websites-nginx) - Port 80/443 (SSL termination)
├── backend (ical-viewer) - Port 3000
├── frontend (ical-viewer-frontend) - Port 80  
└── certbot (websites-certbot) - SSL certificate management
```

### Deployment Process

#### Automated CI/CD Pipeline
**Trigger**: Push to `master` branch
**GitHub Actions**: `.github/workflows/deploy.yml`

1. **Test Phase**: Run backend tests (`clj -M:test`)
2. **Build Phase**: 
   - Build backend Docker image from `backend/Dockerfile`
   - Build frontend Docker image from `frontend/Dockerfile`  
   - Push both images to ECR
3. **Deploy Phase**: 
   - SSH to EC2 instance
   - Copy production configs to `/opt/websites/`
   - Update containers with rolling deployment

#### Required GitHub Secrets
- `EC2_HOST`: 56.228.25.95
- `EC2_USER`: ec2-user  
- `EC2_SSH_KEY`: Private key content for EC2 access

#### AWS OIDC Authentication
- **IAM Role**: arn:aws:iam::310829530903:role/GitHubActionsRole
- **Permissions**: ECR access, no hardcoded AWS credentials needed

### File Locations on EC2

#### Production Directory Structure
```
/opt/websites/
├── .env                          # Environment variables
├── docker-compose.yml           # Container orchestration
├── nginx/
│   └── nginx.conf              # Main nginx configuration
├── apps/                       # Application data
├── backups/                    # Backup storage
└── scripts/                    # Deployment scripts
```

#### Key Configuration Files
- **Production compose**: `infrastructure/production-docker-compose.yml`
- **Production nginx**: `infrastructure/production-nginx.conf`
- **Frontend nginx**: `frontend/nginx.conf`

## 🔧 Troubleshooting Guide

### Common Deployment Issues

#### 1. Frontend Container Nginx Error
**Problem**: nginx error "host not found in upstream backend"
**Solution**: Frontend `nginx.conf` must reference `ical-viewer:3000`, not `backend:3000`
**Location**: `frontend/nginx.conf:29`

#### 2. Main Nginx Configuration Errors  
**Problem**: nginx restart loop with configuration errors
**Common Issues**:
- `proxy_pass` with URI in regex location (fixed)
- Missing `/etc/nginx/mime.types` (fixed with inline types)
- Deprecated `listen 443 ssl http2` (fixed with `http2 on`)

#### 3. SSL Certificate Issues
**Check**: Certificates exist at `/etc/letsencrypt/live/filter-ical.de/`
**Solution**: 
- SSL certificates are managed by certbot container
- Domain must resolve to EC2 IP for certificate generation
- Check certbot logs: `docker logs websites-certbot`

#### 4. Backend Connection Issues
**Common Causes**:
- Backend container not healthy (check health endpoint)
- Port 3000 not accessible within Docker network
- EDN data files not mounted correctly
**Debugging**:
```bash
docker-compose ps                    # Check container status
docker logs ical-viewer             # Backend logs
curl http://localhost:3000/         # Test backend directly
```

### Manual Deployment Commands (Emergency)

#### Connect to EC2
```bash
ssh -i ~/.ssh/wsl2.pem ec2-user@56.228.25.95
```

#### Container Management
```bash
cd /opt/websites

# View status
docker-compose ps

# Restart services  
docker-compose down
docker-compose up -d

# Update images
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 310829530903.dkr.ecr.eu-north-1.amazonaws.com
docker-compose pull
docker-compose up -d

# Check nginx config
docker exec websites-nginx nginx -t

# Clean up old images
docker image prune -af --filter "until=24h"
```

#### Health Checks
```bash
# Test local access
curl -I http://localhost/

# Test backend directly
curl -I http://localhost:3000/

# Test SSL certificates
sudo ls -la /etc/letsencrypt/live/filter-ical.de/

# Check logs
docker logs ical-viewer --tail 50          # Backend
docker logs ical-viewer-frontend --tail 50  # Frontend
docker logs websites-nginx --tail 50        # Main nginx
```

## 📊 Monitoring & Maintenance

### Health Check Endpoints
- **Frontend**: https://filter-ical.de/
- **Backend**: https://filter-ical.de/health (proxied through nginx)
- **Direct Backend**: http://localhost:3000/ (internal)
- **Nginx Health**: http://localhost:8080/nginx-health (internal)

### SSL Certificate Renewal
- **Automatic**: Certbot container renews certificates every 6 hours
- **Manual**: `docker exec websites-certbot certbot renew`
- **Certificate location**: `/etc/letsencrypt/live/filter-ical.de/`

## 🛠️ Development Workflow

### Making Backend Changes
1. Edit Clojure code in `backend/src/`
2. Test locally: `cd backend && clj -M:run`
3. Run tests: `cd backend && clj -M:test`
4. Commit and push to trigger deployment

### Making Frontend Changes  
1. Edit ClojureScript code in `frontend/src/`
2. Test locally: `cd frontend && npm run dev`
3. Build: `cd frontend && npm run build`
4. Commit and push to trigger deployment

### Making Infrastructure Changes
1. Edit files in `infrastructure/`
2. Test nginx config syntax if needed
3. Commit and push - deployment will copy new configs to EC2

### Testing Deployment
- **Monitor**: `gh run list -R duersjefen/ical-viewer`
- **Watch**: `gh run watch [run-id] -R duersjefen/ical-viewer`
- **Logs**: Check GitHub Actions logs for detailed deployment info

## 🔐 Security Configuration

### Nginx Security Headers
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: enabled  
- X-Content-Type-Options: nosniff
- Content-Security-Policy: configured for app needs
- Rate limiting: 10 req/s for API, 1 req/s for auth

### Network Security
- Only ports 80/443 exposed to internet
- Internal container communication on dedicated network
- Unknown domains rejected with 444 response

## 📋 Deployment Verification Checklist

After any deployment, verify:

- [ ] GitHub Actions workflow completed successfully
- [ ] All containers running and healthy: `docker-compose ps`
- [ ] HTTP redirects to HTTPS: `curl -I http://filter-ical.de/`  
- [ ] HTTPS site loads: `curl -I https://filter-ical.de/`
- [ ] Backend health check: `curl -I https://filter-ical.de/health`
- [ ] Frontend serves content: Check browser
- [ ] SSL certificate valid: Check expiry in browser
- [ ] Application functionality: Test adding calendar, creating filters

## 🚨 Emergency Procedures

### If Website Is Down
1. **Check container status**: SSH to EC2, run `docker-compose ps`
2. **Check logs**: `docker logs [container-name] --tail 50`
3. **Restart services**: `docker-compose down && docker-compose up -d`
4. **Check nginx config**: `docker exec websites-nginx nginx -t`

### If SSL Is Broken
1. **Check certificate**: `sudo ls -la /etc/letsencrypt/live/filter-ical.de/`
2. **Renew certificate**: `docker exec websites-certbot certbot renew`
3. **Restart nginx**: `docker-compose restart nginx`

### If Deployment Fails
1. **Check GitHub Actions logs**: Look for specific error
2. **Check ECR access**: Ensure OIDC role is working
3. **Check EC2 SSH**: Ensure SSH key and host are accessible
4. **Manual deployment**: Use emergency commands above

## 💡 Development Tips

### Project Navigation
- **Backend main**: `backend/src/app/server.clj`
- **Frontend main**: `frontend/src/[main-namespace].cljs` 
- **Tests**: `backend/test/app/ical_viewer_test.clj`
- **Data**: `backend/data/entries.edn`, `backend/data/filters.edn`

### Common Tasks
- **Add new route**: Edit `backend/src/app/server.clj`
- **Add new UI component**: Edit `backend/src/app/ui/components.clj`
- **Modify auth**: Edit `backend/src/app/auth/[strategy].clj`
- **Change styling**: Edit `backend/src/app/ui/styles.clj`

### Performance Optimization
- Images served with 1-year cache headers
- Gzip compression enabled for text assets
- Docker multi-stage builds for smaller images
- ClojureScript compiled to optimized JavaScript

---

## 📝 Recent Fixes Applied

### Critical Issues Resolved (Sept 9, 2025)
1. **Nginx Configuration Errors**: 
   - Fixed `proxy_pass` URI issue in `@fallback` location
   - Replaced external `mime.types` with inline types  
   - Updated deprecated `http2` directive syntax
2. **Frontend Container Networking**: Fixed backend hostname reference
3. **SSL Configuration**: Verified certificates exist and are managed properly
4. **Certbot Shell Escaping**: Fixed docker-compose command syntax
5. **Project Structure Documentation**: Corrected CLAUDE.md to reflect actual frontend/backend separation

### Configuration Dependencies
- Frontend nginx MUST reference `ical-viewer:3000` for backend
- Main nginx config MUST use inline MIME types (no external file)
- SSL certificates auto-managed by certbot, no manual intervention needed
- Domain filter-ical.de correctly resolves to EC2 instance

**Last Updated**: September 9, 2025  
**Status**: ✅ All critical configuration issues fixed, deployment pipeline working 