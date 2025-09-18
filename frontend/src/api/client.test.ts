/**
 * Frontend contract validation tests
 * Verify that API client validates responses against OpenAPI contracts
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { TypedApiClient, ContractValidationError, ContractValidator } from './client'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('Frontend Contract Validation', () => {
  let client: TypedApiClient

  beforeEach(() => {
    client = new TypedApiClient('http://localhost:3000')
    vi.clearAllMocks()
  })

  describe('ContractValidator', () => {
    it('validates calendar objects correctly', () => {
      const validCalendar = {
        id: 'cal_001',
        name: 'Test Calendar',
        url: 'https://example.com/cal.ics',
        user_id: 'public',
        created_at: '2024-01-15T10:30:00Z'
      }

      const invalidCalendar = {
        id: 'cal_001',
        name: 'Test Calendar'
        // Missing required fields
      }

      expect(ContractValidator.validateCalendar(validCalendar)).toBe(true)
      expect(ContractValidator.validateCalendar(invalidCalendar)).toBe(false)
      expect(ContractValidator.validateCalendar(null)).toBe(false)
      expect(ContractValidator.validateCalendar('not an object')).toBe(false)
    })

    it('validates event objects with ISO 8601 dates', () => {
      const validEvent = {
        id: 'evt_001',
        title: 'Test Event',
        start: '2024-01-18T10:00:00Z',
        end: '2024-01-18T11:00:00Z',
        event_type: 'Work',
        description: 'Test description',
        location: 'Test location'
      }

      const invalidEvent = {
        id: 'evt_001',
        title: 'Test Event',
        start: '2024-01-18T10:00:00', // Missing Z suffix
        end: '2024-01-18T11:00:00Z',
        event_type: 'Work'
      }

      expect(ContractValidator.validateEvent(validEvent)).toBe(true)
      expect(ContractValidator.validateEvent(invalidEvent)).toBe(false)
    })

    it('validates grouped events response structure', () => {
      const validResponse = {
        events: {
          'Team Meeting': {
            count: 2,
            events: [
              {
                id: 'evt_001',
                title: 'Team Meeting',
                start: '2024-01-18T10:00:00Z',
                end: '2024-01-18T11:00:00Z',
                event_type: 'Work'
              }
            ]
          }
        }
      }

      const invalidResponse = {
        events: {
          'Team Meeting': {
            count: 'not a number', // Should be number
            events: []
          }
        }
      }

      expect(ContractValidator.validateEventsResponse(validResponse)).toBe(true)
      expect(ContractValidator.validateEventsResponse(invalidResponse)).toBe(false)
    })
  })

  describe('API Client Contract Validation', () => {
    it('validates calendar response and throws ContractValidationError on violation', async () => {
      // Mock invalid response that violates contract
      const invalidResponse = {
        data: {
          calendars: [
            {
              id: 'cal_001',
              name: 'Test Calendar'
              // Missing required fields
            }
          ]
        }
      }

      mockedAxios.mockResolvedValueOnce(invalidResponse)

      await expect(client.getCalendars()).rejects.toThrow(ContractValidationError)
    })

    it('validates events response and throws ContractValidationError on date format violation', async () => {
      // Mock response with invalid date format
      const invalidResponse = {
        data: {
          events: {
            'Team Meeting': {
              count: 1,
              events: [
                {
                  id: 'evt_001',
                  title: 'Team Meeting',
                  start: '2024-01-18T10:00:00', // Missing Z suffix - contract violation
                  end: '2024-01-18T11:00:00Z',
                  event_type: 'Work'
                }
              ]
            }
          }
        }
      }

      mockedAxios.mockResolvedValueOnce(invalidResponse)

      await expect(client.getCalendarEvents('cal_001')).rejects.toThrow(ContractValidationError)
    })

    it('passes valid responses through without error', async () => {
      // Mock valid response
      const validResponse = {
        data: {
          calendars: [
            {
              id: 'cal_001',
              name: 'Test Calendar',
              url: 'https://example.com/cal.ics',
              user_id: 'public',
              created_at: '2024-01-15T10:30:00Z'
            }
          ]
        }
      }

      mockedAxios.mockResolvedValueOnce(validResponse)

      const result = await client.getCalendars()
      expect(result.calendars).toHaveLength(1)
      expect(result.calendars[0].id).toBe('cal_001')
    })

    it('logs contract violations with helpful debugging information', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      const invalidResponse = {
        data: {
          calendars: 'not an array' // Contract violation
        }
      }

      mockedAxios.mockResolvedValueOnce(invalidResponse)

      try {
        await client.getCalendars()
      } catch (error) {
        // Error should be thrown
      }

      expect(consoleSpy).toHaveBeenCalledWith(
        'Contract validation failed:',
        expect.objectContaining({
          endpoint: '/api/calendars',
          method: 'GET',
          expected: 'Contract-compliant response'
        })
      )

      consoleSpy.mockRestore()
    })
  })

  describe('TypeScript Integration', () => {
    it('provides compile-time type safety for API responses', async () => {
      const validResponse = {
        data: {
          calendars: [
            {
              id: 'cal_001',
              name: 'Test Calendar',
              url: 'https://example.com/cal.ics',
              user_id: 'public',
              created_at: '2024-01-15T10:30:00Z'
            }
          ]
        }
      }

      mockedAxios.mockResolvedValueOnce(validResponse)

      const result = await client.getCalendars()
      
      // TypeScript should provide full type safety here
      expect(typeof result.calendars[0].id).toBe('string')
      expect(typeof result.calendars[0].name).toBe('string')
      expect(typeof result.calendars[0].url).toBe('string')
      expect(typeof result.calendars[0].user_id).toBe('string')
      expect(typeof result.calendars[0].created_at).toBe('string')
    })
  })
})