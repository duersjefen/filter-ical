import { test, expect } from '@playwright/test';

test('Debug calendar events display', async ({ page }) => {
  // Enable browser console logging  
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  
  // Start intercepting network calls
  let eventsResponse = null;
  let categoriesResponse = null;
  
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('/events')) {
      try {
        eventsResponse = await response.json();
        console.log('EVENTS API RESPONSE:', JSON.stringify(eventsResponse, null, 2));
      } catch (e) {
        console.log('EVENTS API - Failed to parse JSON:', await response.text());
      }
    }
    if (url.includes('/categories')) {
      try {
        categoriesResponse = await response.json();  
        console.log('CATEGORIES API RESPONSE:', JSON.stringify(categoriesResponse, null, 2));
      } catch (e) {
        console.log('CATEGORIES API - Failed to parse JSON:', await response.text());
      }
    }
  });
  
  // Navigate to login page
  await page.goto('http://localhost:8000/login');
  
  // Wait for page to load
  await page.waitForLoadState('networkidle');
  
  // Check if login page loaded properly
  const hasUsernameInput = await page.locator('input[name="username"]').isVisible();
  console.log('Username input visible:', hasUsernameInput);
  
  if (!hasUsernameInput) {
    console.log('Login page not loaded properly, checking current content');
    const pageContent = await page.content();
    console.log('Current page content:', pageContent.substring(0, 500) + '...');
    return;
  }
  
  // Login with test user
  await page.fill('input[name="username"]', 'testuser');
  await page.click('button[type="submit"]');
  
  // Wait for redirect to home page
  await page.waitForURL('**/home');
  await page.waitForTimeout(1000);
  
  // Click on first calendar
  const calendarCards = await page.locator('.bg-white.dark\\:bg-gray-800.rounded-xl.shadow-lg').all();
  if (calendarCards.length > 0) {
    console.log('Found', calendarCards.length, 'calendar cards');
    await calendarCards[0].click();
  }
  
  // Wait for calendar page to load
  await page.waitForTimeout(2000);
  
  // Check what's displayed on the page
  const hasLoadingState = await page.locator('text=Loading events').isVisible();
  const hasNoEventsMessage = await page.locator('text=No events found').isVisible();
  const hasMainContent = await page.locator('[data-testid="category-cards-section"]').isVisible();
  
  console.log('Loading state visible:', hasLoadingState);
  console.log('No events message visible:', hasNoEventsMessage);
  console.log('Main content visible:', hasMainContent);
  
  // Check the raw events data in browser console
  const eventsData = await page.evaluate(() => {
    return {
      events: window.vue_devtools_events || 'Not available',
      categories: window.vue_devtools_categories || 'Not available'
    };
  });
  
  console.log('Browser events data:', eventsData);
  
  // Check localStorage for any cached data
  const localStorage = await page.evaluate(() => {
    return {
      user: localStorage.getItem('user'),
      calendars: localStorage.getItem('calendars'),
      eventsCache: Object.keys(localStorage).filter(key => key.includes('events')),
      allKeys: Object.keys(localStorage)
    };
  });
  
  console.log('LocalStorage data:', localStorage);
  
  // Take a screenshot for visual debugging
  await page.screenshot({ path: 'debug-calendar-events.png' });
  
  // Wait a bit more to see if anything loads
  await page.waitForTimeout(3000);
  
  // Final check
  const finalState = {
    hasLoadingState: await page.locator('text=Loading events').isVisible(),
    hasNoEventsMessage: await page.locator('text=No events found').isVisible(),
    hasMainContent: await page.locator('[data-testid="category-cards-section"]').isVisible(),
    currentURL: page.url()
  };
  
  console.log('Final state:', finalState);
});