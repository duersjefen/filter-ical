/**
 * Tests for Domain Store
 * Handles domain management and groups functionality
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useDomainStore } from '../../src/stores/domain.js';

// Mock useHTTP composable
const mockGet = vi.fn();
vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    get: mockGet
  })
}));

describe('Domain Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('has correct initial state', () => {
      const store = useDomainStore();

      expect(store.availableDomains).toEqual([]);
      expect(store.groups).toEqual({});
    });
  });

  describe('fetchAvailableDomains', () => {
    it('fetches available domains successfully', async () => {
      const mockDomains = [
        { domain_key: 'test', name: 'Test Domain', group_count: 5 },
        { domain_key: 'demo', name: 'Demo Domain', group_count: 3 }
      ];

      mockGet.mockResolvedValueOnce({
        success: true,
        data: mockDomains
      });

      const store = useDomainStore();
      const result = await store.fetchAvailableDomains();

      expect(result.success).toBe(true);
      expect(store.availableDomains).toEqual(mockDomains);
      expect(mockGet).toHaveBeenCalled();
    });

    it('handles API errors gracefully', async () => {
      mockGet.mockResolvedValueOnce({
        success: false,
        error: 'Server error'
      });

      const store = useDomainStore();
      const result = await store.fetchAvailableDomains();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Server error');
      expect(store.availableDomains).toEqual([]);
    });

    it('handles network errors gracefully', async () => {
      mockGet.mockRejectedValueOnce(new Error('Network failed'));

      const store = useDomainStore();
      const result = await store.fetchAvailableDomains();

      expect(result.success).toBe(false);
      expect(result.error).toBe('Failed to load domains');
      expect(store.availableDomains).toEqual([]);
    });
  });

  describe('loadDomainGroups', () => {
    it('loads domain groups successfully', async () => {
      const mockDomainData = {
        domain_key: 'test',
        groups: [
          {
            id: '1',
            name: 'Group 1',
            description: 'Test group',
            recurring_events: [
              {
                title: 'Meeting',
                event_count: 5,
                events: [
                  { id: 1, title: 'Meeting', start: '2024-01-01' }
                ]
              }
            ]
          },
          {
            id: '2',
            name: 'Group 2',
            description: 'Another group',
            recurring_events: []
          }
        ]
      };

      mockGet.mockResolvedValueOnce({
        success: true,
        data: mockDomainData
      });

      const store = useDomainStore();
      const result = await store.loadDomainGroups('test');

      expect(result.success).toBe(true);
      expect(store.groups).toHaveProperty('1');
      expect(store.groups).toHaveProperty('2');
      expect(store.groups['1'].name).toBe('Group 1');
      expect(store.groups['2'].name).toBe('Group 2');
    });

    it('handles empty groups data', async () => {
      mockGet.mockResolvedValueOnce({
        success: true,
        data: { groups: [] }
      });

      const store = useDomainStore();
      const result = await store.loadDomainGroups('test');

      expect(result.success).toBe(true);
      expect(store.groups).toEqual({});
    });
  });

  describe('Computed Properties', () => {
    it('isDomainCalendar returns true when groups exist', () => {
      const store = useDomainStore();
      store.groups = {
        '1': { id: '1', name: 'Group 1', recurring_events: [] }
      };

      expect(store.isDomainCalendar).toBe(true);
    });

    it('isDomainCalendar returns false when no groups exist', () => {
      const store = useDomainStore();
      store.groups = {};

      expect(store.isDomainCalendar).toBe(false);
    });

    it('hasCustomGroups returns true for custom (non-auto) groups', () => {
      const store = useDomainStore();
      store.groups = {
        '1': { id: '1', name: 'Custom Group' },
        '9998': { id: '9998', name: 'Auto Group 1' },
        '9999': { id: '9999', name: 'Auto Group 2' }
      };

      expect(store.hasCustomGroups).toBe(true);
    });

    it('hasCustomGroups returns false when only auto-groups exist', () => {
      const store = useDomainStore();
      store.groups = {
        '9998': { id: '9998', name: 'Auto Group 1' },
        '9999': { id: '9999', name: 'Auto Group 2' }
      };

      expect(store.hasCustomGroups).toBe(false);
    });

    it('hasCustomGroups returns false when no groups exist', () => {
      const store = useDomainStore();
      store.groups = {};

      expect(store.hasCustomGroups).toBe(false);
    });
  });

  describe('allEventsFromGroups', () => {
    it('extracts events from groups structure', () => {
      const store = useDomainStore();
      store.groups = {
        '1': {
          id: '1',
          name: 'Group 1',
          recurring_events: [
            {
              title: 'Meeting',
              events: [
                { id: 1, title: 'Meeting', start: '2024-01-01' },
                { id: 2, title: 'Meeting', start: '2024-01-02' }
              ]
            }
          ]
        },
        '2': {
          id: '2',
          name: 'Group 2',
          recurring_events: [
            {
              title: 'Workshop',
              events: [
                { id: 3, title: 'Workshop', start: '2024-01-03' }
              ]
            }
          ]
        }
      };

      expect(store.allEventsFromGroups).toHaveLength(3);
      expect(store.allEventsFromGroups[0].title).toBe('Meeting');
      expect(store.allEventsFromGroups[2].title).toBe('Workshop');
    });

    it('deduplicates events by UID', () => {
      const store = useDomainStore();
      store.groups = {
        '1': {
          recurring_events: [
            {
              title: 'Meeting',
              events: [
                { id: 1, uid: 'event-1', title: 'Meeting', start: '2024-01-01' },
                { id: 2, uid: 'event-1', title: 'Meeting', start: '2024-01-01' }
              ]
            }
          ]
        }
      };

      expect(store.allEventsFromGroups).toHaveLength(1);
    });

    it('deduplicates events by content when no UID', () => {
      const store = useDomainStore();
      store.groups = {
        '1': {
          recurring_events: [
            {
              title: 'Meeting',
              events: [
                { id: 1, title: 'Meeting', start: '2024-01-01', end: '2024-01-01' },
                { id: 2, title: 'Meeting', start: '2024-01-01', end: '2024-01-01' }
              ]
            }
          ]
        }
      };

      expect(store.allEventsFromGroups).toHaveLength(1);
    });

    it('returns empty array when no groups', () => {
      const store = useDomainStore();
      store.groups = {};

      expect(store.allEventsFromGroups).toEqual([]);
    });
  });
});
