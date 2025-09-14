import { test, expect } from '@playwright/test'

test.describe('Create Calendar Debug', () => {
  test('debug create calendar functionality step by step', async ({ page }) => {
    // Enable console logging
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()))
    
    // Navigate to homepage first to login
    await page.goto('http://localhost:8000/')
    
    // Check if we need to login
    const loginButton = page.locator('button:has-text("Login"), input[value="Login"]')
    if (await loginButton.count() > 0) {
      console.log('Need to login first')
      // Fill username with test user
      const usernameInput = page.locator('input[placeholder*="username"], input[type="text"]').first()
      await usernameInput.fill('testuser')
      await loginButton.click()
      await page.waitForTimeout(1000)
    }
    
    // First add a test calendar if testuser has none
    console.log('Checking if user has calendars...')
    await page.waitForTimeout(2000) // Wait for calendars to load
    
    const addCalendarButton = page.locator('button:has-text("Add Calendar"), button:has-text("Add New Calendar")')
    const existingCalendar = page.locator('a:has-text("View Events")')
    
    let calendarId = null
    
    if (await existingCalendar.count() > 0) {
      console.log('User has existing calendars, using first one')
      // Get the href to extract calendar ID
      const calendarLink = existingCalendar.first()
      const href = await calendarLink.getAttribute('href')
      calendarId = href.split('/').pop()
    } else if (await addCalendarButton.count() > 0) {
      console.log('User has no calendars, adding test calendar')
      await addCalendarButton.click()
      
      // Fill calendar form
      await page.fill('input[placeholder*="Work Calendar"], input[placeholder*="calendar name"]', 'Test BCC Calendar')
      await page.fill('input[placeholder*="https://"], input[placeholder*="ical"]', 'https://widgets.bcc.no/ical-4fea7cc56289cdfc/35490/Portal-Calendar.ics')
      
      // Submit form
      const submitButton = page.locator('button:has-text("Add Calendar")')
      await submitButton.click()
      await page.waitForTimeout(3000) // Wait for calendar to be added
      
      // Get the new calendar ID from the view events link
      const newCalendarLink = page.locator('a:has-text("View Events")').first()
      const href = await newCalendarLink.getAttribute('href')
      calendarId = href.split('/').pop()
    }
    
    if (!calendarId) {
      throw new Error('Could not get or create a calendar for testing')
    }
    
    console.log('Using calendar ID:', calendarId)
    
    // Navigate to calendar view
    await page.goto(`http://localhost:8000/calendar/${calendarId}`)
    
    // Wait for page to load
    console.log('Waiting for page to load...')
    try {
      await page.waitForSelector('h1, h2, h3', { timeout: 10000 })
      console.log('Page loaded')
    } catch (error) {
      console.log('Failed to load page headers, taking screenshot anyway')
    }
    
    // Take screenshot to see what's actually on the page
    await page.screenshot({ path: 'debug-create-calendar-initial.png', fullPage: true })
    
    // Log page content for debugging
    const pageText = await page.textContent('body')
    console.log('PAGE CONTENT:', pageText.slice(0, 500)) // First 500 chars
    
    // First select some categories to make the filtered calendar section appear
    console.log('Looking for category checkboxes...')
    await page.waitForSelector('input[type="checkbox"]', { timeout: 10000 })
    
    // Click the first category checkbox to enable filtered calendar section
    const firstCheckbox = page.locator('input[type="checkbox"]').first()
    await firstCheckbox.check()
    await page.waitForTimeout(1000)
    
    console.log('Checkbox selected, looking for filtered calendar section...')
    
    // Now look for filtered calendar section (should appear after selecting categories)
    await page.waitForSelector('[data-testid="filtered-calendar-section"], .filtered-calendar-section, h3:has-text("Filtered Calendar Links")', { timeout: 5000 })
    
    // Check if create form is visible or if create button exists
    const createButton = page.locator('button:has-text("Create Filtered Calendar")')
    const createFormTitle = page.locator('h4:has-text("Create New Filtered Calendar")')
    
    console.log('CREATE BUTTON EXISTS:', await createButton.count() > 0)
    console.log('CREATE FORM VISIBLE:', await createFormTitle.count() > 0)
    
    // If create form is not visible, try to show it
    if (await createButton.count() > 0) {
      console.log('Clicking create button...')
      await createButton.click()
      await page.waitForTimeout(1000)
    }
    
    // Check form state after potential click
    console.log('FORM VISIBLE AFTER CLICK:', await createFormTitle.count() > 0)
    
    // Look for form inputs
    const nameInput = page.locator('input[placeholder*="name"], input[id*="name"]')
    const submitButton = page.locator('button:has-text("Create Calendar")')
    
    console.log('NAME INPUT EXISTS:', await nameInput.count() > 0)
    console.log('SUBMIT BUTTON EXISTS:', await submitButton.count() > 0)
    
    if (await submitButton.count() > 0) {
      console.log('SUBMIT BUTTON DISABLED:', await submitButton.isDisabled())
    }
    
    // Take screenshot of form state
    await page.screenshot({ path: 'debug-create-calendar-form.png', fullPage: true })
    
    // Try to fill out the form if inputs exist
    if (await nameInput.count() > 0) {
      console.log('Filling out form...')
      await nameInput.fill('Test Debug Calendar')
      await page.waitForTimeout(500)
      
      console.log('SUBMIT BUTTON DISABLED AFTER FILL:', await submitButton.isDisabled())
      
      if (!await submitButton.isDisabled()) {
        // Listen for network requests
        page.on('request', request => {
          if (request.url().includes('filtered-calendars')) {
            console.log('API REQUEST:', request.method(), request.url())
            console.log('REQUEST BODY:', request.postData())
          }
        })
        
        page.on('response', response => {
          if (response.url().includes('filtered-calendars')) {
            console.log('API RESPONSE:', response.status(), response.url())
          }
        })
        
        console.log('Clicking submit button...')
        await submitButton.click()
        
        // Wait for potential response
        await page.waitForTimeout(2000)
        
        // Check if calendar was created (look for success message or updated list)
        const successMessage = page.locator('text="Calendar created successfully", text="created", .success')
        const newCalendarItem = page.locator('text="Test Debug Calendar"')
        
        console.log('SUCCESS MESSAGE VISIBLE:', await successMessage.count() > 0)
        console.log('NEW CALENDAR IN LIST:', await newCalendarItem.count() > 0)
        
        // Take final screenshot
        await page.screenshot({ path: 'debug-create-calendar-result.png', fullPage: true })
      }
    }
    
    // Log current localStorage state
    const localStorage = await page.evaluate(() => {
      const items = {}
      for (let i = 0; i < window.localStorage.length; i++) {
        const key = window.localStorage.key(i)
        items[key] = window.localStorage.getItem(key)
      }
      return items
    })
    console.log('LOCALSTORAGE STATE:', JSON.stringify(localStorage, null, 2))
  })
  
  test('debug API call directly', async ({ page }) => {
    // First get available calendars for testuser
    const calendarsResponse = await page.request.get('http://localhost:3000/api/calendars', {
      headers: {
        'X-User-ID': 'testuser'
      }
    })
    
    const calendarsData = await calendarsResponse.json()
    console.log('AVAILABLE CALENDARS:', JSON.stringify(calendarsData, null, 2))
    
    if (!calendarsData.calendars || calendarsData.calendars.length === 0) {
      console.log('No calendars found for testuser, skipping API test')
      return
    }
    
    const firstCalendar = calendarsData.calendars[0]
    console.log('Using calendar:', firstCalendar.id)
    
    // Test the API call that should be made
    const response = await page.request.post('http://localhost:3000/api/filtered-calendars', {
      data: {
        name: 'Direct API Test',
        source_calendar_id: firstCalendar.id,
        filter_config: {
          categories: ['Ateam sport'],
          mode: 'include'
        }
      },
      headers: {
        'X-User-ID': 'testuser'
      }
    })
    
    console.log('DIRECT API RESPONSE STATUS:', response.status())
    const responseBody = await response.json()
    console.log('DIRECT API RESPONSE BODY:', JSON.stringify(responseBody, null, 2))
    
    expect(response.status()).toBe(200)
  })
})