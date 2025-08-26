# iCal Viewer

A web application for viewing and filtering iCal events, built with Clojure.

## Features

✅ **Implemented Features:**

- Add multiple iCal calendars by name and URL
- View all saved calendars in a clean interface
- Parse iCal events from remote URLs
- Group events by summary/title
- Select specific events with checkboxes
- Generate filtered .ics files for download
- Clean modular code structure with proper error handling

## Architecture

The application is split into focused modules:

- **`app.storage`** - Calendar entry persistence (EDN file storage)
- **`app.ics`** - iCal fetching, parsing, and generation
- **`app.server`** - Web interface with Hiccup templates and Compojure routes

## Running the Application

```bash
# Start the server
clj -M -m app.server

# Server starts on http://localhost:3000
```

## Usage

1. **Add Calendar**: Enter a name and iCal URL on the home page
2. **View Events**: Click "View Events" on any calendar card
3. **Filter Events**: Events are grouped by summary - use checkboxes to select desired events
4. **Download**: Click "Generate Filtered .ics" to download selected events

## Code Structure

```
src/
├── app/
│   ├── storage.clj    # Data persistence layer
│   ├── ics.clj        # iCal parsing and generation
│   └── server.clj     # Web server and UI
test/
└── app/
    └── ical_viewer_test.clj    # Unit tests
```

## Key Functions

### Storage Layer (`app.storage`)

- `add-entry!` - Add new calendar entry
- `get-entry` - Retrieve calendar by ID
- `delete-entry!` - Remove calendar entry
- `all-entries` - Get all stored calendars

### iCal Processing (`app.ics`)

- `fetch-ics` - Download iCal from URL with error handling
- `extract-vevents` - Parse VEVENT blocks from iCal text
- `parse-vevent` - Extract properties (UID, summary, dates, etc.)
- `events-for-url` - Complete parsing pipeline
- `build-calendar` - Generate valid iCal from selected events

### Web Interface (`app.server`)

- `home-page` - Main interface with calendar list and add form
- `view-page` - Event display with grouping and selection
- `group-events-by-summary` - Group events for better UX
- Routes for CRUD operations and filtered export

## Data Flow

1. User adds calendar URL → Stored in `data/entries.edn`
2. User views calendar → Fetch and parse iCal events
3. Events grouped by summary → Display with checkboxes
4. User selects events → Generate filtered .ics file
5. Download provided as attachment

## Error Handling

- Invalid URLs return empty event lists with logged errors
- Missing calendar entries redirect to home page
- File I/O wrapped in try-catch blocks
- Graceful degradation for malformed iCal data

## Dependencies

- **Clojure 1.11.1** - Core language
- **Ring + Jetty** - Web server
- **Compojure** - Routing
- **Hiccup** - HTML generation
- **EDN** - Data persistence

The application successfully implements all requested features with clean, modular Clojure code!
