# 🔄 Perfect Development Workflow Guide

## 🎯 **Your Ideal Workflow: Keep It Simple**

### **Branch Strategy (Simple & Effective)**
```
master/main         → 🚀 Production (auto-deploys to filter-ical.de)
feature/xxx         → 🔧 Development branches  
hotfix/xxx          → 🚑 Emergency fixes
```

**No staging branch needed** because:
- PR testing catches issues before merge
- Docker rollbacks are instant
- Small team = simple workflow

## 🧪 **Testing Strategy**

### **Where Testing Happens:**

#### **1. Local Development** 
```bash
# Before pushing any code
cd backend
clj -M:test  # Run your Clojure tests locally
```

#### **2. Pull Request Testing**
```yaml
# .github/workflows/deploy.yml already configured
on:
  pull_request:
    branches: [main, master]    # Tests run, NO deployment

# What happens:
✅ Clojure tests execute
✅ Build validation
❌ No deployment to production
✅ PR shows test results
```

#### **3. Production Deployment**  
```yaml
on:
  push:
    branches: [main, master]    # Tests + Deployment

# What happens:
✅ Run tests
✅ Build Docker image  
✅ Deploy to EC2
✅ Health checks verify success
```

## 📋 **Daily Development Workflow**

### **1. Starting New Feature**
```bash
# Get latest code
git checkout master
git pull origin master

# Create feature branch
git checkout -b feature/add-export-functionality
```

### **2. Development Cycle**
```bash
# Make changes
# Test locally: clj -M:test
# Commit frequently
git add .
git commit -m "Add export button to UI"

# Push to GitHub
git push origin feature/add-export-functionality
```

### **3. Code Review & Testing**
```bash
# Create PR via GitHub CLI
gh pr create --title "Add export functionality" --body "Allows users to export filtered calendars"

# GitHub automatically:
# ✅ Runs tests
# ✅ Shows test results in PR
# ✅ No deployment (safe!)
```

### **4. Merge & Deploy**
```bash
# After PR approval, merge via GitHub UI or:
gh pr merge --squash

# GitHub automatically:  
# ✅ Runs tests again
# ✅ Builds new Docker image
# ✅ Deploys to filter-ical.de
# ✅ Runs health checks
```

### **5. Verify Production**
```bash
# Check deployment status
gh run list

# Test your website
curl https://filter-ical.de/
```

## 🚑 **Emergency Hotfix Workflow**

### **For Critical Bugs:**
```bash
# Create hotfix from master
git checkout master
git pull origin master
git checkout -b hotfix/fix-calendar-parsing

# Make minimal fix
# Test locally
git commit -m "Fix calendar parsing issue"
git push origin hotfix/fix-calendar-parsing

# Create PR with priority label
gh pr create --title "🚑 HOTFIX: Calendar parsing" --body "Critical fix" --label "priority:high"

# Fast-track merge and deploy
gh pr merge --squash
```

## 📊 **Testing Levels Explained**

### **Level 1: Unit Tests (Backend)**
```clojure
; In backend/test/app/ical_viewer_test.clj
(deftest storage-tests
  (testing "Storage functionality"
    (is (= expected-result (storage/add-entry! "test" "url")))))
```
**When:** Every PR, every deployment  
**Speed:** Fast (seconds)

### **Level 2: Integration Tests (Future)**
```bash
# Test API endpoints
curl -X POST http://localhost:3000/api/calendars
```
**When:** Before deployment  
**Speed:** Medium (30 seconds)

### **Level 3: End-to-End Tests (Optional)**
```javascript
// Test user workflows in browser
describe('Calendar Filter', () => {
  it('should filter events correctly', () => {
    // Automated browser tests
  });
});
```
**When:** Major releases  
**Speed:** Slow (minutes)

## 🎯 **Deployment Strategy: Two Projects**

### **Current: iCal Viewer → filter-ical.de**
```
Repository: duersjefen/ical-viewer
Domain: filter-ical.de
Port: 3000 (internal)
Tech: Clojure + Ring
```

### **Future: Massage Website → gabs-massage.de**
```
Repository: duersjefen/gabs-massage  
Domain: gabs-massage.de
Port: 4000 (internal)  
Tech: Your choice (Next.js? PHP? Python?)
```

## 🔧 **Project Setup for gabs-massage.de**

### **1. Create New Repository**
```bash
# Create new repo
gh repo create duersjefen/gabs-massage --public

# Clone and set up
git clone https://github.com/duersjefen/gabs-massage.git
cd gabs-massage
```

### **2. Copy Infrastructure Template**
```bash
# Copy proven deployment setup from ical-viewer
cp -r ../ical-viewer/.github .
cp -r ../ical-viewer/infrastructure .
cp ../ical-viewer/Dockerfile .  # Adapt for your tech stack
```

### **3. Customize for Massage Website**
```bash
# Update .github/workflows/deploy.yml
# Change:
# - Repository name: gabs-massage  
# - Domain: gabs-massage.de
# - Port: 4000
# - Docker image name
```

### **4. Deploy Both Projects**
Both projects deploy to same EC2, different containers:

```yaml
# On EC2: /opt/multi-apps/docker-compose.yml
services:
  ical-viewer:          # From duersjefen/ical-viewer
    image: ical-viewer:latest
    ports: ["3000"]
    
  gabs-massage:         # From duersjefen/gabs-massage  
    image: gabs-massage:latest
    ports: ["4000"]
    
  nginx:               # Routes traffic by domain
    # filter-ical.de → ical-viewer:3000
    # gabs-massage.de → gabs-massage:4000
```

## 🚀 **Deployment Commands (CLI)**

### **Check Deployment Status**
```bash
# See all deployments
gh run list

# Watch current deployment  
gh run watch

# View logs if something fails
gh run view --log-failed
```

### **Manual Deployment (Emergency)**
```bash
# Trigger deployment without code changes
gh workflow run deploy.yml
```

### **Rollback Strategy**
```bash
# If deployment fails, previous version keeps running
# To rollback: revert the merge commit
git revert HEAD
git push origin master  # Triggers deployment of previous version
```

## 📈 **Monitoring & Health Checks**

### **Built-in Health Checks**
```bash
# Your apps automatically include:
https://filter-ical.de/health      # Health endpoint
https://gabs-massage.de/health     # Health endpoint

# GitHub Actions automatically tests these
```

### **Manual Monitoring**
```bash
# Check all services on EC2
ssh ec2-user@56.228.25.95
docker ps                          # See running containers
docker logs ical-viewer            # Check app logs
docker logs gabs-massage           # Check app logs
docker logs nginx                  # Check proxy logs
```

## 🎯 **Summary: Your Perfect Workflow**

### **Daily Development**
1. `git checkout -b feature/new-thing`
2. Code + test locally
3. `git push` + create PR
4. Review + merge
5. Auto-deployment to production ✨

### **Two Website Management**
- **Separate repos** = Clean separation
- **Same EC2** = Cost efficient  
- **Domain-based routing** = Professional URLs
- **Independent deployments** = No conflicts

### **Testing Coverage**
- **PR testing** = Catch bugs early
- **Local testing** = Fast feedback
- **Health checks** = Verify production

**This workflow scales from solo development to team collaboration while keeping everything simple and automated!** 🚀