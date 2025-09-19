/**
 * Data Persistence Integration Tests
 * Tests the authentication state management and data source switching
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAppStore } from '../../src/stores/app.js'
import { useUsername } from '../../src/composables/useUsername.js'

// Mock localStorage
const localStorageMock = {
  data: {},
  getItem(key) {
    return this.data[key] || null
  },
  setItem(key, value) {
    this.data[key] = value
  },
  removeItem(key) {
    delete this.data[key]
  },
  clear() {
    this.data = {}
  }
}
global.localStorage = localStorageMock

// Mock API calls
vi.mock('../../src/composables/useApiCall.js', () => ({
  useApiCall: () => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    del: vi.fn(),
    loading: { value: false },
    error: { value: null },
    clearError: vi.fn(),
    setError: vi.fn()
  })
}))

describe('Data Persistence', () => {
  let appStore
  let username

  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.clear()
    appStore = useAppStore()
    username = useUsername()
  })

  describe('Authentication State Switching', () => {
    it('should use localStorage for anonymous users', async () => {
      // Start as anonymous user
      expect(username.getUserId()).toMatch(/^anon_/)
      
      // Add a calendar locally
      appStore.newCalendar.name = 'Test Calendar'
      appStore.newCalendar.url = 'https://example.com/test.ics'
      
      const result = await appStore.addCalendar()
      
      // Should succeed and store locally
      expect(result.success).toBe(true)
      expect(appStore.calendars.length).toBe(1)
      expect(appStore.calendars[0].source).toBe('local')
      
      // Should be saved to localStorage
      const storageKey = appStore.getCalendarsStorageKey()
      const stored = JSON.parse(localStorage.getItem(storageKey))
      expect(stored).toHaveLength(1)
      expect(stored[0].name).toBe('Test Calendar')
    })

    it('should switch to server data when user logs in', async () => {
      // Start as anonymous with local data
      appStore.newCalendar.name = 'Local Calendar'
      appStore.newCalendar.url = 'https://example.com/local.ics'
      await appStore.addCalendar()
      
      expect(appStore.calendars.length).toBe(1)
      expect(appStore.calendars[0].source).toBe('local')
      
      // Mock server response for logged-in user
      const mockServerCalendars = [
        {
          id: 'server_123',
          name: 'Server Calendar',
          url: 'https://example.com/server.ics',
          user_id: 'testuser',
          created_at: '2024-01-01T00:00:00Z'
        }
      ]
      
      vi.mocked(appStore.get).mockResolvedValue({
        success: true,
        data: { calendars: mockServerCalendars }
      })
      
      // Login (change username)
      username.setUsername('testuser')
      
      // Should trigger data reload and switch to server data
      await new Promise(resolve => setTimeout(resolve, 10)) // Wait for async
      
      expect(appStore.calendars.length).toBe(1)
      expect(appStore.calendars[0].name).toBe('Server Calendar')
      expect(appStore.calendars[0].id).toBe('server_123')
    })

    it('should clear server data when user logs out', async () => {
      // Start as logged-in user with server data
      username.setUsername('testuser')
      
      const mockServerCalendars = [
        {
          id: 'server_123',
          name: 'Server Calendar',
          url: 'https://example.com/server.ics',
          user_id: 'testuser',
          created_at: '2024-01-01T00:00:00Z'
        }
      ]
      
      vi.mocked(appStore.get).mockResolvedValue({
        success: true,
        data: { calendars: mockServerCalendars }
      })
      
      await appStore.fetchCalendars()
      expect(appStore.calendars.length).toBe(1)
      
      // Logout (clear username)
      username.clearUsername()
      
      // Should trigger data reload and switch to localStorage (empty)
      await new Promise(resolve => setTimeout(resolve, 10)) // Wait for async
      
      expect(appStore.calendars.length).toBe(0)
    })
  })

  describe('Calendar Addition Flow', () => {
    it('should handle server warnings properly for logged-in users', async () => {
      username.setUsername('testuser')
      
      // Mock server response with warnings
      vi.mocked(appStore.post).mockResolvedValue({
        success: true,
        data: {
          id: 'cal_123',
          name: 'Test Calendar',
          url: 'https://example.com/test.ics',
          user_id: 'testuser',
          created_at: '2024-01-01T00:00:00Z',
          warnings: ['Calendar URL is valid but contains no events']
        }
      })
      
      appStore.newCalendar.name = 'Test Calendar'
      appStore.newCalendar.url = 'https://example.com/test.ics'
      
      const result = await appStore.addCalendar()
      
      expect(result.success).toBe(true)
      expect(result.warnings).toHaveLength(1)
      expect(result.warnings[0]).toBe('Calendar URL is valid but contains no events')
      expect(appStore.calendars.length).toBe(1)
    })

    it('should handle server errors properly for logged-in users', async () => {
      username.setUsername('testuser')
      
      // Mock server error response
      vi.mocked(appStore.post).mockResolvedValue({
        success: false,
        error: 'Calendar URL is not accessible'
      })
      
      appStore.newCalendar.name = 'Bad Calendar'
      appStore.newCalendar.url = 'https://invalid-url.com/bad.ics'
      
      const result = await appStore.addCalendar()
      
      expect(result.success).toBe(false)
      expect(result.error).toBe('Calendar URL is not accessible')
      expect(appStore.calendars.length).toBe(0)
    })
  })

  describe('Calendar Deletion Flow', () => {
    it('should handle 404 errors gracefully for logged-in users', async () => {
      username.setUsername('testuser')
      
      // Add a calendar first
      appStore.calendars.push({
        id: 'cal_123',
        name: 'Test Calendar',
        url: 'https://example.com/test.ics',
        user_id: 'testuser'
      })
      
      // Mock 404 response from server
      vi.mocked(appStore.del).mockResolvedValue({
        success: false,
        error: 'Calendar not found',
        status: 404
      })
      
      const result = await appStore.deleteCalendar('cal_123')
      
      // Should succeed because 404 means calendar is already gone
      expect(result.success).toBe(true)
      expect(appStore.calendars.length).toBe(0)
    })

    it('should handle actual server errors properly for logged-in users', async () => {
      username.setUsername('testuser')
      
      // Add a calendar first
      appStore.calendars.push({
        id: 'cal_123',
        name: 'Test Calendar',
        url: 'https://example.com/test.ics',
        user_id: 'testuser'
      })
      
      // Mock actual server error (not 404)
      vi.mocked(appStore.del).mockResolvedValue({
        success: false,
        error: 'Internal server error',
        status: 500
      })
      
      const result = await appStore.deleteCalendar('cal_123')
      
      // Should fail and calendar should remain
      expect(result.success).toBe(false)
      expect(result.error).toBe('Internal server error')
      expect(appStore.calendars.length).toBe(1)
    })

    it('should delete locally for anonymous users', async () => {
      // Start as anonymous user
      expect(username.getUserId()).toMatch(/^anon_/)
      
      // Add a local calendar
      appStore.calendars.push({
        id: 'local_123',
        name: 'Local Calendar',
        url: 'https://example.com/local.ics',
        user_id: username.getUserId(),
        source: 'local'
      })
      
      const result = await appStore.deleteCalendar('local_123')
      
      expect(result.success).toBe(true)
      expect(appStore.calendars.length).toBe(0)
    })
  })
})