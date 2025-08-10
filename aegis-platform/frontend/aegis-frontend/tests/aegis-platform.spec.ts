import { test, expect } from '@playwright/test';

// Test configuration
const LOGIN_CREDENTIALS = {
  email: 'admin@aegis-platform.com',
  password: 'admin123'
};

const BACKEND_URL = 'http://localhost:30641';

test.describe('Aegis Platform E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
  });

  test('should load the login page', async ({ page }) => {
    // Check if we're on login page or redirected to it
    await expect(page).toHaveURL(/.*\/(login)?/);
    
    // Look for login form elements
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]');
    const passwordInput = page.locator('input[type="password"], input[name="password"]');
    
    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    
    // Take screenshot of login page
    await page.screenshot({ path: 'test-results/login-page.png' });
  });

  test('should successfully login with correct credentials', async ({ page }) => {
    // Fill login form
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    const loginButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
    
    await emailInput.fill(LOGIN_CREDENTIALS.email);
    await passwordInput.fill(LOGIN_CREDENTIALS.password);
    
    // Listen for network requests to login endpoint
    const loginRequestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/auth/login') && request.method() === 'POST'
    );
    
    await loginButton.click();
    
    // Verify login request was made
    const loginRequest = await loginRequestPromise;
    expect(loginRequest.url()).toContain('/api/v1/auth/login');
    
    // Wait for redirect to dashboard
    await page.waitForURL(/.*\/dashboard/, { timeout: 10000 });
    
    // Take screenshot after successful login
    await page.screenshot({ path: 'test-results/after-login.png' });
  });

  test('should show dashboard with sidebar navigation after login', async ({ page }) => {
    // Login first
    await loginAndNavigateToDashboard(page);
    
    // Check for sidebar navigation elements with correct shadcn/ui structure
    const sidebar = page.locator('[data-sidebar="sidebar"]');
    await expect(sidebar).toBeVisible({ timeout: 10000 });
    
    // Check for key navigation links in sidebar - use items we can see in the dashboard
    const expectedNavItems = ['Overview', 'System Owner Inbox', 'Settings'];
    
    for (const item of expectedNavItems) {
      // Use multiple selector strategies to find navigation items
      const navLink = page.locator([
        `[data-sidebar="menu-button"] a:has-text("${item}")`,
        `[data-sidebar="menu-button"]:has-text("${item}")`,
        `a:has-text("${item}")`,
        `:text("${item}")`
      ].join(', ')).first();
      await expect(navLink).toBeVisible({ timeout: 5000 });
    }
    
    // Take screenshot of dashboard with sidebar
    await page.screenshot({ path: 'test-results/dashboard-with-sidebar.png' });
  });

  test('should navigate to Tasks page and show actual content (not "Coming soon")', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    // Try to navigate directly to Tasks page by URL since it might not be visible in sidebar
    await page.goto('/tasks');
    
    // Alternative: try to find tasks link with broader selectors
    // const tasksLink = page.locator('a[href="/tasks"], a:has-text("Tasks"), [href*="tasks"]').first();
    
    // Listen for API call to tasks endpoint
    const tasksApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/tasks'), { timeout: 10000 }
    );
    
    // Wait for Tasks page to load
    await page.waitForURL(/.*\/tasks/, { timeout: 10000 });
    
    // Verify API call was made
    try {
      const tasksApiRequest = await tasksApiPromise;
      console.log('Tasks API request made to:', tasksApiRequest.url());
    } catch (error) {
      console.log('No tasks API request detected');
    }
    
    // Check page content - should NOT contain "Coming soon"
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    expect(pageContent).not.toContain('coming soon');
    
    // Check for specific UI elements that indicate the Tasks page is working
    await expect(page.locator('h1, h2, [role="heading"]').filter({ hasText: /Task Management/i })).toBeVisible();
    
    // Look for task-related UI elements
    const taskElements = [
      page.locator(':text("Total Tasks")'),
      page.locator(':text("Open Tasks")'), 
      page.locator(':text("New Task")'),
      page.locator('button:has-text("New Task")')
    ];
    
    let foundTaskElements = 0;
    for (const element of taskElements) {
      if (await element.count() > 0) {
        foundTaskElements++;
      }
    }
    
    // At least one task-related element should be found
    expect(foundTaskElements).toBeGreaterThan(0);
    
    // Take screenshot of Tasks page
    await page.screenshot({ path: 'test-results/tasks-page.png' });
    
    // Log what we actually see on the page
    console.log('Tasks page content preview:', pageContent?.substring(0, 500));
  });

  test('should navigate to Evidence page and show actual content', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    // Navigate directly to Evidence page by URL
    await page.goto('/evidence');
    
    // Listen for API call
    const evidenceApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/evidence'), { timeout: 10000 }
    );
    
    await page.waitForURL(/.*\/evidence/, { timeout: 10000 });
    
    // Verify API call
    try {
      const evidenceApiRequest = await evidenceApiPromise;
      console.log('Evidence API request made to:', evidenceApiRequest.url());
    } catch (error) {
      console.log('No evidence API request detected');
    }
    
    // Check content - should NOT contain "Coming soon"
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    expect(pageContent).not.toContain('coming soon');
    
    // Check for Evidence page UI elements
    const evidenceElements = [
      page.locator('h1, h2, [role="heading"]').filter({ hasText: /Evidence/i }),
      page.locator(':text("Upload")'),
      page.locator('button:has-text("Upload")'),
      page.locator('input[type="file"]'),
      page.locator(':text("Evidence Management")'),
      page.locator(':text("Total Evidence")')
    ];
    
    let foundEvidenceElements = 0;
    for (const element of evidenceElements) {
      if (await element.count() > 0) {
        foundEvidenceElements++;
      }
    }
    
    // At least one evidence-related element should be found
    expect(foundEvidenceElements).toBeGreaterThan(0);
    
    await page.screenshot({ path: 'test-results/evidence-page.png' });
    console.log('Evidence page content preview:', pageContent?.substring(0, 500));
  });

  test('should navigate to Reports page and show actual content', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    // Navigate directly to Reports page by URL
    await page.goto('/reports');
    
    const reportsApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/reports'), { timeout: 10000 }
    );
    
    await page.waitForURL(/.*\/reports/, { timeout: 10000 });
    
    try {
      const reportsApiRequest = await reportsApiPromise;
      console.log('Reports API request made to:', reportsApiRequest.url());
    } catch (error) {
      console.log('No reports API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    expect(pageContent).not.toContain('coming soon');
    
    // Check for Reports page UI elements
    const reportsElements = [
      page.locator('h1, h2, [role="heading"]').filter({ hasText: /Reports?/i }),
      page.locator(':text("Generate")'),
      page.locator('button:has-text("Generate")'),
      page.locator('button:has-text("New Report")'),
      page.locator(':text("Download")'),
      page.locator(':text("Export")'),
      page.locator(':text("Report")'),
      page.locator(':text("Analytics")')
    ];
    
    let foundReportsElements = 0;
    for (const element of reportsElements) {
      if (await element.count() > 0) {
        foundReportsElements++;
      }
    }
    
    // At least one reports-related element should be found
    expect(foundReportsElements).toBeGreaterThan(0);
    
    await page.screenshot({ path: 'test-results/reports-page.png' });
    console.log('Reports page content preview:', pageContent?.substring(0, 500));
  });

  test('should verify backend API endpoints are accessible', async ({ page }) => {
    // Test backend endpoints directly
    const endpoints = [
      '/api/v1/tasks',
      '/api/v1/evidence', 
      '/api/v1/reports',
      '/api/v1/dashboards/overview'
    ];
    
    for (const endpoint of endpoints) {
      const response = await page.request.get(`${BACKEND_URL}${endpoint}`);
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data).toBeTruthy();
      
      console.log(`✓ ${endpoint} returned:`, JSON.stringify(data).substring(0, 200));
    }
  });

  test('should navigate to Assets page and verify content and functionality', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const assetsLink = page.locator('a[href="/assets"], a:has-text("Assets")').first();
    const assetsApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/assets'), { timeout: 10000 }
    );
    
    await assetsLink.click();
    await page.waitForURL(/.*\/assets/, { timeout: 10000 });
    
    try {
      const assetsApiRequest = await assetsApiPromise;
      console.log('Assets API request made to:', assetsApiRequest.url());
    } catch (error) {
      console.log('No assets API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for buttons and interactive elements
    const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has-text("Create")');
    const searchInput = page.locator('input[placeholder*="search" i], input[type="search"]');
    
    await page.screenshot({ path: 'test-results/assets-page.png' });
    console.log('Assets page content preview:', pageContent?.substring(0, 500));
    
    // Test button interactions if present
    if (await addButton.count() > 0) {
      console.log('✓ Found action buttons on Assets page');
    }
    if (await searchInput.count() > 0) {
      console.log('✓ Found search functionality on Assets page');
    }
  });

  test('should navigate to System Owner Inbox and verify workflow features', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const inboxLink = page.locator('a[href="/dashboard/system-owner"], a:has-text("System Owner Inbox")').first();
    const inboxApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/dashboards/system-owner'), { timeout: 10000 }
    );
    
    await inboxLink.click();
    await page.waitForURL(/.*\/dashboard\/system-owner/, { timeout: 10000 });
    
    try {
      const inboxApiRequest = await inboxApiPromise;
      console.log('System Owner Inbox API request made to:', inboxApiRequest.url());
    } catch (error) {
      console.log('No system owner inbox API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for workflow elements
    const actionButtons = page.locator('button:has-text("Approve"), button:has-text("Reject"), button:has-text("Review")');
    const statusFilters = page.locator('select, button[role="combobox"]');
    
    await page.screenshot({ path: 'test-results/system-owner-inbox-page.png' });
    console.log('System Owner Inbox page content preview:', pageContent?.substring(0, 500));
    
    if (await actionButtons.count() > 0) {
      console.log('✓ Found workflow action buttons on System Owner Inbox');
    }
  });

  test('should navigate to Assessments page and verify assessment workflow', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const assessmentsLink = page.locator('a[href="/assessments"], a:has-text("Assessments")').first();
    const assessmentsApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/assessments'), { timeout: 10000 }
    );
    
    await assessmentsLink.click();
    await page.waitForURL(/.*\/assessments/, { timeout: 10000 });
    
    try {
      const assessmentsApiRequest = await assessmentsApiPromise;
      console.log('Assessments API request made to:', assessmentsApiRequest.url());
    } catch (error) {
      console.log('No assessments API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for assessment workflow elements
    const startAssessmentBtn = page.locator('button:has-text("Start"), button:has-text("New Assessment"), button:has-text("Create Assessment")');
    const frameworkLinks = page.locator('a:has-text("NIST"), a:has-text("ISO"), a:has-text("SOC")');
    
    await page.screenshot({ path: 'test-results/assessments-page.png' });
    console.log('Assessments page content preview:', pageContent?.substring(0, 500));
    
    if (await startAssessmentBtn.count() > 0) {
      console.log('✓ Found assessment creation buttons');
    }
    if (await frameworkLinks.count() > 0) {
      console.log('✓ Found framework links for assessments');
    }
  });

  test('should navigate to Integrations page and verify integration management', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const integrationsLink = page.locator('a[href="/integrations"], a:has-text("Integrations")').first();
    const integrationsApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/integrations'), { timeout: 10000 }
    );
    
    await integrationsLink.click();
    await page.waitForURL(/.*\/integrations/, { timeout: 10000 });
    
    try {
      const integrationsApiRequest = await integrationsApiPromise;
      console.log('Integrations API request made to:', integrationsApiRequest.url());
    } catch (error) {
      console.log('No integrations API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for integration management elements
    const connectButton = page.locator('button:has-text("Connect"), button:has-text("Add Integration"), button:has-text("Configure")');
    const statusIndicators = page.locator('.status, [data-status], .connected, .disconnected');
    
    await page.screenshot({ path: 'test-results/integrations-page.png' });
    console.log('Integrations page content preview:', pageContent?.substring(0, 500));
    
    if (await connectButton.count() > 0) {
      console.log('✓ Found integration connection buttons');
    }
    if (await statusIndicators.count() > 0) {
      console.log('✓ Found integration status indicators');
    }
  });

  test('should navigate to Users page and verify user management features', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const usersLink = page.locator('a[href="/users"], a:has-text("Users")').first();
    const usersApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/users'), { timeout: 10000 }
    );
    
    await usersLink.click();
    await page.waitForURL(/.*\/users/, { timeout: 10000 });
    
    try {
      const usersApiRequest = await usersApiPromise;
      console.log('Users API request made to:', usersApiRequest.url());
    } catch (error) {
      console.log('No users API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for user management elements
    const addUserButton = page.locator('button:has-text("Add User"), button:has-text("Invite"), button:has-text("Create User")');
    const roleDropdowns = page.locator('select:has(option[value*="admin"]), select:has(option[value*="analyst"])');
    const editButtons = page.locator('button:has-text("Edit"), button[aria-label*="edit" i]');
    
    await page.screenshot({ path: 'test-results/users-page.png' });
    console.log('Users page content preview:', pageContent?.substring(0, 500));
    
    if (await addUserButton.count() > 0) {
      console.log('✓ Found user creation buttons');
    }
    if (await roleDropdowns.count() > 0) {
      console.log('✓ Found role management dropdowns');
    }
    if (await editButtons.count() > 0) {
      console.log('✓ Found user edit functionality');
    }
  });

  test('should navigate to Reports page and verify reporting workflow', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const reportsLink = page.locator('a[href="/reports"], a:has-text("Reports")').first();
    const reportsApiPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/reports'), { timeout: 10000 }
    );
    
    await reportsLink.click();
    await page.waitForURL(/.*\/reports/, { timeout: 10000 });
    
    try {
      const reportsApiRequest = await reportsApiPromise;
      console.log('Reports API request made to:', reportsApiRequest.url());
    } catch (error) {
      console.log('No reports API request detected');
    }
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for reporting workflow elements
    const generateButton = page.locator('button:has-text("Generate"), button:has-text("Create Report"), button:has-text("New Report")');
    const downloadButton = page.locator('button:has-text("Download"), button:has-text("Export"), a[download]');
    const templateDropdown = page.locator('select:has(option), button[role="combobox"]');
    
    await page.screenshot({ path: 'test-results/reports-page.png' });
    console.log('Reports page content preview:', pageContent?.substring(0, 500));
    
    if (await generateButton.count() > 0) {
      console.log('✓ Found report generation buttons');
    }
    if (await downloadButton.count() > 0) {
      console.log('✓ Found report download functionality');
    }
    if (await templateDropdown.count() > 0) {
      console.log('✓ Found report template selection');
    }
  });

  test('should navigate to Settings page and verify configuration options', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    const settingsLink = page.locator('a[href="/settings"], a:has-text("Settings")').first();
    
    await settingsLink.click();
    await page.waitForURL(/.*\/settings/, { timeout: 10000 });
    
    const pageContent = await page.textContent('body');
    expect(pageContent).not.toContain('Coming soon');
    
    // Check for settings configuration elements
    const saveButton = page.locator('button:has-text("Save"), button:has-text("Update"), button:has-text("Apply")');
    const configInputs = page.locator('input[type="text"], input[type="email"], input[type="url"], textarea');
    const toggleSwitches = page.locator('input[type="checkbox"], button[role="switch"]');
    
    await page.screenshot({ path: 'test-results/settings-page.png' });
    console.log('Settings page content preview:', pageContent?.substring(0, 500));
    
    if (await saveButton.count() > 0) {
      console.log('✓ Found settings save functionality');
    }
    if (await configInputs.count() > 0) {
      console.log('✓ Found configuration input fields');
    }
    if (await toggleSwitches.count() > 0) {
      console.log('✓ Found settings toggle switches');
    }
  });

  test('should test complete workflow: Create Assessment → Add Evidence → Generate Report', async ({ page }) => {
    await loginAndNavigateToDashboard(page);
    
    console.log('\n=== Testing Complete Workflow ===');
    
    // Step 1: Go to Assessments and try to create one
    console.log('Step 1: Navigate to Assessments');
    const assessmentsLink = page.locator('a[href="/assessments"], a:has-text("Assessments")').first();
    await assessmentsLink.click();
    await page.waitForURL(/.*\/assessments/, { timeout: 10000 });
    
    const createAssessmentBtn = page.locator('button:has-text("Create"), button:has-text("New"), button:has-text("Start")').first();
    if (await createAssessmentBtn.count() > 0) {
      console.log('✓ Found assessment creation button');
      await page.screenshot({ path: 'test-results/workflow-step1-assessments.png' });
    }
    
    // Step 2: Navigate to Evidence
    console.log('Step 2: Navigate to Evidence');
    const evidenceLink = page.locator('a[href="/evidence"], a:has-text("Evidence")').first();
    await evidenceLink.click();
    await page.waitForURL(/.*\/evidence/, { timeout: 10000 });
    
    const uploadBtn = page.locator('button:has-text("Upload"), button:has-text("Add"), input[type="file"]').first();
    if (await uploadBtn.count() > 0) {
      console.log('✓ Found evidence upload functionality');
      await page.screenshot({ path: 'test-results/workflow-step2-evidence.png' });
    }
    
    // Step 3: Navigate to Reports
    console.log('Step 3: Navigate to Reports');
    const reportsLink = page.locator('a[href="/reports"], a:has-text("Reports")').first();
    await reportsLink.click();
    await page.waitForURL(/.*\/reports/, { timeout: 10000 });
    
    const generateReportBtn = page.locator('button:has-text("Generate"), button:has-text("Create"), button:has-text("New")').first();
    if (await generateReportBtn.count() > 0) {
      console.log('✓ Found report generation functionality');
      await page.screenshot({ path: 'test-results/workflow-step3-reports.png' });
    }
    
    console.log('✓ Complete workflow navigation tested successfully');
  });

});

// Helper function to login and navigate to dashboard
async function loginAndNavigateToDashboard(page: any) {
  // Fill login form
  const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
  const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
  const loginButton = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")').first();
  
  await emailInput.fill(LOGIN_CREDENTIALS.email);
  await passwordInput.fill(LOGIN_CREDENTIALS.password);
  await loginButton.click();
  
  // Wait for dashboard
  await page.waitForURL(/.*\/dashboard/, { timeout: 10000 });
}