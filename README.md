# iCal Viewer

A professional web application for filtering and subscribing to iCal events, built with Clojure.

## 🌐 Live Site
**Production:** https://filter-ical.de _(after domain setup)_

## ✨ Features
- Filter iCal events by type and keywords
- Create custom filtered subscriptions
- Save and manage multiple calendars
- Professional domain hosting with free SSL
- Responsive modern web interface

## 🚀 Quick Start

**Local Development:**
```bash
clj -M -m app.server
# Visit http://localhost:3000
```

**Production Deployment:**
1. Buy domain at Namecheap (~5€)
2. Run: `./scripts/complete-domain-automation.sh`
3. Your site is live with SSL!

## 🏗️ Architecture

- **Backend:** Clojure with Ring + Jetty
- **Storage:** EDN file persistence
- **Hosting:** AWS EC2 with Docker
- **SSL:** Free Let's Encrypt certificates
- **Proxy:** Nginx with domain routing

### Core Modules
- **`app.storage`** - Calendar and filter persistence
- **`app.ics`** - iCal parsing and generation  
- **`app.server`** - Web interface and API

## 📁 Project Structure

```
├── src/app/           # Clojure source code
├── scripts/           # Domain automation scripts  
├── infrastructure/    # AWS deployment configs
├── archive/           # Old documentation
└── docs/             # Current documentation
```

## 🔧 Development Commands

```bash
# Run application
clj -M -m app.server

# Run tests  
clj -M -e "(require 'app.ical-viewer-test) (app.ical-viewer-test/test-runner)"
```

See `CLAUDE.md` for detailed development instructions.

## 💰 SSL Certificate - FREE!

**❌ DON'T buy SSL from Namecheap** - it's expensive (~20€/year)

**✅ USE Let's Encrypt** - completely free and automated:
- Certificates auto-install during domain setup
- Auto-renewal every 3 months  
- Industry-standard security
- Zero ongoing costs

The automation scripts handle everything!