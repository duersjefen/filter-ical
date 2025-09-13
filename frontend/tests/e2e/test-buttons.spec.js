import { test, expect } from '@playwright/test';

test('Test calendar button functionality', async ({ page }) => {
  console.log('=== TESTING CALENDAR BUTTONS ===');

  // Navigate and login
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('TestUser');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  await page.waitForURL('**/home');
  console.log('✅ Logged in successfully');

  // Add a calendar first
  const calendarNameInput = page.locator('input[id="calendar-name"]');
  await calendarNameInput.fill('Test Button Calendar');
  
  const calendarUrlInput = page.locator('input[id="calendar-url"]');
  await calendarUrlInput.fill('https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics');
  
  const addCalendarButton = page.locator('button[type="submit"]');
  await addCalendarButton.click();
  
  // Wait for calendar to appear
  await page.waitForTimeout(2000);
  
  // Look for the calendar in the table
  const calendarRow = page.locator('table').locator('text=Test Button Calendar').first();
  await expect(calendarRow).toBeVisible();
  console.log('✅ Calendar added and visible');

  // Add console listener to see what happens
  page.on('console', msg => {
    console.log(`BROWSER: ${msg.text()}`);
  });

  // Test "View Events" button - specifically in the desktop table
  console.log('Testing View Events button...');
  const viewEventsButton = page.locator('table').locator('button:has-text("View Events")').first();
  console.log('View Events button found:', await viewEventsButton.count() > 0);
  
  if (await viewEventsButton.count() > 0) {
    await viewEventsButton.click();
    console.log('✅ Clicked View Events button');
    
    // Wait to see if navigation happens
    await page.waitForTimeout(3000);
    const currentUrl = page.url();
    console.log('Current URL after click:', currentUrl);
    
    // Check if we navigated to calendar view
    if (currentUrl.includes('/calendar/')) {
      console.log('✅ Successfully navigated to calendar view!');
      
      // Navigate back to home to test delete button
      console.log('Navigating back to home page for delete test...');
      await page.goto('http://localhost:8000/home');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000); // Wait for calendars to load
    } else {
      console.log('❌ Navigation to calendar view failed');
    }
  }

  // Test Delete button - check in desktop table (should be on home page now)
  console.log('Testing Delete button...');
  const deleteButton = page.locator('table').locator('button:has-text("Delete")').first();
  console.log('Delete button found in table:', await deleteButton.count() > 0);
  
  // Try mobile version if not found in table
  if (await deleteButton.count() === 0) {
    const mobileDeleteButton = page.locator('.sm\\:hidden').locator('button:has-text("Delete")').first();
    console.log('Mobile delete button found:', await mobileDeleteButton.count() > 0);
    
    if (await mobileDeleteButton.count() > 0) {
      console.log('Found delete button in mobile layout, but we are in desktop view');
    }
  }
  
  if (await deleteButton.count() > 0) {
    await deleteButton.click();
    console.log('✅ Clicked Delete button');
    
    // Wait to see if confirmation dialog appears or calendar is deleted
    await page.waitForTimeout(2000);
  }

  console.log('=== BUTTON TEST COMPLETE ===');
});