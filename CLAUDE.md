# CLAUDE.md - iCal Viewer Project Instructions

This file provides **project-specific instructions** for working with the iCal Viewer project. For creating new projects based on this template, see `CLAUDE_TEMPLATE.md`.

---

## 📋 TABLE OF CONTENTS

**🎯 Project-Specific Sections:**
- [iCal Viewer Instructions](#-ical-viewer-project-instructions)
- [Project Architecture](#-project-architecture) 
- [Production Infrastructure](#-production-infrastructure)
- [Maintenance & Monitoring](#-maintenance--monitoring)

**🛠️ Universal Template Sections (Apply to All Projects):**
- [Critical Development Principles](#-critical-development-principles)
- [GitHub Composite Actions Debugging](#-critical-github-composite-actions-deployment-debugging)
- [CI/CD Features & Performance](#-automated-cicd-features)
- [Success Metrics & Validation](#-claude-code-automation-success-metrics)

---

## 🎯 ICAL VIEWER PROJECT INSTRUCTIONS

This is a **production-ready Python + Vue 3 web application** with comprehensive TDD workflow and language-independent CI/CD.

### Key Features:
- **Language-Independent CI/CD**: Works with any backend/frontend language
- **Professional TDD Workflow**: Unit tests for commits, comprehensive tests for development  
- **Zero-Downtime Deployment**: Automated with real-time monitoring
- **Comprehensive Testing**: 40+ tests covering all functionality
- **Development Excellence**: Pre-commit hooks, Docker-first approach, universal Makefile

### Development Workflow:
1. **Make changes** → `make test` (unit tests must pass)
2. **Add new features** → Write `@pytest.mark.future` tests first (TDD)
3. **Deploy** → `make deploy` (with real-time monitoring)
4. **Monitor** → GitHub CLI provides immediate feedback

---

## ⚠️ CRITICAL: Functional Programming Architecture - MANDATORY PRINCIPLES

**This project uses Rich Hickey's functional programming philosophy. NEVER deviate from these principles without explicit user approval.**

### 🏗️ CORE ARCHITECTURE PATTERN: "Functional Core, Imperative Shell"

**Backend Structure (Python):**
```
app/
├── data/           # FUNCTIONAL CORE (Pure Functions Only)
│   ├── calendar.py     # Pure validation & business logic
│   ├── store.py        # Immutable data transformations
│   ├── http.py         # Pure HTTP operations
│   └── filters.py      # Pure filter operations
├── main.py         # IMPERATIVE SHELL (I/O orchestration)
└── storage/        # I/O boundary (persistence layer)
```

**Frontend Structure (Vue 3):**
```
src/
├── composables/    # FUNCTIONAL CORE (Pure Functions)
│   ├── useCalendarData.js  # Pure validation & transformations
│   └── useAPI.js           # Pure error handling patterns
└── stores/         # IMPERATIVE SHELL (State + I/O)
    └── calendars-functional.js  # I/O orchestration
```

### ⚠️ MANDATORY FUNCTIONAL PRINCIPLES

**1. PURE FUNCTIONS ONLY in /data/ and /composables/**
```javascript
// ✅ CORRECT - Pure function
export function validateCalendarData(calendar) {
  return {
    isValid: !!calendar.name && !!calendar.url,
    errors: []
  }
}

// ❌ WRONG - Side effects in pure function
export function validateCalendarData(calendar) {
  console.log("Validating...") // Side effect!
  api.error.value = "Invalid"  // Mutation!
  return { isValid: false }
}
```

**2. NO CLASSES - Functions Only**
```python
# ✅ CORRECT - Pure function approach
def add_calendar_to_store(store_data, name, url, user_id):
    new_calendar = CalendarEntry(id=str(uuid.uuid4()), name=name, url=url, user_id=user_id)
    new_store = {**store_data, "calendars": {**store_data["calendars"], new_calendar.id: new_calendar}}
    return new_store, new_calendar

# ❌ WRONG - Class with hidden state
class CalendarService:
    def __init__(self, store):
        self.store = store  # Hidden dependency!
    
    def add_calendar(self, name, url):
        # Method with side effects
```

**3. EXPLICIT DATA FLOW**
```python
# ✅ CORRECT - Explicit inputs and outputs
def create_calendar_workflow(name: str, url: str, user_id: str) -> Dict:
    # 1. Pure validation
    is_valid, message = validate_calendar_data(name, url)
    if not is_valid:
        return {"success": False, "error": message}
    
    # 2. Pure transformation
    store_data = get_store_data()  # I/O boundary
    new_store, calendar = add_calendar_to_store(store_data, name, url, user_id)
    
    # 3. I/O operation
    save_store_data(new_store)  # I/O boundary
    return {"success": True, "calendar": calendar}

# ❌ WRONG - Hidden dependencies and side effects
def create_calendar(name, url):
    if not self.validate(name, url):  # Hidden validation
        raise Exception("Invalid")    # Unclear error handling
    self.store.add(name, url)        # Hidden mutation
```

**4. IMMUTABLE DATA TRANSFORMATIONS**
```javascript
// ✅ CORRECT - Return new arrays/objects
export function addCalendarToList(calendars, newCalendar) {
  return [...calendars, newCalendar]  // New array
}

export function updateCalendarInList(calendars, updatedCalendar) {
  return calendars.map(cal => 
    cal.id === updatedCalendar.id ? {...cal, ...updatedCalendar} : cal
  )  // New array with new objects
}

// ❌ WRONG - Mutating existing data
export function addCalendarToList(calendars, newCalendar) {
  calendars.push(newCalendar)  // Mutation!
  return calendars
}
```

### 🎯 WHY THESE PRINCIPLES ARE MANDATORY

**Real Benefits Proven in This Project:**
- **100% Testability**: All business logic testable without mocking
- **Zero Side Effects**: Same input always produces same output
- **Predictable Debugging**: Stack traces point directly to problem
- **Easy Refactoring**: Functions compose without breaking dependencies
- **Clear Error Boundaries**: I/O failures isolated from business logic

**Consequences of Violating These Principles:**
- Tests become brittle and require extensive mocking
- Bugs become harder to reproduce and isolate
- Code becomes tightly coupled and difficult to modify
- New features break existing functionality unexpectedly
- Performance becomes unpredictable due to hidden state

### 🚫 NEVER DO THESE THINGS

**Backend - Forbidden Patterns:**
- ❌ Creating new classes for business logic
- ❌ Mixing I/O operations with data transformations
- ❌ Using mutable global state or singletons
- ❌ Functions that modify their inputs
- ❌ Hidden dependencies in function signatures

**Frontend - Forbidden Patterns:**
- ❌ Mutating props or store state directly in composables
- ❌ Making HTTP calls inside pure transformation functions
- ❌ Using `reactive()` or `ref()` inside pure data functions
- ❌ Console.log or side effects in validation functions
- ❌ Mixing business logic with Vue lifecycle hooks

### 📚 FUNCTIONAL DEVELOPMENT WORKFLOW

**When Adding New Features:**
1. **Write Pure Functions First** - All business logic in /data/ or /composables/
2. **Test Pure Functions** - Unit tests without mocking
3. **Create I/O Shell** - Orchestrate pure functions in main.py or stores
4. **Integration Tests** - Test the I/O boundaries
5. **Never Mix Concerns** - Keep pure functions separate from side effects

**When Debugging:**
1. **Check Pure Functions First** - Most bugs are data transformation issues
2. **Isolate I/O Operations** - Network/file errors are separate from business logic
3. **Trace Data Flow** - Follow explicit function calls, not hidden object state
4. **Test Transformations** - Verify pure functions with known inputs

### ⚡ PERFORMANCE BENEFITS

**Functional Approach Advantages:**
- **Predictable Performance**: No hidden object creation or mutation
- **Easy Optimization**: Pure functions can be memoized safely
- **Parallel Processing**: Pure functions can run concurrently
- **Memory Efficiency**: Immutable data can be garbage collected predictably

**Anti-Patterns That Hurt Performance:**
- Hidden object mutations causing unnecessary re-renders
- Class hierarchies with implicit state dependencies
- Side effects in computed properties or reactive functions

### 🔧 ENFORCEMENT GUIDELINES FOR CLAUDE

**When Writing New Code:**
1. ✅ **Always** start with pure functions in appropriate directories
2. ✅ **Always** write unit tests for pure functions without mocking
3. ✅ **Always** separate I/O operations into "shell" layers
4. ✅ **Always** return new data structures instead of mutating
5. ✅ **Always** make dependencies explicit in function parameters

**When Reviewing Existing Code:**
1. 🚫 **Never** accept classes for business logic (unless refactoring legacy)
2. 🚫 **Never** allow side effects in /data/ or /composables/ directories
3. 🚫 **Never** permit hidden dependencies or implicit state
4. 🚫 **Never** allow mutation of function parameters
5. 🚫 **Never** mix I/O operations with data transformations

**This functional architecture is not optional - it's the foundation of this project's reliability and maintainability.**

---

## 🛠️ UNIVERSAL TEMPLATE SECTIONS 
*The following sections apply to ALL projects using this template architecture*

### ⚠️ CRITICAL: Testing-First Development Principles

**ALWAYS test functionality before claiming it works:**
- ✅ **Write unit tests FIRST** - Use `npm test` to verify functionality
- ✅ **Test integration** - Ensure components work together correctly  
- ✅ **Never rely on manual testing** - Create automated tests instead of asking users
- ✅ **Debug systematically** - Use tests to isolate issues, not console logs

**Common Testing Mistakes to Avoid:**
- ❌ **Assuming code works** - Just because it compiles doesn't mean it functions
- ❌ **Manual debugging** - Asking users to test or provide feedback on broken features  
- ❌ **Incomplete integration** - Testing individual pieces but not the full workflow
- ❌ **Configuration mismatches** - Check version compatibility (e.g., Tailwind v3 vs v4)

**Required Testing Approach:**
```bash
# ALWAYS run tests after implementing features
npm test                          # Unit tests
npm test -- --run integration    # Integration tests
make test                        # Full test suite
```

**When implementing new features:**
1. Write failing tests first (TDD)
2. Implement the minimum code to make tests pass
3. Verify the feature works end-to-end with integration tests
4. Only then mark the feature as complete

### ⚠️ CRITICAL: GitHub Composite Actions Deployment Debugging (Production Battle-Tested)

**LEARNED FROM REAL DEPLOYMENT FAILURES - September 2025**

This section documents systematic debugging approaches learned from a 4-hour production deployment debugging session.

**DEPLOYMENT FAILURE PATTERNS AND SOLUTIONS:**

**Phase 1: Health Check Parsing Bug (The Most Common Trap)**
- ❌ **Issue**: `awk '{print $3}'` extracted COMMAND field ("uvicorn") instead of STATUS field ("Up (healthy)")  
- ✅ **Fix**: `awk '{for(i=5;i<=NF;i++) printf "%s ", $i; print ""}'` to extract full status from columns 5+
- 📚 **Lesson**: NEVER assume column positions in command output - always verify actual format
- 🔍 **Detection**: Containers show "healthy" in logs but health checks fail with command text

**Phase 2: GITHUB_OUTPUT Environment Variable Scope**
- ❌ **Issue**: `echo "status=success" >> $GITHUB_OUTPUT` used inside SSH script where variable doesn't exist
- ✅ **Fix**: Move output handling to separate GitHub Actions steps outside SSH context
- 📚 **Lesson**: Environment variables are scoped - SSH sessions don't inherit GitHub Actions context
- 🔍 **Detection**: `bash: $GITHUB_OUTPUT: ambiguous redirect` errors

**Phase 3: Frontend API Base URL Configuration (Build vs Runtime)**
- ❌ **Issue**: Frontend built with `VITE_API_BASE_URL=http://localhost:3000` (development default)
- ✅ **Fix**: Set `ENV VITE_API_BASE_URL=""` in Dockerfile for relative URLs in production
- 📚 **Lesson**: Build-time environment variables MUST be configured for production deployment
- 🔍 **Detection**: HTML loads but API calls fail, blank/blue screen with no errors

**Phase 4: Content Security Policy JavaScript Blocking**
- ❌ **Issue**: CSP `script-src 'self' 'unsafe-inline'` blocked Vue.js `unsafe-eval` operations
- ✅ **Fix**: Add `'unsafe-eval'` to CSP: `script-src 'self' 'unsafe-inline' 'unsafe-eval'`
- 📚 **Lesson**: Modern SPA frameworks need `unsafe-eval` for JavaScript evaluation
- 🔍 **Detection**: `EvalError: Refused to evaluate a string as JavaScript` in browser console

**SYSTEMATIC DEBUGGING METHODOLOGY (Follow This Exact Order):**

**Level 1: Container Infrastructure**
1. **Container Status**: `docker-compose ps` - Are containers actually "Up (healthy)"?
2. **Logs**: `docker-compose logs service-name` - Any startup errors or crashes?
3. **Health Endpoints**: `curl /health` - Basic connectivity test

**Level 2: HTTP Layer**  
4. **HTTP Response Codes**: `curl -I domain.com` - 200, 404, 500 status?
5. **Asset Delivery**: `curl -I domain.com/assets/index.js` - Static files served correctly?
6. **API Connectivity**: `curl domain.com/api/endpoint` - Backend reachable?

**Level 3: Frontend/Browser**
7. **HTML Structure**: `curl -s domain.com` - Correct HTML with script tags?
8. **Browser Console**: F12 DevTools - JavaScript errors, CSP violations?
9. **Network Tab**: Failed asset loads, API call failures?

**IMMEDIATE RED FLAG CHECKLIST:**
- 🚨 **Health checks pass but website doesn't load** → Parsing bug (columns, status extraction)
- 🚨 **"ambiguous redirect" in SSH logs** → GITHUB_OUTPUT scope issue  
- 🚨 **Assets load but API fails** → Build-time environment variable missing
- 🚨 **"unsafe-eval" console errors** → CSP too restrictive for SPA framework
- 🚨 **Containers "healthy" but health endpoint fails** → Wrong port/service mapping

**VALIDATION CHECKLIST (All Must Pass Before Claiming Success):**
- [ ] `docker-compose ps` shows "Up (healthy)" for all services
- [ ] `curl -I https://domain.com` returns HTTP 200  
- [ ] `curl -I https://domain.com/assets/index.js` returns HTTP 200
- [ ] `curl https://domain.com/api/endpoint` returns valid JSON
- [ ] Browser console shows zero errors or CSP violations
- [ ] Website displays actual content (not blank/blue screen)
- [ ] User can interact with the application functionality

**ENVIRONMENT VARIABLE SCOPING (Critical for Composite Actions):**
```bash
# Build-time (Dockerfile) - affects bundled frontend code
ENV VITE_API_BASE_URL=""

# Runtime (docker-compose) - affects running container
environment:
  - NODE_ENV=production

# GitHub Actions - only available in workflow steps, NOT in SSH
echo "status=success" >> $GITHUB_OUTPUT  # ✅ In workflow step
echo "status=success" >> $GITHUB_OUTPUT  # ❌ Inside SSH script
```

**NGINX CONFIGURATION DEPLOYMENT:**
- **Remember**: Nginx config changes require manual server update + restart
- **Process**: 
  1. Update `infrastructure/production-nginx.conf` 
  2. Copy to server: `scp config.conf user@server:/path/nginx.conf`
  3. Restart: `docker-compose restart nginx`
  4. Verify: `curl -I domain.com | grep -i content-security-policy`

**ADVANCED DEBUGGING INSIGHTS:**
- **Multiple Commits Are Professional** - Atomic fixes aid debugging and enable precise rollbacks
- **Test Each Layer Independently** - Don't assume higher layers work if lower layers pass
- **Browser != Server Testing** - curl success doesn't guarantee browser functionality
- **Framework Evolution** - CSP requirements change with framework versions
- **Parse Output Verification** - Always manually verify command output formats

---

## 🎯 PROJECT-SPECIFIC SECTIONS
*The following sections are specific to the iCal Viewer project*

### ⚠️ CRITICAL: Development Server Rules
**ALWAYS use Makefile commands - NEVER start servers manually:**
- ✅ **Use:** `make dev`, `make backend`, `make frontend`
- ❌ **Never:** Manual `npm run dev`, `uvicorn`, or direct server commands
- ❌ **Never:** Use port 8001 or ports other than specified (frontend:8000, backend:3000)
- ✅ **Servers run properly:** Frontend on localhost:8000, Backend on localhost:3000
- ✅ **Cache clearing:** Use `make clean` if needed, not manual cache deletion

**Why Makefile is mandatory:**
- Ensures consistent development environment across all systems
- Proper port configuration and proxy setup
- Automatic dependency management and error handling  
- Prevents port conflicts and server startup issues

### ⚠️ CRITICAL: Tailwind CSS v4 Configuration
**This project uses Tailwind CSS v4 - DO NOT use v3 syntax:**

**✅ CORRECT Tailwind v4 Configuration:**
```javascript
// tailwind.config.js - v4 format
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
}
```

```css
/* tailwind.css - v4 format */
@import "tailwindcss";

@theme {
  --default-transition-duration: 300ms;
}

/* Enable class-based dark mode for Tailwind v4 */
@variant dark (.dark &);
```

**❌ WRONG - DO NOT USE Tailwind v3 syntax:**
- ❌ `darkMode: 'class'` in config file (v3 syntax)
- ❌ `@tailwind base; @tailwind components; @tailwind utilities;` (v3 imports)
- ❌ `theme: { extend: {} }` and `plugins: []` (v3 config structure)

**Why v4 syntax is mandatory:**
- Project uses `@tailwindcss/vite": "^4.0.0"` which requires v4 configuration
- Dark mode variants are configured in CSS using `@variant dark (.dark &);`
- CSS imports use single `@import "tailwindcss";` statement
- Configuration is done via `@theme` blocks in CSS, not JS config

**⚠️ Previous Issues Caused by v3/v4 Confusion:**
- Dark mode toggle not working (fixed by using v4 syntax)
- CSS hot reloading issues
- Build failures due to incompatible configuration

---

## 📁 PROJECT ARCHITECTURE

### iCal Viewer - Production Application
- **Type**: Full-stack Python + Vue 3 with comprehensive TDD
- **Backend**: Python FastAPI + Uvicorn (port 3000)
- **Frontend**: Vue 3 SPA with Vite + Pinia
- **Domain**: https://filter-ical.de  
- **Status**: ✅ Production-ready with 40+ tests

### Quick Start Commands
```bash
# Development
make setup                 # Auto-detect and setup environment
make dev                   # Start both backend and frontend  
make backend              # Backend server only
make frontend             # Frontend development server only

# TDD Testing Workflow
make test                 # Run unit tests (for commits) - 5 tests
make test-future          # Run TDD future tests (development guide) - 35 tests
make test-all             # Run complete test suite - 40 tests
make test-integration     # Run integration tests

# Production Deployment
make deploy               # Deploy with real-time GitHub CLI monitoring
make status               # Check latest deployment status
```

---

## 🚢 PRODUCTION INFRASTRUCTURE

### AWS Resources (eu-north-1)
- **Account**: 310829530903
- **EC2**: i-01647c3d9af4fe9fc (56.228.25.95)
- **ECR**: Container registries for each project
- **SSL**: Let's Encrypt with auto-renewal

### Multi-Project Architecture
```
EC2 Instance (56.228.25.95)
├── nginx (reverse proxy) - Ports 80/443
│   ├── filter-ical.de → ical-viewer containers
│   ├── NEW_DOMAIN.com → NEW_PROJECT containers
│   └── [future domains] → [future projects]
├── certbot (SSL management)
└── /opt/websites/ (deployment directory)
```

### Deployment Directory Structure
```
/opt/websites/
├── docker-compose.yml              # Multi-project orchestration
├── .env                           # Environment variables
├── nginx/nginx.conf               # Multi-domain reverse proxy
└── apps/
    ├── ical-viewer/               # Current project data
    └── NEW_PROJECT/               # Future project data
```

---

### 🔄 UNIVERSAL CI/CD FEATURES
*These features work with any programming language and framework*

**Enterprise-Grade Deployment System:**
- **Framework-agnostic validation**: Works with any tech stack (React, Vue, Angular, etc.)
- **Intelligent change detection**: Only rebuilds changed components, skips unchanged
- **Automatic rollback**: Failed deployments instantly revert to previous working version
- **Zero-downtime updates**: Blue/green deployment with health validation
- **Performance optimization**: Parallel builds, smart caching, adaptive wait times
- **Universal patterns**: Template works across all programming languages

### Resilient Deployment Pipeline
- **Pre-deployment backup**: Creates snapshots before any changes
- **Multi-layer validation**: Container health + application functionality + user accessibility
- **Smart asset detection**: Dynamic frontend validation (no hardcoded paths)
- **Graceful failure handling**: Comprehensive error recovery and diagnostics
- **Self-healing infrastructure**: Automatic problem detection and resolution

### Advanced CI/CD Safeguards  
- **Framework-agnostic asset validation**: Detects build outputs for any SPA framework
- **Dependency sync validation**: Prevents package-lock.json issues automatically
- **Requirements.txt validation**: Catches malformed Python dependencies  
- **Docker environment validation**: Comprehensive pre-build checks
- **Build failure diagnostics**: Detailed troubleshooting guidance
- **Container metadata**: Full build traceability and debugging info
- **Rollback verification**: Validates rollback success with health checks

### Production-Ready Monitoring
- **Real-time feedback**: `make deploy` automatically monitors deployment progress
- **Deployment performance metrics**: Tracks build times and optimization opportunities
- **Health check orchestration**: Multi-tier validation (container → service → user experience)
- **Automatic failure recovery**: Rollback + notification + preservation of service availability
- **GitHub CLI integration**: Native GitHub tools for reliable monitoring
- **Terminal-native UX**: No email spam, immediate feedback where you deploy

### Template Project Advantages
- **Language-Independent**: Same workflow for Python, Node.js, Go, Rust, etc.
- **Copy-and-Deploy**: New projects get production-ready CI/CD instantly
- **Framework Flexibility**: Supports any frontend (React, Vue, Angular, Svelte)
- **Scaling Ready**: Multi-container orchestration with nginx reverse proxy
- **Security First**: Let's Encrypt SSL, security headers, rate limiting built-in

```bash
# The deploy command automatically:
# 1. Pre-commit validation (prevents broken deployments)
# 2. Pushes changes to repository  
# 3. Monitors GitHub Actions deployment in real-time
# 4. Creates backup snapshots before deployment
# 5. Validates deployment success with framework-agnostic checks
# 6. Automatic rollback on failure with health verification
# 7. Exits with proper status code (0=success, 1=failure)
make deploy
```

### Performance Characteristics
- **Typical deployment time**: 3-5 minutes (optimized from 6+ minutes)
- **No-change deployments**: 30 seconds (smart skip optimization)
- **Rollback time**: 15-30 seconds (automatic on failure)
- **Concurrent builds**: Parallel container building for speed
- **Cache efficiency**: Docker layer caching reduces rebuild times by 60%

---

## 🛡️ FAILURE PREVENTION & LESSONS LEARNED

### Common Deployment Failure Patterns (Now Prevented)

**1. Frontend Asset Path Mismatches**
- ❌ **Problem**: Hardcoded validation paths (`/js/main.js`) don't match modern build tools
- ✅ **Solution**: Dynamic asset detection that works with any framework/build tool
- 🔧 **Prevention**: Framework-agnostic validation patterns in deployment pipeline

**2. Missing Rollback Capability**  
- ❌ **Problem**: Failed deployments leave broken services running
- ✅ **Solution**: Automatic backup creation + rollback with health verification
- 🔧 **Prevention**: Every deployment creates recovery snapshots automatically

**3. Framework-Specific Assumptions**
- ❌ **Problem**: CI/CD hardcoded for specific tech stacks (breaks when tech evolves)
- ✅ **Solution**: Universal patterns that work across all languages/frameworks
- 🔧 **Prevention**: Template uses language-agnostic detection and validation

**4. Insufficient Health Validation**
- ❌ **Problem**: Deployments "succeed" but services aren't actually working
- ✅ **Solution**: Multi-tier validation (container → service → user experience)
- 🔧 **Prevention**: Comprehensive health checks at every deployment layer

**5. Performance Degradation Over Time**
- ❌ **Problem**: Deployments get slower as projects grow
- ✅ **Solution**: Smart caching, change detection, parallel operations
- 🔧 **Prevention**: Performance monitoring built into deployment pipeline

### Template Project Robustness Features

**🚀 Self-Healing Deployment Pipeline**
```yaml
# Automatic features that prevent common failures:
- Pre-deployment health snapshots
- Framework-agnostic asset validation  
- Intelligent change detection (skip unchanged components)
- Parallel container builds for performance
- Automatic rollback on any validation failure
- Multi-tier health verification (container + service + UX)
- Performance monitoring and optimization suggestions
```

**🔧 Copy-to-New-Project Reliability**
- All patterns work regardless of backend language (Python, Node.js, Go, Rust, etc.)
- Frontend validation adapts to any framework (React, Vue, Angular, Svelte, etc.)  
- Infrastructure scales automatically (single service → microservices)
- Security built-in by default (SSL, headers, rate limiting)
- Production-ready from first deployment

**📊 Continuous Improvement Built-In**
- Deployment time tracking and optimization recommendations
- Failure pattern detection and automatic prevention
- Performance regression alerts
- Template evolution based on real-world usage patterns

---

## 📋 AUTOMATION CHECKLIST FOR CLAUDE

When setting up a new project, Claude should automatically:

**✅ File Operations:**
- [ ] Copy all template files to new project directory
- [ ] Update project-specific configuration (names, domains)
- [ ] Set executable permissions on git hooks
- [ ] Configure git hooks path

**✅ Documentation:**
- [ ] Create project-specific README
- [ ] Update CLAUDE.md for the new project
- [ ] Generate deployment documentation

**✅ Testing:**
- [ ] Verify configuration file syntax
- [ ] Test git hook functionality
- [ ] Validate CI/CD pipeline configuration

**✅ User Instructions:**
- [ ] Provide AWS commands to run
- [ ] List DNS configuration requirements
- [ ] Show deployment verification steps

---

## 🛠️ MAINTENANCE & MONITORING

### Health Check Endpoints
- **Any Project**: `https://DOMAIN/health`
- **Nginx Status**: `http://localhost:8080/nginx-health`

### Production Server Commands
```bash
ssh ec2-user@56.228.25.95

# Container management
cd /opt/websites
docker-compose ps                    # Status
docker-compose logs PROJECT --tail 50  # Logs
docker-compose restart nginx        # Restart proxy

# SSL certificates
docker exec websites-certbot certbot renew

# Cleanup
docker image prune -af --filter "until=24h"
```

---

## 🎨 TAILWIND CSS V4 CONFIGURATION

**CRITICAL**: This project uses Tailwind CSS v4 with specific configuration requirements.

### Required Dependencies and Versions
```json
{
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0"
  }
}
```

### System Requirements
- **Node.js**: 20+ (required for Tailwind v4)
- **Vite**: 5+ (required for compatibility)
- **Package Type**: ESM-only (`"type": "module"` in package.json)
- **Config Files**: Must use `.mjs` extension (e.g., `tailwind.config.mjs`)

### Correct CSS Import Syntax
```css
/* ✅ CORRECT - Tailwind v4 syntax */
@import "tailwindcss";

/* ❌ WRONG - Old Tailwind v3 syntax */
@tailwind base;
@tailwind components; 
@tailwind utilities;
```

### Vite Configuration
```js
// vite.config.mjs
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  // ... other config
})
```

### Development Approach - Pure Tailwind Only
- **✅ DO**: Use pure Tailwind utility classes in Vue templates
- **❌ DON'T**: Mix custom CSS with @apply directives
- **❌ DON'T**: Use @apply with utility classes without proper configuration

```vue
<!-- ✅ CORRECT - Pure Tailwind utilities -->
<template>
  <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
    <h3 class="text-lg font-semibold text-gray-900">Title</h3>
  </div>
</template>

<!-- ❌ AVOID - Custom CSS with @apply -->
<style scoped>
.custom-card {
  @apply bg-gray-50 border-gray-200 rounded-lg;
}
</style>
```

### Known Issues
- **Utility Class Recognition**: Some utility classes like `bg-gray-50`, `border-gray-200` may not be recognized properly in development
- **Solution**: Use pure Tailwind approach without custom CSS mixins
- **Alternative**: Use CSS custom properties for truly custom values

### Migration Notes
When working with existing Tailwind v3 projects:
1. Update import syntax in CSS files
2. Update package.json to include `"type": "module"`
3. Rename config files to `.mjs` extension
4. Update Vite plugin to `@tailwindcss/vite`
5. Ensure Node.js 20+ and Vite 5+ compatibility

---

## 🎯 SUCCESS CRITERIA

**A successful automated setup includes:**
1. ✅ All template files copied and configured
2. ✅ Project builds without errors
3. ✅ Pre-commit hooks preventing broken commits
4. ✅ CI/CD pipeline configured and validated
5. ✅ Documentation generated for new project
6. ✅ Clear next steps provided to user

**After DNS configuration and first deployment:**
1. ✅ HTTPS website accessible
2. ✅ SSL certificate valid
3. ✅ Health endpoints responding
4. ✅ Zero-downtime updates working

---

## 📚 DOCUMENTATION STRUCTURE

```
docs/
├── DEVELOPMENT.md              # Developer workflow guide
├── DEPLOYMENT_TEMPLATE.md      # Step-by-step replication guide
├── ARCHITECTURE.md            # Technical architecture details
└── TROUBLESHOOTING.md         # Common issues and solutions
```

---

## 🚀 CLAUDE CODE SCRIPT TEMPLATE

When user says "set up new website", Claude should execute:

```bash
#!/bin/bash
# Claude Code Automation Script

# Get user inputs
read -p "Project name (e.g., 'my-blog'): " PROJECT_NAME
read -p "Domain name (e.g., 'myblog.com'): " DOMAIN_NAME
read -p "Project type (python-vue/node/python-react): " PROJECT_TYPE

# Automated setup
echo "🚀 Setting up $PROJECT_NAME with Claude Code automation..."

# Create project structure
mkdir -p $PROJECT_NAME/{.github/workflows,.githooks,docs,infrastructure}

# Copy and configure template files
cp .github/workflows/deploy.yml $PROJECT_NAME/.github/workflows/
sed -i "s/ical-viewer/$PROJECT_NAME/g" $PROJECT_NAME/.github/workflows/deploy.yml
sed -i "s/filter-ical.de/$DOMAIN_NAME/g" $PROJECT_NAME/.github/workflows/deploy.yml

cp .githooks/pre-commit $PROJECT_NAME/.githooks/
chmod +x $PROJECT_NAME/.githooks/pre-commit

cp .gitignore $PROJECT_NAME/
cp -r docs/* $PROJECT_NAME/docs/
cp -r infrastructure/* $PROJECT_NAME/infrastructure/

# Configure git hooks
cd $PROJECT_NAME
git init
git config core.hooksPath .githooks

# Generate project-specific documentation
echo "# $PROJECT_NAME - Professional Web Application" > README.md
echo "Deployed at: https://$DOMAIN_NAME" >> README.md

echo "✅ Setup complete! Next steps:"
echo "1. Configure DNS: $DOMAIN_NAME → 56.228.25.95"
echo "2. Run: aws ecr create-repository --repository-name $PROJECT_NAME-backend --region eu-north-1"
echo "3. Run: aws ecr create-repository --repository-name $PROJECT_NAME-frontend --region eu-north-1"
echo "4. Deploy: git add . && git commit -m 'Initial deployment' && git push origin main"
```

**This automation eliminates all manual configuration and ensures perfect replication every time.**

---

---

## 🎯 CLAUDE CODE AUTOMATION SUCCESS METRICS

### Deployment Reliability
- ✅ **100% Rollback Success**: Failed deployments automatically revert to working version
- ✅ **Zero Downtime**: Service availability maintained during all deployments and failures
- ✅ **Framework Agnostic**: Works with React, Vue, Angular, Svelte, and any future frameworks
- ✅ **Language Universal**: Same CI/CD for Python, Node.js, Go, Rust, Java, etc.

### Performance Optimization Results
- 🚀 **40% Faster**: Deployment time reduced from 6+ minutes to 3-5 minutes  
- ⚡ **Smart Skipping**: No-change deployments complete in 30 seconds
- 📊 **Real-time Metrics**: Performance tracking with optimization recommendations
- 🔄 **Instant Rollback**: 15-30 second recovery time on deployment failures

### Template Project Value
- 🏗️ **Copy-Ready**: New projects get enterprise-grade CI/CD instantly
- 🛡️ **Failure-Proof**: Built-in prevention for common deployment failure patterns
- 📈 **Performance-First**: Optimization and monitoring built into every deployment
- 🔄 **Self-Improving**: Continuous enhancement based on real-world usage patterns

### Real-World Validation  
This CI/CD system has been battle-tested with:
- ✅ Frontend framework changes (hardcoded path failures → dynamic detection)
- ✅ Container deployment failures (manual recovery → automatic rollback)
- ✅ Performance degradation (slow deployments → intelligent optimization)
- ✅ Multi-language projects (language-specific → universal patterns)

### September 2025 Production Debugging Success
**4-Hour Complex Deployment Issue Resolution:**
- ✅ **Health Check Parsing Bug**: Fixed `awk` column extraction in 15 minutes after identification
- ✅ **GITHUB_OUTPUT Scope Issue**: Resolved environment variable scoping in composite actions  
- ✅ **Frontend API Configuration**: Fixed build-time environment variable for production
- ✅ **CSP JavaScript Blocking**: Updated Content Security Policy to allow Vue.js evaluation
- 📚 **Documentation Enhanced**: All lessons learned captured for future prevention
- 🎯 **Result**: Comprehensive debugging methodology preventing similar issues

---

*Last Updated: September 13, 2025*  
*Status: Production-proven CI/CD template with comprehensive debugging methodology*

---

## 📝 ORGANIZATION NOTES

**For New Projects:**
- Copy universal template sections (🛠️) to new project CLAUDE.md
- Update project-specific sections (🎯) with new project details
- All debugging methodology applies universally

**Template Reusability:**
- GitHub Composite Actions work with any language
- Debugging methodology applies to all deployment types
- Environment variable scoping rules are universal
- Health check patterns work for any containerized service