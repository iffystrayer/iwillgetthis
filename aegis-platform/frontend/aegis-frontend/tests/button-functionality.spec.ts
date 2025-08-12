import { test, expect } from '@playwright/test';

// Test configuration
const LOGIN_CREDENTIALS = {
  email: 'admin@aegis-platform.com',
  password: 'admin123'
};

test.describe('Button Functionality Tests - Manual Testing Verification', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAndNavigateToDashboard(page);
  });

  test('User Management Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing User Management Buttons ===');
    
    // Navigate to Users page
    await page.goto('/users');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot before testing
    await page.screenshot({ path: 'test-results/users-page-before-testing.png' });
    
    // Test Add User button
    console.log('Testing Add User button...');
    const addUserBtn = page.locator('button:has-text("Add User")').first();
    await expect(addUserBtn).toBeVisible();
    
    // Listen for dialog/alert
    page.on('dialog', async dialog => {
      console.log('✓ Add User alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Add User functionality');
      await dialog.accept();
    });
    
    await addUserBtn.click();
    await page.waitForTimeout(1000); // Allow time for dialog
    
    // Test Invite Users button
    console.log('Testing Invite Users button...');
    const inviteBtn = page.locator('button:has-text("Invite Users")').first();
    await expect(inviteBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Invite Users alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Invite Users functionality');
      await dialog.accept();
    });
    
    await inviteBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Edit User button if present
    console.log('Testing Edit User button...');
    const editBtn = page.locator('button:has-text("Edit")').first();
    if (await editBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ Edit User alert triggered:', dialog.message());
        expect(dialog.message()).toContain('Edit User functionality');
        await dialog.accept();
      });
      
      await editBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/users-page-after-testing.png' });
    console.log('✅ User Management buttons tested successfully');
  });

  test('Integration Management Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Integration Management Buttons ===');
    
    await page.goto('/integrations');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/integrations-page-before-testing.png' });
    
    // Test Add Integration button
    console.log('Testing Add Integration button...');
    const addIntegrationBtn = page.locator('button:has-text("Add Integration")').first();
    await expect(addIntegrationBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Add Integration alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Add Integration functionality');
      await dialog.accept();
    });
    
    await addIntegrationBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Sync All button
    console.log('Testing Sync All button...');
    const syncAllBtn = page.locator('button:has-text("Sync All")').first();
    await expect(syncAllBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Sync All alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Sync All functionality');
      await dialog.accept();
    });
    
    await syncAllBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Configure button if present
    console.log('Testing Configure button...');
    const configureBtn = page.locator('button:has-text("Configure")').first();
    if (await configureBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ Configure alert triggered:', dialog.message());
        expect(dialog.message()).toContain('Configure functionality');
        await dialog.accept();
      });
      
      await configureBtn.click();
      await page.waitForTimeout(1000);
    }
    
    // Test individual Sync button if present (not "Sync All")
    console.log('Testing individual Sync button...');
    const allSyncButtons = page.locator('button:has-text("Sync")');
    const syncAllButtons = page.locator('button:has-text("Sync All")');
    const syncBtnCount = await allSyncButtons.count();
    const syncAllCount = await syncAllButtons.count();
    
    if (syncBtnCount > syncAllCount) {
      // There are individual sync buttons beyond "Sync All"
      const syncBtn = allSyncButtons.nth(syncAllCount); // Get first non-"Sync All" button
      
      page.on('dialog', async dialog => {
        console.log('✓ Sync alert triggered:', dialog.message());
        expect(dialog.message()).toContain('Sync functionality');
        await dialog.accept();
      });
      
      await syncBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/integrations-page-after-testing.png' });
    console.log('✅ Integration Management buttons tested successfully');
  });

  test('Reports Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Reports Page Buttons ===');
    
    await page.goto('/reports');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/reports-page-before-testing.png' });
    
    // Test New Report button
    console.log('Testing New Report button...');
    const newReportBtn = page.locator('button:has-text("New Report")').first();
    await expect(newReportBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ New Report alert triggered:', dialog.message());
      expect(dialog.message()).toContain('New Report functionality');
      await dialog.accept();
    });
    
    await newReportBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Schedule Report button
    console.log('Testing Schedule Report button...');
    const scheduleBtn = page.locator('button:has-text("Schedule Report")').first();
    await expect(scheduleBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Schedule Report alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Schedule Report functionality');
      await dialog.accept();
    });
    
    await scheduleBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Download button if present
    console.log('Testing Download button...');
    const downloadBtn = page.locator('button:has-text("Download")').first();
    if (await downloadBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ Download alert triggered:', dialog.message());
        expect(dialog.message()).toContain('Download functionality');
        await dialog.accept();
      });
      
      await downloadBtn.click();
      await page.waitForTimeout(1000);
    }
    
    // Test View Details button if present
    console.log('Testing View Details button...');
    const viewDetailsBtn = page.locator('button:has-text("View Details")').first();
    if (await viewDetailsBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ View Details alert triggered:', dialog.message());
        expect(dialog.message()).toContain('View Details functionality');
        await dialog.accept();
      });
      
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/reports-page-after-testing.png' });
    console.log('✅ Reports page buttons tested successfully');
  });

  test('Tasks Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Tasks Page Buttons ===');
    
    await page.goto('/tasks');
    await page.waitForLoadState('networkidle');
    
    // Close any open modals before testing
    await closeOpenModals(page);
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'test-results/tasks-page-before-testing.png' });
    
    // Test New Task button
    console.log('Testing New Task button...');
    const newTaskBtn = page.locator('button:has-text("New Task")').first();
    await expect(newTaskBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ New Task alert triggered:', dialog.message());
      expect(dialog.message()).toContain('New Task functionality');
      await dialog.accept();
    });
    
    await newTaskBtn.click({ force: true });
    await page.waitForTimeout(1000);
    
    // Close any dialog that opened and wait
    await closeOpenModals(page);
    await page.waitForTimeout(1000);
    
    // Test View Calendar button
    console.log('Testing View Calendar button...');
    const calendarBtn = page.locator('button:has-text("View Calendar")').first();
    await expect(calendarBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ View Calendar alert triggered:', dialog.message());
      expect(dialog.message()).toContain('View Calendar functionality');
      await dialog.accept();
    });
    
    await calendarBtn.click({ force: true });
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test View Details button if present
    console.log('Testing View Details button...');
    const viewDetailsBtn = page.locator('button:has-text("View Details")').first();
    if (await viewDetailsBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ View Details alert triggered:', dialog.message());
        expect(dialog.message()).toContain('View Details functionality');
        await dialog.accept();
      });
      
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/tasks-page-after-testing.png' });
    console.log('✅ Tasks page buttons tested successfully');
  });

  test('Evidence Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Evidence Page Buttons ===');
    
    await page.goto('/evidence');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/evidence-page-before-testing.png' });
    
    // Test Upload Evidence button
    console.log('Testing Upload Evidence button...');
    const uploadBtn = page.locator('button:has-text("Upload Evidence")').first();
    await expect(uploadBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Upload Evidence alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Upload Evidence functionality');
      await dialog.accept();
    });
    
    await uploadBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Export All button
    console.log('Testing Export All button...');
    const exportBtn = page.locator('button:has-text("Export All")').first();
    await expect(exportBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Export All alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Export All functionality');
      await dialog.accept();
    });
    
    await exportBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Download button if present
    console.log('Testing Download button...');
    const downloadBtn = page.locator('button:has-text("Download")').first();
    if (await downloadBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ Download alert triggered:', dialog.message());
        expect(dialog.message()).toContain('Download functionality');
        await dialog.accept();
      });
      
      await downloadBtn.click();
      await page.waitForTimeout(1000);
    }
    
    // Test View Details button if present
    console.log('Testing View Details button...');
    const viewDetailsBtn = page.locator('button:has-text("View Details")').first();
    if (await viewDetailsBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ View Details alert triggered:', dialog.message());
        expect(dialog.message()).toContain('View Details functionality');
        await dialog.accept();
      });
      
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/evidence-page-after-testing.png' });
    console.log('✅ Evidence page buttons tested successfully');
  });

  test('Risk Register Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Risk Register Buttons ===');
    
    await page.goto('/risks');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/risks-page-before-testing.png' });
    
    // Test Add Risk button
    console.log('Testing Add Risk button...');
    const addRiskBtn = page.locator('button:has-text("Add Risk")').first();
    await expect(addRiskBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Add Risk alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Add Risk functionality');
      await dialog.accept();
    });
    
    await addRiskBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Risk Matrix button
    console.log('Testing Risk Matrix button...');
    const matrixBtn = page.locator('button:has-text("Risk Matrix")').first();
    await expect(matrixBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Risk Matrix alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Risk Matrix functionality');
      await dialog.accept();
    });
    
    await matrixBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test View Details button if present
    console.log('Testing View Details button...');
    const viewDetailsBtn = page.locator('button:has-text("View Details")').first();
    if (await viewDetailsBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ View Details alert triggered:', dialog.message());
        expect(dialog.message()).toContain('View Details functionality');
        await dialog.accept();
      });
      
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/risks-page-after-testing.png' });
    console.log('✅ Risk Register buttons tested successfully');
  });

  test('Assessments Page - Button Functionality', async ({ page }) => {
    console.log('\n=== Testing Assessments Page Buttons ===');
    
    await page.goto('/assessments');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/assessments-page-before-testing.png' });
    
    // Test New Assessment button
    console.log('Testing New Assessment button...');
    const newAssessmentBtn = page.locator('button:has-text("New Assessment")').first();
    await expect(newAssessmentBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ New Assessment alert triggered:', dialog.message());
      expect(dialog.message()).toContain('New Assessment functionality');
      await dialog.accept();
    });
    
    await newAssessmentBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Schedule button
    console.log('Testing Schedule button...');
    const scheduleBtn = page.locator('button:has-text("Schedule")').first();
    await expect(scheduleBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Schedule alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Schedule functionality');
      await dialog.accept();
    });
    
    await scheduleBtn.click();
    await page.waitForTimeout(1000);
    
    // Test Filters button
    console.log('Testing Filters button...');
    const filtersBtn = page.locator('button:has-text("Filters")').first();
    await expect(filtersBtn).toBeVisible();
    
    page.on('dialog', async dialog => {
      console.log('✓ Filters alert triggered:', dialog.message());
      expect(dialog.message()).toContain('Filters functionality');
      await dialog.accept();
    });
    
    await filtersBtn.click();
    await page.waitForTimeout(1000);
    
    // Test View Details button if present
    console.log('Testing View Details button...');
    const viewDetailsBtn = page.locator('button:has-text("View Details")').first();
    if (await viewDetailsBtn.count() > 0) {
      page.on('dialog', async dialog => {
        console.log('✓ View Details alert triggered:', dialog.message());
        expect(dialog.message()).toContain('View Details functionality');
        await dialog.accept();
      });
      
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'test-results/assessments-page-after-testing.png' });
    console.log('✅ Assessments page buttons tested successfully');
  });

  test('Comprehensive Button Functionality Summary', async ({ page }) => {
    console.log('\n=== Comprehensive Button Functionality Test ===');
    
    const pages = [
      { name: 'Users', path: '/users', buttons: ['Add User', 'Invite Users', 'Filters'] },
      { name: 'Integrations', path: '/integrations', buttons: ['Add Integration', 'Sync All'] },
      { name: 'Reports', path: '/reports', buttons: ['New Report', 'Schedule Report', 'Filters'] },
      { name: 'Tasks', path: '/tasks', buttons: ['New Task', 'View Calendar', 'Filters'] },
      { name: 'Evidence', path: '/evidence', buttons: ['Upload Evidence', 'Export All', 'Filters'] },
      { name: 'Risks', path: '/risks', buttons: ['Add Risk', 'Risk Matrix', 'Filters'] },
      { name: 'Assessments', path: '/assessments', buttons: ['New Assessment', 'Schedule', 'Filters'] }
    ];
    
    const testResults: any = {};
    
    for (const pageInfo of pages) {
      console.log(`\nTesting ${pageInfo.name} page...`);
      await page.goto(pageInfo.path);
      await page.waitForLoadState('networkidle');
      
      testResults[pageInfo.name] = {
        pageLoaded: true,
        buttonsFound: [],
        buttonsFunctional: []
      };
      
      for (const buttonText of pageInfo.buttons) {
        const button = page.locator(`button:has-text("${buttonText}")`).first();
        const isVisible = await button.count() > 0;
        
        if (isVisible) {
          testResults[pageInfo.name].buttonsFound.push(buttonText);
          console.log(`  ✓ Found button: ${buttonText}`);
          
          // Test click functionality
          let alertTriggered = false;
          page.on('dialog', async dialog => {
            alertTriggered = true;
            await dialog.accept();
          });
          
          await button.click();
          await page.waitForTimeout(500);
          
          if (alertTriggered) {
            testResults[pageInfo.name].buttonsFunctional.push(buttonText);
            console.log(`  ✓ Button functional: ${buttonText}`);
          } else {
            console.log(`  ⚠ Button not functional: ${buttonText}`);
          }
        } else {
          console.log(`  ✗ Button not found: ${buttonText}`);
        }
      }
    }
    
    // Generate summary report
    console.log('\n=== BUTTON FUNCTIONALITY TEST SUMMARY ===');
    let totalButtons = 0;
    let functionalButtons = 0;
    
    for (const [pageName, results] of Object.entries(testResults)) {
      const pageResults = results as any;
      console.log(`\n${pageName} Page:`);
      console.log(`  Buttons Found: ${pageResults.buttonsFound.length}`);
      console.log(`  Buttons Functional: ${pageResults.buttonsFunctional.length}`);
      
      totalButtons += pageResults.buttonsFound.length;
      functionalButtons += pageResults.buttonsFunctional.length;
      
      if (pageResults.buttonsFunctional.length === pageResults.buttonsFound.length) {
        console.log(`  Status: ✅ ALL BUTTONS WORKING`);
      } else {
        console.log(`  Status: ⚠ SOME BUTTONS NOT WORKING`);
      }
    }
    
    console.log(`\n=== OVERALL SUMMARY ===`);
    console.log(`Total Buttons Found: ${totalButtons}`);
    console.log(`Functional Buttons: ${functionalButtons}`);
    console.log(`Success Rate: ${Math.round((functionalButtons / totalButtons) * 100)}%`);
    
    if (functionalButtons === totalButtons) {
      console.log(`🎉 ALL BUTTONS ARE WORKING! Manual testing issues have been resolved.`);
    } else {
      console.log(`⚠ Some buttons still need attention.`);
    }
    
    // Save results to file
    await page.evaluate((results) => {
      localStorage.setItem('buttonTestResults', JSON.stringify(results));
    }, testResults);
    
    await page.screenshot({ path: 'test-results/button-functionality-summary.png' });
  });

});

