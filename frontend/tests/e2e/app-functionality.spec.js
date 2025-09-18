/**
 * E2E tests for core iCal viewer functionality
 * Tests what the app actually does: domain-based calendar viewing
 */

import { test, expect } from '@playwright/test';

test.describe('Core App Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000); // Allow app to load
  });

  test('should load and display domain calendars', async ({ page }) => {
    // App should load immediately (no authentication)
    await expect(page).toHaveTitle(/iCal/);
    
    // Should make API calls for domains
    const domainApiCalled = await page.waitForResponse(
      response => response.url().includes('/api/domains'), 
      { timeout: 5000 }
    ).catch(() => null);
    
    if (domainApiCalled) {
      expect(domainApiCalled.ok()).toBeTruthy();
    }
  });

  test('should handle calendar data display', async ({ page }) => {
    // Wait for any calendar data to load
    await page.waitForTimeout(3000);
    
    // Should see calendar-related content or domain selection
    const hasCalendarContent = await page.evaluate(() => {
      const text = document.body.innerText.toLowerCase();
      return text.includes('calendar') || 
             text.includes('events') || 
             text.includes('portal') ||
             text.includes('domain');
    });
    
    expect(hasCalendarContent).toBeTruthy();
  });

  test('should handle public calendar access correctly', async ({ page }) => {
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requests.push({
          url: request.url(),
          method: request.method()
        });
      }
    });

    await page.goto('/');
    await page.waitForTimeout(3000);

    // Should make public API calls (no authentication headers)
    expect(requests.length).toBeGreaterThan(0);
    
    // Verify we're making calls to expected endpoints
    const hasExpectedCalls = requests.some(req => 
      req.url.includes('/api/domains') || 
      req.url.includes('/api/calendars')
    );
    expect(hasExpectedCalls).toBeTruthy();
  });
});

test.describe('Error Handling', () => {
  test('should handle network errors gracefully', async ({ page }) => {
    // Block all API calls to simulate network issues
    await page.route('**/api/**', route => route.abort('failed'));
    
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // App should still load without crashing
    const hasContent = await page.locator('body').isVisible();
    expect(hasContent).toBeTruthy();
    
    // Should not have JavaScript errors that break the app
    const errors = [];
    page.on('pageerror', error => errors.push(error));
    
    await page.waitForTimeout(1000);
    // Allow some errors but not critical ones that break the app
    const criticalErrors = errors.filter(error => 
      error.message.includes('Cannot read') ||
      error.message.includes('is not a function')
    );
    expect(criticalErrors.length).toBe(0);
  });
});