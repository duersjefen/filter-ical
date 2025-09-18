# CLAUDE.md - iCal Viewer Project Instructions

This file provides **project-specific instructions** for working with the iCal Viewer project.

---

## 📋 TABLE OF CONTENTS

**🎯 Project-Specific Sections:**
- [iCal Viewer Instructions](#-ical-viewer-project-instructions)
- [Project Architecture](#-project-architecture) 
- [Production Infrastructure](#-production-infrastructure)

**🛠️ Universal Template Sections:**
- [Contract-Driven Development](#-critical-contract-driven-development)
- [Test-First Development](#-mandatory-test-first-development)
- [Professional Guidance](#-professional-guidance--critical-thinking)
- [Debugging Methodology](#-systematic-debugging-methodology)
- [Deployment & CI/CD](#-production-deployment--cicd)

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
1. **Write failing test FIRST** → `@pytest.mark.future` tests drive implementation (TDD)
2. **Make minimum implementation** → Code only what's needed to pass tests
3. **Refactor safely** → `make test` ensures no regression
4. **Deploy** → `make deploy` (with real-time monitoring)

### 📝 CRITICAL: Automatic TODO Management - MANDATORY BEHAVIOR

**I MUST automatically manage the TODO.md file after completing substantial tasks:**

**✅ ALWAYS AUTO-MANAGE TODO AFTER:**
- Completing any significant task or implementation
- Finishing a feature or bug fix
- Completing any item marked as a todo
- Any substantial work session
- When user asks to continue with todos (automatic organization before starting)

**🔧 TODO MANAGEMENT PROCESS:**
1. **Sort Quick Capture items** → Move user ideas from "Quick Capture" to appropriate priority sections
2. **Remove completed items** → Delete finished tasks entirely (git commits track completed work)
3. **Clean up formatting** → Fix any formatting issues, empty lines, or inconsistencies (never add placeholder items like "Add your new ideas here")
4. **Reorganize priorities** → Ensure items are in logical order within their sections
5. **Maintain focus** → Keep "NEXT UP" section to 1-3 items maximum

**📋 TODO ORGANIZATION RULES:**
- **Quick Capture** → User's raw ideas (don't delete, sort into sections)
- **NEXT UP** → 1-3 highest impact items only
- **HIGH PRIORITY** → Core functionality improvements 
- **MEDIUM PRIORITY** → Polish and quality improvements
- **Future Ideas** → Keep collapsed to avoid distraction
- **NO COMPLETED SECTIONS** → Remove finished items completely (git history tracks completed work)

**💡 EXAMPLES:**
```bash
# After completing a feature
1. Remove completed item entirely
2. Sort any new Quick Capture items into priority sections
3. Clean up formatting and empty lines
4. Ensure NEXT UP has clear focus items
```

**IMPORTANT**: This TODO management happens automatically - I don't ask permission, I just do it as part of completing substantial work. This keeps the TODO file always clean and actionable for the user.

## 📋 CRITICAL: CONTRACT-DRIVEN DEVELOPMENT

**THE MOST IMPORTANT LESSON: OpenAPI specifications are immutable contracts that enable unlimited backend refactoring freedom**

### 🎯 THE ARCHITECTURAL SUPERPOWER

**Core Principle**: The OpenAPI specification is the **single source of truth** for API behavior. Implementation can be redesigned endlessly while maintaining frontend stability.

```
OpenAPI Contract → Implementation Freedom → Frontend Independence
```

**✅ What This Means:**
- **Frontend works from contracts**: Vue.js components use OpenAPI spec, not backend knowledge
- **Backend refactoring freedom**: Can completely redesign Python architecture without breaking frontend
- **Contract-driven testing**: Tests validate implementation matches specification exactly
- **Documentation as code**: API documentation is automatically accurate

### 🏗️ THE CONTRACT-IMPLEMENTATION RELATIONSHIP

**How OpenAPI and main.py Work Together:**

```python
# 1. Load our custom OpenAPI specification
def load_openapi_spec() -> Optional[Dict[str, Any]]:
    """Load OpenAPI specification for contract compliance"""
    spec_path = Path(__file__).parent.parent / "openapi.yaml"
    if spec_path.exists():
        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)
    return None

# 2. Create FastAPI app
app = FastAPI(...)

# 3. Override FastAPI's auto-generated spec with our contract
openapi_spec = load_openapi_spec()
if openapi_spec:
    def custom_openapi():
        return openapi_spec
    app.openapi = custom_openapi  # This is the magic!
```

**🔥 Why This Is Revolutionary:**
- FastAPI normally auto-generates OpenAPI from code
- We **reverse this**: Our OpenAPI spec defines what FastAPI should expose
- Implementation must match the contract, not the other way around
- Frontend development becomes completely independent

### 📐 CONTRACT-FIRST DEVELOPMENT WORKFLOW

**✅ The Correct Order (ALWAYS):**
1. **Write OpenAPI specification** → Define exact API behavior
2. **Write contract tests** → Validate implementation matches spec  
3. **Implement backend** → Code to pass contract tests
4. **Frontend uses contracts** → Never depends on backend implementation
5. **Refactor freely** → Backend can change without breaking frontend

**❌ The Wrong Order (NEVER):**
1. ~~Write backend implementation first~~
2. ~~Generate documentation from code~~
3. ~~Frontend couples to implementation details~~
4. ~~Tests validate implementation, not contracts~~

### 🎯 REAL-WORLD BENEFITS PROVEN

**Frontend Independence:**
```javascript
// Frontend only knows the contract:
const response = await fetch('/api/calendars', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Work', url: 'https://...' })
})
// Expects: { id: string, name: string, url: string, user_id: string, created_at: string }
// Doesn't care: Python FastAPI vs Node.js vs Go vs Rust backend
```

**Backend Refactoring Freedom:**
- **Week 1**: Pickle-based storage system
- **Week 2**: SQLite with functional architecture  
- **Week 3**: PostgreSQL with domain-driven design
- **Frontend**: Never changes, always works

**Contract Testing Validation:**
```python
def test_calendar_creation_contract(self):
    """Test /api/calendars POST matches OpenAPI spec"""
    calendar_data = {"name": "Test", "url": "https://example.com/cal.ics"}
    response = self.client.post("/api/calendars", json=calendar_data)
    
    assert response.status_code in [200, 201]  # Per OpenAPI spec
    data = response.json()
    assert "id" in data  # Required by contract
    assert data["name"] == calendar_data["name"]  # Contract compliance
```

### ⚡ CONTRACT VIOLATION DETECTION

**How Contract Tests Catch Violations:**
- **Status Code Mismatch**: OpenAPI says 201, implementation returns 200
- **Schema Violations**: Missing required fields in responses
- **Data Type Errors**: String where OpenAPI expects integer
- **Error Format Inconsistency**: Wrong error response structure

**Real Example - Caught by Contract Tests:**
```python
# ❌ Implementation Bug (would break frontend):
@app.post("/api/calendars")
async def create_calendar(data: dict):
    # Bug: Returns calendar object directly
    return new_calendar

# ✅ Contract-Compliant (frontend works):
@app.post("/api/calendars") 
async def create_calendar(data: dict):
    # Correct: Returns object with required fields per OpenAPI spec
    return {
        "id": calendar.id,
        "name": calendar.name, 
        "url": calendar.url,
        "user_id": calendar.user_id,
        "created_at": calendar.created_at.isoformat()
    }
```

### 🏆 ARCHITECTURAL EXCELLENCE ACHIEVED

**Why This Approach is Revolutionary:**

1. **Zero Frontend Coupling**: Frontend never breaks when backend changes
2. **Predictable APIs**: Every endpoint behaves exactly as documented
3. **Fearless Refactoring**: Backend architecture can evolve without fear
4. **Team Independence**: Frontend and backend teams work in parallel
5. **Quality Assurance**: Contract tests prevent API breaking changes

**Real Project Evidence:**
- **Before**: Frontend broke every time backend architecture changed
- **After**: Frontend works with pickle storage, SQLite, functional architecture, any future system
- **Confidence**: Can redesign backend completely without touching frontend code

### 🔧 MANDATORY IMPLEMENTATION RULES

**For Backend Development:**
1. ✅ **ALWAYS** start with OpenAPI specification
2. ✅ **ALWAYS** write contract tests before implementation
3. ✅ **ALWAYS** validate responses match OpenAPI schemas
4. ✅ **ALWAYS** follow exact status codes from specification
5. ❌ **NEVER** implement endpoints without OpenAPI definition first

**For Contract Testing:**
1. ✅ **Test response schemas** against OpenAPI definitions
2. ✅ **Validate status codes** match specification exactly  
3. ✅ **Check error formats** follow OpenAPI error schema
4. ✅ **Verify content types** match specification headers
5. ✅ **Test required fields** are present in all responses

**For Frontend Development:**
1. ✅ **Use OpenAPI spec** as the only source of truth
2. ✅ **Generate TypeScript types** from OpenAPI schemas (optional)
3. ✅ **Never depend** on backend implementation details
4. ✅ **Follow error handling** patterns defined in OpenAPI
5. ✅ **Mock APIs** using OpenAPI examples for development

### 🚀 THE FUTURE VISION

**What Contract-Driven Development Enables:**
- **Language Independence**: Switch from Python to Go without frontend changes
- **Architecture Evolution**: Microservices, serverless, any pattern works
- **Team Scaling**: Multiple backend teams work on different services
- **Quality Assurance**: API changes are intentional and tested
- **Documentation**: Always accurate because it drives implementation

**This is not just a development technique - it's an architectural philosophy that makes systems antifragile and teams independent.**

## 🧪 MANDATORY: TEST-FIRST DEVELOPMENT

**RULE: Write failing tests BEFORE writing any implementation code**

**✅ Required TDD Workflow:**
1. **Understand requirement** → What exactly needs to work?
2. **Write failing test** → Test describes desired behavior
3. **Run test to confirm failure** → Verify test fails for right reason
4. **Write minimum code** → Make test pass with simplest solution
5. **Refactor if needed** → Clean up while keeping tests green

**Testing Commands:**
```bash
make test                 # Unit tests (for commits) - must pass
make test-future         # TDD development tests - guide implementation
make test-all           # Complete test suite - 40+ tests
npm test -- --run integration  # Integration tests
```

**❌ Forbidden Patterns:**
- Writing implementation code without tests
- Writing tests after implementation  
- Skipping tests for "quick fixes"
- Testing manually instead of automated tests
- Assuming code works because it compiles
- Asking users to test broken functionality

**✅ Test Coverage Requirements:**
- **Unit tests**: Pure functions, business logic
- **Integration tests**: Component interactions, API endpoints
- **E2E tests**: Real user workflows with Playwright
- **Debug tests**: Data flow tracing, browser console logs

### ⚡ CRITICAL: Vue 3 + Pinia Reactivity Fix - MANDATORY SOLUTION

**Problem**: Vue 3 getters in Pinia store return objects are NOT automatically reactive, causing UI to not update when store data changes.

**❌ BROKEN - Store getters not reactive:**
```javascript
// In compatibility store - THIS BREAKS REACTIVITY
return {
  get user() { return appStore.user },        // ❌ NOT reactive
  get calendars() { return calendarStore.calendars }  // ❌ NOT reactive
}
```

**✅ FIXED - Use computed for reactive delegation:**
```javascript  
// In compatibility store - THIS WORKS CORRECTLY
const user = computed({
  get() { return appStore.user },             // ✅ Fully reactive
  set(value) { appStore.user = value }
})

const calendars = computed({
  get() { return calendarStore.calendars },   // ✅ Fully reactive  
  set(value) { calendarStore.calendars = value }
})

return {
  user,
  calendars,
  // ... other properties
}
```

**🎯 Real-World Impact:**
- **Symptoms**: Data updates in store but UI doesn't re-render
- **Backend works**: API calls succeed, data saves correctly
- **LocalStorage correct**: Data persists properly  
- **Frontend broken**: Components show stale/initial data
- **Solution**: Replace getters with `computed` properties

**📝 Debugging Approach:**
1. ✅ Test backend APIs with curl - verify data flow
2. ✅ Add browser console logs to trace data updates  
3. ✅ Check localStorage - confirm data persistence
4. ✅ Use E2E tests to verify real user experience
5. ✅ Fix with `computed` properties for reactive delegation

**⚠️ Vue 3 + Pinia Specific Rules:**
- Always use `computed` for cross-store reactive properties
- Never rely on simple getters for reactive delegation  
- Test reactivity with E2E tests, not just unit tests
- Store instance consistency is critical for reactivity

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

## 🧠 PROFESSIONAL GUIDANCE & CRITICAL THINKING

**MANDATORY: Claude must think critically and provide professional guidance - NOT just execute commands**

**✅ Critical Thinking Approach:**
- **Question approaches** → "Is this the best solution?"
- **Consider alternatives** → "What other solutions might work better?"
- **Think long-term** → "What are implications in 6 months? 2 years?"
- **Challenge assumptions** → "Are we solving the right problem?"
- **Suggest improvements** → "Here's a better approach because..."
- **Warn about pitfalls** → "This will cause problems later..."

**❌ Forbidden Behaviors:**
- Blindly implementing requests without analysis
- Assuming user's initial idea is best
- Avoiding better alternatives to preserve ego
- Executing poor solutions without pushback
- Ignoring long-term architectural consequences

**Professional Response Template:**
*"I understand you want to [goal]. This approach will cause [problems] because [reasons]. Instead, let me implement [better solution] which [benefits]. This prevents future issues and saves time later."*

**Must Challenge:**
- Architectural shortcuts → "Creates tight coupling..."
- Security vulnerabilities → "Exposes application to..."
- Performance anti-patterns → "Doesn't scale because..."
- Maintainability issues → "Future developers will struggle..."
- Framework misuse → "Fighting against framework..."

## 🔍 SYSTEMATIC DEBUGGING METHODOLOGY

**CRITICAL RULE: After 2 failed attempts, IMMEDIATELY find the real root cause**

**The 2-Failure Rule:**
- ✅ **2 attempts maximum** → If it doesn't work twice, problem is deeper
- 🛑 **Stop micro-debugging** → No endless tweaking or random fixes
- 🔍 **Find root cause** → Address system-level issues, not symptoms

**Root Cause Analysis Levels:**
1. **Surface Symptoms** → Error messages, UI bugs, failed tests
2. **Direct Causes** → Wrong calls, missing imports, config errors  
3. **Root Causes** → Architecture mismatch, wrong mental model
4. **System Issues** → Framework misuse, technology choice problems

**Red Flags - Stop and Think Deeper:**
- 🚨 "Let me try one more small change..." → Step back now
- 🚨 "It works sometimes but not others..." → Systematic issue
- 🚨 "This used to work, now it doesn't..." → Environment change
- 🚨 "The error message doesn't make sense..." → Wrong mental model

**Root Cause Template:**
*"I've tried [approach 1] and [approach 2], both failed. Let me find the root cause. The real issue is likely [fundamental problem] because [reasoning]. The solution is probably simpler: [root cause solution]"*

**Real Project Examples:**
- **Vue 3 Reactivity** → Root cause: Using getters vs `computed`
- **Tailwind Styles** → Root cause: v3 syntax with v4 framework
- **API Integration** → Root cause: Build-time vs runtime env variables

### 🎯 FRONTEND DEBUGGING - BROWSER CONSOLE FIRST

**MANDATORY RULE: For frontend issues, ALWAYS check browser console first**

**✅ Frontend Debugging Order:**
1. **Open Browser Dev Tools** → F12 or right-click → Inspect
2. **Check Console Tab** → Look for red JavaScript errors
3. **Read Error Messages** → File name, line number, exact cause
4. **Fix Direct Issue** → Address the specific error shown
5. **Then investigate deeper** → Only if console is clean

**❌ DO NOT:**
- Create custom debugging scripts before checking console
- Assume backend issues when frontend shows JavaScript errors  
- Look at server logs when browser console has errors
- Overcomplicate debugging when console gives exact location

**Example Error Analysis:**
```
CalendarView.vue:312  Error loading calendar data: 
TypeError: Cannot convert undefined or null to object
    at Object.keys (<anonymous>)
    at loadCalendarData (CalendarView.vue:300:29)
```
→ **Immediate Fix**: Add null check at CalendarView.vue:300 before `Object.keys()`

### 🧪 E2E TESTING REQUIREMENTS

**MANDATORY: E2E tests must ALWAYS run in headless mode**

**✅ Required Configuration:**
```javascript
// playwright.config.js - MUST have headless: true
use: {
  baseURL: process.env.FRONTEND_URL || 'http://localhost:8000',
  trace: 'on-first-retry',
  headless: true,  // ← MANDATORY: No browser pop-ups
},
```

**❌ NEVER:**
- Run E2E tests with `--headed` flag in development
- Allow browser windows to pop up during automated testing
- Override headless setting for "debugging" E2E tests
- Use interactive browser sessions for automated tests

---


## 🚢 PRODUCTION DEPLOYMENT & CI/CD

**Universal deployment system - works with any programming language**

**Core Features:**
- **Framework-agnostic validation** - Works with React, Vue, Angular, etc.
- **Zero-downtime updates** - Blue/green deployment with health validation  
- **Automatic rollback** - Failed deployments instantly revert (100% success rate)
- **Performance optimization** - 40% faster deployments (6min → 3-5min)
- **Smart caching** - Change detection, parallel builds

**Common Deployment Failures:**
1. **Health Check Parsing** → `awk '{print $3}'` gets COMMAND not STATUS
2. **Environment Scope** → `$GITHUB_OUTPUT` doesn't exist in SSH
3. **Build-time Variables** → Frontend built with localhost URLs
4. **CSP Restrictions** → Vue.js needs `'unsafe-eval'` for JS evaluation

**Debugging Methodology (Follow Order):**
1. **Container Layer** → `docker-compose ps`, logs, health endpoints
2. **HTTP Layer** → `curl -I domain.com`, asset delivery, API connectivity
3. **Frontend Layer** → Browser console, network tab, CSP violations

**Deployment Validation (All Must Pass):**
- [ ] `docker-compose ps` shows "Up (healthy)"
- [ ] `curl -I https://domain.com` returns HTTP 200
- [ ] Browser console shows zero errors
- [ ] User can interact with application

**Performance Results:**
- Typical deployment: 3-5 minutes (was 6+ minutes)
- No-change deployments: 30 seconds (smart skip)
- Rollback time: 15-30 seconds (automatic)

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


---

---


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