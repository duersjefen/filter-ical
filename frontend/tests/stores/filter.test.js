/**
 * Tests for Filter Store
 * Handles filters, filtered calendars, and iCal generation
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useFilterStore } from '../../src/stores/filter.js';

// Mock useHTTP composable
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockDel = vi.fn();
vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    get: mockGet,
    post: mockPost,
    del: mockDel
  })
}));

// Mock useUsername composable
const mockGetUserId = vi.fn(() => 'testuser');
vi.mock('../../src/composables/useUsername', () => ({
  useUsername: () => ({
    getUserId: mockGetUserId
  })
}));

describe('Filter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mockGetUserId.mockReturnValue('testuser');
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const store = useFilterStore();

      expect(store.savedFilters).toEqual([]);
      expect(store.userDomainFilters).toEqual([]);
      expect(store.filteredCalendars).toEqual([]);
    });
  });

  describe('fetchFilters', () => {
    it('returns success with empty filters (not implemented yet)', async () => {
      const store = useFilterStore();
      const result = await store.fetchFilters();

      expect(result.success).toBe(true);
      expect(result.data.filters).toEqual([]);
    });
  });

  describe('fetchUserFilters', () => {
    it('fetches user filters for logged-in user', async () => {
      const mockFilters = [
        { id: 1, domain_key: 'test', name: 'Test Filter' },
        { id: 2, domain_key: 'demo', name: 'Demo Filter' }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: mockFilters
      });

      const store = useFilterStore();
      const result = await store.fetchUserFilters();

      expect(result.success).toBe(true);
      expect(store.userDomainFilters).toEqual(mockFilters);
    });

    it('returns empty filters for anonymous users', async () => {
      mockGetUserId.mockReturnValue('anon_12345');

      mockGet.mockResolvedValueOnce({
        success: true,
        data: []
      });

      const store = useFilterStore();
      const result = await store.fetchUserFilters();

      expect(result.success).toBe(true);
      expect(store.userDomainFilters).toEqual([]);
    });

    it('handles API errors gracefully', async () => {
      mockGet.mockResolvedValueOnce({
        success: false,
        error: 'Server error'
      });

      const store = useFilterStore();
      const result = await store.fetchUserFilters();

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to fetch filters');
      expect(store.userDomainFilters).toEqual([]);
    });
  });

  describe('domainsWithFilters computed', () => {
    it('extracts unique domains from user filters', () => {
      const store = useFilterStore();
      store.userDomainFilters = [
        { id: 1, domain_key: 'test', name: 'Filter 1' },
        { id: 2, domain_key: 'test', name: 'Filter 2' },
        { id: 3, domain_key: 'demo', name: 'Filter 3' }
      ];

      expect(store.domainsWithFilters).toHaveLength(2);
      expect(store.domainsWithFilters[0].domain_key).toBe('test');
      expect(store.domainsWithFilters[0].filter_count).toBe(2);
      expect(store.domainsWithFilters[1].domain_key).toBe('demo');
      expect(store.domainsWithFilters[1].filter_count).toBe(1);
    });

    it('returns empty array when no filters exist', () => {
      const store = useFilterStore();
      store.userDomainFilters = [];

      expect(store.domainsWithFilters).toEqual([]);
    });

    it('handles null userDomainFilters gracefully', () => {
      const store = useFilterStore();
      store.userDomainFilters = null;

      expect(store.domainsWithFilters).toEqual([]);
    });
  });

  describe('saveFilter', () => {
    it('creates and saves a new filter', async () => {
      const store = useFilterStore();
      const config = { selectedRecurringEvents: ['Meeting', 'Workshop'] };

      const result = await store.saveFilter('My Filter', config);

      expect(result.success).toBe(true);
      expect(store.savedFilters).toHaveLength(1);
      expect(store.savedFilters[0].name).toBe('My Filter');
      expect(store.savedFilters[0].config).toEqual(config);
    });

    it('generates default name if not provided', async () => {
      const store = useFilterStore();
      const config = { selectedRecurringEvents: ['Meeting'] };

      const result = await store.saveFilter('', config);

      expect(result.success).toBe(true);
      expect(store.savedFilters[0].name).toContain('Filter 1 types');
    });
  });

  describe('deleteFilter', () => {
    it('deletes a filter by ID', async () => {
      const store = useFilterStore();
      store.savedFilters = [
        { id: 'filter_1', name: 'Filter 1' },
        { id: 'filter_2', name: 'Filter 2' }
      ];

      const result = await store.deleteFilter('filter_1');

      expect(result.success).toBe(true);
      expect(store.savedFilters).toHaveLength(1);
      expect(store.savedFilters[0].id).toBe('filter_2');
    });

    it('handles filter not found', async () => {
      const store = useFilterStore();
      store.savedFilters = [];

      const result = await store.deleteFilter('nonexistent');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Filter not found');
    });
  });

  describe('loadFilteredCalendars', () => {
    it('returns empty list (not implemented yet)', async () => {
      const store = useFilterStore();
      const result = await store.loadFilteredCalendars();

      expect(result.success).toBe(true);
      expect(result.data).toEqual([]);
      expect(store.filteredCalendars).toEqual([]);
    });
  });

  describe('createFilteredCalendar', () => {
    it('returns not implemented error', async () => {
      const store = useFilterStore();
      const result = await store.createFilteredCalendar(1, 'Test', {});

      expect(result.success).toBe(false);
      expect(result.error).toContain('not yet implemented');
    });

    it('validates name is provided', async () => {
      const store = useFilterStore();
      const result = await store.createFilteredCalendar(1, '', {});

      expect(result.success).toBe(false);
      expect(result.error).toBe('Name is required');
    });
  });

  describe('updateFilteredCalendar', () => {
    it('returns not implemented error', async () => {
      const store = useFilterStore();
      const result = await store.updateFilteredCalendar(1, { name: 'Updated' });

      expect(result.success).toBe(false);
      expect(result.error).toContain('not yet implemented');
    });

    it('validates calendar ID is provided', async () => {
      const store = useFilterStore();
      const result = await store.updateFilteredCalendar(null, {});

      expect(result.success).toBe(false);
      expect(result.error).toBe('Calendar ID is required');
    });
  });

  describe('deleteFilteredCalendar', () => {
    it('returns not implemented error', async () => {
      const store = useFilterStore();
      const result = await store.deleteFilteredCalendar(1);

      expect(result.success).toBe(false);
      expect(result.error).toContain('not yet implemented');
    });

    it('validates calendar ID is provided', async () => {
      const store = useFilterStore();
      const result = await store.deleteFilteredCalendar(null);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Calendar ID is required');
    });
  });

  describe('generateIcal', () => {
    it('generates iCal using filter workflow', async () => {
      const mockFilter = { link_uuid: 'test-uuid-123' };
      const mockIcalData = 'BEGIN:VCALENDAR\nEND:VCALENDAR';

      mockPost.mockResolvedValueOnce({
        success: true,
        data: mockFilter
      });

      mockGet.mockResolvedValueOnce({
        success: true,
        data: mockIcalData
      });

      const store = useFilterStore();
      const result = await store.generateIcal({
        calendarId: 1,
        selectedRecurringEvents: ['Meeting']
      });

      expect(result.success).toBe(true);
      expect(mockPost).toHaveBeenCalled();
      expect(mockGet).toHaveBeenCalled();
    });

    it('handles filter creation failure', async () => {
      mockPost.mockResolvedValueOnce({
        success: false,
        error: 'Failed to create filter'
      });

      const store = useFilterStore();
      const result = await store.generateIcal({
        calendarId: 1,
        selectedRecurringEvents: []
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to create filter');
    });

    it('handles missing link_uuid in filter response', async () => {
      mockPost.mockResolvedValueOnce({
        success: true,
        data: { id: 1 }
      });

      const store = useFilterStore();
      const result = await store.generateIcal({
        calendarId: 1,
        selectedRecurringEvents: []
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to create filter');
    });

    it('handles exceptions during generation', async () => {
      mockPost.mockRejectedValueOnce(new Error('Network error'));

      const store = useFilterStore();
      const result = await store.generateIcal({
        calendarId: 1,
        selectedRecurringEvents: []
      });

      expect(result.success).toBe(false);
      expect(result.error).toContain('Failed to generate iCal');
    });
  });
});
