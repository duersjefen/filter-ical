# 🚀 Multi-App Deployment Architecture

This guide explains how to deploy multiple applications on a single EC2 instance with proper URL routing.

## 🏗️ **Architecture Overview**

```
Internet → Route 53 (DNS) → EC2 (56.228.25.95) → Nginx (Reverse Proxy) → Apps
```

### **Current Setup:**
- **Base URL**: `http://56.228.25.95/`
- **iCal Viewer**: `http://56.228.25.95/ical/`
- **Health Check**: `http://56.228.25.95/health`

### **Future Domain Setup:**
- **Primary**: `https://filter-my-calendar.com` → iCal Viewer
- **Other Apps**: `https://your-other-domain.com` → App 2
- **Path-based**: `https://yourdomain.com/app1`, `https://yourdomain.com/app2`

## 🔄 **Complete CI/CD Automation**

### **What's Automated:**
✅ **Tests**: Automatic Clojure test execution  
✅ **Build**: Docker image building and ECR push  
✅ **Deploy**: Multi-app infrastructure deployment  
✅ **Configuration**: Nginx reverse proxy setup  
✅ **Health Checks**: Automatic service verification  
✅ **Cleanup**: Old image removal  

### **Zero Manual Steps:**
1. Push code → GitHub Actions triggers
2. Tests run → Images build → Deploy to EC2
3. Nginx routes traffic → Apps available instantly

## 🌐 **URL Routing Strategies**

### **1. Path-Based Routing (Current)**
```
http://56.228.25.95/ical/          → iCal Viewer
http://56.228.25.95/portfolio/     → Future: Portfolio site
http://56.228.25.95/api/           → Future: API services
```

**Pros:** Single domain, easy SSL, simple setup  
**Cons:** URL paths must be managed, apps need path awareness

### **2. Domain-Based Routing (Recommended for Production)**
```
https://filter-my-calendar.com     → iCal Viewer (full domain)
https://portfolio.yourname.com     → Portfolio site
https://api.yourname.com           → API services
```

**Pros:** Clean URLs, app isolation, professional appearance  
**Cons:** Multiple domains to manage, more DNS setup

### **3. Subdirectory + Domain Hybrid**
```
https://yourname.com/              → Portfolio/landing page
https://yourname.com/ical/         → iCal Viewer
https://filter-my-calendar.com     → iCal Viewer (branded domain)
```

## 📁 **File Structure**
```
/opt/multi-apps/
├── .env                           # Environment variables
├── docker-compose.multi-app.yml   # Multi-service orchestration
├── nginx.conf                     # Reverse proxy configuration
└── apps/
    ├── ical-viewer/               # App-specific data
    ├── app2/                      # Future apps
    └── shared/                    # Shared resources
```

## 🚀 **Adding New Applications**

### **Step 1: Add to docker-compose.multi-app.yml**
```yaml
  new-app-backend:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/new-app:latest
    expose:
      - "5000"
    environment:
      - ENV=production
      - BASE_PATH=/newapp
    networks:
      - web-network
```

### **Step 2: Add to nginx.conf**
```nginx
    location /newapp/ {
        rewrite ^/newapp/(.*)$ /$1 break;
        proxy_pass http://new-app-backend:5000;
        # ... standard proxy settings
    }
```

### **Step 3: Update GitHub Actions**
```yaml
    - name: Build new app image
      run: |
        cd new-app
        docker build -t $ECR_REGISTRY/new-app:latest .
        docker push $ECR_REGISTRY/new-app:latest
```

### **Step 4: Deploy**
```bash
git add . && git commit -m "Add new application" && git push
# → Automatic deployment via GitHub Actions
```

## 🔐 **Domain Setup Guide**

### **For `filter-my-calendar.com`:**

#### **1. Buy Domain** (e.g., Namecheap, GoDaddy, Route 53)

#### **2. Set DNS Records**
```
Type: A
Name: @
Value: 56.228.25.95
TTL: 300

Type: A  
Name: www
Value: 56.228.25.95
TTL: 300
```

#### **3. Update Nginx Configuration**
```nginx
server {
    listen 80;
    server_name filter-my-calendar.com www.filter-my-calendar.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name filter-my-calendar.com www.filter-my-calendar.com;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/filter-my-calendar.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/filter-my-calendar.com/privkey.pem;
    
    location / {
        proxy_pass http://ical-viewer;
        # ... proxy settings
    }
}
```

#### **4. Get SSL Certificate**
```bash
# On EC2 instance
sudo yum install certbot
sudo certbot --nginx -d filter-my-calendar.com -d www.filter-my-calendar.com
```

## 📊 **Monitoring & Management**

### **View All Apps:**
```bash
ssh ec2-user@56.228.25.95
cd /opt/multi-apps
docker-compose -f docker-compose.multi-app.yml ps
```

### **View Logs:**
```bash
# All services
docker-compose -f docker-compose.multi-app.yml logs -f

# Specific service
docker-compose -f docker-compose.multi-app.yml logs -f nginx
docker-compose -f docker-compose.multi-app.yml logs -f ical-viewer-backend
```

### **Scale Services:**
```bash
# Scale specific service
docker-compose -f docker-compose.multi-app.yml up -d --scale ical-viewer-backend=2
```

## 🔄 **Migration from Single-App**

The GitHub Actions workflow automatically:
1. **Stops** old single-app deployment
2. **Migrates** to multi-app structure  
3. **Preserves** data and configurations
4. **Tests** new setup before completing

## 🎯 **Next Steps Priority**

1. **✅ Deploy Multi-App Setup** (ready to deploy)
2. **🔜 Domain Purchase** (`filter-my-calendar.com`)
3. **🔜 SSL Setup** (Let's Encrypt)
4. **🔜 Add Frontend Build** (when needed)
5. **🔜 Add New Apps** (following the pattern)

## 🚨 **Security & Best Practices**

- **✅ Reverse Proxy**: All traffic through Nginx
- **✅ Internal Networking**: Apps communicate via internal Docker network
- **✅ Health Checks**: Automatic service monitoring
- **✅ Rate Limiting**: Built into Nginx config
- **✅ Security Headers**: XSS protection, CSRF prevention
- **✅ Log Management**: Centralized logging via Nginx

---

**Ready to deploy? Just push your code and watch the magic happen! 🎉**