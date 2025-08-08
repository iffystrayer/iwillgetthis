const { chromium } = require('playwright');

async function testProductionFrontend() {
  console.log('🎭 Testing Production Frontend at http://localhost:42361');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    console.log('📍 Navigating to production frontend...');
    await page.goto('http://localhost:42361', { waitUntil: 'networkidle' });
    
    console.log('📄 Page title:', await page.title());
    
    // Check if the root div exists
    const rootDiv = await page.locator('#root');
    console.log('🎯 Root div exists:', await rootDiv.count() > 0);
    
    // Check if root div has content
    const rootContent = await rootDiv.innerHTML();
    console.log('📦 Root div content length:', rootContent.length);
    console.log('📦 Root div content preview:', rootContent.substring(0, 200));
    
    // Check for any console errors
    const consoleMessages = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleMessages.push(msg.text());
      }
    });
    
    // Wait a bit for any async operations
    await page.waitForTimeout(5000);
    
    console.log('❌ Console errors:', consoleMessages);
    
    // Check if we can find any React components
    const hasReactComponents = await page.evaluate(() => {
      return window.React !== undefined || 
             document.querySelector('[data-reactroot]') !== null ||
             document.querySelector('div[id="root"]').children.length > 0;
    });
    
    console.log('⚛️  React components detected:', hasReactComponents);
    
    // Take a screenshot
    await page.screenshot({ 
      path: '/Users/ifiokmoses/code/iwillgetthis/aegis-platform/frontend/aegis-frontend/production-test-screenshot.png',
      fullPage: true 
    });
    console.log('📸 Screenshot saved as production-test-screenshot.png');
    
    // Check network requests
    const failedRequests = [];
    page.on('requestfailed', request => {
      failedRequests.push(`${request.method()} ${request.url()} - ${request.failure().errorText}`);
    });
    
    console.log('🌐 Failed network requests:', failedRequests);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testProductionFrontend().catch(console.error);