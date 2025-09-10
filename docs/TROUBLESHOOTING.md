# Troubleshooting Guide

## Common Issues and Solutions

### Deployment Failures

#### Issue: "Change detection failed - FORCING update for safety"
**Cause**: Git diff commands failing in shallow clone or missing commit history  
**Solution**: This is expected behavior. The system forces updates when uncertain to ensure reliability.  
**Action**: No action needed - this is the fail-safe working correctly.

#### Issue: Deployment reports success but website shows old version
**Cause**: Containers not actually updating due to failed change detection  
**Solution**: Check deployment logs for "No application containers need updating"  
**Action**: Force rebuild by pushing a minor change or manually restart containers

#### Issue: SSL certificate generation fails
**Cause**: Domain not resolving to EC2 instance or firewall issues  
**Solution**: 
```bash
# Verify DNS resolution
dig your-domain.com
# Should return: 56.228.25.95

# Check nginx is running and accessible
curl -I http://your-domain.com/.well-known/acme-challenge/test
```

### Container Issues

#### Issue: Backend container fails to start
**Symptoms**: `docker-compose ps` shows backend as "Exit 1"  
**Debugging**:
```bash
# Check container logs
docker-compose logs ical-viewer --tail 50

# Common causes:
# - Port 3000 already in use
# - Missing environment variables
# - Database connection failure
# - EDN data file corruption
```

#### Issue: Frontend container serves 404 for all routes
**Cause**: Build artifacts missing or nginx misconfiguration  
**Solution**:
```bash
# Verify build artifacts exist
ls frontend/resources/public/js/

# Check nginx configuration
docker exec ical-viewer-frontend nginx -t

# Rebuild frontend if needed
cd frontend && npm run build
```

#### Issue: nginx fails to start with "address already in use"
**Cause**: Port 80/443 conflict with existing services  
**Solution**:
```bash
# Find conflicting processes
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Stop conflicting services or change ports in docker-compose
```

### Pre-commit Hook Issues

#### Issue: Pre-commit hook fails with "command not found"
**Cause**: Missing dependencies (clj, npm) or incorrect PATH  
**Solution**:
```bash
# Verify dependencies
which clj
which npm
which node

# Install missing tools or fix PATH
```

#### Issue: Tests pass locally but fail in pre-commit hook
**Cause**: Different environment or missing files  
**Solution**:
```bash
# Run hook manually for debugging
.githooks/pre-commit

# Check working directory and file permissions
pwd
ls -la .githooks/pre-commit
```

### Development Issues

#### Issue: Backend server won't start on port 3000
**Debugging**:
```bash
# Check if port is in use
lsof -i :3000

# Kill existing process if needed
kill -9 $(lsof -t -i:3000)

# Check for environment variable issues
echo $PORT
```

#### Issue: Frontend hot reload not working
**Cause**: shadow-cljs compilation errors or port conflicts  
**Solution**:
```bash
# Check shadow-cljs logs
cd frontend
npx shadow-cljs compile app

# Verify package.json scripts
npm run dev
```

### AWS/ECR Issues

#### Issue: "Unable to locate credentials" error
**Cause**: AWS credentials not configured or expired  
**Solution**:
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Configure if needed (for local development)
aws configure

# For GitHub Actions, check OIDC role permissions
```

#### Issue: ECR repository not found
**Cause**: Repository doesn't exist or wrong region  
**Solution**:
```bash
# List repositories
aws ecr describe-repositories --region eu-north-1

# Create if missing
aws ecr create-repository --repository-name PROJECT-backend --region eu-north-1
```

### DNS and SSL Issues

#### Issue: Domain resolves but SSL certificate is invalid
**Debugging**:
```bash
# Check certificate details
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Verify Let's Encrypt certificate
sudo ls -la /etc/letsencrypt/live/your-domain.com/
```

#### Issue: www subdomain not working
**Cause**: DNS not configured for www or nginx missing www server_name  
**Solution**:
- Add www CNAME record pointing to main domain
- Verify nginx config includes `www.your-domain.com` in server_name

### Performance Issues

#### Issue: Slow deployment times
**Optimizations**:
- Verify Docker build cache is working (`--cache-from type=gha`)
- Check if change detection is working (only changed components should build)
- Monitor ECR push/pull times

#### Issue: Website loads slowly
**Debugging**:
```bash
# Check nginx gzip compression
curl -I -H "Accept-Encoding: gzip" https://your-domain.com/

# Verify static file caching
curl -I https://your-domain.com/js/main.js

# Check container resource usage
docker stats
```

## Emergency Procedures

### Complete Service Recovery
```bash
# SSH to production server
ssh ec2-user@56.228.25.95
cd /opt/websites

# Stop all services
docker-compose down

# Pull fresh images
aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 310829530903.dkr.ecr.eu-north-1.amazonaws.com
docker-compose pull

# Start with clean slate
docker-compose up -d

# Verify health
docker-compose ps
curl -I https://your-domain.com/
```

### Rollback Deployment
```bash
# Quick rollback via git
git revert HEAD
git push origin main

# Or use specific container tag
docker-compose down
docker run -d --name temp-backend YOUR_ECR_REGISTRY/backend:PREVIOUS_TAG
docker-compose up -d
```

### SSL Certificate Emergency Renewal
```bash
# Force certificate renewal
docker exec websites-certbot certbot renew --force-renewal

# Restart nginx to pick up new certificate
docker-compose restart nginx
```

## Monitoring Commands

### Regular Health Checks
```bash
# Container status
docker-compose ps

# Service logs (last 50 lines)
docker-compose logs --tail 50

# SSL certificate expiry
sudo openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout | grep "Not After"

# Disk usage
df -h
docker system df
```

### Performance Monitoring
```bash
# Container resource usage
docker stats --no-stream

# nginx access log analysis
docker exec websites-nginx tail -f /var/log/nginx/access.log

# Response time testing
curl -w "@curl-format.txt" -s -o /dev/null https://your-domain.com/
```

## Getting Help

### Log Files to Check
1. GitHub Actions deployment logs
2. Container logs: `docker-compose logs SERVICE_NAME`  
3. nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
4. Pre-commit hook output
5. Let's Encrypt logs: `docker logs websites-certbot`

### Information to Gather
- Error messages and stack traces
- Container status: `docker-compose ps`
- Recent deployments: `gh run list`
- DNS resolution: `dig your-domain.com`
- SSL certificate status
- System resources: `free -h && df -h`