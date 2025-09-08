# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the application
```bash
# Start the server (default port 3000)
clj -M -m app.server

# Start with custom port
clj -M -m app.server 8080
```

### Running tests
```bash
# Run all tests
clj -M -e "(require 'app.ical-viewer-test) (app.ical-viewer-test/test-runner)"
```

## Architecture Overview

This is a user-friendly Clojure web application for filtering iCal events and creating custom subscriptions with a modular architecture:

### Core Modules
- **`app.storage`** - Calendar and filter persistence using EDN file storage (`data/entries.edn`, `data/filters.edn`)
- **`app.ics`** - iCal fetching, parsing, and generation
- **`app.server`** - Modern web interface with enhanced filtering, subscription management

### Technology Stack
- **Backend**: Clojure 1.11.1 with Ring + Jetty web server
- **Routing**: Compojure for HTTP routes
- **UI**: Server-side HTML with responsive design and JavaScript enhancements
- **Storage**: EDN files for calendar entries and saved filters
- **Dependencies**: Managed via `deps.edn`

### Key Features
- **Smart Filtering**: Filter events by type/summary with keyword search
- **Saved Filters**: Persistent filter management with names
- **Subscription URLs**: Generate subscribable iCal URLs for any filter
- **Modern UI**: Clean, responsive design with statistics and quick actions

### Data Flow
1. User adds calendar URL → Stored in `data/entries.edn`
2. User creates filter → Events grouped by type, filtered by selection
3. Filter saved → Stored in `data/filters.edn` with calendar reference
4. Subscription → Dynamic iCal generation at `/subscribe/{filter-id}` for any calendar app

### Key Functions

#### Storage (`app.storage`)
- `add-entry!`, `get-entry`, `delete-entry!`, `all-entries` - Calendar CRUD operations
- `add-filter!`, `get-filter`, `delete-filter!`, `all-filters` - Filter management
- `filters-for-calendar` - Get saved filters for a specific calendar

#### iCal Processing (`app.ics`)
- `events-for-url` - Complete pipeline: fetch → parse → return event list
- `build-calendar` - Generate valid iCal from selected events
- `extract-vevents`, `parse-vevent` - Low-level parsing utilities

#### Web Interface (`app.server`)
- `home-page` - Modern dashboard with calendar stats and management
- `view-page` - Enhanced filtering interface with saved filters and quick actions
- `subscription-info-page` - Subscription URL management with setup instructions
- `filter-events-by-summaries` - Core filtering logic by event summary/type

### Routes
- `GET /` - Main dashboard
- `GET /view/{id}` - Calendar filtering interface (supports `?filter=` parameter)
- `POST /filter/save` - Save/download filtered events
- `GET /filter/info/{filter-id}` - Subscription information and setup
- `GET /subscribe/{filter-id}` - Live iCal feed for subscriptions

## Testing

The test suite (`test/app/ical_viewer_test.clj`) includes:
- Unit tests for storage operations
- iCal parsing and generation tests  
- Server functionality tests
- Integration tests for full workflow

Run tests using the command above or by loading the test namespace and calling `test-runner`.