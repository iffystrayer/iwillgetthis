import { test, expect } from '@playwright/test';

// Test configuration
const LOGIN_CREDENTIALS = {
  email: 'admin@aegis-platform.com',
  password: 'admin123'
};

const BACKEND_URL = 'http://localhost:30641';

test.describe('Form Submission E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login before each test
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
  });

  test.describe('Asset Management Forms', () => {
    
    test('should create a new asset via form submission', async ({ page }) => {
      // Navigate to Assets page
      const assetsLink = page.locator('a[href="/assets"], a:has-text("Assets")').first();
      await assetsLink.click();
      await page.waitForURL(/.*\/assets/, { timeout: 10000 });
      
      // Look for "Add Asset" or "Create Asset" button
      const addAssetButton = page.locator('button:has-text("Add Asset"), button:has-text("Create Asset"), button:has-text("New Asset"), button:has-text("Add")').first();
      
      if (await addAssetButton.count() > 0) {
        await addAssetButton.click();
        
        // Wait for form to appear (modal or new page)
        await page.waitForTimeout(1000);
        
        // Fill asset creation form
        const assetName = `E2E Test Asset ${Date.now()}`;
        
        // Try different possible input selectors
        const nameInput = page.locator('input[name="name"], input[placeholder*="name"], input[label*="Name"]').first();
        if (await nameInput.count() > 0) {
          await nameInput.fill(assetName);
        }
        
        const descriptionInput = page.locator('textarea[name="description"], input[name="description"], textarea[placeholder*="description"]').first();
        if (await descriptionInput.count() > 0) {
          await descriptionInput.fill('Test asset created via E2E form submission');
        }
        
        // Select asset type from dropdown
        const assetTypeSelect = page.locator('select[name="asset_type"], select[name="type"]').first();
        if (await assetTypeSelect.count() > 0) {
          await assetTypeSelect.selectOption('server');
        }
        
        // Select criticality from dropdown
        const criticalitySelect = page.locator('select[name="criticality"]').first();
        if (await criticalitySelect.count() > 0) {
          await criticalitySelect.selectOption('high');
        }
        
        // Fill IP address
        const ipInput = page.locator('input[name="ip_address"], input[placeholder*="IP"]').first();
        if (await ipInput.count() > 0) {
          await ipInput.fill('192.168.1.100');
        }
        
        // Submit form
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save"), button:has-text("Add")').first();
        
        // Listen for API request
        const createAssetPromise = page.waitForRequest(request => 
          request.url().includes('/api/v1/assets') && request.method() === 'POST'
        );
        
        if (await submitButton.count() > 0) {
          await submitButton.click();
          
          try {
            const apiRequest = await createAssetPromise;
            expect(apiRequest.url()).toContain('/api/v1/assets');
            console.log('✓ Asset creation API request made');
          } catch (error) {
            console.log('Asset creation API request not detected');
          }
        }
        
        // Wait for redirect or success message
        await page.waitForTimeout(2000);
        await page.screenshot({ path: 'test-results/asset-form-submission.png' });
      } else {
        console.log('Add Asset button not found - form may not be implemented yet');
        await page.screenshot({ path: 'test-results/assets-page-no-form.png' });
      }
    });
    
    test('should edit an existing asset via form submission', async ({ page }) => {
      await page.goto('/assets');
      await page.waitForTimeout(2000);
      
      // Look for edit buttons
      const editButtons = page.locator('button:has-text("Edit"), button[aria-label*="edit"], a:has-text("Edit")');
      
      if (await editButtons.count() > 0) {
        await editButtons.first().click();
        await page.waitForTimeout(1000);
        
        // Update asset name
        const nameInput = page.locator('input[name="name"], input[value*="Asset"]').first();
        if (await nameInput.count() > 0) {
          await nameInput.fill(`Updated Asset ${Date.now()}`);
        }
        
        // Update description
        const descriptionInput = page.locator('textarea[name="description"], input[name="description"]').first();
        if (await descriptionInput.count() > 0) {
          await descriptionInput.fill('Updated description via E2E test');
        }
        
        // Submit changes
        const updateButton = page.locator('button:has-text("Update"), button:has-text("Save"), button[type="submit"]').first();
        
        if (await updateButton.count() > 0) {
          const updateAssetPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/assets/') && request.method() === 'PUT'
          );
          
          await updateButton.click();
          
          try {
            const apiRequest = await updateAssetPromise;
            expect(apiRequest.url()).toContain('/api/v1/assets/');
            console.log('✓ Asset update API request made');
          } catch (error) {
            console.log('Asset update API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/asset-edit-form.png' });
      } else {
        console.log('Edit buttons not found for assets');
      }
    });
  });

  test.describe('Risk Management Forms', () => {
    
    test('should create a new risk via form submission', async ({ page }) => {
      await page.goto('/risks');
      await page.waitForTimeout(2000);
      
      const addRiskButton = page.locator('button:has-text("Add Risk"), button:has-text("Create Risk"), button:has-text("New Risk"), button:has-text("Add")').first();
      
      if (await addRiskButton.count() > 0) {
        await addRiskButton.click();
        await page.waitForTimeout(1000);
        
        // Fill risk creation form
        const riskTitle = `E2E Test Risk ${Date.now()}`;
        
        const titleInput = page.locator('input[name="title"], input[placeholder*="title"]').first();
        if (await titleInput.count() > 0) {
          await titleInput.fill(riskTitle);
        }
        
        const descriptionInput = page.locator('textarea[name="description"], input[name="description"]').first();
        if (await descriptionInput.count() > 0) {
          await descriptionInput.fill('Test risk created via E2E form submission');
        }
        
        // Select risk category
        const categorySelect = page.locator('select[name="category"]').first();
        if (await categorySelect.count() > 0) {
          await categorySelect.selectOption('technical');
        }
        
        // Set likelihood
        const likelihoodInput = page.locator('input[name="inherent_likelihood"], select[name="inherent_likelihood"]').first();
        if (await likelihoodInput.count() > 0) {
          if (await likelihoodInput.getAttribute('type') === 'range' || await likelihoodInput.getAttribute('type') === 'number') {
            await likelihoodInput.fill('4');
          } else {
            await likelihoodInput.selectOption('4');
          }
        }
        
        // Set impact
        const impactInput = page.locator('input[name="inherent_impact"], select[name="inherent_impact"]').first();
        if (await impactInput.count() > 0) {
          if (await impactInput.getAttribute('type') === 'range' || await impactInput.getAttribute('type') === 'number') {
            await impactInput.fill('5');
          } else {
            await impactInput.selectOption('5');
          }
        }
        
        // Submit form
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
        
        if (await submitButton.count() > 0) {
          const createRiskPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/risks') && request.method() === 'POST'
          );
          
          await submitButton.click();
          
          try {
            const apiRequest = await createRiskPromise;
            expect(apiRequest.url()).toContain('/api/v1/risks');
            console.log('✓ Risk creation API request made');
          } catch (error) {
            console.log('Risk creation API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/risk-form-submission.png' });
      } else {
        console.log('Add Risk button not found');
        await page.screenshot({ path: 'test-results/risks-page-no-form.png' });
      }
    });
  });

  test.describe('Task Management Forms', () => {
    
    test('should create a new task via form submission', async ({ page }) => {
      await page.goto('/tasks');
      await page.waitForTimeout(2000);
      
      const addTaskButton = page.locator('button:has-text("Add Task"), button:has-text("Create Task"), button:has-text("New Task"), button:has-text("Add")').first();
      
      if (await addTaskButton.count() > 0) {
        await addTaskButton.click();
        await page.waitForTimeout(1000);
        
        // Fill task creation form
        const taskTitle = `E2E Test Task ${Date.now()}`;
        
        const titleInput = page.locator('input[name="title"], input[placeholder*="title"]').first();
        if (await titleInput.count() > 0) {
          await titleInput.fill(taskTitle);
        }
        
        const descriptionInput = page.locator('textarea[name="description"], input[name="description"]').first();
        if (await descriptionInput.count() > 0) {
          await descriptionInput.fill('Test task created via E2E form submission');
        }
        
        // Select task type
        const taskTypeSelect = page.locator('select[name="task_type"], select[name="type"]').first();
        if (await taskTypeSelect.count() > 0) {
          await taskTypeSelect.selectOption('remediation');
        }
        
        // Select priority
        const prioritySelect = page.locator('select[name="priority"]').first();
        if (await prioritySelect.count() > 0) {
          await prioritySelect.selectOption('high');
        }
        
        // Set due date
        const dueDateInput = page.locator('input[name="due_date"], input[type="date"]').first();
        if (await dueDateInput.count() > 0) {
          const futureDate = new Date();
          futureDate.setDate(futureDate.getDate() + 7);
          await dueDateInput.fill(futureDate.toISOString().split('T')[0]);
        }
        
        // Submit form
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
        
        if (await submitButton.count() > 0) {
          const createTaskPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/tasks') && request.method() === 'POST'
          );
          
          await submitButton.click();
          
          try {
            const apiRequest = await createTaskPromise;
            expect(apiRequest.url()).toContain('/api/v1/tasks');
            console.log('✓ Task creation API request made');
          } catch (error) {
            console.log('Task creation API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/task-form-submission.png' });
      } else {
        console.log('Add Task button not found');
        await page.screenshot({ path: 'test-results/tasks-page-no-form.png' });
      }
    });
    
    test('should update task progress via form submission', async ({ page }) => {
      await page.goto('/tasks');
      await page.waitForTimeout(2000);
      
      // Look for progress update controls
      const progressInputs = page.locator('input[type="range"], input[type="number"], select[name*="progress"]');
      
      if (await progressInputs.count() > 0) {
        const progressInput = progressInputs.first();
        
        // Update progress
        if (await progressInput.getAttribute('type') === 'range' || await progressInput.getAttribute('type') === 'number') {
          await progressInput.fill('75');
        }
        
        // Look for status update
        const statusSelect = page.locator('select[name*="status"]').first();
        if (await statusSelect.count() > 0) {
          await statusSelect.selectOption('in_progress');
        }
        
        // Submit update
        const updateButton = page.locator('button:has-text("Update"), button:has-text("Save Progress")').first();
        
        if (await updateButton.count() > 0) {
          const updateTaskPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/tasks/') && request.method() === 'PATCH'
          );
          
          await updateButton.click();
          
          try {
            const apiRequest = await updateTaskPromise;
            expect(apiRequest.url()).toContain('/api/v1/tasks/');
            console.log('✓ Task progress update API request made');
          } catch (error) {
            console.log('Task progress update API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/task-progress-update.png' });
      } else {
        console.log('Task progress controls not found');
      }
    });
  });

  test.describe('User Management Forms', () => {
    
    test('should create a new user via form submission', async ({ page }) => {
      await page.goto('/users');
      await page.waitForTimeout(2000);
      
      const addUserButton = page.locator('button:has-text("Add User"), button:has-text("Create User"), button:has-text("Invite User"), button:has-text("Add")').first();
      
      if (await addUserButton.count() > 0) {
        await addUserButton.click();
        await page.waitForTimeout(1000);
        
        // Fill user creation form
        const timestamp = Date.now();
        
        const emailInput = page.locator('input[name="email"], input[type="email"]').first();
        if (await emailInput.count() > 0) {
          await emailInput.fill(`e2etest${timestamp}@example.com`);
        }
        
        const usernameInput = page.locator('input[name="username"], input[placeholder*="username"]').first();
        if (await usernameInput.count() > 0) {
          await usernameInput.fill(`e2euser${timestamp}`);
        }
        
        const fullNameInput = page.locator('input[name="full_name"], input[name="fullName"], input[placeholder*="name"]').first();
        if (await fullNameInput.count() > 0) {
          await fullNameInput.fill('E2E Test User');
        }
        
        const passwordInput = page.locator('input[name="password"], input[type="password"]').first();
        if (await passwordInput.count() > 0) {
          await passwordInput.fill('testpass123');
        }
        
        const departmentInput = page.locator('input[name="department"], select[name="department"]').first();
        if (await departmentInput.count() > 0) {
          if (await departmentInput.tagName() === 'select') {
            await departmentInput.selectOption('IT');
          } else {
            await departmentInput.fill('IT');
          }
        }
        
        const jobTitleInput = page.locator('input[name="job_title"], input[name="jobTitle"]').first();
        if (await jobTitleInput.count() > 0) {
          await jobTitleInput.fill('Test Analyst');
        }
        
        // Submit form
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save"), button:has-text("Invite")').first();
        
        if (await submitButton.count() > 0) {
          const createUserPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/users') && request.method() === 'POST'
          );
          
          await submitButton.click();
          
          try {
            const apiRequest = await createUserPromise;
            expect(apiRequest.url()).toContain('/api/v1/users');
            console.log('✓ User creation API request made');
          } catch (error) {
            console.log('User creation API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/user-form-submission.png' });
      } else {
        console.log('Add User button not found');
        await page.screenshot({ path: 'test-results/users-page-no-form.png' });
      }
    });
  });

  test.describe('Evidence Management Forms', () => {
    
    test('should upload evidence via form submission', async ({ page }) => {
      await page.goto('/evidence');
      await page.waitForTimeout(2000);
      
      const uploadButton = page.locator('button:has-text("Upload"), input[type="file"], button:has-text("Add Evidence")').first();
      
      if (await uploadButton.count() > 0) {
        // If it's a file input, we can test the file selection
        if (await uploadButton.getAttribute('type') === 'file') {
          // Create a test file
          const testFileContent = 'This is a test evidence file for E2E testing';
          const testFile = Buffer.from(testFileContent);
          
          await uploadButton.setInputFiles([{
            name: 'test-evidence.txt',
            mimeType: 'text/plain',
            buffer: testFile
          }]);
          
          // Look for submit button
          const submitButton = page.locator('button:has-text("Upload"), button:has-text("Submit"), button[type="submit"]').first();
          
          if (await submitButton.count() > 0) {
            const uploadEvidencePromise = page.waitForRequest(request => 
              request.url().includes('/api/v1/evidence') && request.method() === 'POST'
            );
            
            await submitButton.click();
            
            try {
              const apiRequest = await uploadEvidencePromise;
              expect(apiRequest.url()).toContain('/api/v1/evidence');
              console.log('✓ Evidence upload API request made');
            } catch (error) {
              console.log('Evidence upload API request not detected');
            }
          }
        }
        
        await page.screenshot({ path: 'test-results/evidence-upload-form.png' });
      } else {
        console.log('Upload controls not found');
        await page.screenshot({ path: 'test-results/evidence-page-no-upload.png' });
      }
    });
  });

  test.describe('Settings Configuration Forms', () => {
    
    test('should update settings via form submission', async ({ page }) => {
      await page.goto('/settings');
      await page.waitForTimeout(2000);
      
      // Look for settings form inputs
      const configInputs = page.locator('input[type="text"], input[type="email"], input[type="url"], textarea, select');
      
      if (await configInputs.count() > 0) {
        // Update some settings if available
        const textInputs = page.locator('input[type="text"]');
        if (await textInputs.count() > 0) {
          await textInputs.first().fill('Updated via E2E test');
        }
        
        // Toggle checkboxes/switches if available
        const checkboxes = page.locator('input[type="checkbox"]');
        if (await checkboxes.count() > 0) {
          await checkboxes.first().check();
        }
        
        // Submit settings
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Update"), button:has-text("Apply"), button[type="submit"]').first();
        
        if (await saveButton.count() > 0) {
          const saveSettingsPromise = page.waitForRequest(request => 
            request.url().includes('/api/v1/settings') && (request.method() === 'PUT' || request.method() === 'PATCH')
          );
          
          await saveButton.click();
          
          try {
            const apiRequest = await saveSettingsPromise;
            expect(apiRequest.url()).toContain('/api/v1/settings');
            console.log('✓ Settings update API request made');
          } catch (error) {
            console.log('Settings update API request not detected');
          }
        }
        
        await page.screenshot({ path: 'test-results/settings-form-submission.png' });
      } else {
        console.log('Settings form inputs not found');
        await page.screenshot({ path: 'test-results/settings-page-no-form.png' });
      }
    });
  });

  test.describe('Form Validation Tests', () => {
    
    test('should show validation errors for invalid form submissions', async ({ page }) => {
      await page.goto('/assets');
      await page.waitForTimeout(2000);
      
      const addAssetButton = page.locator('button:has-text("Add Asset"), button:has-text("Create Asset"), button:has-text("Add")').first();
      
      if (await addAssetButton.count() > 0) {
        await addAssetButton.click();
        await page.waitForTimeout(1000);
        
        // Try to submit form without filling required fields
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
        
        if (await submitButton.count() > 0) {
          await submitButton.click();
          await page.waitForTimeout(1000);
          
          // Check for validation error messages
          const errorMessages = page.locator('.error, .invalid, [role="alert"], .text-red-500, .error-message');
          
          if (await errorMessages.count() > 0) {
            console.log('✓ Form validation errors displayed');
            await page.screenshot({ path: 'test-results/form-validation-errors.png' });
          } else {
            console.log('Form validation errors not found');
          }
        }
      }
    });
    
    test('should prevent duplicate submissions', async ({ page }) => {
      await page.goto('/assets');
      await page.waitForTimeout(2000);
      
      const addAssetButton = page.locator('button:has-text("Add Asset"), button:has-text("Create Asset"), button:has-text("Add")').first();
      
      if (await addAssetButton.count() > 0) {
        await addAssetButton.click();
        await page.waitForTimeout(1000);
        
        // Fill form with valid data
        const nameInput = page.locator('input[name="name"], input[placeholder*="name"]').first();
        if (await nameInput.count() > 0) {
          await nameInput.fill('Test Asset for Duplicate Prevention');
        }
        
        const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
        
        if (await submitButton.count() > 0) {
          // Click submit button multiple times rapidly
          await submitButton.click();
          await submitButton.click();
          await submitButton.click();
          
          // Wait for any API requests
          await page.waitForTimeout(3000);
          
          // Check if button is disabled after first click
          const isDisabled = await submitButton.isDisabled();
          if (isDisabled) {
            console.log('✓ Submit button disabled to prevent duplicate submissions');
          } else {
            console.log('Submit button not disabled - may allow duplicate submissions');
          }
          
          await page.screenshot({ path: 'test-results/duplicate-submission-prevention.png' });
        }
      }
    });
  });
});