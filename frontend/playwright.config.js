import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
    // Run tests in headless mode (no browser pop-up)
    headless: true,
  },
  
  // Environment variables for tests
  env: {
    FRONTEND_URL: process.env.FRONTEND_URL || 'http://localhost:8000',
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:3000',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Start dev server before tests
  webServer: {
    command: 'npm run dev',
    port: 8000,
    reuseExistingServer: !process.env.CI,
  },
});