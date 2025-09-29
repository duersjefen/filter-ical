# Scripts Directory - Local Development Tools

This directory contains **local development scripts** that mirror the CI/CD pipeline logic exactly.

## 🎯 **Architecture Principle**

```
Local Scripts = GitHub Actions Logic
(Same containers, same environment variables, same validation)
```

## 📂 **Script Organization**

### ✅ **Current Scripts (Updated)**
- `dev-deploy.sh` - Fast local development deployment
- `validate-contracts.sh` - Local contract validation (mirrors CI/CD)
- `clean-deploy.sh` - Fresh local deployment with database reset

### 🚀 **Usage Pattern**

```bash
# Local development (fast iteration)
./scripts/dev-deploy.sh

# Validate before pushing (same as CI/CD)
./scripts/validate-contracts.sh

# Fresh start (same as production clean deploy)
./scripts/clean-deploy.sh
```

## 🏗️ **Environment Parity Strategy**

### Local Development
```bash
# Uses same containers as production
docker run -e ENV=development ical-viewer-backend
docker run -e ENV=development ical-viewer-frontend
```

### CI/CD (GitHub Actions)
```bash
# Uses identical containers
docker run -e ENV=staging ical-viewer-backend  
docker run -e ENV=production ical-viewer-backend
```

## 🔄 **Perfect Parity Benefits**

1. **Local debugging** = Production debugging
2. **Local tests pass** = CI/CD tests pass  
3. **Local deployment works** = Production deployment works
4. **Offline development** capabilities maintained
5. **Fast feedback loop** for developers

## 🚦 **When to Use What**

| Scenario | Tool | Why |
|----------|------|-----|
| Local development | `./scripts/dev-deploy.sh` | Fast iteration |
| Testing changes | `./scripts/validate-contracts.sh` | Quick validation |
| Fresh database | `./scripts/clean-deploy.sh` | Local reset |
| Feature branch | Push → GitHub Actions Development | Integration testing |
| Main branch | Push → GitHub Actions Staging | Pre-production validation |
| Production | Manual approval → GitHub Actions | Safe deployment |

## 🎯 **The Result**

Perfect parity between local development and production deployment:
- **Same Docker containers**
- **Same environment logic**  
- **Same validation steps**
- **Same deployment patterns**

But with the speed of local scripts and the reliability of GitHub Actions!