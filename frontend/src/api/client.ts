/**
 * Contract-aware API client with TypeScript validation
 * Provides compile-time type safety AND runtime contract validation
 * Uses generated OpenAPI types to ensure frontend-backend contract compliance
 */

import axios, { AxiosResponse } from 'axios'
import type { paths, components } from '../types/api'

// Type helpers for API paths and responses
type ApiPaths = paths
type Calendar = components['schemas']['Calendar']
type Event = components['schemas']['Event']
type FilteredCalendar = components['schemas']['FilteredCalendar']
type FilterConfig = components['schemas']['FilterConfig']
type CalendarPreferences = components['schemas']['CalendarPreferences']
type SavedFilter = components['schemas']['SavedFilter']
type ApiError = components['schemas']['Error']

// Contract validation error
class ContractValidationError extends Error {
  constructor(
    message: string,
    public endpoint: string,
    public expectedType: string,
    public actualData: unknown
  ) {
    super(`Contract violation at ${endpoint}: ${message}`)
    this.name = 'ContractValidationError'
  }
}

// Runtime contract validation utilities
class ContractValidator {
  static validateCalendar(data: unknown): data is Calendar {
    if (!data || typeof data !== 'object') return false
    const obj = data as Record<string, unknown>
    
    return (
      typeof obj.id === 'string' &&
      typeof obj.name === 'string' &&
      typeof obj.url === 'string' &&
      typeof obj.user_id === 'string' &&
      typeof obj.created_at === 'string'
    )
  }

  static validateEvent(data: unknown): data is Event {
    if (!data || typeof data !== 'object') return false
    const obj = data as Record<string, unknown>
    
    return (
      typeof obj.id === 'string' &&
      typeof obj.title === 'string' &&
      typeof obj.start === 'string' &&
      typeof obj.end === 'string' &&
      typeof obj.event_type === 'string' &&
      // ISO 8601 date format validation
      obj.start.endsWith('Z') &&
      obj.end.endsWith('Z') &&
      (obj.description === undefined || typeof obj.description === 'string') &&
      (obj.location === undefined || obj.location === null || typeof obj.location === 'string')
    )
  }

  static validateEventsResponse(data: unknown): data is GetEventsResponse {
    if (!data || typeof data !== 'object') return false
    const obj = data as Record<string, unknown>
    
    if (!obj.events || typeof obj.events !== 'object') return false
    const events = obj.events as Record<string, unknown>
    
    // Validate grouped events structure
    for (const [recurringEvent, eventData] of Object.entries(events)) {
      if (!eventData || typeof eventData !== 'object') return false
      const group = eventData as Record<string, unknown>
      
      if (typeof group.count !== 'number' || !Array.isArray(group.events)) return false
      
      // Validate each event in the group
      for (const event of group.events) {
        if (!ContractValidator.validateEvent(event)) return false
      }
    }
    
    return true
  }

  static validateCalendarsResponse(data: unknown): data is GetCalendarsResponse {
    if (!data || typeof data !== 'object') return false
    const obj = data as Record<string, unknown>
    
    return (
      Array.isArray(obj.calendars) && 
      obj.calendars.every(cal => ContractValidator.validateCalendar(cal))
    )
  }
}

// Extract response types from OpenAPI specification
type GetCalendarsResponse = ApiPaths['/api/calendars']['get']['responses'][200]['content']['application/json']
type CreateCalendarRequest = ApiPaths['/api/calendars']['post']['requestBody']['content']['application/json']
type CreateCalendarResponse = ApiPaths['/api/calendars']['post']['responses'][201]['content']['application/json']
type GetEventsResponse = ApiPaths['/api/calendar/{calendar_id}/events']['get']['responses'][200]['content']['application/json']
type GetFilteredCalendarsResponse = ApiPaths['/api/filtered-calendars']['get']['responses'][200]['content']['application/json']
type CreateFilteredCalendarRequest = ApiPaths['/api/filtered-calendars']['post']['requestBody']['content']['application/json']
type CreateFilteredCalendarResponse = ApiPaths['/api/filtered-calendars']['post']['responses'][201]['content']['application/json']

// Create type-safe API client
export class TypedApiClient {
  private baseURL: string
  private userHeaders: Record<string, string>

  constructor(baseURL: string = '', userHeaders: Record<string, string> = {}) {
    this.baseURL = baseURL
    this.userHeaders = userHeaders
  }

