import { test, expect } from '@playwright/test';

test('Debug AppHeader user prop', async ({ page }) => {
  console.log('=== DEBUGGING APPHEADER USER PROP ===');

  // Navigate to the application
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  // Login with username "Martijn"
  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('Martijn');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  await page.waitForURL('**/home');

  // Add debugging code to the page
  await page.addScriptTag({
    content: `
      // Find Vue app instance and inspect stores
      console.log('=== DEBUGGING USER DATA FLOW ===');
      
      // Check if we can access Vue app
      if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {
        console.log('Vue devtools hook available');
      }
      
      // Look for the user data in DOM attributes or data
      const headerElement = document.querySelector('header, [role="banner"], div');
      if (headerElement) {
        console.log('Header element found');
      }
      
      // Check localStorage directly
      const userFromStorage = localStorage.getItem('user');
      console.log('LocalStorage user:', userFromStorage);
      
      // Try to access Vue component data via element reference
      setTimeout(() => {
        const welcomeElement = document.querySelector('*[class*="username"], span:contains("Welcome"), div:contains("Welcome")');
        console.log('Welcome element found:', welcomeElement?.textContent);
      }, 1000);
    `
  });

  await page.waitForTimeout(2000);

  // Get all console logs
  page.on('console', msg => {
    console.log(`BROWSER: ${msg.text()}`);
  });

  // Check what's in the welcome area specifically
  const welcomeArea = page.locator('text=/Welcome/');
  const welcomeText = await welcomeArea.first().textContent();
  console.log(`Welcome text: "${welcomeText}"`);

  // Check the user object being passed to the component
  const userDataCheck = await page.evaluate(() => {
    // Try to find any Vue component instances
    const elements = document.querySelectorAll('[data-v-*], [class*="v-"]');
    console.log(`Found ${elements.length} Vue elements`);
    
    return {
      localStorage: localStorage.getItem('user'),
      currentUrl: window.location.href
    };
  });
  
  console.log('User data check:', userDataCheck);
  console.log('=== DEBUG COMPLETE ===');
});