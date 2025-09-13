import { test, expect } from '@playwright/test';

test('Debug calendar data flow in real workflow', async ({ page }) => {
  // Enable browser console logging  
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  
  // Navigate to home page (should handle redirects automatically)
  await page.goto('http://localhost:8000');
  
  // Wait for page to load
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
  
  console.log('Current URL:', page.url());
  
  // Try to find username input (this tells us if we're on login page)
  const hasUsernameInput = await page.locator('input#username').isVisible();
  console.log('On login page:', hasUsernameInput);
  
  if (hasUsernameInput) {
    // Login with test user
    await page.fill('input#username', 'testuser');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to home page
    await page.waitForURL('**/home');
    await page.waitForTimeout(1000);
  }
  
  console.log('After login - Current URL:', page.url());
  
  // Wait for calendars to load
  console.log('Waiting for calendars to load...');
  await page.waitForTimeout(3000);
  
  // Check what's visible on the home page
  const hasLoadingSpinner = await page.locator('.animate-spin').isVisible();
  const hasNoCalendarsMessage = await page.locator('text=No calendars found').isVisible();
  const calendarSection = await page.locator('h2:has-text("Your Calendars")').isVisible();
  
  console.log('Loading spinner visible:', hasLoadingSpinner);
  console.log('No calendars message visible:', hasNoCalendarsMessage);
  console.log('Calendar section visible:', calendarSection);
  
  // Look for "View Events" buttons (try both mobile and desktop)
  const mobileButtons = await page.locator('.sm\\:hidden button:has-text("View Events")');
  const desktopButtons = await page.locator('.hidden.sm\\:block button:has-text("View Events")');
  const allButtons = await page.locator('button:has-text("View Events")');
  
  const mobileCount = await mobileButtons.count();
  const desktopCount = await desktopButtons.count();
  const totalCount = await allButtons.count();
  
  console.log('Mobile buttons:', mobileCount);
  console.log('Desktop buttons:', desktopCount);  
  console.log('Total buttons:', totalCount);
  
  if (totalCount > 0) {
    // Click on desktop button (should be visible on most screen sizes)
    if (desktopCount > 0) {
      console.log('Clicking first desktop View Events button...');
      await desktopButtons.first().click();
    } else if (mobileCount > 0) {
      console.log('Clicking first mobile View Events button...');
      await mobileButtons.first().click();
    } else {
      console.log('No visible buttons found');
    }
    
    // Wait for navigation to calendar page
    await page.waitForTimeout(3000);
    
    console.log('After calendar click - Current URL:', page.url());
    
    // Check what's displayed on the page
    const hasLoadingState = await page.locator('text=Loading events').isVisible();
    const hasNoEventsMessage = await page.locator('text=No events found').isVisible();
    const hasMainContent = await page.locator('.text-lg.font-semibold').first().isVisible();
    
    console.log('Loading state visible:', hasLoadingState);
    console.log('No events message visible:', hasNoEventsMessage);  
    console.log('Main content visible:', hasMainContent);
    
    // Add debug logging to the component
    const debugInfo = await page.evaluate(() => {
      // Try to access Vue component data through dev tools or global variables
      return {
        location: window.location.href,
        userAgent: navigator.userAgent,
        // These may not be available in production
        vue: typeof window.Vue !== 'undefined',
        vueDevtools: typeof window.__VUE_DEVTOOLS_GLOBAL_HOOK__ !== 'undefined'
      };
    });
    
    console.log('Debug info:', debugInfo);
    
    // Take a screenshot for visual debugging
    await page.screenshot({ path: 'debug-calendar-data-flow.png' });
    
    // Wait longer to see if content eventually loads
    console.log('Waiting for content to potentially load...');
    await page.waitForTimeout(5000);
    
    // Final check
    const finalCheck = {
      hasLoadingState: await page.locator('text=Loading events').isVisible(),
      hasNoEventsMessage: await page.locator('text=No events found').isVisible(),
      hasMainContent: await page.locator('.text-lg.font-semibold').first().isVisible(),
      currentURL: page.url()
    };
    
    console.log('Final check:', finalCheck);
    
    // Try to find any error messages or debug info in the page
    const pageText = await page.textContent('body');
    if (pageText && pageText.includes('error')) {
      console.log('Page contains error text');
    }
    
  } else {
    console.log('No calendar cards found');
    const bodyText = await page.textContent('body');
    console.log('Page body text:', bodyText.substring(0, 500));
  }
});