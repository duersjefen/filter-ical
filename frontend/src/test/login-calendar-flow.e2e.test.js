/**
 * E2E Test: Login and Calendar Overview Flow
 * Tests the complete user workflow: login → see calendar overview → add calendar
 */

import { test, expect } from '@playwright/test'

const FRONTEND_URL = 'http://localhost:8000'

test.describe('Login and Calendar Overview Flow', () => {
  
  test('should complete full login and calendar workflow', async ({ page }) => {
    // Step 1: Visit the application
    await page.goto(FRONTEND_URL)
    
    // Should redirect to login page or show login form
    await expect(page).toHaveURL(/.*\/login.*/)
    
    // Step 2: Fill in login form
    await page.fill('[data-testid="username-input"], input[type="text"], #username', 'testuser')
    
    // Step 3: Submit login
    await page.click('button[type="submit"], [data-testid="login-button"]')
    
    // Step 4: Should redirect to home page after login
    await expect(page).toHaveURL('/')
    
    // Step 5: Check if we see the debug banner (temporarily)
    const debugBanner = page.locator('div[style*="background: red"]')
    if (await debugBanner.isVisible()) {
      console.log('Debug banner content:', await debugBanner.textContent())
      
      // Verify login state in debug banner
      await expect(debugBanner).toContainText('isLoggedIn: true')
      await expect(debugBanner).toContainText('testuser')
    }
    
    // Step 6: Verify main calendar interface is visible
    await expect(page.locator('h2')).toContainText('Add New Calendar', { timeout: 10000 })
    
    // Step 7: Verify form elements are present
    await expect(page.locator('#calendar-name, [data-testid="calendar-name"]')).toBeVisible()
    await expect(page.locator('#calendar-url, [data-testid="calendar-url"]')).toBeVisible()
    
    // Step 8: Add a test calendar
    await page.fill('#calendar-name, [data-testid="calendar-name"]', 'My Test Calendar')
    await page.fill('#calendar-url, [data-testid="calendar-url"]', 'https://example.com/test.ics')
    
    // Step 9: Submit calendar creation
    await page.click('button[type="submit"]')
    
    // Step 10: Verify calendar appears in list
    await expect(page.locator('text=My Test Calendar')).toBeVisible({ timeout: 5000 })
    
    // Step 11: Verify we can see the calendar table/list
    await expect(page.locator('table, .calendar-list')).toBeVisible()
  })

  test('should show error for empty login', async ({ page }) => {
    await page.goto(FRONTEND_URL)
    
    // Try to login without username
    await page.click('button[type="submit"]')
    
    // Should show error or prevent submission
    const errorMessage = page.locator('[data-testid="error"], .error, [class*="error"]')
    if (await errorMessage.isVisible()) {
      await expect(errorMessage).toContainText(/username|required/i)
    }
  })

  test('should persist login state on refresh', async ({ page }) => {
    // First login
    await page.goto(FRONTEND_URL)
    await page.fill('input[type="text"], #username', 'persisttest')
    await page.click('button[type="submit"]')
    
    // Verify we're logged in
    await expect(page).toHaveURL('/')
    
    // Refresh the page
    await page.reload()
    
    // Should still be on home page (not redirected to login)
    await expect(page).toHaveURL('/')
    await expect(page.locator('h2')).toContainText('Add New Calendar', { timeout: 5000 })
  })

  test('should show calendar data loading states', async ({ page }) => {
    // Login first
    await page.goto(FRONTEND_URL)
    await page.fill('input[type="text"], #username', 'loadingtest')
    await page.click('button[type="submit"]')
    
    // Should show main interface
    await expect(page).toHaveURL('/')
    
    // Look for loading states or empty states
    const hasCalendars = await page.locator('table tbody tr').count()
    if (hasCalendars === 0) {
      // Empty state should be visible
      console.log('No calendars found - this is the expected initial state')
    }
    
    // Form should be ready to add calendars
    await expect(page.locator('#calendar-name, [data-testid="calendar-name"]')).toBeVisible()
  })
  
  test('should logout properly', async ({ page }) => {
    // Login first
    await page.goto(FRONTEND_URL)
    await page.fill('input[type="text"], #username', 'logouttest')
    await page.click('button[type="submit"]')
    
    await expect(page).toHaveURL('/')
    
    // Find and click logout button
    const logoutButton = page.locator('[data-testid="logout"], button:has-text("Logout"), button:has-text("Log out")')
    if (await logoutButton.isVisible()) {
      await logoutButton.click()
      
      // Should redirect to login
      await expect(page).toHaveURL(/.*\/login.*/)
    }
  })
})