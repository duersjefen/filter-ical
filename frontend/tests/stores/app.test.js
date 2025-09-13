/**
 * Tests for Pinia app store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import axios from 'axios';
import { useAppStore } from '../../src/stores/app.js';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => null),
    removeItem: vi.fn(() => null),
    clear: vi.fn(() => null),
  },
  writable: true,
});

describe('App Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.resetAllMocks();
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const store = useAppStore();
      
      expect(store.events).toEqual([]);
      expect(store.filters).toEqual([]);
      expect(store.loading).toBe(false);
      expect(store.error).toBe(null);
      expect(store.currentView).toBe('login');
      expect(store.user.loggedIn).toBe(false);
    });
  });

  describe('Getters', () => {
    it('filteredEvents returns all events when no filters applied', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting', dtstart: '2024-01-01' },
        { id: 2, summary: 'Workshop', description: 'Training session', dtstart: '2024-01-02' }
      ];

      expect(store.filteredEvents).toHaveLength(2);
    });

    it('filteredEvents applies keyword filter correctly', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting', dtstart: '2024-01-01' },
        { id: 2, summary: 'Workshop', description: 'Training session', dtstart: '2024-01-02' }
      ];
      store.keywordFilter = 'Meeting';

      expect(store.filteredEvents).toHaveLength(1);
      expect(store.filteredEvents[0].summary).toBe('Meeting');
    });

    it('filteredEvents applies event type filter correctly', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting', dtstart: '2024-01-01' },
        { id: 2, summary: 'Workshop', description: 'Training session', dtstart: '2024-01-02' }
      ];
      store.selectedEventTypes.add('Meeting');

      expect(store.filteredEvents).toHaveLength(1);
      expect(store.filteredEvents[0].summary).toBe('Meeting');
    });

    it('eventTypes returns unique event summaries', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting', dtstart: '2024-01-01' },
        { id: 2, summary: 'Meeting', description: 'Another meeting', dtstart: '2024-01-02' },
        { id: 3, summary: 'Workshop', description: 'Training session', dtstart: '2024-01-03' }
      ];

      expect(store.eventTypes).toEqual(['Meeting', 'Workshop']);
    });
  });

  describe('Actions', () => {
    it('login sets user state correctly', async () => {
      const store = useAppStore();
      store.loginForm.username = 'testuser';
      
      // Mock successful calendar fetch
      mockedAxios.get.mockResolvedValueOnce({
        data: { calendars: [] }
      });

      await store.login();

      expect(store.user.username).toBe('testuser');
      expect(store.user.loggedIn).toBe(true);
      expect(store.currentView).toBe('home');
      expect(store.error).toBe(null);
    });

    it('logout clears user state', () => {
      const store = useAppStore();
      store.user = { username: 'testuser', loggedIn: true };
      store.currentView = 'home';
      
      store.logout();

      expect(store.user.loggedIn).toBe(false);
      expect(store.user.username).toBe(null);
      expect(store.currentView).toBe('login');
    });

    it('fetchCalendars makes API call', async () => {
      const mockCalendars = [
        { id: 1, name: 'Test Calendar', url: 'http://example.com/cal.ics' }
      ];
      
      mockedAxios.get.mockResolvedValueOnce({
        data: { calendars: mockCalendars }
      });

      const store = useAppStore();
      await store.fetchCalendars();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/calendars', {
        headers: { 'X-User-ID': 'anonymous' }
      });
      expect(store.calendars).toEqual(mockCalendars);
    });

    it('addCalendar creates new calendar', async () => {
      const store = useAppStore();
      store.newCalendar = { name: 'Test Cal', url: 'http://example.com/cal.ics' };
      
      mockedAxios.post.mockResolvedValueOnce({ data: { success: true } });
      mockedAxios.get.mockResolvedValueOnce({ data: { calendars: [] } });

      await store.addCalendar();

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/calendars', {
        name: 'Test Cal',
        url: 'http://example.com/cal.ics'
      }, {
        headers: { 'X-User-ID': 'anonymous' }
      });
      expect(store.newCalendar.name).toBe('');
      expect(store.newCalendar.url).toBe('');
    });

    it('clearFilters resets all filter state', () => {
      const store = useAppStore();
      store.keywordFilter = 'test';
      store.selectedEventTypes.add('Meeting');
      store.dateRange = { start: new Date(), end: new Date() };
      
      store.clearFilters();
      
      expect(store.keywordFilter).toBe('');
      expect(store.selectedEventTypes.size).toBe(0);
      expect(store.dateRange.start).toBe(null);
      expect(store.dateRange.end).toBe(null);
    });

    it('clearError resets error state', () => {
      const store = useAppStore();
      store.error = 'Some error';
      
      store.clearError();
      
      expect(store.error).toBe(null);
    });

    it('toggleEventType adds and removes event types', () => {
      const store = useAppStore();
      
      store.toggleEventType('Meeting');
      expect(store.selectedEventTypes.has('Meeting')).toBe(true);
      
      store.toggleEventType('Meeting');
      expect(store.selectedEventTypes.has('Meeting')).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { data: { message: 'Server error' } }
      });

      const store = useAppStore();
      await store.fetchCalendars();

      expect(store.error).toBe('Server error');
      expect(store.loading).toBe(false);
    });

    it('handles network errors gracefully', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Network failed'));

      const store = useAppStore();
      store.newCalendar = { name: 'Test', url: 'http://test.com' };
      
      await store.addCalendar();

      expect(store.error).toContain('Error adding calendar');
      expect(store.loading).toBe(false);
    });

    it('handles missing response data', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: {}
      });

      const store = useAppStore();
      await store.fetchCalendars();

      expect(store.calendars).toEqual(undefined);
    });
  });
});