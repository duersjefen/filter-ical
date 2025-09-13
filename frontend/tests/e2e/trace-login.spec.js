import { test, expect } from '@playwright/test';

test('Trace login data flow', async ({ page }) => {
  console.log('=== TRACING LOGIN DATA FLOW ===');

  // Navigate to the application
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  console.log('1. On login page, checking form...');

  // Check initial form state
  const usernameInput = page.locator('input[id="username"]');
  const initialValue = await usernameInput.inputValue();
  console.log(`Initial username input value: "${initialValue}"`);

  // Fill in the username
  console.log('2. Filling username with "Martijn"...');
  await usernameInput.fill('Martijn');
  
  const afterFillValue = await usernameInput.inputValue();
  console.log(`After fill, username input value: "${afterFillValue}"`);

  // Add a console log listener to see what happens in the browser
  page.on('console', msg => {
    if (msg.type() === 'log') {
      console.log(`BROWSER LOG: ${msg.text()}`);
    }
  });

  // Click login
  console.log('3. Clicking login button...');
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  // Wait for navigation
  await page.waitForURL('**/home', { timeout: 10000 });
  console.log('4. Successfully navigated to home page');

  // Wait for page to settle
  await page.waitForTimeout(1000);

  // Look for welcome text
  const welcomeText = await page.locator('text=/Welcome/i').first().textContent();
  console.log(`5. Welcome text displayed: "${welcomeText}"`);

  // Check localStorage to see what was stored
  const localStorage = await page.evaluate(() => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  });
  console.log('6. LocalStorage user data:', JSON.stringify(localStorage));

  console.log('=== TRACE COMPLETE ===');
});