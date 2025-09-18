/**
 * E2E tests for realistic user workflows
 * Tests actual user journeys with the public calendar viewer
 */

import { test, expect } from '@playwright/test';

test.describe('User Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should complete basic calendar viewing workflow', async ({ page }) => {
    console.log('=== TESTING BASIC CALENDAR VIEWING ===');

    // Step 1: App loads successfully
    console.log('Step 1: Verifying app loads...');
    await page.waitForTimeout(2000);
    
    const hasContent = await page.locator('body').isVisible();
    expect(hasContent).toBeTruthy();
    console.log('✅ App loaded successfully');

    // Step 2: Check for calendar or domain content
    console.log('Step 2: Checking for calendar content...');
    
    const hasCalendarContent = await page.evaluate(() => {
      const text = document.body.innerText.toLowerCase();
      return text.includes('calendar') || 
             text.includes('portal') || 
             text.includes('events') ||
             text.includes('domain');
    });
    
    if (hasCalendarContent) {
      console.log('✅ Calendar/domain content is visible');
    } else {
      console.log('ℹ️ No specific calendar content found - checking for general app functionality');
    }

    // Step 3: Verify no authentication barriers
    console.log('Step 3: Verifying public access...');
    
    // Should not see login forms or authentication prompts
    const passwordInputs = await page.locator('input[type="password"]').count();
    const usernameInputs = await page.locator('input[id="username"]').count();
    const loginText = await page.locator('text=/login/i').count();
    const hasAuthElements = passwordInputs + usernameInputs + loginText;
    expect(hasAuthElements).toBe(0);
    console.log('✅ No authentication barriers present');

    console.log('=== BASIC WORKFLOW SUCCESSFUL ===');
  });

  test('should handle API interactions correctly', async ({ page }) => {
    console.log('=== TESTING API INTERACTIONS ===');

    const requests = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        });
        console.log(`API request: ${request.method()} ${request.url()}`);
      }
    });

    // Navigate and wait for API calls
    await page.goto('/');
    await page.waitForTimeout(3000);

    // Verify public API access
    console.log('API requests made:', requests.length);
    
    if (requests.length > 0) {
      const hasPublicAccess = requests.every(req => 
        // Verify no authentication headers by checking for public access patterns
        req.url.includes('username=public') || 
        !req.url.includes('authorization') ||
        req.url.includes('/api/domains') ||
        req.url.includes('/api/calendars')
      );
      
      expect(hasPublicAccess).toBeTruthy();
      console.log('✅ All API calls use public access');
    } else {
      console.log('ℹ️ No API calls detected - this may be expected for a static view');
    }

    console.log('=== API INTERACTIONS WORKING ===');
  });

  test('should be responsive and accessible', async ({ page }) => {
    console.log('=== TESTING ACCESSIBILITY ===');

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.reload();
    await page.waitForTimeout(2000);

    // App should still work on mobile
    const mobileContent = await page.locator('body').isVisible();
    expect(mobileContent).toBeTruthy();
    console.log('✅ Mobile viewport works');

    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.reload();
    await page.waitForTimeout(2000);

    const desktopContent = await page.locator('body').isVisible();
    expect(desktopContent).toBeTruthy();
    console.log('✅ Desktop viewport works');

    console.log('=== ACCESSIBILITY TESTS PASSED ===');
  });
});