# TODO — iCal Viewer

## High priority
- [x] Fix login page reload issue (resolved with restart)
- [x] Add basic E2E smoke test (15sec test to catch major issues)
- [x] be able to remove entire calendars (already implemented with confirmation)
- [ ] be able to remove/clear individual filters

## Planned features
- [ ] Improve event keyword filtering:
  - Refine matching logic and performance.
  - Add sorting options (e.g., by number of matching events).
  - Provide quick timeframe presets (1 week, 1 month, 1 year) and an easy toggle.
- [] Remove invalid calenders from testuser, and test if the ical url really has events in it before accepting it to be added
- [ ] Allow multiple saved filters per calendar with a simple, discoverable UX.
- [] be able to remove filters, and also be able to remove entire calenders
- [ ] Add calendar sync status indicators (last sync, errors).
- [ ] Export a filtered calendar as a new .ics file.
- [] Implement right server setup, to always serve user up-to-date filterd ical.
  - We need good architecture choices here.
  - We need to test this rigorously, before shipping the website to real users.
- [ ] Support calendar sharing between users.

## Crazy Features
- [] Add AI for the user to quickly create a new filter.

## Technical debt / polish
- [ ] Add robust error handling for calendar fetch failures and surfaced user messages.
- [ ] Implement proper loading states in the frontend.
- [ ] Add form validation and inline feedback.

## Development best practices (later)
- [ ] Add code formatting/linting (Black + Ruff for backend, Prettier for frontend)
- [ ] Add dependency security scanning (pip-audit, npm audit)
- [ ] Add basic performance monitoring (response times)
- [ ] Create API.md and DEVELOPMENT.md documentation
- [ ] Add .env.example for environment management

## Done ✓
- [x] Basic calendar subscription and display
- [x] Event caching for performance
- [x] User isolation and data persistence
- [x] Comprehensive backend API tests
- [x] Test data isolation