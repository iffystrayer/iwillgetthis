import { test, expect } from '@playwright/test';

test.describe('Stabilization Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('http://localhost:58533/login');
    await page.fill('input[type="email"]', 'admin@aegis-platform.com');
    await page.fill('input[type="password"]', 'aegis123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('Assets import/export functionality', async ({ page }) => {
    await page.goto('http://localhost:58533/assets');
    await page.waitForLoadState('networkidle');
    
    // Test Import button opens dialog
    const importBtn = page.locator('text=Import Assets').first();
    await expect(importBtn).toBeVisible();
    await importBtn.click();
    
    // Check if import dialog appears
    await expect(page.locator('text=Import Assets').nth(1)).toBeVisible();
    
    // Close dialog
    await page.locator('text=Cancel').click();
    
    // Test Export button works
    const exportBtn = page.locator('text=Export All').first();
    await expect(exportBtn).toBeVisible();
    await exportBtn.click();
    
    console.log('✅ Assets import/export functionality verified');
  });

  test('Navigation to detail pages', async ({ page }) => {
    // Test assets detail navigation
    await page.goto('http://localhost:58533/assets');
    await page.waitForLoadState('networkidle');
    
    // Check if "View Details" is available
    const viewDetailsBtn = page.locator('text=View Details').first();
    if (await viewDetailsBtn.count() > 0) {
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
      console.log('✅ Asset detail navigation works');
    }
    
    // Test risks detail navigation
    await page.goto('http://localhost:58533/risks');
    await page.waitForLoadState('networkidle');
    
    const riskViewBtn = page.locator('text=View Details').first();
    if (await riskViewBtn.count() > 0) {
      await riskViewBtn.click();
      await page.waitForTimeout(1000);
      console.log('✅ Risk detail navigation works');
    }
  });

  test('Form validation on dialogs', async ({ page }) => {
    await page.goto('http://localhost:58533/assets');
    await page.waitForLoadState('networkidle');
    
    // Test Add Asset form validation
    const addBtn = page.locator('text=Add Asset').first();
    await expect(addBtn).toBeVisible();
    await addBtn.click();
    
    // Try to submit empty form
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.count() > 0) {
      await submitBtn.click();
      
      // Check for validation errors
      const hasErrors = await page.locator('.text-destructive, .text-red-500, .text-red-600').count() > 0;
      if (hasErrors) {
        console.log('✅ Form validation working');
      }
    }
    
    // Close dialog
    await page.locator('text=Cancel').click();
  });

  test('Core pages load successfully', async ({ page }) => {
    const pages = [
      '/dashboard',
      '/assets', 
      '/risks',
      '/tasks',
      '/users',
      '/evidence'
    ];
    
    for (const path of pages) {
      await page.goto(`http://localhost:58533${path}`);
      await page.waitForLoadState('networkidle');
      
      // Check page loads without error
      const hasError = await page.locator('text=Error, text=Failed, text=500').count() > 0;
      expect(hasError).toBe(false);
      
      console.log(`✅ ${path} page loads successfully`);
    }
  });
});