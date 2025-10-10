/**
 * Tests for Calendar Store
 * Handles calendar management, events, and sync functionality
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useCalendarStore } from '../../src/stores/calendar.js';

// Mock useHTTP composable
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockDel = vi.fn();
const mockLoading = { value: false };
const mockError = { value: null };
const mockClearError = vi.fn();

vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    get: mockGet,
    post: mockPost,
    del: mockDel,
    loading: mockLoading,
    error: mockError,
    clearError: mockClearError
  })
}));

// Mock useUsername composable
const mockGetUserId = vi.fn(() => 'testuser');
vi.mock('../../src/composables/useUsername', () => ({
  useUsername: () => ({
    getUserId: mockGetUserId
  })
}));

describe('Calendar Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mockGetUserId.mockReturnValue('testuser');
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const store = useCalendarStore();

      expect(store.calendars).toEqual([]);
      expect(store.selectedCalendar).toBeNull();
      expect(store.newCalendar).toEqual({ name: '', url: '' });
      expect(store.events).toEqual([]);
      expect(store.recurringEvents).toEqual({});
    });
  });

  describe('fetchCalendars', () => {
    it('fetches calendars for logged-in user', async () => {
      const mockCalendars = [
        { id: 1, name: 'Test Calendar', source_url: 'http://example.com/cal.ics' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: mockCalendars
      });

      const store = useCalendarStore();
      const result = await store.fetchCalendars();

      expect(result.success).toBe(true);
      expect(store.calendars).toEqual(mockCalendars);
      expect(mockGet).toHaveBeenCalled();
    });

    it('returns empty array for anonymous users', async () => {
      mockGetUserId.mockReturnValue('anon_12345');

      const store = useCalendarStore();
      const result = await store.fetchCalendars();

      expect(result.success).toBe(true);
      expect(result.data).toEqual([]);
      expect(store.calendars).toEqual([]);
      expect(result.message).toBe('Login required for calendar management');
    });

    it('handles API errors gracefully', async () => {
      mockGet.mockResolvedValueOnce({
        success: false,
        error: 'Server error'
      });

      const store = useCalendarStore();
      const result = await store.fetchCalendars();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Server error');
      expect(store.calendars).toEqual([]);
    });
  });

  describe('addCalendar', () => {
    it('adds calendar for logged-in user', async () => {
      const newCal = { id: 1, name: 'New Calendar', source_url: 'http://example.com/cal.ics' };

      mockPost.mockResolvedValueOnce({
        success: true,
        data: newCal
      });

      const store = useCalendarStore();
      store.newCalendar = { name: 'New Calendar', url: 'http://example.com/cal.ics' };

      const result = await store.addCalendar();

      expect(result.success).toBe(true);
      expect(store.calendars).toHaveLength(1);
      expect(store.calendars[0]).toEqual(newCal);
      expect(store.newCalendar).toEqual({ name: '', url: '' });
    });

    it('validates input before adding', async () => {
      const store = useCalendarStore();
      store.newCalendar = { name: '', url: '' };

      const result = await store.addCalendar();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Please provide both calendar name and URL');
      expect(mockPost).not.toHaveBeenCalled();
    });

    it('prevents calendar creation for anonymous users', async () => {
      mockGetUserId.mockReturnValue('anon_12345');

      const store = useCalendarStore();
      store.newCalendar = { name: 'Test', url: 'http://example.com/cal.ics' };

      const result = await store.addCalendar();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Login required to create calendars');
    });

    it('handles warnings from server', async () => {
      const newCal = {
        id: 1,
        name: 'New Calendar',
        source_url: 'http://example.com/cal.ics',
        warnings: ['Some events could not be parsed']
      };

      mockPost.mockResolvedValueOnce({
        success: true,
        data: newCal
      });

      const store = useCalendarStore();
      store.newCalendar = { name: 'New Calendar', url: 'http://example.com/cal.ics' };

      const result = await store.addCalendar();

      expect(result.success).toBe(true);
      expect(result.warnings).toEqual(['Some events could not be parsed']);
    });
  });

  describe('deleteCalendar', () => {
    it('deletes calendar for logged-in user', async () => {
      mockDel.mockResolvedValueOnce({ success: true });

      const store = useCalendarStore();
      store.calendars = [
        { id: 1, name: 'Test Calendar', source_url: 'http://example.com/cal.ics' }
      ];

      const result = await store.deleteCalendar(1);

      expect(result.success).toBe(true);
      expect(store.calendars).toHaveLength(0);
    });

    it('prevents deletion of domain calendars', async () => {
      const store = useCalendarStore();
      store.calendars = [
        { id: 'cal_domain_test', name: 'Domain Calendar' }
      ];

      const result = await store.deleteCalendar('cal_domain_test');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Domain calendars cannot be deleted');
      expect(mockDel).not.toHaveBeenCalled();
    });

    it('handles calendar not found gracefully', async () => {
      const store = useCalendarStore();
      store.calendars = [];

      const result = await store.deleteCalendar(999);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Calendar not found');
    });

    it('prevents deletion for anonymous users', async () => {
      mockGetUserId.mockReturnValue('anon_12345');

      const store = useCalendarStore();
      store.calendars = [{ id: 1, name: 'Test' }];

      const result = await store.deleteCalendar(1);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Login required to delete calendars');
    });
  });

  describe('syncCalendar', () => {
    it('syncs calendar for logged-in user', async () => {
      mockPost.mockResolvedValueOnce({
        success: true,
        data: { event_count: 25 }
      });

      const store = useCalendarStore();
      const result = await store.syncCalendar(1);

      expect(result.success).toBe(true);
      expect(result.data.event_count).toBe(25);
    });

    it('prevents sync for anonymous users', async () => {
      mockGetUserId.mockReturnValue('anon_12345');

      const store = useCalendarStore();
      const result = await store.syncCalendar(1);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Login required to sync calendars');
    });
  });

  describe('Calendar Selection', () => {
    it('selects calendar', () => {
      const store = useCalendarStore();
      const calendar = { id: 1, name: 'Test Calendar' };

      store.selectCalendar(calendar);

      expect(store.selectedCalendar).toEqual(calendar);
    });

    it('clears selection', () => {
      const store = useCalendarStore();
      store.selectedCalendar = { id: 1, name: 'Test Calendar' };

      store.clearSelection();

      expect(store.selectedCalendar).toBeNull();
    });
  });

  describe('Event Loading', () => {
    it('loads calendar events', async () => {
      const mockEvents = [
        { id: 1, title: 'Meeting', start: '2024-01-01' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: { events: mockEvents }
      });

      const store = useCalendarStore();
      const result = await store.loadCalendarEvents(1);

      expect(result.success).toBe(true);
      expect(store.events).toEqual(mockEvents);
    });

    it('loads recurring events structure', async () => {
      const mockEvents = [
        { id: 1, title: 'Meeting', start: '2024-01-01' },
        { id: 2, title: 'Meeting', start: '2024-01-02' },
        { id: 3, title: 'Workshop', start: '2024-01-03' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: { events: mockEvents }
      });

      const store = useCalendarStore();
      await store.loadCalendarRecurringEvents(1);

      expect(store.recurringEvents).toHaveProperty('Meeting');
      expect(store.recurringEvents).toHaveProperty('Workshop');
      expect(store.recurringEvents['Meeting'].count).toBe(2);
      expect(store.recurringEvents['Workshop'].count).toBe(1);
    });
  });

  describe('Group Loading', () => {
    it('loads calendar groups for user calendars', async () => {
      const mockEvents = [
        { id: 1, title: 'Meeting', start_time: '2024-01-01', end_time: '2024-01-01' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: { events: mockEvents }
      });

      const store = useCalendarStore();
      const result = await store.loadCalendarGroups(1);

      expect(result.success).toBe(true);
      expect(store.events).toHaveLength(1);
      expect(store.recurringEvents).toHaveProperty('Meeting');
    });

    it('normalizes event field names', async () => {
      const mockEvents = [
        { id: 1, title: 'Meeting', start_time: '2024-01-01T10:00:00', end_time: '2024-01-01T11:00:00' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: { events: mockEvents }
      });

      const store = useCalendarStore();
      await store.loadCalendarGroups(1);

      // Check that start_time is mapped to start and dtstart
      expect(store.events[0].start).toBe('2024-01-01T10:00:00');
      expect(store.events[0].dtstart).toBe('2024-01-01T10:00:00');
      expect(store.events[0].end).toBe('2024-01-01T11:00:00');
      expect(store.events[0].dtend).toBe('2024-01-01T11:00:00');
    });
  });
});
