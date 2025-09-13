import { test, expect } from '@playwright/test';

test('Test direct calendar URL access and refresh', async ({ page }) => {
  console.log('=== TESTING DIRECT URL ACCESS AND REFRESH ===');

  // First, get a calendar ID by adding a calendar normally
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('DirectUrlTestUser');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  await page.waitForURL('**/home');
  console.log('✅ Logged in successfully');

  // Add a calendar to get an ID
  const calendarNameInput = page.locator('input[id="calendar-name"]');
  await calendarNameInput.fill('Direct URL Test Calendar');
  
  const calendarUrlInput = page.locator('input[id="calendar-url"]');
  await calendarUrlInput.fill('https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics');
  
  const addCalendarButton = page.locator('button[type="submit"]');
  await addCalendarButton.click();
  
  await page.waitForTimeout(3000);
  console.log('✅ Calendar added');

  // Click "View Events" to navigate and get the calendar URL
  const viewEventsButton = page.locator('table').locator('button:has-text("View Events")').first();
  await viewEventsButton.click();
  await page.waitForTimeout(3000);
  
  const calendarUrl = page.url();
  console.log('Calendar URL:', calendarUrl);

  // TEST 1: Direct URL access in new tab/window
  console.log('=== TEST 1: Direct URL Access ===');
  await page.goto('http://localhost:8000/login'); // Go back to start
  await page.waitForLoadState('networkidle');
  
  // Login again
  await usernameInput.fill('DirectUrlTestUser');
  await loginButton.click();
  await page.waitForTimeout(2000);
  
  // Now navigate directly to calendar URL
  console.log('Navigating directly to:', calendarUrl);
  await page.goto(calendarUrl);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000); // Wait for data to load
  
  // Check what's visible
  const downloadSection = page.locator('text=Download Your Selection');
  const categorySection = page.locator('text=Event-Kategorien', 'text=Event Categories');
  const noEventsMessage = page.locator('text=No events found');
  
  console.log('Download section visible:', await downloadSection.count() > 0);
  console.log('Category section visible:', await categorySection.count() > 0);
  console.log('No events message visible:', await noEventsMessage.count() > 0);
  
  if (await categorySection.count() === 0) {
    console.log('❌ DIRECT URL: Categories not loading properly');
  } else {
    console.log('✅ DIRECT URL: Categories loaded successfully');
  }

  // TEST 2: Page refresh
  console.log('=== TEST 2: Page Refresh ===');
  await page.reload();
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000); // Wait for data to reload
  
  const downloadSectionAfterRefresh = page.locator('text=Download Your Selection');
  const categorySectionAfterRefresh = page.locator('text=Event-Kategorien', 'text=Event Categories');  
  const noEventsMessageAfterRefresh = page.locator('text=No events found');
  
  console.log('AFTER REFRESH:');
  console.log('Download section visible:', await downloadSectionAfterRefresh.count() > 0);
  console.log('Category section visible:', await categorySectionAfterRefresh.count() > 0);
  console.log('No events message visible:', await noEventsMessageAfterRefresh.count() > 0);
  
  if (await noEventsMessageAfterRefresh.count() > 0) {
    console.log('❌ REFRESH: Shows "No events found" after refresh');
  } else if (await categorySectionAfterRefresh.count() === 0) {
    console.log('❌ REFRESH: Categories not loading after refresh');
  } else {
    console.log('✅ REFRESH: Page refreshed successfully with categories');
  }

  console.log('=== DIRECT URL AND REFRESH TEST COMPLETE ===');
});