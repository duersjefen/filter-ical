# TODO — iCal Viewer

## High Priority (Current Session)
- [ ] Optimize performance for large datasets (virtual scrolling, pagination)
- [ ] Break down CalendarView.vue into smaller components (1400+ lines currently)
- [ ] Add robust error handling and loading states
- [ ] Implement exclude mode functionality in backend (currently only include works)

## Recently Completed ✨
- [x] **MAJOR**: Transform to category-based filtering system with premium UI
- [x] **MAJOR**: Add responsive card-based interface with smart selection
- [x] **MAJOR**: Create collapsible single-event categories section
- [x] **MAJOR**: Implement include/exclude mode switching with auto-inversion
- [x] **MAJOR**: Add advanced preview with sorting and grouping
- [x] **MAJOR**: Professional design system with gradients and animations
- [x] Add smart category selection buttons (Top 5, Main Only, Singles Only)
- [x] Enhanced statistics display (4 statistics cards)
- [x] Fixed time display in category dropdowns
- [x] Proper iCal file generation and download

## Planned Features
- [ ] Remove invalid calendars from testuser, validate iCal URLs before adding
- [ ] Allow multiple saved filters per calendar with simple UX
- [ ] Add calendar sync status indicators (last sync, errors)
- [ ] Implement proper server setup for real-time filtered iCal serving
- [ ] Support calendar sharing between users

## Technical Debt / Polish
- [ ] Add form validation and inline feedback
- [ ] Create API.md and DEVELOPMENT.md documentation
- [ ] Add .env.example for environment management

## Development Best Practices (Later)
- [ ] Add code formatting/linting (Black + Ruff for backend, Prettier for frontend)
- [ ] Add dependency security scanning (pip-audit, npm audit)
- [ ] Add basic performance monitoring (response times)

## Ideas from Claude 🤖

### 🎯 Advanced Features
- [ ] **🔍 Fuzzy Search**: Search by keywords across event descriptions, not just titles
- [ ] **📅 Date Range Picker**: Visual calendar widget to filter events by date ranges
- [ ] **🏷️ Smart Tagging**: Auto-detect event types (meeting, holiday, sport, etc.) using AI/ML
- [ ] **📈 Usage Analytics**: Track which categories users select most often
- [ ] **💾 Saved Filters**: Let users save and name their favorite category combinations
- [ ] **🔗 Shareable Links**: Generate URLs for specific category combinations

### 🎨 UX Enhancements
- [ ] **🎭 Dark Mode**: Toggle between light/dark themes
- [ ] **🎨 Color-Coded Categories**: Assign colors to different category types automatically
- [ ] **📱 Mobile App Feel**: Add PWA capabilities for mobile installation
- [ ] **⌨️ Keyboard Shortcuts**: Hotkeys for common actions (Ctrl+A for select all, etc.)
- [ ] **🔄 Undo/Redo**: Let users undo their last selection changes
- [ ] **📋 Drag & Drop**: Drag categories between included/excluded lists

### 🧠 Intelligence Features
- [ ] **🤖 Smart Recommendations**: "Users who selected X also selected Y"
- [ ] **📊 Calendar Health Score**: Analyze how balanced/busy the calendar is
- [ ] **⚡ Quick Actions**: "Select weekends only", "Select work hours only"
- [ ] **🔮 Predictive Selection**: Learn user patterns and pre-select likely choices

### 🔧 Technical Improvements
- [ ] **📦 Component Library**: Break into reusable Vue components
- [ ] **🚀 Lazy Loading**: Load categories on-demand for huge calendars
- [ ] **💨 Debounced Search**: Optimize search performance
- [ ] **🎬 Smooth Animations**: Add micro-interactions and loading states

## Crazy Features
- [ ] Add AI for the user to quickly create a new filter
- [ ] Possibility to change language between English and German

## Done ✓ (Historical)
- [x] Basic calendar subscription and display
- [x] Event caching for performance  
- [x] User isolation and data persistence
- [x] Comprehensive backend API tests
- [x] Test data isolation
- [x] Fix login page reload issue
- [x] Add basic E2E smoke test
- [x] Ability to remove entire calendars