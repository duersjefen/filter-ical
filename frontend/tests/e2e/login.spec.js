/**
 * E2E tests to catch login and navigation issues
 * This would have caught the login reload issue!
 */

import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the homepage
    await page.goto('/');
  });

  test('should navigate to login page and back', async ({ page }) => {
    // Check we're on the homepage
    await expect(page).toHaveTitle(/iCal Filter/);
    
    // Look for login button/link
    const loginButton = page.locator('button:has-text("Login"), a:has-text("Login")');
    
    if (await loginButton.count() > 0) {
      // Click login button
      await loginButton.click();
      
      // Should navigate somewhere (not reload the same page)
      await page.waitForTimeout(1000);
      
      // Check URL changed or content changed
      const currentUrl = page.url();
      const hasLoginForm = await page.locator('form, input[type="email"], input[type="password"]').count() > 0;
      
      // Either URL should change OR login form should appear
      expect(
        currentUrl.includes('/login') || hasLoginForm
      ).toBeTruthy();
      
      // Make sure we're not in an infinite reload loop
      let reloadCount = 0;
      page.on('load', () => reloadCount++);
      
      await page.waitForTimeout(2000);
      expect(reloadCount).toBeLessThan(3); // Allow some reloads but not infinite
    }
  });

  test('should be able to use app without login (anonymous)', async ({ page }) => {
    // App should work without login
    await page.goto('/');
    
    // Should see calendars or some content
    await page.waitForTimeout(2000);
    
    // Look for calendar-related content
    const hasContent = await page.locator('text=/calendar|event|subscribe/i').count() > 0 ||
                       await page.locator('[data-testid="calendar"]').count() > 0 ||
                       await page.locator('.calendar').count() > 0;
    
    expect(hasContent).toBeTruthy();
  });

  test('should handle API calls correctly', async ({ page }) => {
    // Monitor network requests
    const apiCalls = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push(request.url());
      }
    });

    // First go to home (will redirect to login)
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Should be on login page now
    const usernameInput = page.locator('input[id="username"]');
    const loginButton = page.locator('button[type="submit"]');
    
    // Login
    await usernameInput.fill('TestUser');
    await loginButton.click();
    
    // Wait for login to complete and redirect to home
    await page.waitForTimeout(3000);

    // Should make API calls to get calendars after login
    expect(apiCalls.some(url => url.includes('/api/calendars'))).toBeTruthy();
  });
});

test.describe('Calendar Functionality', () => {
  test('should display calendars', async ({ page }) => {
    await page.goto('/');
    
    // Wait for app to load
    await page.waitForTimeout(3000);
    
    // Should see some calendar content
    const calendarElements = await page.locator('text=/holiday|calendar/i').count() +
                            await page.locator('.calendar-item').count() + 
                            await page.locator('[data-testid="calendar"]').count();
    
    expect(calendarElements).toBeGreaterThan(0);
  });
});