  // Helper method to make requests with proper typing and contract validation
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any,
    validator?: (data: unknown) => data is T
  ): Promise<T> {
    try {
      const response: AxiosResponse<T> = await axios({
        method,
        url: `${this.baseURL}${url}`,
        data,
        headers: {
          'Content-Type': 'application/json',
          ...this.userHeaders
        }
      })

      // Runtime contract validation if validator provided
      if (validator && !validator(response.data)) {
        console.error('Contract validation failed:', {
          endpoint: url,
          method,
          expected: 'Contract-compliant response',
          actual: response.data
        })
        
        throw new ContractValidationError(
          'Response does not match OpenAPI schema',
          url,
          'Expected contract-compliant response',
          response.data
        )
      }

      return response.data
    } catch (error) {
      if (error instanceof ContractValidationError) {
        throw error
      }
      
      if (axios.isAxiosError(error) && error.response) {
        const apiError = error.response.data as ApiError
        throw new Error(apiError.detail || 'API request failed')
      }
      throw error
    }
  }

  // Calendar Management
  async getCalendars(): Promise<GetCalendarsResponse> {
    return this.request<GetCalendarsResponse>(
      'GET', 
      '/api/calendars',
      undefined,
      ContractValidator.validateCalendarsResponse
    )
  }

  async createCalendar(calendar: CreateCalendarRequest): Promise<CreateCalendarResponse> {
    return this.request<CreateCalendarResponse>(
      'POST', 
      '/api/calendars', 
      calendar,
      ContractValidator.validateCalendar
    )
  }

  async deleteCalendar(calendarId: string): Promise<void> {
    return this.request<void>('DELETE', `/api/calendars/${calendarId}`)
  }

  // Calendar Data
  async getCalendarEvents(calendarId: string): Promise<GetEventsResponse> {
    return this.request<GetEventsResponse>(
      'GET', 
      `/api/calendar/${calendarId}/events`,
      undefined,
      ContractValidator.validateEventsResponse
    )
  }

  async getCalendarRawEvents(calendarId: string): Promise<{ events: Event[] }> {
    return this.request<{ events: Event[] }>('GET', `/api/calendar/${calendarId}/raw-events`)
  }

  // Filtered Calendars
  async getFilteredCalendars(): Promise<GetFilteredCalendarsResponse> {
    return this.request<GetFilteredCalendarsResponse>('GET', '/api/filtered-calendars')
  }

  async createFilteredCalendar(request: CreateFilteredCalendarRequest): Promise<CreateFilteredCalendarResponse> {
    return this.request<CreateFilteredCalendarResponse>('POST', '/api/filtered-calendars', request)
  }

  async updateFilteredCalendar(
    filteredCalendarId: string, 
    update: { name?: string; filter_config?: FilterConfig }
  ): Promise<FilteredCalendar> {
    return this.request<FilteredCalendar>('PUT', `/api/filtered-calendars/${filteredCalendarId}`, update)
  }

  async deleteFilteredCalendar(filteredCalendarId: string): Promise<void> {
    return this.request<void>('DELETE', `/api/filtered-calendars/${filteredCalendarId}`)
  }

  // User Preferences
  async getUserPreferences(): Promise<{ success: boolean; preferences: Record<string, any> }> {
    return this.request<{ success: boolean; preferences: Record<string, any> }>('GET', '/api/user/preferences')
  }

  async saveUserPreferences(preferences: Record<string, any>): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('PUT', '/api/user/preferences', preferences)
  }

  async getCalendarPreferences(calendarId: string): Promise<{ success: boolean; preferences: CalendarPreferences }> {
    return this.request<{ success: boolean; preferences: CalendarPreferences }>('GET', `/api/calendars/${calendarId}/preferences`)
  }

  async saveCalendarPreferences(calendarId: string, preferences: CalendarPreferences): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('PUT', `/api/calendars/${calendarId}/preferences`, preferences)
  }

  // Saved Filters
  async getSavedFilters(): Promise<{ filters: SavedFilter[] }> {
    return this.request<{ filters: SavedFilter[] }>('GET', '/api/filters')
  }

  async createSavedFilter(filter: { name: string; config: any }): Promise<SavedFilter> {
    return this.request<SavedFilter>('POST', '/api/filters', filter)
  }

  async deleteSavedFilter(filterId: string): Promise<void> {
    return this.request<void>('DELETE', `/api/filters/${filterId}`)
  }

  // iCal Generation
  async generateFilteredICal(
    calendarId: string, 
    request: { selected_events: string[]; filter_mode: 'include' | 'exclude' }
  ): Promise<string> {
    const response = await axios({
      method: 'POST',
      url: `${this.baseURL}/api/calendar/${calendarId}/generate`,
      data: request,
      headers: {
        'Content-Type': 'application/json',
        ...this.userHeaders
      },
      responseType: 'text'
    })
    return response.data
  }
}

// Export types for use in components
export type {
  Calendar,
  Event,
  FilteredCalendar,
  FilterConfig,
  CalendarPreferences,
  SavedFilter,
  ApiError,
  GetEventsResponse,
  CreateCalendarRequest,
  CreateFilteredCalendarRequest
}

// Export validation utilities
export { ContractValidationError, ContractValidator }

// Default client instance
export const apiClient = new TypedApiClient()