// Helper function to close any open modals/dialogs
async function closeOpenModals(page: any) {
  try {
    // Try various methods to close modals
    const closeSelectors = [
      'button:has-text("Close")',
      'button:has-text("Cancel")', 
      'button[aria-label="Close"]',
      '[data-state="open"] button:last-child',
      '.dialog-close',
      '[role="dialog"] button:first-child'
    ];
    
    for (const selector of closeSelectors) {
      try {
        const elements = page.locator(selector);
        const count = await elements.count();
        for (let i = 0; i < count; i++) {
          const element = elements.nth(i);
          if (await element.isVisible({ timeout: 500 })) {
            await element.click({ timeout: 1000 });
            await page.waitForTimeout(300);
          }
        }
      } catch (e) {
        // Continue if element can't be clicked
      }
    }
    
    // Try pressing Escape key multiple times
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
    
  } catch (e) {
    console.log('Note: Some modals may still be open');
  }
}

// Helper function to login and navigate to dashboard
async function loginAndNavigateToDashboard(page: any) {
  await page.goto('/');
  
  // Fill login form
  const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
  const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
  const loginButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
  
  await emailInput.fill(LOGIN_CREDENTIALS.email);
  await passwordInput.fill(LOGIN_CREDENTIALS.password);
  await loginButton.click();
  
  // Wait for dashboard
  await page.waitForURL(/.*\/dashboard/, { timeout: 10000 });
  
  // Close any modals that might be open after login
  await closeOpenModals(page);
  await page.waitForTimeout(1000);
}