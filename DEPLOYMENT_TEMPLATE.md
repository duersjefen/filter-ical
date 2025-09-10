# 🚀 DEPLOYMENT TEMPLATE - Copy This to New Projects

This template allows you to replicate the **professional CI/CD infrastructure** to any new project on the same AWS infrastructure without debugging.

---

## 📋 QUICK SETUP CHECKLIST

### ✅ Step 1: Repository Foundation
Copy these files to your new project:

**Essential CI/CD Files:**
- [ ] `.github/workflows/deploy.yml` → Your CI/CD pipeline
- [ ] `.githooks/pre-commit` → Automated testing (run `chmod +x .githooks/pre-commit`)
- [ ] `.pre-commit-config.yaml` → Code quality framework
- [ ] `.gitignore` → Professional workspace management
- [ ] `DEVELOPMENT.md` → Developer workflow guide

**Infrastructure Files:**
- [ ] `infrastructure/production-nginx.conf` → Reverse proxy config
- [ ] `infrastructure/production-docker-compose.yml` → Container orchestration

### ✅ Step 2: Configuration Updates

**In `.github/workflows/deploy.yml`:**
```yaml
# Update these lines for your new project:
env:
  ECR_REPOSITORY_BACKEND: your-new-project-backend      # Line 13
  ECR_REPOSITORY_FRONTEND: your-new-project-frontend    # Line 14
  DOMAIN_NAME: your-new-domain.com                      # Line 16
```

**In `infrastructure/production-nginx.conf`:**
```nginx
# Update domain names (multiple locations):
server_name your-new-domain.com www.your-new-domain.com;

# Update SSL certificate paths:
ssl_certificate /etc/letsencrypt/live/your-new-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-new-domain.com/privkey.pem;
```

**In `infrastructure/production-docker-compose.yml`:**
```yaml
# Update container names:
services:
  your-new-project:        # Backend container name
  your-new-project-frontend:  # Frontend container name
```

### ✅ Step 3: AWS Resources Setup

**Create ECR Repositories:**
```bash
aws ecr create-repository --repository-name your-new-project-backend --region eu-north-1
aws ecr create-repository --repository-name your-new-project-frontend --region eu-north-1
```

**GitHub Secrets (Already configured for same server):**
- ✅ `EC2_HOST: 56.228.25.95`
- ✅ `EC2_USER: ec2-user`  
- ✅ `EC2_SSH_KEY: [Your private key content]`

### ✅ Step 4: Local Development Setup

**Configure Git Hooks:**
```bash
git config core.hooksPath .githooks
```

**Test Pre-commit Hook:**
```bash
.githooks/pre-commit  # Should run successfully
```

### ✅ Step 5: DNS & SSL Setup

**Domain Configuration:**
1. Point `your-new-domain.com` to `56.228.25.95`
2. Point `www.your-new-domain.com` to `56.228.25.95`

**SSL Certificate (Auto-generated on first deployment):**
- Certificates will be created automatically via Let's Encrypt
- The certbot container handles renewal automatically

### ✅ Step 6: Deploy!

**First Deployment:**
```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

The deployment will:
1. ✅ Run tests automatically
2. ✅ Build containers
3. ✅ Deploy to production
4. ✅ Generate SSL certificates  
5. ✅ Validate deployment health

---

## 🔧 CUSTOMIZATION POINTS

### Backend Modifications
**If using different backend stack:**
- Update `backend/Dockerfile`
- Modify health check endpoint in nginx config
- Update test commands in `.githooks/pre-commit`

### Frontend Modifications
**If using different frontend stack:**
- Update `frontend/Dockerfile` 
- Modify build commands in `deploy.yml`
- Update nginx static file serving rules

### Database Integration
**If adding database:**
- Add database service to `docker-compose.yml`
- Configure environment variables in `.env`
- Update backup scripts in infrastructure

---

## 🛠️ PRODUCTION SERVER SETUP

### Container Directory Structure
Your new project will deploy to:
```
/opt/websites/
├── docker-compose.yml              # Multi-project orchestration
├── .env                           # Shared environment
├── nginx/nginx.conf               # Reverse proxy (multi-domain)
└── apps/
    ├── ical-viewer/               # Existing project
    └── your-new-project/          # Your new project data
```

### Nginx Multi-Domain Configuration
The production nginx automatically handles multiple domains:
- Each project gets its own server block
- SSL certificates managed per domain
- Automatic HTTP→HTTPS redirects
- Shared security headers and optimization

---

## 📊 MONITORING & MAINTENANCE

### Health Check URLs
After deployment, verify these URLs work:
- `https://your-new-domain.com/` → Frontend
- `https://your-new-domain.com/health` → Backend health
- `https://your-new-domain.com/api/` → Backend API

### Log Monitoring
```bash
# SSH to production server
ssh ec2-user@56.228.25.95

# View container logs
cd /opt/websites
docker-compose logs your-new-project --tail 50
docker-compose logs your-new-project-frontend --tail 50
```

### SSL Certificate Status
```bash
# Check certificate expiration
sudo ls -la /etc/letsencrypt/live/your-new-domain.com/
```

---

## 🎯 VALIDATION CHECKLIST

After deployment, verify:

**✅ Application Health:**
- [ ] Website loads at https://your-new-domain.com
- [ ] SSL certificate is valid (green lock icon)
- [ ] HTTP redirects to HTTPS automatically
- [ ] API endpoints respond correctly
- [ ] No console errors in browser

**✅ CI/CD Pipeline:**
- [ ] GitHub Actions deployment succeeded  
- [ ] Pre-commit hooks block broken commits
- [ ] Tests run automatically before deployment
- [ ] Deployment validations pass

**✅ Infrastructure:**
- [ ] Containers running: `docker-compose ps`
- [ ] Nginx configuration valid: `docker exec websites-nginx nginx -t`
- [ ] SSL auto-renewal scheduled
- [ ] Log aggregation working

---

## 🚨 TROUBLESHOOTING COMMON ISSUES

### Domain Not Resolving
```bash
# Verify DNS propagation
dig your-new-domain.com
# Should return: 56.228.25.95
```

### SSL Certificate Issues
```bash
# Force certificate generation
ssh ec2-user@56.228.25.95
docker exec websites-certbot certbot certonly --webroot -w /var/www/certbot -d your-new-domain.com -d www.your-new-domain.com
```

### Container Startup Issues
```bash
# Check container logs
docker-compose logs your-new-project
# Check nginx config syntax  
docker exec websites-nginx nginx -t
```

### Deployment Pipeline Failures
- Check GitHub Actions logs for specific errors
- Verify ECR repository names match configuration
- Ensure all required secrets are configured

---

## 🎉 SUCCESS CRITERIA

**Deployment is successful when:**
1. ✅ Website accessible at HTTPS URL
2. ✅ SSL certificate valid and auto-renewing
3. ✅ Pre-commit hooks preventing broken code
4. ✅ CI/CD pipeline deploying automatically
5. ✅ Health checks passing
6. ✅ Zero-downtime updates working

**You now have a professional, production-ready web application with automated CI/CD!**

---

*Template last updated: September 10, 2025*  
*Based on proven architecture from ical-viewer project*