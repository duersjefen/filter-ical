# Development Setup & Best Practices

## 🧪 Automated Testing Workflow

This project follows **industry-standard testing practices**:

### 1. Pre-commit Hooks (Automatic)
Tests run automatically before every commit to catch issues early.

**Setup:**
```bash
# Already configured! Git hooks are active.
# Tests will run automatically on git commit
```

**What gets tested:**
- ✅ Backend tests (if backend files changed)
- ✅ Frontend build compilation (if frontend files changed)  
- ✅ Code linting (if clj-kondo available)
- ✅ File format validation

### 2. CI/CD Pipeline (GitHub Actions)
Tests run again in CI to catch integration/environment issues.

Located in: `.github/workflows/deploy.yml`

### 3. Manual Testing Commands

**Backend tests:**
```bash
cd backend && python3 -m pytest
```

**Frontend build check:**
```bash
cd frontend && npm run build
```

**All quality checks:**
```bash
# This runs the same checks as the pre-commit hook
.githooks/pre-commit
```

## 📋 Code Quality Standards

### Lint Issues to Fix
- ✅ Unused bindings (fixed)
- ✅ Misplaced docstrings (fixed)
- ✅ Import style issues (fixed)

### Current Status
- ✅ Pre-commit hooks configured
- ✅ CI/CD testing pipeline  
- ✅ Basic backend test coverage
- ⚠️  Frontend tests recommended (consider adding)

## 🔄 Development Workflow

1. **Make changes**
2. **Git add & commit** → Tests run automatically
3. **If tests fail** → Fix issues, commit again
4. **Push to main** → CI/CD runs full deployment pipeline
5. **Deploy only if all tests pass**

## 🛠️ Optional: Enhanced Pre-commit Setup

For even more comprehensive checking, install pre-commit framework:

```bash
pip install pre-commit
pre-commit install
```

This uses the config in `.pre-commit-config.yaml` for additional checks.

---

**Key Principle:** Never commit code that doesn't pass tests. The automated hooks enforce this industry best practice.