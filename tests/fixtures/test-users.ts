import type { Page } from '@playwright/test';

export async function loginUser(page: Page) {
  await page.goto('/debugLogin');
  await page.click('text=Login as User 1');
  await page.waitForURL('/');
}

export const TEST_USERS = {
  regular: {
    email: 'user1@test2.com',
    password: 'password'
  },
  admin: {
    email: 'admin@test2.com',
    password: 'password'
  }
};