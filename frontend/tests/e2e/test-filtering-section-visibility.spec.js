/**
 * @testfile: Filtering Section Visibility Bug Test
 * @purpose: Test that the filtering section doesn't disappear when combining search + show selected
 * @bug: Filtering section disappears completely when search & show selected interaction clears selectedCategories
 */

import { test, expect } from '@playwright/test'

test.describe('Filtering Section Visibility', () => {
  test.beforeEach(async ({ page }) => {
    // Follow existing pattern for login
    await page.goto('http://localhost:8000')
    await page.waitForLoadState('networkidle')

    const usernameInput = page.locator('input[id="username"]')
    await usernameInput.fill('FilterTestUser')
    
    const loginButton = page.locator('button[type="submit"]')
    await loginButton.click()
    
    await page.waitForURL('**/home')
    
    // Navigate to test calendar that exists
    await page.goto('http://localhost:8000/calendar/cm4stdfdt000008jqasp1f8ze')
    
    // Wait for calendar data to load
    await page.waitForTimeout(3000)
  })

  test('filtering section should remain visible when combining search and show selected', async ({ page }) => {
    // 1. Verify filtering section is initially visible
    const filteringSection = page.locator('[data-testid="filtered-calendar-section"]').or(
      page.locator('text=🔗').locator('..').locator('..')
    )
    
    // If no test ID, look for the section with "🔗" emoji (Filtered Calendar section)
    await expect(filteringSection.first()).toBeVisible()
    
    // 2. Select some categories first
    const firstCategory = page.locator('[data-testid="category-card"]').first()
    await firstCategory.click()
    
    // Verify category is selected
    await expect(firstCategory).toHaveClass(/bg-green-100|border-green-500/)
    
    // 3. Enable "show selected only" mode
    const showSelectedButton = page.locator('text=🎯').or(page.locator('text=Show Selected Only'))
    await showSelectedButton.click()
    
    // 4. Verify filtering section is still visible after enabling show selected
    await expect(filteringSection.first()).toBeVisible()
    
    // 5. Use search functionality
    const searchInput = page.locator('input[placeholder*="Search"]').or(
      page.locator('input[type="text"]').filter({ hasText: '' }).first()
    )
    await searchInput.fill('test search that matches nothing')
    
    // 6. Clear the search
    await searchInput.clear()
    
    // 7. CRITICAL TEST: Filtering section should still be visible
    await expect(filteringSection.first()).toBeVisible()
    
    // 8. Try clearing all categories (which might trigger the bug)
    const clearAllButton = page.locator('text=Clear All').or(page.locator('text=🗑️'))
    if (await clearAllButton.count() > 0) {
      await clearAllButton.click()
    }
    
    // 9. CRITICAL TEST: Filtering section should still be visible even with no selected categories
    // if there are existing filtered calendars
    const hasExistingCalendars = await page.locator('text=Your Filtered Calendars').count() > 0
    if (hasExistingCalendars) {
      await expect(filteringSection.first()).toBeVisible()
    }
  })

  test('filtering section visibility logic should work correctly', async ({ page }) => {
    // Test the core visibility conditions:
    // shouldShowSection = filteredCalendars.length > 0 || selectedCategories.length > 0
    
    // 1. No categories selected, no existing calendars -> section should be hidden
    // (Skip this test if there are existing calendars)
    
    // 2. Select categories -> section should appear
    const firstCategory = page.locator('[data-testid="category-card"]').first()
    await firstCategory.click()
    
    const filteringSection = page.locator('[data-testid="filtered-calendar-section"]').or(
      page.locator('text=🔗').locator('..').locator('..')
    )
    await expect(filteringSection.first()).toBeVisible()
    
    // 3. Clear categories but keep existing calendars -> section should remain visible
    const clearAllButton = page.locator('text=Clear All').or(page.locator('text=🗑️'))
    if (await clearAllButton.count() > 0) {
      await clearAllButton.click()
      
      // Check if there are existing filtered calendars
      const hasExistingCalendars = await page.locator('text=Your Filtered Calendars').count() > 0
      if (hasExistingCalendars) {
        await expect(filteringSection.first()).toBeVisible()
      }
    }
  })

  test('show selected only should not interfere with section visibility', async ({ page }) => {
    // Test that the showSelectedOnly watcher doesn't break section visibility
    
    // 1. Select categories
    const firstCategory = page.locator('[data-testid="category-card"]').first()
    await firstCategory.click()
    
    // 2. Enable show selected only
    const showSelectedButton = page.locator('text=🎯').or(page.locator('text=Show Selected Only'))
    await showSelectedButton.click()
    
    // 3. Clear categories (this triggers the watcher that auto-turns off showSelectedOnly)
    const clearAllButton = page.locator('text=Clear All').or(page.locator('text=🗑️'))
    if (await clearAllButton.count() > 0) {
      await clearAllButton.click()
    }
    
    // 4. Verify showSelectedOnly was auto-disabled (button should show "Show Selected Only" again)
    await expect(showSelectedButton).toBeVisible()
    
    // 5. CRITICAL: Filtering section visibility should not be affected by this auto-clearing
    const filteringSection = page.locator('[data-testid="filtered-calendar-section"]').or(
      page.locator('text=🔗').locator('..').locator('..')
    )
    
    // Section should be visible if there are existing filtered calendars
    const hasExistingCalendars = await page.locator('text=Your Filtered Calendars').count() > 0
    if (hasExistingCalendars) {
      await expect(filteringSection.first()).toBeVisible()
    }
  })
})