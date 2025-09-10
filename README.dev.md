# iCal Viewer - Development Setup

**Professional full-stack Clojure/ClojureScript development environment with live reloading.**

## 🚀 Quick Start

```bash
# First time setup
make setup

# Start development environment
make dev

# Access your app at http://localhost:3000/app
```

## 📋 Prerequisites

- **Java 17+** (for Clojure backend)
- **Node.js 18+** (for ClojureScript frontend)
- **Make** (for task automation)
- **curl** (for health checks)

## 🏗️ Development Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Development Environment                      │
├─────────────────┬───────────────────────┬───────────────────┤
│   Backend       │    Frontend           │    Integration    │
│   (Port 3000)   │    (Port 8001)        │                   │
├─────────────────┼───────────────────────┼───────────────────┤
│ • Clojure       │ • ClojureScript       │ • Live Reloading  │
│ • Ring + Jetty  │ • Shadow-cljs         │ • Hot Module      │
│ • Live Reload   │ • Reagent + Re-frame  │   Replacement     │
│ • User Storage  │ • ~0.16s Compilation  │ • Instant Updates │
└─────────────────┴───────────────────────┴───────────────────┘
```

## 🛠️ Available Commands

```bash
make setup     # Setup development environment
make dev       # Start full development (backend + frontend)
make backend   # Start only backend server
make frontend  # Start only frontend development server
make test      # Run backend tests
make health    # Check application health
make clean     # Clean development artifacts
make help      # Show all available commands
```

## 🔄 Development Workflow

### 1. Initial Setup
```bash
git clone <repository>
cd ical-viewer
make setup
```

### 2. Daily Development
```bash
make dev
# Edit files in backend/src/ or frontend/src/
# Changes appear immediately (live reload + hot reloading)
```

### 3. Testing
```bash
make test      # Backend tests
make health    # Application health check
```

## 📂 Project Structure

```
ical-viewer/
├── backend/                 # Clojure backend
│   ├── src/app/            # Backend source code
│   │   ├── server.clj      # Main server + API routes
│   │   ├── core/           # Core business logic
│   │   │   ├── user_storage.clj  # User-specific data storage
│   │   │   ├── auth.clj    # Authentication middleware
│   │   │   └── types.clj   # Data types & functions
│   │   └── ics.clj         # iCal parsing & generation
│   ├── test/               # Backend tests
│   ├── data/               # Local data files (EDN)
│   └── deps.edn           # Backend dependencies
├── frontend/               # ClojureScript frontend
│   ├── src/ical_viewer/   # Frontend source code
│   │   ├── core.cljs      # Main app initialization
│   │   ├── events.cljs    # Re-frame events (API calls)
│   │   ├── subs.cljs      # Re-frame subscriptions
│   │   ├── views.cljs     # Main UI components
│   │   └── components/    # UI component library
│   ├── resources/public/  # Static assets + compiled JS
│   ├── package.json       # Frontend dependencies
│   └── shadow-cljs.edn    # Build configuration
└── Makefile               # Development automation
```

## ⚡ Live Development Features

### Backend (Clojure)
- **Instant server restart** on code changes
- **REPL-driven development** capability
- **Hot code reloading** for most changes
- **Persistent data** during development

### Frontend (ClojureScript)
- **Hot module replacement** (~0.16s compilation)
- **State preservation** across code changes
- **Instant browser updates** on save
- **Shadow-cljs web interface** at http://localhost:9630

## 🌍 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000/app | Full application |
| **API** | http://localhost:3000/api/ | Backend API endpoints |
| **Health** | http://localhost:3000/health | Service health check |
| **Frontend Dev** | http://localhost:8001 | Frontend development server |
| **Shadow-cljs** | http://localhost:9630 | Build tool web interface |

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill processes using the ports
sudo lsof -ti:3000 | xargs kill
sudo lsof -ti:8001 | xargs kill
```

### Clean Start
```bash
make clean
make setup
make dev
```

### Check Health
```bash
make health
# Should return: ✅ Backend healthy
```

## 🚀 Production Deployment

The same codebase deploys to production via GitHub Actions:
- Push to `master` triggers deployment
- Docker containers built and deployed to AWS EC2
- Live at https://filter-ical.de

## 📝 Development Principles

1. **Fast Feedback Loop**: Changes visible within seconds
2. **Production Parity**: Same code, same behavior
3. **Repeatable Setup**: `make setup` works on any machine
4. **Clean Architecture**: Functional programming principles
5. **Type Safety**: ClojureScript + Clojure for reliability

---

**Ready to develop!** Run `make dev` and start building amazing features! 🎉