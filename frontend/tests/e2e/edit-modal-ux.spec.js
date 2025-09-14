/**
 * E2E Test for Edit Modal UX
 * Verifies that the edit modal closes properly after saving
 */

import { test, expect } from '@playwright/test'

test.describe('Edit Modal UX', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/')
    
    // Mock user authentication
    await page.evaluate(() => {
      localStorage.setItem('user', JSON.stringify({
        id: 'test-user',
        username: 'testuser',
        token: 'test-token'
      }))
    })
    
    // Navigate to a calendar view (assuming we have test data)
    // This is a placeholder - adjust based on your actual test setup
    await page.goto('/calendar/test-calendar-id')
  })

  test('edit modal closes after successful save with green button feedback', async ({ page }) => {
    // Wait for the page to load filtered calendars
    await page.waitForSelector('.filtered-calendar-section', { timeout: 5000 })
    
    // Look for an edit button (pencil icon)
    const editButton = page.locator('button[title="Edit"], button:has(svg)')
    await expect(editButton.first()).toBeVisible({ timeout: 5000 })
    
    // Click the edit button
    await editButton.first().click()
    
    // Verify modal opens
    await expect(page.locator('.fixed.inset-0')).toBeVisible()
    await expect(page.locator('h3:has-text("Edit")')).toBeVisible()
    
    // Get the input field and change the name
    const nameInput = page.locator('input[type="text"]').last()
    await nameInput.clear()
    await nameInput.fill('Updated Calendar Name')
    
    // Click save button
    const saveButton = page.locator('button[type="submit"]:has-text("Save")')
    await saveButton.click()
    
    // Verify button turns green with "Saved!" text
    await expect(saveButton).toHaveClass(/bg-green-600/)
    await expect(saveButton).toContainText('Saved!')
    
    // Verify modal closes within reasonable time (1.5 seconds)
    await expect(page.locator('.fixed.inset-0')).toBeHidden({ timeout: 2000 })
    
    // Verify we're still on the calendar view
    await expect(page.locator('.calendar-view, .category-cards-section')).toBeVisible()
  })

  test('edit modal closes even if API call fails', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/filtered-calendars/*', route => {
      if (route.request().method() === 'PUT') {
        route.abort('failed')
      } else {
        route.continue()
      }
    })
    
    // Wait for the page to load
    await page.waitForSelector('.filtered-calendar-section', { timeout: 5000 })
    
    // Click edit button
    const editButton = page.locator('button[title="Edit"], button:has(svg)')
    await editButton.first().click()
    
    // Verify modal opens
    await expect(page.locator('.fixed.inset-0')).toBeVisible()
    
    // Change name and save
    const nameInput = page.locator('input[type="text"]').last()
    await nameInput.clear()
    await nameInput.fill('Test Name Change')
    
    const saveButton = page.locator('button[type="submit"]:has-text("Save")')
    await saveButton.click()
    
    // Even with API failure, modal should close within 2 seconds
    await expect(page.locator('.fixed.inset-0')).toBeHidden({ timeout: 2500 })
  })

  test('modal can be cancelled and closes properly', async ({ page }) => {
    // Wait for the page to load
    await page.waitForSelector('.filtered-calendar-section', { timeout: 5000 })
    
    // Click edit button
    const editButton = page.locator('button[title="Edit"], button:has(svg)')
    await editButton.first().click()
    
    // Verify modal opens
    await expect(page.locator('.fixed.inset-0')).toBeVisible()
    
    // Click cancel button
    const cancelButton = page.locator('button:has-text("Cancel")')
    await cancelButton.click()
    
    // Modal should close immediately
    await expect(page.locator('.fixed.inset-0')).toBeHidden({ timeout: 1000 })
  })
})