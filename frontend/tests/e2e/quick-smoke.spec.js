/**
 * Quick smoke test - catches major breakage without being slow
 */

import { test, expect } from '@playwright/test';

test('App works and login doesn\'t infinite loop', async ({ page }) => {
  test.setTimeout(15000); // 15 second max
  
  await page.goto('/');
  await page.waitForTimeout(2000);
  
  // Basic smoke test - app loaded
  const title = await page.title();
  expect(title).toContain('iCal');
  
  // Check for infinite reload (this would catch the login issue)
  let reloadCount = 0;
  page.on('load', () => {
    reloadCount++;
    if (reloadCount > 3) {
      throw new Error('Too many page reloads - possible infinite loop!');
    }
  });
  
  await page.waitForTimeout(3000);
  expect(reloadCount).toBeLessThan(3);
  
  console.log('✅ App loads without infinite loops');
});