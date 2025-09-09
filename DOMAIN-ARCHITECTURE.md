# 🌐 Multi-Domain Architecture Guide

## 🏗️ **Recommended Architecture: Domain-Based Separation**

### **Why Domain-Based is Best:**
✅ **Complete Separation**: Each project is independent  
✅ **Simple Deployment**: One domain = one GitHub repo  
✅ **Clean URLs**: No ugly `/ical/` paths  
✅ **Individual Control**: Different teams, different release cycles  
✅ **Easier Maintenance**: Debug issues per project  

## 🎯 **Your Setup:**

```
GitHub Repos:
├── duersjefen/ical-viewer          → filter-ical.de
└── duersjefen/gabs-massage         → gabs-massage.de (future)

EC2 Architecture:
Internet → Route 53/DNS → EC2 (56.228.25.95) → Nginx → Individual Apps

filter-ical.de     → Docker: ical-viewer:3000
gabs-massage.de    → Docker: gabs-massage:4000
```

## 📁 **Project Structure (Recommended)**

### **Current Project: `ical-viewer`**
```
duersjefen/ical-viewer/
├── .github/workflows/deploy.yml    # CI/CD for filter-ical.de
├── backend/                        # Clojure app
├── infrastructure/                 # Docker, Nginx config
├── Dockerfile                      # Build definition
└── README.md                       # Project docs
```

### **Future Project: `gabs-massage`**
```
duersjefen/gabs-massage/
├── .github/workflows/deploy.yml    # CI/CD for gabs-massage.de  
├── src/                            # Whatever tech stack
├── infrastructure/                 # Docker, Nginx config
├── Dockerfile                      # Build definition
└── README.md                       # Project docs
```

## 🔄 **Updated Nginx Configuration**

Let me show you the perfect nginx setup for domain-based routing:

```nginx
events {
    worker_connections 1024;
}

http {
    # Upstream services
    upstream ical-viewer {
        server ical-viewer:3000;
    }
    
    upstream gabs-massage {
        server gabs-massage:4000;
    }

    # filter-ical.de - iCal Viewer
    server {
        listen 80;
        server_name filter-ical.de www.filter-ical.de;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name filter-ical.de www.filter-ical.de;
        
        ssl_certificate /etc/letsencrypt/live/filter-ical.de/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/filter-ical.de/privkey.pem;
        
        location / {
            proxy_pass http://ical-viewer;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # gabs-massage.de - Massage Website  
    server {
        listen 80;
        server_name gabs-massage.de www.gabs-massage.de;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name gabs-massage.de www.gabs-massage.de;
        
        ssl_certificate /etc/letsencrypt/live/gabs-massage.de/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/gabs-massage.de/privkey.pem;
        
        location / {
            proxy_pass http://gabs-massage;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    
    # Default server for unknown domains
    server {
        listen 80 default_server;
        listen 443 ssl default_server;
        server_name _;
        return 444;  # Close connection for unknown domains
    }
}
```

## 🚀 **Deployment Strategy**

### **Option 1: Shared Infrastructure (Recommended)**
Both projects deploy to the same EC2, but maintain separation:

```yaml
# In both repos: .github/workflows/deploy.yml
# Each project manages its own service in docker-compose

# ical-viewer deploys: ical-viewer service
# gabs-massage deploys: gabs-massage service
# Nginx config updated centrally
```

### **Option 2: Completely Separate (Ultra Clean)**
Each project has its own docker-compose and deployment:

```yaml
# ical-viewer/docker-compose.yml
services:
  ical-viewer:
    # only this app
  nginx:
    # config for filter-ical.de only

# gabs-massage/docker-compose.yml  
services:
  gabs-massage:
    # only this app
  nginx:
    # config for gabs-massage.de only
```

## 🎯 **Recommended Workflow**

### **For Each Project:**

#### **1. Development Process**
```bash
# Local development
git checkout -b feature/new-calendar-filter
# Make changes, test locally
git add . && git commit -m "Add new feature"
git push origin feature/new-calendar-filter

# Create PR for review
gh pr create --title "Add calendar filter" --body "Description"
```

#### **2. Testing Strategy**
```yaml
# In .github/workflows/deploy.yml
on:
  push:
    branches: [main, master]        # Auto-deploy production
  pull_request:
    branches: [main, master]        # Test PRs but don't deploy
```

**Testing happens in:**
- ✅ **Every PR**: Tests run, no deployment
- ✅ **Every push to main**: Tests run + deployment
- ✅ **Local development**: Run tests before pushing

#### **3. Branch Strategy (Simple)**
```
main/master     → Production (filter-ical.de)
feature/*       → Development branches
```

**No separate staging needed** because:
- PR testing catches issues
- Rollbacks are instant (previous Docker image)
- Small projects = low complexity

## 📊 **Domain Setup Process**

### **1. Buy Domains**
```bash
filter-ical.de      # Buy from registrar (Namecheap, etc.)
gabs-massage.de     # Buy from registrar
```

### **2. Set DNS Records**
```
filter-ical.de:
A Record: @ → 56.228.25.95
A Record: www → 56.228.25.95

gabs-massage.de:
A Record: @ → 56.228.25.95  
A Record: www → 56.228.25.95
```

### **3. Get SSL Certificates**
```bash
# SSH to EC2
ssh ec2-user@56.228.25.95

# Install certbot
sudo yum install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d filter-ical.de -d www.filter-ical.de
sudo certbot --nginx -d gabs-massage.de -d www.gabs-massage.de
```

## 🔄 **Migration Plan**

### **Step 1: Update Current Project for Domain**
1. Update nginx.conf for filter-ical.de
2. Test with domain pointing to EC2
3. Get SSL certificate
4. Update GitHub Actions

### **Step 2: Create Second Project**
1. Create new repo: `duersjefen/gabs-massage`
2. Copy deployment structure from ical-viewer
3. Customize for massage website
4. Deploy alongside existing app

## 🎯 **Benefits of This Architecture**

### **✅ Simplicity**
- Each project is self-contained
- Independent development and deployment
- Clear separation of concerns

### **✅ Scalability**
- Add new domains easily
- Individual scaling per service
- No project conflicts

### **✅ Maintenance**
- Debug issues per project
- Update projects independently
- Clear responsibility boundaries

### **✅ Professional**
- Clean branded URLs
- Individual SSL certificates
- Proper domain management

---

**Ready to implement? I can help you set up the domain-based architecture step by step!**