import { test, expect } from '@playwright/test';

test('Test delete calendar functionality', async ({ page }) => {
  console.log('=== TESTING DELETE FUNCTIONALITY ===');

  // Navigate and login
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  const usernameInput = page.locator('input[id="username"]');
  await usernameInput.fill('DeleteTestUser');
  
  const loginButton = page.locator('button[type="submit"]');
  await loginButton.click();
  
  await page.waitForURL('**/home');
  console.log('✅ Logged in successfully');

  // Add a test calendar
  const calendarNameInput = page.locator('input[id="calendar-name"]');
  await calendarNameInput.fill('Calendar to Delete');
  
  const calendarUrlInput = page.locator('input[id="calendar-url"]');
  await calendarUrlInput.fill('https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics');
  
  const addCalendarButton = page.locator('button[type="submit"]');
  await addCalendarButton.click();
  
  // Wait for calendar to appear
  await page.waitForTimeout(2000);
  
  // Look for the calendar in the table
  const calendarRow = page.locator('table').locator('text=Calendar to Delete').first();
  await expect(calendarRow).toBeVisible();
  console.log('✅ Calendar added and visible');

  // Add console listener to see what happens
  page.on('console', msg => {
    console.log(`BROWSER: ${msg.text()}`);
  });

  // Get initial calendar count
  const initialCalendarRows = page.locator('table tbody tr');
  const initialCount = await initialCalendarRows.count();
  console.log(`Initial calendar count: ${initialCount}`);

  // Test Delete button
  console.log('Testing Delete button with confirmation...');
  const deleteButton = page.locator('table').locator('button:has-text("Delete")').first();
  console.log('Delete button found:', await deleteButton.count() > 0);
  
  if (await deleteButton.count() > 0) {
    await deleteButton.click();
    console.log('✅ Clicked Delete button');
    
    // Wait for the Vue confirmation dialog to appear
    await page.waitForTimeout(1000);
    
    // Look for the confirmation dialog
    const confirmDialog = page.locator('[class*="fixed inset-0"]').first();
    const isDialogVisible = await confirmDialog.isVisible();
    console.log('Confirmation dialog visible:', isDialogVisible);
    
    if (isDialogVisible) {
      // Click the "Delete" button in the modal
      const confirmButton = page.locator('button:has-text("Delete")').last();
      await confirmButton.click();
      console.log('✅ Confirmed deletion in modal');
      
      // Wait longer for the UI to update after deletion
      await page.waitForTimeout(5000);
      console.log('Waited for UI to refresh...');
    } else {
      console.log('❌ Confirmation dialog did not appear');
    }
    
    // Check if calendar count decreased
    const finalCount = await initialCalendarRows.count();
    console.log(`Final calendar count: ${finalCount}`);
    
    if (finalCount < initialCount) {
      console.log('✅ Calendar successfully deleted!');
    } else {
      console.log('❌ Calendar was not deleted');
    }
    
    // Check if the specific calendar is gone
    const deletedCalendar = page.locator('table').locator('text=Calendar to Delete');
    const stillVisible = await deletedCalendar.count() > 0;
    console.log('Calendar still visible:', stillVisible);
  }

  console.log('=== DELETE TEST COMPLETE ===');
});