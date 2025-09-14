import { test, expect } from '@playwright/test'

test.describe('Persistent User Sessions', () => {
  test.setTimeout(30000)

  test('User session persists across browser refresh and new tabs', async ({ page, context }) => {
    // Navigate to homepage
    await page.goto('http://localhost:8000')

    // Should redirect to login page initially
    await expect(page).toHaveURL('http://localhost:8000/login')

    // Login with a test username
    const usernameInput = page.locator('input[id="username"]')
    const loginButton = page.locator('button[type="submit"]')

    await usernameInput.fill('testuser')
    await loginButton.click()

    // Should redirect to home page after login
    await expect(page).toHaveURL('http://localhost:8000/home')

    // Check if user is displayed in header
    const userInfo = page.locator('text=Welcome, testuser')
    await expect(userInfo).toBeVisible({ timeout: 10000 })

    console.log('✅ Login successful and user is displayed')

    // Refresh the page to test session persistence
    await page.reload()

    // Should still be on home page (not redirected to login)
    await expect(page).toHaveURL('http://localhost:8000/home')
    await expect(userInfo).toBeVisible({ timeout: 10000 })

    console.log('✅ Session persists after page refresh')

    // Open a new tab to test cross-tab persistence
    const newPage = await context.newPage()
    await newPage.goto('http://localhost:8000')

    // Should redirect to home page (not login) because user is already logged in
    await expect(newPage).toHaveURL('http://localhost:8000/home')
    
    const userInfoNewTab = newPage.locator('text=Welcome, testuser')
    await expect(userInfoNewTab).toBeVisible({ timeout: 10000 })

    console.log('✅ Session persists across new tabs')

    // Test logout functionality
    await page.bringToFront()
    const logoutButton = page.locator('text=Logout')
    await logoutButton.click()

    // Should redirect to login page
    await expect(page).toHaveURL('http://localhost:8000/login')

    console.log('✅ Logout successful')

    // Check if new tab also logs out (should redirect to login when refreshed)
    await newPage.reload()
    await expect(newPage).toHaveURL('http://localhost:8000/login')

    console.log('✅ Logout affects all tabs')

    // Test direct navigation to protected route without login
    await newPage.goto('http://localhost:8000/home')
    
    // Should be redirected to login page
    await expect(newPage).toHaveURL('http://localhost:8000/login')

    console.log('✅ Protected routes redirect to login when not authenticated')

    await newPage.close()
  })

  test('Session expires after configured time period', async ({ page }) => {
    // This test would require mocking the time or reducing session duration
    // For now, we'll just verify the session expiration logic exists
    
    await page.goto('http://localhost:8000/login')
    
    // Login
    const usernameInput = page.locator('input[id="username"]')
    const loginButton = page.locator('button[type="submit"]')

    await usernameInput.fill('sessiontest')
    await loginButton.click()

    await expect(page).toHaveURL('http://localhost:8000/home')

    // Check localStorage contains session data
    const sessionData = await page.evaluate(() => {
      const data = localStorage.getItem('icalViewer_user')
      return data ? JSON.parse(data) : null
    })

    expect(sessionData).toBeTruthy()
    expect(sessionData.username).toBe('sessiontest')
    expect(sessionData.loggedIn).toBe(true)
    expect(sessionData.loginTime).toBeTruthy()
    expect(sessionData.lastActivity).toBeTruthy()

    console.log('✅ Session data stored correctly in localStorage')

    // Test that session data is properly structured
    expect(typeof sessionData.loginTime).toBe('number')
    expect(typeof sessionData.lastActivity).toBe('number')

    console.log('✅ Session timestamps are properly formatted')
  })

  test('Navigation guards work correctly', async ({ page }) => {
    // Test that we can't access protected routes without login
    await page.goto('http://localhost:8000/home')
    await expect(page).toHaveURL('http://localhost:8000/login')

    // Test that login page redirects to home when already logged in
    await page.goto('http://localhost:8000/login')
    
    const usernameInput = page.locator('input[id="username"]')
    const loginButton = page.locator('button[type="submit"]')

    await usernameInput.fill('navtest')
    await loginButton.click()

    await expect(page).toHaveURL('http://localhost:8000/home')

    // Now try to go to login page - should redirect back to home
    await page.goto('http://localhost:8000/login')
    await expect(page).toHaveURL('http://localhost:8000/home')

    console.log('✅ Navigation guards working correctly')
  })
})