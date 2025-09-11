/**
 * Tests for Pinia app store
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAppStore } from '../../src/stores/app.js';

// Mock fetch globally for this test file
global.fetch = vi.fn();

describe('App Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.resetAllMocks();
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const store = useAppStore();
      
      expect(store.events).toEqual([]);
      expect(store.filters).toEqual({
        titleFilter: '',
        descriptionFilter: '',
        locationFilter: '',
        excludeKeywords: ''
      });
      expect(store.loading).toBe(false);
      expect(store.error).toBe(null);
      expect(store.currentView).toBe('home');
    });
  });

  describe('Getters', () => {
    it('filteredEvents returns all events when no filters applied', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting' },
        { id: 2, summary: 'Workshop', description: 'Training session' }
      ];

      expect(store.filteredEvents).toHaveLength(2);
    });

    it('filteredEvents applies title filter correctly', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Meeting', description: 'Team meeting' },
        { id: 2, summary: 'Workshop', description: 'Training session' }
      ];
      store.filters.titleFilter = 'Meeting';

      expect(store.filteredEvents).toHaveLength(1);
      expect(store.filteredEvents[0].summary).toBe('Meeting');
    });

    it('filteredEvents excludes events with excluded keywords', () => {
      const store = useAppStore();
      store.events = [
        { id: 1, summary: 'Important Meeting', description: 'Team meeting' },
        { id: 2, summary: 'Optional Workshop', description: 'Training session' }
      ];
      store.filters.excludeKeywords = 'Optional';

      expect(store.filteredEvents).toHaveLength(1);
      expect(store.filteredEvents[0].summary).toBe('Important Meeting');
    });

    it('hasActiveFilters returns true when filters are applied', () => {
      const store = useAppStore();
      expect(store.hasActiveFilters).toBe(false);
      
      store.filters.titleFilter = 'test';
      expect(store.hasActiveFilters).toBe(true);
    });
  });

  describe('Actions', () => {
    it('processCalendar makes API call and updates events', async () => {
      const mockResponse = {
        events: [
          { id: 1, summary: 'Test Event', description: 'Test description' }
        ]
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const store = useAppStore();
      const icsContent = 'mock ics content';
      
      await store.processCalendar(icsContent);

      expect(fetch).toHaveBeenCalledWith('/api/calendars', {
        method: 'POST',
        body: expect.any(FormData)
      });
      expect(store.events).toEqual(mockResponse.events);
      expect(store.loading).toBe(false);
    });

    it('processCalendar handles API errors', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        text: async () => 'Bad request'
      });

      const store = useAppStore();
      
      await store.processCalendar('invalid ics');

      expect(store.error).toContain('Failed to process calendar');
      expect(store.events).toEqual([]);
      expect(store.loading).toBe(false);
    });

    it('processCalendar handles network errors', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const store = useAppStore();
      
      await store.processCalendar('ics content');

      expect(store.error).toContain('Network error');
      expect(store.loading).toBe(false);
    });

    it('updateFilter updates specific filter', () => {
      const store = useAppStore();
      
      store.updateFilter('titleFilter', 'meeting');
      
      expect(store.filters.titleFilter).toBe('meeting');
    });

    it('clearFilters resets all filters', () => {
      const store = useAppStore();
      store.filters.titleFilter = 'test';
      store.filters.descriptionFilter = 'test';
      
      store.clearFilters();
      
      expect(store.filters.titleFilter).toBe('');
      expect(store.filters.descriptionFilter).toBe('');
    });

    it('clearError resets error state', () => {
      const store = useAppStore();
      store.error = 'Some error';
      
      store.clearError();
      
      expect(store.error).toBe(null);
    });

    it('setCurrentView updates current view', () => {
      const store = useAppStore();
      
      store.setCurrentView('calendar');
      
      expect(store.currentView).toBe('calendar');
    });
  });

  describe('Error Handling', () => {
    it('handles malformed JSON response', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      const store = useAppStore();
      
      await store.processCalendar('ics content');

      expect(store.error).toContain('Invalid JSON');
    });

    it('handles empty response', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      });

      const store = useAppStore();
      
      await store.processCalendar('ics content');

      expect(store.events).toEqual([]);
    });
  });
});