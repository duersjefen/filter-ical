/**
 * End-to-End Tests for Recurring Events Functionality
 * 
 * Tests the complete recurring events workflow from user perspective:
 * - Calendar creation with recurring events
 * - Event type classification and grouping
 * - Filtering by recurring event types
 * - UI display and interaction
 */

import { test, expect } from '@playwright/test'

test.describe('Recurring Events E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8000')
    
    // Login with test user
    await page.fill('[data-testid="username-input"]', 'testuser')
    await page.click('[data-testid="login-button"]')
    
    // Wait for home page to load
    await expect(page.locator('[data-testid="home-view"]')).toBeVisible()
  })

  test('should handle calendar with recurring events correctly', async ({ page }) => {
    // Test Step 1: Add a calendar with recurring events
    await page.click('[data-testid="add-calendar-button"]')
    
    // Fill in calendar details
    await page.fill('[data-testid="calendar-name-input"]', 'Test Recurring Calendar')
    await page.fill('[data-testid="calendar-url-input"]', 'https://calendar.google.com/calendar/ical/testrecurring%40example.com/public/basic.ics')
    
    // Submit the form
    await page.click('[data-testid="create-calendar-submit"]')
    
    // Wait for calendar to be created and events to load
    await expect(page.locator('[data-testid="calendar-item"]')).toContainText('Test Recurring Calendar')
    
    // Test Step 2: View calendar events
    await page.click('[data-testid="view-calendar-button"]')
    
    // Wait for calendar view to load
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 3: Verify recurring events are grouped correctly
    // Look for recurring event type sections
    await expect(page.locator('[data-testid="recurring-event-section"]')).toHaveCount({ min: 1 })
    
    // Check that events are grouped by recurring type
    const recurringGroups = page.locator('[data-testid="recurring-group"]')
    const groupCount = await recurringGroups.count()
    expect(groupCount).toBeGreaterThan(0)
    
    // Test Step 4: Verify event count display
    for (let i = 0; i < groupCount; i++) {
      const group = recurringGroups.nth(i)
      
      // Each group should have a count
      await expect(group.locator('[data-testid="event-count"]')).toBeVisible()
      
      // Each group should have events list
      await expect(group.locator('[data-testid="events-list"]')).toBeVisible()
      
      // Events should have required fields
      const events = group.locator('[data-testid="event-item"]')
      const eventCount = await events.count()
      
      if (eventCount > 0) {
        const firstEvent = events.first()
        await expect(firstEvent.locator('[data-testid="event-title"]')).toBeVisible()
        await expect(firstEvent.locator('[data-testid="event-time"]')).toBeVisible()
      }
    }
  })

  test('should filter recurring events by event type', async ({ page }) => {
    // Prerequisite: Add a calendar (simplified for this test)
    await addTestCalendar(page, 'Filtered Recurring Calendar')
    
    // Navigate to calendar view
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 1: Open filtering section
    await page.click('[data-testid="filter-toggle-button"]')
    await expect(page.locator('[data-testid="filter-section"]')).toBeVisible()
    
    // Test Step 2: Apply event type filter
    const eventTypeFilter = page.locator('[data-testid="event-type-filter"]')
    await eventTypeFilter.selectOption('work')
    
    // Apply filter
    await page.click('[data-testid="apply-filter-button"]')
    
    // Test Step 3: Verify filtered results
    // Should only show recurring groups that contain work events
    const visibleGroups = page.locator('[data-testid="recurring-group"]:visible')
    const visibleCount = await visibleGroups.count()
    
    // Verify that all visible events are work-related
    for (let i = 0; i < visibleCount; i++) {
      const group = visibleGroups.nth(i)
      const events = group.locator('[data-testid="event-item"]')
      const eventCount = await events.count()
      
      for (let j = 0; j < eventCount; j++) {
        const event = events.nth(j)
        const eventType = await event.getAttribute('data-event-type')
        expect(eventType).toBe('work')
      }
    }
  })

  test('should create filtered calendar from recurring events', async ({ page }) => {
    // Prerequisite: Add a calendar
    await addTestCalendar(page, 'Source Recurring Calendar')
    
    // Navigate to calendar view
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 1: Select specific events from recurring groups
    // Click on first recurring group
    const firstGroup = page.locator('[data-testid="recurring-group"]').first()
    await firstGroup.click()
    
    // Select some events
    const eventCheckboxes = firstGroup.locator('[data-testid="event-checkbox"]')
    const checkboxCount = await eventCheckboxes.count()
    
    if (checkboxCount > 0) {
      // Select first two events
      await eventCheckboxes.first().check()
      if (checkboxCount > 1) {
        await eventCheckboxes.nth(1).check()
      }
    }
    
    // Test Step 2: Create filtered calendar
    await page.click('[data-testid="create-filtered-calendar-button"]')
    
    // Fill filtered calendar form
    await page.fill('[data-testid="filtered-calendar-name"]', 'Selected Recurring Events')
    await page.selectOption('[data-testid="filter-mode-select"]', 'include')
    
    // Submit
    await page.click('[data-testid="create-filtered-submit"]')
    
    // Test Step 3: Verify filtered calendar creation
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Filtered calendar created')
    
    // Navigate back to home
    await page.click('[data-testid="home-button"]')
    
    // Verify filtered calendar appears in list
    await expect(page.locator('[data-testid="filtered-calendar-item"]')).toContainText('Selected Recurring Events')
  })

  test('should handle empty recurring events gracefully', async ({ page }) => {
    // Test Step 1: Add calendar with no events
    await page.click('[data-testid="add-calendar-button"]')
    await page.fill('[data-testid="calendar-name-input"]', 'Empty Calendar')
    await page.fill('[data-testid="calendar-url-input"]', 'https://example.com/empty.ics')
    await page.click('[data-testid="create-calendar-submit"]')
    
    // Test Step 2: View empty calendar
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 3: Verify empty state handling
    await expect(page.locator('[data-testid="no-events-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="no-events-message"]')).toContainText('No events found')
    
    // Should not show any recurring groups
    await expect(page.locator('[data-testid="recurring-group"]')).toHaveCount(0)
  })

  test('should display recurring events with correct time formatting', async ({ page }) => {
    // Prerequisite: Add a calendar
    await addTestCalendar(page, 'Time Format Test Calendar')
    
    // Navigate to calendar view
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 1: Check time format in recurring events
    const eventItems = page.locator('[data-testid="event-item"]')
    const eventCount = await eventItems.count()
    
    if (eventCount > 0) {
      const firstEvent = eventItems.first()
      
      // Check that time is displayed
      const timeElement = firstEvent.locator('[data-testid="event-time"]')
      await expect(timeElement).toBeVisible()
      
      // Verify time format (should include date and time)
      const timeText = await timeElement.textContent()
      expect(timeText).toMatch(/\d{4}-\d{2}-\d{2}/) // ISO date format
      expect(timeText).toMatch(/\d{2}:\d{2}/) // Time format
    }
    
    // Test Step 2: Verify future events only
    // All displayed events should be in the future or today
    for (let i = 0; i < Math.min(eventCount, 5); i++) {
      const event = eventItems.nth(i)
      const timeElement = event.locator('[data-testid="event-time"]')
      const timeText = await timeElement.textContent()
      
      // Extract date from time text and verify it's not in the past
      const dateMatch = timeText.match(/(\d{4}-\d{2}-\d{2})/)
      if (dateMatch) {
        const eventDate = new Date(dateMatch[1])
        const today = new Date()
        today.setHours(0, 0, 0, 0) // Set to start of day
        
        expect(eventDate >= today).toBeTruthy()
      }
    }
  })

  test('should handle recurring events language switching', async ({ page }) => {
    // Prerequisite: Add a calendar
    await addTestCalendar(page, 'Language Test Calendar')
    
    // Navigate to calendar view
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 1: Switch to German
    await page.click('[data-testid="language-toggle"]')
    
    // Verify German text appears
    await expect(page.locator('[data-testid="events-section-title"]')).toContainText('Ereignisse')
    
    // Test Step 2: Switch back to English
    await page.click('[data-testid="language-toggle"]')
    
    // Verify English text returns
    await expect(page.locator('[data-testid="events-section-title"]')).toContainText('Events')
    
    // Test Step 3: Verify event data remains unchanged
    const eventItems = page.locator('[data-testid="event-item"]')
    const eventCount = await eventItems.count()
    
    // Event titles and times should remain the same regardless of language
    if (eventCount > 0) {
      const firstEvent = eventItems.first()
      await expect(firstEvent.locator('[data-testid="event-title"]')).toBeVisible()
      await expect(firstEvent.locator('[data-testid="event-time"]')).toBeVisible()
    }
  })

  test('should handle network errors gracefully during recurring events load', async ({ page }) => {
    // Test Step 1: Add calendar with invalid URL
    await page.click('[data-testid="add-calendar-button"]')
    await page.fill('[data-testid="calendar-name-input"]', 'Invalid Calendar')
    await page.fill('[data-testid="calendar-url-input"]', 'https://invalid-url-that-does-not-exist.com/calendar.ics')
    await page.click('[data-testid="create-calendar-submit"]')
    
    // Test Step 2: Try to view calendar with network error
    await page.click('[data-testid="view-calendar-button"]')
    await expect(page.locator('[data-testid="calendar-view"]')).toBeVisible()
    
    // Test Step 3: Verify error handling
    // Should show error message instead of crashing
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Error loading events')
    
    // Should not show recurring groups when there's an error
    await expect(page.locator('[data-testid="recurring-group"]')).toHaveCount(0)
    
    // Should show retry option
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible()
  })
})

/**
 * Helper function to add a test calendar
 */
async function addTestCalendar(page, calendarName) {
  await page.click('[data-testid="add-calendar-button"]')
  await page.fill('[data-testid="calendar-name-input"]', calendarName)
  await page.fill('[data-testid="calendar-url-input"]', 'https://calendar.google.com/calendar/ical/test%40example.com/public/basic.ics')
  await page.click('[data-testid="create-calendar-submit"]')
  
  // Wait for calendar to be created
  await expect(page.locator('[data-testid="calendar-item"]')).toContainText(calendarName)
}