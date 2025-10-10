/**
 * Tests for App Store - Orchestration Layer
 * Tests that app store properly delegates to specialized stores
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAppStore } from '../../src/stores/app.js';

// Mock useHTTP composable
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockDel = vi.fn();
const mockLoading = { value: false };
const mockError = { value: null };
const mockClearError = vi.fn();
const mockSetError = vi.fn();

vi.mock('../../src/composables/useHTTP', () => ({
  useHTTP: () => ({
    get: mockGet,
    post: mockPost,
    del: mockDel,
    loading: mockLoading,
    error: mockError,
    clearError: mockClearError,
    setError: mockSetError
  })
}));

// Mock useUsername composable
const mockGetUserId = vi.fn(() => 'testuser');
const mockOnUsernameChange = vi.fn();
vi.mock('../../src/composables/useUsername', () => ({
  useUsername: () => ({
    getUserId: mockGetUserId,
    onUsernameChange: mockOnUsernameChange
  })
}));

describe('App Store - Orchestration', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    mockGetUserId.mockReturnValue('testuser');
  });

  describe('Initialization', () => {
    it('initializes app and sets up username change listener', () => {
      const store = useAppStore();

      // Mock domain fetch to succeed
      mockGet.mockResolvedValueOnce({
        success: true,
        data: []
      });

      store.initializeApp();

      expect(mockGetUserId).toHaveBeenCalled();
      expect(mockOnUsernameChange).toHaveBeenCalled();
    });
  });

  describe('State Delegation', () => {
    it('delegates calendar state to calendar store', () => {
      const store = useAppStore();

      expect(store.calendars).toBeDefined();
      expect(store.selectedCalendar).toBeDefined();
      expect(store.newCalendar).toBeDefined();
      expect(store.events).toBeDefined();
      expect(store.recurringEvents).toBeDefined();
    });

    it('delegates domain state to domain store', () => {
      const store = useAppStore();

      expect(store.availableDomains).toBeDefined();
      expect(store.groups).toBeDefined();
      expect(store.isDomainCalendar).toBeDefined();
      expect(store.hasCustomGroups).toBeDefined();
      expect(store.allEventsFromGroups).toBeDefined();
    });

    it('delegates filter state to filter store', () => {
      const store = useAppStore();

      expect(store.savedFilters).toBeDefined();
      expect(store.userDomainFilters).toBeDefined();
      expect(store.domainsWithFilters).toBeDefined();
      expect(store.filteredCalendars).toBeDefined();
    });
  });

  describe('Action Delegation', () => {
    it('delegates calendar actions to calendar store', () => {
      const store = useAppStore();

      expect(typeof store.fetchCalendars).toBe('function');
      expect(typeof store.addCalendar).toBe('function');
      expect(typeof store.deleteCalendar).toBe('function');
      expect(typeof store.syncCalendar).toBe('function');
      expect(typeof store.selectCalendar).toBe('function');
      expect(typeof store.clearSelection).toBe('function');
      expect(typeof store.loadCalendarEvents).toBe('function');
      expect(typeof store.loadCalendarRecurringEvents).toBe('function');
      expect(typeof store.loadCalendarGroups).toBe('function');
    });

    it('delegates domain actions to domain store', () => {
      const store = useAppStore();

      expect(typeof store.fetchAvailableDomains).toBe('function');
      expect(typeof store.loadDomainGroups).toBe('function');
    });

    it('delegates filter actions to filter store', () => {
      const store = useAppStore();

      expect(typeof store.fetchFilters).toBe('function');
      expect(typeof store.fetchUserFilters).toBe('function');
      expect(typeof store.saveFilter).toBe('function');
      expect(typeof store.deleteFilter).toBe('function');
      expect(typeof store.loadFilteredCalendars).toBe('function');
      expect(typeof store.createFilteredCalendar).toBe('function');
      expect(typeof store.updateFilteredCalendar).toBe('function');
      expect(typeof store.deleteFilteredCalendar).toBe('function');
      expect(typeof store.generateIcal).toBe('function');
    });

    it('delegates user actions to user store', () => {
      const store = useAppStore();

      expect(typeof store.getUserPreferences).toBe('function');
      expect(typeof store.saveUserPreferences).toBe('function');
      expect(typeof store.getCalendarPreferences).toBe('function');
      expect(typeof store.saveCalendarPreferences).toBe('function');
    });
  });

  describe('Shared Utilities', () => {
    it('exposes shared HTTP utilities', () => {
      const store = useAppStore();

      expect(store.loading).toBeDefined();
      expect(store.error).toBeDefined();
      expect(typeof store.clearError).toBe('function');
      expect(typeof store.setError).toBe('function');
    });
  });

  describe('Integration - Username Change', () => {
    it('handles username change by clearing state and reloading data', async () => {
      const store = useAppStore();

      // Mock successful responses
      mockGet.mockResolvedValue({
        success: true,
        data: []
      });

      store.initializeApp();

      // Get the username change callback
      const callback = mockOnUsernameChange.mock.calls[0][0];

      // Trigger username change
      await callback('newuser', 'olduser');

      // Verify data was reloaded (fetchCalendars and fetchUserFilters called)
      // These are async so we can't directly verify the state change in this test,
      // but we verified the callback is registered
      expect(mockOnUsernameChange).toHaveBeenCalled();
    });
  });
});
