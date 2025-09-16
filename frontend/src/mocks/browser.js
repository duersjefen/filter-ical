/**
 * MSW browser setup for frontend development
 * Enables API mocking in development mode
 */

import { setupWorker } from 'msw/browser'
import { handlers } from './handlers.js'

// Setup MSW worker with our API handlers
export const worker = setupWorker(...handlers)

// Enable mocking conditionally
export async function enableMocking() {
  // Only enable mocking in development mode
  if (import.meta.env.MODE === 'development' && import.meta.env.VITE_ENABLE_API_MOCKING === 'true') {
    console.log('🔧 Starting MSW for API mocking...')
    
    await worker.start({
      onUnhandledRequest: 'warn', // Warn about unmocked requests
      serviceWorker: {
        url: '/mockServiceWorker.js'
      }
    })
    
    console.log('✅ MSW started - API calls will be mocked')
    return true
  }
  
  return false
}