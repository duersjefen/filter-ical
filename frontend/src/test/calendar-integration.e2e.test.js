/**
 * E2E Integration Test: Calendar Add/List/Delete Workflow
 * Tests frontend-backend integration using contract-based APIs
 */

import { beforeAll, afterAll, describe, test, expect } from 'vitest'

const BASE_URL = 'http://localhost:3000'
const TEST_USER = `testuser_${Date.now()}`

describe('Calendar Integration E2E', () => {
  let testCalendarId = null
  
  // Helper function to make API calls like the frontend does
  async function apiCall(endpoint, options = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'x-user-id': TEST_USER,
        ...options.headers
      },
      ...options
    })
    
    const data = await response.json()
    return { response, data }
  }

  beforeAll(async () => {
    // Ensure backend is running
    const healthCheck = await fetch(`${BASE_URL}/health`)
    expect(healthCheck.ok).toBe(true)
  })

  test('should list calendars (empty initially)', async () => {
    const { response, data } = await apiCall('/api/calendars')
    
    expect(response.status).toBe(200)
    expect(Array.isArray(data)).toBe(true)
    // Should be empty for our test user initially
    expect(data.length).toBe(0)
  })

  test('should create a new calendar', async () => {
    const calendarData = {
      name: 'Test Calendar E2E',
      url: 'https://example.com/test-e2e.ics'
    }

    const { response, data } = await apiCall('/api/calendars', {
      method: 'POST',
      body: JSON.stringify(calendarData)
    })

    expect(response.status).toBe(200)
    expect(data.id).toBeDefined()
    expect(data.name).toBe(calendarData.name)
    expect(data.url).toBe(calendarData.url)
    expect(data.user_id).toBe(TEST_USER)
    expect(data.is_active).toBe(true)
    
    // Store ID for subsequent tests
    testCalendarId = data.id
  })

  test('should list calendars (with our new calendar)', async () => {
    const { response, data } = await apiCall('/api/calendars')
    
    expect(response.status).toBe(200)
    expect(Array.isArray(data)).toBe(true)
    expect(data.length).toBe(1)
    
    const calendar = data[0]
    expect(calendar.id).toBe(testCalendarId)
    expect(calendar.name).toBe('Test Calendar E2E')
    expect(calendar.url).toBe('https://example.com/test-e2e.ics')
    expect(calendar.user_id).toBe(TEST_USER)
  })

  test('should get specific calendar details', async () => {
    const { response, data } = await apiCall(`/api/calendars/${testCalendarId}`)
    
    expect(response.status).toBe(200)
    expect(data.id).toBe(testCalendarId)
    expect(data.name).toBe('Test Calendar E2E')
    expect(data.user_id).toBe(TEST_USER)
  })

  test('should delete the calendar', async () => {
    const { response } = await apiCall(`/api/calendars/${testCalendarId}`, {
      method: 'DELETE'
    })
    
    expect(response.status).toBe(200)
  })

  test('should list calendars (empty after deletion)', async () => {
    const { response, data } = await apiCall('/api/calendars')
    
    expect(response.status).toBe(200)
    expect(Array.isArray(data)).toBe(true)
    expect(data.length).toBe(0)
  })

  test('should handle invalid calendar creation', async () => {
    const invalidData = {
      name: '', // Empty name should fail
      url: 'https://example.com/test.ics'
    }

    const { response, data } = await apiCall('/api/calendars', {
      method: 'POST',
      body: JSON.stringify(invalidData)
    })

    // Should return error for invalid data
    expect(response.status).toBeGreaterThanOrEqual(400)
  })

  test('should handle missing user header', async () => {
    const { response } = await fetch(`${BASE_URL}/api/calendars`, {
      headers: {
        'Content-Type': 'application/json'
        // No x-user-id header
      }
    })

    // Should require user header
    expect(response.status).toBeGreaterThanOrEqual(400)
  })
})