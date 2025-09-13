import { test, expect } from '@playwright/test';

test.describe('Complete User Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8000');
    
    // Wait for the app to load
    await page.waitForLoadState('networkidle');
  });

  test('should complete full user workflow: login → add calendar → verify display → logout', async ({ page }) => {
    console.log('=== STARTING COMPLETE USER WORKFLOW TEST ===');

    // Step 1: Verify we're on login page
    console.log('Step 1: Checking login page...');
    await expect(page.locator('h2')).toContainText('Login');
    
    // Step 2: Login with username "Martijn"
    console.log('Step 2: Logging in with username "Martijn"...');
    const usernameInput = page.locator('input[id="username"]');
    await usernameInput.fill('Martijn');
    
    const loginButton = page.locator('button[type="submit"]');
    await loginButton.click();
    
    // Wait for navigation to home page
    await page.waitForURL('**/home');
    console.log('✅ Successfully navigated to home page');

    // Step 3: Verify username display
    console.log('Step 3: Verifying username display...');
    const welcomeText = page.locator('text=/Welcome.*Martijn/');
    await expect(welcomeText).toBeVisible();
    console.log('✅ Username "Martijn" is displayed correctly');

    // Step 4: Add a calendar
    console.log('Step 4: Adding a calendar...');
    const calendarNameInput = page.locator('input[id="calendar-name"]');
    await calendarNameInput.fill('Norwegian Test Calendar');
    
    const calendarUrlInput = page.locator('input[id="calendar-url"]');
    await calendarUrlInput.fill('https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics');
    
    const addCalendarButton = page.locator('button[type="submit"]');
    await addCalendarButton.click();
    
    // Wait for the calendar to be added and form to reset
    await expect(calendarNameInput).toHaveValue('');
    console.log('✅ Form reset successfully after adding calendar');

    // Step 5: Verify calendar appears in the list
    console.log('Step 5: Verifying calendar appears in list...');
    
    // Wait a bit for the UI to update after form submission
    await page.waitForTimeout(2000);
    
    // Debug: Check what's visible
    const pageContent = await page.locator('body').textContent();
    console.log('Page content includes Norwegian:', pageContent.includes('Norwegian Test Calendar'));
    
    // Look for the calendar in the desktop table layout (which should be visible)
    const calendarInTable = page.locator('table').locator('text=Norwegian Test Calendar').first();
    await expect(calendarInTable).toBeVisible({ timeout: 10000 });
    console.log('✅ Calendar appears in the list correctly');

    // Step 6: Test logout functionality
    console.log('Step 6: Testing logout...');
    const logoutButton = page.locator('text=Logout');
    await logoutButton.click();
    
    // Verify we're back on login page
    await page.waitForURL('**/login');
    await expect(page.locator('h2')).toContainText('Login');
    console.log('✅ Logout successful, redirected to login page');

    console.log('=== ALL TESTS PASSED! WORKFLOW WORKING CORRECTLY ===');
  });

  test('should handle API calls correctly during workflow', async ({ page }) => {
    console.log('=== TESTING API CALLS DURING WORKFLOW ===');

    // Track network requests
    const requests = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requests.push(request.url());
        console.log(`API request: ${request.method()} ${request.url()}`);
      }
    });

    // Login
    const usernameInput = page.locator('input[id="username"]');
    await usernameInput.fill('TestUser');
    
    const loginButton = page.locator('button[type="submit"]');
    await loginButton.click();
    
    await page.waitForURL('**/home');

    // This should trigger fetchCalendars API call
    await page.waitForTimeout(2000); // Allow time for API calls

    // Verify API calls were made
    console.log('API requests made:', requests);
    expect(requests.some(url => url.includes('/api/calendars'))).toBeTruthy();
    console.log('✅ API calls working correctly');
  });
});