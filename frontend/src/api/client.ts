/**
 * Type-safe API client generated from OpenAPI specification
 * Provides compile-time type safety for all API endpoints
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

  // Helper method to make requests with proper typing
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
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
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const apiError = error.response.data as ApiError
        throw new Error(apiError.detail || 'API request failed')
      }
      throw error
    }
  }

  // Calendar Management
  async getCalendars(): Promise<GetCalendarsResponse> {
    return this.request<GetCalendarsResponse>('GET', '/api/calendars')
  }

  async createCalendar(calendar: CreateCalendarRequest): Promise<CreateCalendarResponse> {
    return this.request<CreateCalendarResponse>('POST', '/api/calendars', calendar)
  }

  async deleteCalendar(calendarId: string): Promise<void> {
    return this.request<void>('DELETE', `/api/calendars/${calendarId}`)
  }

  // Calendar Data
  async getCalendarEvents(calendarId: string): Promise<GetEventsResponse> {
    return this.request<GetEventsResponse>('GET', `/api/calendar/${calendarId}/events`)
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

// Default client instance
export const apiClient = new TypedApiClient()