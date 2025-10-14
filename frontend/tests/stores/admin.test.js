/**
 * Tests for Admin Store - Token Expiry & Error Handling
 * Tests authentication, token validation, and session management
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAdminStore } from '../../src/stores/admin.js';

// Mock fetch globally
global.fetch = vi.fn();

// Mock localStorage with actual storage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => { store[key] = value.toString(); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

global.localStorage = localStorageMock;

describe('Admin Store - Token Management', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Token Expiry Detection', () => {
    it('detects expired token', () => {
      const store = useAdminStore();

      // Create an expired JWT token (exp is in the past)
      const expiredPayload = {
        role: 'global_admin',
        iat: Math.floor(Date.now() / 1000) - 86400, // 1 day ago
        exp: Math.floor(Date.now() / 1000) - 3600   // Expired 1 hour ago
      };

      // Create fake JWT (header.payload.signature)
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify(expiredPayload));
      const expiredToken = `${header}.${payload}.fake_signature`;

      // Set expired token
      store.setAdminToken(expiredToken);

      // Verify token is detected as expired
      expect(store.isTokenExpired()).toBe(true);
    });

    it('detects valid (non-expired) token', () => {
      const store = useAdminStore();

      // Create a valid JWT token (exp is in the future)
      const validPayload = {
        role: 'global_admin',
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 86400 // Expires in 1 day
      };

      // Create fake JWT
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const payload = btoa(JSON.stringify(validPayload));
      const validToken = `${header}.${payload}.fake_signature`;

      // Set valid token
      store.setAdminToken(validToken);

      // Verify token is NOT expired
      expect(store.isTokenExpired()).toBe(false);
    });

    it('detects invalid token format as expired', () => {
      const store = useAdminStore();

      // Set malformed token
      store.setAdminToken('invalid.token.format');

      // Verify invalid token is treated as expired
      expect(store.isTokenExpired()).toBe(true);
    });

    it('treats missing token as expired', () => {
      const store = useAdminStore();

      // No token set
      expect(store.adminToken).toBe(null);

      // Verify missing token is treated as expired
      expect(store.isTokenExpired()).toBe(true);
    });
  });

  describe('Token Storage', () => {
    it('persists token to localStorage', () => {
      const store = useAdminStore();
      const testToken = 'test.jwt.token';

      store.setAdminToken(testToken);

      expect(localStorage.getItem('admin_token')).toBe(testToken);
      expect(store.adminToken).toBe(testToken);
    });

    it('removes token from localStorage on logout', () => {
      const store = useAdminStore();
      const testToken = 'test.jwt.token';

      store.setAdminToken(testToken);
      expect(localStorage.getItem('admin_token')).toBe(testToken);

      store.logout();

      expect(localStorage.getItem('admin_token')).toBe(null);
      expect(store.adminToken).toBe(null);
    });

    it('loads token from localStorage on initialization', () => {
      const testToken = 'test.jwt.token';
      localStorage.setItem('admin_token', testToken);

      const store = useAdminStore();

      expect(store.adminToken).toBe(testToken);
    });
  });

  describe('Authentication Error Handling', () => {
    it('clears token on "Invalid token" error', async () => {
      const store = useAdminStore();
      const validToken = 'test.jwt.token';
      store.setAdminToken(validToken);

      // Mock 401 response with "Invalid token" error
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid token' })
      });

      // Attempt to list configs
      try {
        await store.listDomainConfigs();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toContain('session has expired');
        expect(store.adminToken).toBe(null);
        expect(localStorage.getItem('admin_token')).toBe(null);
      }
    });

    it('clears token on "Token has expired" error', async () => {
      const store = useAdminStore();
      const validToken = 'test.jwt.token';
      store.setAdminToken(validToken);

      // Mock 401 response with "Token has expired" error
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Token has expired' })
      });

      // Attempt to list configs
      try {
        await store.listDomainConfigs();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toContain('session has expired');
        expect(store.adminToken).toBe(null);
      }
    });

    it('preserves token on non-auth errors', async () => {
      const store = useAdminStore();
      const validToken = 'test.jwt.token';
      store.setAdminToken(validToken);

      // Mock 500 response (server error, not auth error)
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' })
      });

      // Attempt to list configs
      try {
        await store.listDomainConfigs();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toBe('Internal server error');
        // Token should NOT be cleared for non-auth errors
        expect(store.adminToken).toBe(validToken);
      }
    });
  });

  describe('Login Flow', () => {
    it('saves token on successful login', async () => {
      const store = useAdminStore();
      const mockToken = 'new.jwt.token';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: mockToken, expires_in_days: 30 })
      });

      const result = await store.login('correct_password');

      expect(result.token).toBe(mockToken);
      expect(store.adminToken).toBe(mockToken);
      expect(localStorage.getItem('admin_token')).toBe(mockToken);
    });

    it('throws error on failed login', async () => {
      const store = useAdminStore();

      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid admin password' })
      });

      try {
        await store.login('wrong_password');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.message).toBe('Invalid admin password');
        expect(store.adminToken).toBe(null);
      }
    });
  });

  describe('API Calls with Auth Headers', () => {
    it('includes Authorization header when token exists', async () => {
      const store = useAdminStore();
      const testToken = 'test.jwt.token';
      store.setAdminToken(testToken);

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ configs: [] })
      });

      await store.listDomainConfigs();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${testToken}`
          })
        })
      );
    });

    it('does not include Authorization header when no token', async () => {
      const store = useAdminStore();

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: 'new.token' })
      });

      await store.login('password');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.not.objectContaining({
            'Authorization': expect.anything()
          })
        })
      );
    });
  });
});
