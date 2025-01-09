import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should allow user to register', async ({ page }) => {
    await page.goto('/register');
    
    // Fill registration form
    await page.fill('#name', 'Test User');
    await page.fill('#email', `test-${Date.now()}@example.com`);
    await page.fill('#password', 'password123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to home
    await expect(page).toHaveURL('/');
  });

  test('should allow user to login', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('#email', 'demo@demo.com');
    await page.fill('#password', 'demodemo');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/');
  });
});