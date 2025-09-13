import { test, expect } from '@playwright/test';

test('Test complete calendar workflow', async ({ page }) => {
  console.log('=== TESTING COMPLETE WORKFLOW ===');

  // Navigate and login
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('WorkflowTestUser');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  await page.waitForURL('**/home');
  console.log('✅ Logged in successfully');

  // Add a calendar
  const calendarNameInput = page.locator('input[id="calendar-name"]');
  await calendarNameInput.fill('Complete Workflow Calendar');
  
  const calendarUrlInput = page.locator('input[id="calendar-url"]');
  await calendarUrlInput.fill('https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics');
  
  const addCalendarButton = page.locator('button[type="submit"]');
  await addCalendarButton.click();
  
  // Wait for calendar to appear
  await page.waitForTimeout(3000);
  
  // Verify calendar appears
  const calendarRow = page.locator('table').locator('text=Complete Workflow Calendar').first();
  await expect(calendarRow).toBeVisible();
  console.log('✅ Calendar added and visible');

  // Test View Events button
  const viewEventsButton = page.locator('table').locator('button:has-text("View Events")').first();
  await viewEventsButton.click();
  
  // Wait for navigation
  await page.waitForTimeout(3000);
  const currentUrl = page.url();
  console.log('Current URL:', currentUrl);
  
  if (currentUrl.includes('/calendar/')) {
    console.log('✅ Successfully navigated to calendar view');
    
    // Wait for events to load and check if we see events or "No events found"
    await page.waitForTimeout(5000);
    
    // Look for events content
    const eventsSection = page.locator('[class*="bg-white dark:bg-gray-800"]').filter({ hasText: 'events' });
    const noEventsMessage = page.locator('text=No events found');
    const loadingMessage = page.locator('[class*="animate-spin"]');
    
    console.log('Events section visible:', await eventsSection.count());
    console.log('No events message visible:', await noEventsMessage.count());
    console.log('Loading spinner visible:', await loadingMessage.count());
    
    // Check page content
    const pageContent = await page.content();
    if (pageContent.includes('No events found')) {
      console.log('❌ Still showing "No events found"');
    } else if (pageContent.includes('events')) {
      console.log('✅ Events are being displayed');
    } else {
      console.log('❓ Unable to determine events status');
    }
  } else {
    console.log('❌ Navigation to calendar view failed');
  }

  console.log('=== COMPLETE WORKFLOW TEST DONE ===');
});