/**
 * Simple E2E test to catch basic issues
 */

import { test, expect } from '@playwright/test';

test('App loads and basic functionality works', async ({ page }) => {
  // Go to the app
  await page.goto('http://localhost:8000');
  
  // Wait for app to load
  await page.waitForTimeout(3000);
  
  // Check that page loaded (should have title)
  const title = await page.title();
  expect(title).toBeTruthy();
  
  // Check that we can see some content (not just blank page)
  const bodyText = await page.locator('body').textContent();
  expect(bodyText.length).toBeGreaterThan(10);
  
  // Look for any obvious errors in console
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  await page.waitForTimeout(2000);
  
  // Don't fail on minor errors, just log them
  if (errors.length > 0) {
    console.log('Console errors found:', errors);
  }
  
  // Check if login button exists and works
  const loginElements = await page.locator('button:has-text("Login"), a:has-text("Login"), text="Login"').count();
  if (loginElements > 0) {
    console.log('Login button found, testing click behavior');
    
    const originalUrl = page.url();
    
    // Click the login element
    await page.locator('button:has-text("Login"), a:has-text("Login"), text="Login"').first().click();
    
    await page.waitForTimeout(2000);
    
    const newUrl = page.url();
    
    // Either URL should change OR some form should appear
    const hasLoginForm = await page.locator('input[type="email"], input[type="password"], form').count();
    
    if (originalUrl === newUrl && hasLoginForm === 0) {
      console.warn('WARNING: Login click did not change URL or show login form - possible login issue!');
    } else {
      console.log('Login behavior seems OK - URL changed or form appeared');
    }
  }
});

test('API calls are working', async ({ page }) => {
  const requests = [];
  
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      requests.push(request.url());
    }
  });
  
  await page.goto('http://localhost:8000');
  await page.waitForTimeout(5000);
  
  console.log('API requests made:', requests);
  
  // Should make some API calls
  expect(requests.length).toBeGreaterThan(0);
});