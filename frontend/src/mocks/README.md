# API Mocking with Mock Service Worker (MSW)

This directory contains Mock Service Worker (MSW) configuration for frontend development.

## Overview

MSW allows frontend developers to work with realistic API responses without needing the backend server running. All mock responses are generated from our OpenAPI specification to ensure they match the real API exactly.

## Usage

### Enable Mocking

Set the environment variable in `.env.development`:

```bash
VITE_ENABLE_API_MOCKING=true
```

When enabled, all API requests will be intercepted and handled by MSW instead of reaching the backend.

### Disable Mocking

To use the real backend API:

```bash
VITE_ENABLE_API_MOCKING=false
```

Or simply remove/comment out the variable from `.env.development`.

## Mock Data

The mock handlers in `handlers.js` provide realistic responses for all API endpoints:

- **Calendars**: CRUD operations with proper validation
- **Events**: Calendar events grouped by recurring event types
- **Filtered Calendars**: Custom calendar filtering functionality
- **User Preferences**: User settings and preferences
- **Error Responses**: Proper HTTP status codes and error messages

## Benefits

1. **Frontend Independence**: Develop frontend features without backend
2. **Contract Compliance**: Mock responses match OpenAPI specification exactly
3. **Realistic Testing**: Test with realistic data scenarios
4. **Error Testing**: Test error conditions easily
5. **Fast Development**: No network latency or backend startup time

## Files

- `handlers.js` - MSW request handlers for all API endpoints
- `browser.js` - MSW browser setup and configuration
- `README.md` - This documentation

## Development Workflow

1. **Start Development**: Run `npm run dev` with mocking enabled
2. **Develop Features**: Build components using mocked API responses
3. **Test Integration**: Switch to real backend API for integration testing
4. **Deploy**: Production automatically uses real backend API

## Adding New Endpoints

When adding new API endpoints:

1. Update the OpenAPI specification in `backend/openapi.yaml`
2. Regenerate TypeScript types: `npm run types:generate`
3. Add corresponding mock handlers in `handlers.js`
4. Test with both mocked and real API responses

This ensures frontend and backend stay synchronized through the contract-first development approach.