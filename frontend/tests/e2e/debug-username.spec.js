import { test, expect } from '@playwright/test';

test('Debug username display issue', async ({ page }) => {
  console.log('=== DEBUGGING USERNAME DISPLAY ===');

  // Navigate to the application
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  // Login with username "Martijn"
  console.log('Logging in with username "Martijn"...');
  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('Martijn');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  // Wait for navigation to home page
  await page.waitForURL('**/home');
  console.log('✅ Successfully navigated to home page');

  // Take a screenshot for debugging
  await page.screenshot({ path: 'debug-home-page.png', fullPage: true });

  // Log all text content on the page
  const bodyText = await page.locator('body').textContent();
  console.log('=== FULL PAGE TEXT CONTENT ===');
  console.log(bodyText);
  console.log('=== END PAGE TEXT ===');

  // Check for any Welcome text
  const welcomeElements = page.locator('text=/Welcome/i');
  const welcomeCount = await welcomeElements.count();
  console.log(`Found ${welcomeCount} elements containing "Welcome"`);
  
  if (welcomeCount > 0) {
    for (let i = 0; i < welcomeCount; i++) {
      const welcomeText = await welcomeElements.nth(i).textContent();
      console.log(`Welcome element ${i}: "${welcomeText}"`);
    }
  }

  // Check header area specifically
  const headerArea = page.locator('header, [role="banner"], .header, div:has-text("Welcome")').first();
  if (await headerArea.count() > 0) {
    const headerText = await headerArea.textContent();
    console.log(`Header area text: "${headerText}"`);
  }

  // Look for user info display
  const userInfoElements = page.locator('[class*="user"], [class*="username"], span:has-text("Martijn"), div:has-text("Martijn")');
  const userInfoCount = await userInfoElements.count();
  console.log(`Found ${userInfoCount} elements that might contain user info`);
  
  if (userInfoCount > 0) {
    for (let i = 0; i < userInfoCount; i++) {
      const userText = await userInfoElements.nth(i).textContent();
      console.log(`User info element ${i}: "${userText}"`);
    }
  }

  console.log('=== DEBUG COMPLETE ===');
});