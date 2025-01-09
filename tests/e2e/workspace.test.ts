import { test, expect } from '@playwright/test';

// Configure timeout for the entire test file
test.setTimeout(5000); // 5 seconds max for each test

test.describe('Workspace and Channel Interactions', () => {
  // Setup: Login before each test
  test.beforeEach(async ({ page }) => {
    // Set shorter timeout for actions
    page.setDefaultTimeout(2000); // 2 seconds timeout for all actions
    
    await page.goto('/login');
    await page.fill('#email', 'demo@demo.com');
    await page.fill('#password', 'demodemo');
    await page.click('button[type="submit"]');
    await expect(page, 'Should redirect to home after login').toHaveURL('/', { timeout: 2000 });
  });

  test('should create and join a workspace', async ({ page }) => {
    // Click create workspace button with strict assertion
    const createButton = page.getByRole('button', { name: 'Create New Workspace' });
    await expect(createButton, 'Create Workspace button should be visible').toBeVisible({ timeout: 2000 });
    await createButton.click();
    
    // Fill workspace creation form in dialog
    const workspaceName = `Test Workspace ${Date.now()}`;
    const nameInput = page.locator('input[name="workspace_name"]');
    await expect(nameInput, 'Workspace name input should be visible').toBeVisible({ timeout: 2000 });
    await nameInput.fill(workspaceName);
    
    const descInput = page.locator('input[name="workspace_description"]');
    await expect(descInput, 'Workspace description input should be visible').toBeVisible({ timeout: 2000 });
    await descInput.fill('Test workspace description');
    
    const submitButton = page.getByRole('button', { name: /submit|create/i });
    await expect(submitButton, 'Submit button should be visible').toBeVisible({ timeout: 2000 });
    await submitButton.click();
    
    // Verify workspace appears with strict assertions
    await expect(page.getByText(workspaceName), 'New workspace should appear in the list').toBeVisible({ timeout: 2000 });
    
    const workspaceCard = page.locator('.grid').getByText(workspaceName).locator('xpath=ancestor::*[contains(@class, "card")]');
    await expect(workspaceCard.getByText('0 members'), 'Member count should be visible').toBeVisible({ timeout: 2000 });
    await expect(workspaceCard.getByRole('button', { name: 'Enter Workspace' }), 'Enter button should be visible').toBeVisible({ timeout: 2000 });
  });

  test('should navigate workspace and create channel', async ({ page }) => {
    const enterButton = page.getByRole('button', { name: 'Enter Workspace' }).first();
    await expect(enterButton, 'Enter Workspace button should be visible').toBeVisible({ timeout: 2000 });
    await enterButton.click();
    
    // Verify empty state with strict assertions
    await expect(page.getByText('No Channels Yet'), 'Empty state message should be visible').toBeVisible({ timeout: 2000 });
    await expect(page.getByText('Channels will appear here once they\'re created'), 'Empty state description should be visible').toBeVisible({ timeout: 2000 });
    
    const createChannelButton = page.getByRole('button', { name: 'Create Channel' });
    await expect(createChannelButton, 'Create Channel button should be visible').toBeVisible({ timeout: 2000 });
    await createChannelButton.click();
    
    const channelName = `test-channel-${Date.now()}`;
    const nameInput = page.locator('input[name="name"]');
    await expect(nameInput, 'Channel name input should be visible').toBeVisible({ timeout: 2000 });
    await nameInput.fill(channelName);
    
    const submitButton = page.getByRole('button', { name: /submit|create/i });
    await expect(submitButton, 'Submit button should be visible').toBeVisible({ timeout: 2000 });
    await submitButton.click();
    
    await expect(page.getByText(channelName), 'New channel should appear in the list').toBeVisible({ timeout: 2000 });
  });

  test('should send and react to messages in channel', async ({ page }) => {
    const enterButton = page.getByRole('button', { name: 'Enter Workspace' }).first();
    await expect(enterButton, 'Enter Workspace button should be visible').toBeVisible({ timeout: 2000 });
    await enterButton.click();

    const generalChannel = page.getByText('general');
    await expect(generalChannel, 'General channel should be visible').toBeVisible({ timeout: 2000 });
    await generalChannel.click();
    
    await expect(page.locator('.channel-header'), 'Channel header should be visible').toBeVisible({ timeout: 2000 });
    
    const messageInput = page.locator('div[contenteditable="true"]');
    await expect(messageInput, 'Message input should be visible').toBeVisible({ timeout: 2000 });
    
    const testMessage = `Test message ${Date.now()}`;
    await messageInput.fill(testMessage);
    await page.keyboard.press('Enter');
    
    await expect(page.locator('.message-list').getByText(testMessage), 'Message should appear in the list').toBeVisible({ timeout: 2000 });
    
    const lastMessage = page.locator('.message-list > div').last();
    await lastMessage.hover();
    
    const reactionButton = lastMessage.getByRole('button', { name: 'Add reaction' });
    await expect(reactionButton, 'Reaction button should be visible').toBeVisible({ timeout: 2000 });
    await reactionButton.click();
    
    const emojiButton = page.getByRole('button', { name: '👍' });
    await expect(emojiButton, 'Emoji button should be visible').toBeVisible({ timeout: 2000 });
    await emojiButton.click();
    
    await expect(lastMessage.getByText('👍'), 'Reaction should be visible').toBeVisible({ timeout: 2000 });
  });

  test('should manage workspace notifications', async ({ page }) => {
    const workspaceCard = page.locator('.grid > div').first();
    await expect(workspaceCard, 'Workspace card should be visible').toBeVisible({ timeout: 2000 });
    
    const notificationButton = workspaceCard.getByRole('button', { name: 'Notifications' });
    await expect(notificationButton, 'Notification button should be visible').toBeVisible({ timeout: 2000 });
    await notificationButton.click();
    
    // Verify and click each notification option with strict assertions
    const options = ['Workspace Updates', '@Mentions', 'All Messages'];
    for (const option of options) {
      const checkbox = page.getByRole('menuitemcheckbox', { name: option });
      await expect(checkbox, `${option} checkbox should be visible`).toBeVisible({ timeout: 2000 });
      await checkbox.click();
    }
    
    await page.click('body');
    await expect(page.getByRole('menu'), 'Menu should be hidden').not.toBeVisible({ timeout: 2000 });
  });
}); 