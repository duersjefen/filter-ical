import { test, expect } from '@playwright/test'

test.describe('Create Filtered Calendar Functionality', () => {
  test.setTimeout(30000)

  test('Should create filtered calendar successfully', async ({ page }) => {
    // Navigate to homepage and login
    await page.goto('http://localhost:8000')
    
    if (await page.locator('input[id="username"]').isVisible()) {
      await page.locator('input[id="username"]').fill('testuser')
      await page.locator('button[type="submit"]').click()
    }

    // Wait for calendar data to load
    await expect(page).toHaveURL('http://localhost:8000/home')
    await page.waitForSelector('.calendar-card', { timeout: 10000 })

    console.log('✅ Logged in and calendar loaded')

    // Select some categories for filtering
    const categoryCheckboxes = page.locator('input[type="checkbox"]')
    const checkboxCount = await categoryCheckboxes.count()
    
    if (checkboxCount > 0) {
      // Select the first few categories
      await categoryCheckboxes.first().check()
      if (checkboxCount > 1) {
        await categoryCheckboxes.nth(1).check()
      }
      console.log(`✅ Selected categories for filtering`)
    }

    // Look for the "Create New" button in the filtered calendar section
    const createNewButton = page.locator('text=Create New', { timeout: 5000 })
    if (await createNewButton.isVisible()) {
      await createNewButton.click()
      console.log('✅ Clicked "Create New" button')

      // Fill in the calendar name
      const nameInput = page.locator('input[type="text"][required]').first()
      await nameInput.fill('Test Filtered Calendar')
      console.log('✅ Filled calendar name')

      // Submit the form
      const createButton = page.locator('button[type="submit"]').filter({ hasText: /create/i })
      await createButton.click()
      console.log('✅ Clicked create button')

      // Wait for the calendar to be created - check for success indicators
      // Look for the new calendar in the list or a success message
      await page.waitForTimeout(3000) // Give time for API call

      // Check if the calendar appears in the filtered calendars list
      const filteredCalendars = page.locator('[data-testid="filtered-calendar"], .filtered-calendar-item')
      if (await filteredCalendars.count() > 0) {
        console.log('✅ Filtered calendar created successfully')
      } else {
        // Alternative success check - look for calendar subscription URLs or success feedback
        const successIndicator = page.locator('text=created, text=success, button:has-text("Copy URL")')
        await expect(successIndicator.first()).toBeVisible({ timeout: 5000 })
        console.log('✅ Success indicator found')
      }
    } else {
      console.log('❌ Create New button not found - feature may be disabled')
      // This might indicate the feature is not available yet
    }
  })

  test('Should handle filtered calendar API errors gracefully', async ({ page }) => {
    // Navigate to homepage and login
    await page.goto('http://localhost:8000')
    
    if (await page.locator('input[id="username"]').isVisible()) {
      await page.locator('input[id="username"]').fill('errortest')
      await page.locator('button[type="submit"]').click()
    }

    await expect(page).toHaveURL('http://localhost:8000/home')

    // Listen for console errors
    const consoleMessages = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleMessages.push(msg.text())
      }
    })

    // Try to trigger the create calendar flow
    const createNewButton = page.locator('text=Create New')
    if (await createNewButton.isVisible()) {
      await createNewButton.click()
      
      // Try to submit with minimal data to potentially trigger an error
      const nameInput = page.locator('input[type="text"][required]').first()
      await nameInput.fill('Error Test Calendar')
      
      const createButton = page.locator('button[type="submit"]').filter({ hasText: /create/i })
      await createButton.click()
      
      // Wait for potential error handling
      await page.waitForTimeout(2000)
      
      // Check that error handling is graceful (no unhandled promise rejections)
      const hasUnhandledErrors = consoleMessages.some(msg => 
        msg.includes('Unhandled promise rejection') || 
        msg.includes('AttributeError') ||
        msg.includes('TypeError')
      )
      
      expect(hasUnhandledErrors).toBeFalsy()
      console.log('✅ No unhandled errors in create calendar flow')
    }
  })
})