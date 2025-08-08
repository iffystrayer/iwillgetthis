const { chromium } = require('playwright');

async function testJavaScriptLoading() {
  console.log('🧪 Testing JavaScript Module Loading');
  
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture all console messages including errors
  const allMessages = [];
  page.on('console', msg => {
    const text = msg.text();
    allMessages.push({
      type: msg.type(),
      text: text,
      args: msg.args().length
    });
    console.log(`[${msg.type().toUpperCase()}] ${text}`);
  });
  
  // Capture page errors
  page.on('pageerror', error => {
    console.log(`❌ PAGE ERROR: ${error.message}`);
    allMessages.push({
      type: 'pageerror',
      text: error.message,
      stack: error.stack
    });
  });
  
  // Capture request failures
  page.on('requestfailed', request => {
    console.log(`❌ REQUEST FAILED: ${request.method()} ${request.url()} - ${request.failure().errorText}`);
  });
  
  try {
    console.log('🌐 Loading page...');
    await page.goto('http://localhost:42361');
    
    console.log('⏳ Waiting for initial load...');
    await page.waitForTimeout(5000);
    
    console.log('🔍 Checking JavaScript execution...');
    
    // Test basic JavaScript execution
    const basicTest = await page.evaluate(() => {
      try {
        return {
          hasDocument: typeof document !== 'undefined',
          hasWindow: typeof window !== 'undefined',
          moduleSupport: 'noModule' in HTMLScriptElement.prototype,
          esModuleSupport: window.navigator ? window.navigator.modules : 'unknown'
        };
      } catch (error) {
        return { error: error.message };
      }
    });
    
    console.log('📊 Basic JavaScript Environment:', basicTest);
    
    // Check if modules can load manually
    const moduleTest = await page.evaluate(async () => {
      try {
        // Try to dynamically import one of the modules
        const result = await import('./assets/react-vendor-B391mDFM.js');
        return { success: true, hasReact: typeof result.j !== 'undefined' };
      } catch (error) {
        return { 
          success: false, 
          error: error.message,
          name: error.name 
        };
      }
    });
    
    console.log('🔧 Module Import Test:', moduleTest);
    
    // Check network requests to see if all JS files were actually requested and loaded
    const finalCheck = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll('script[type="module"]'));
      return {
        moduleScriptCount: scripts.length,
        moduleScripts: scripts.map(s => ({
          src: s.src,
          loaded: s.readyState || 'unknown'
        })),
        rootContent: document.getElementById('root').innerHTML.length
      };
    });
    
    console.log('📄 Final Module Status:', finalCheck);
    
    console.log('💬 All Messages Summary:', allMessages.length);
    
    // Keep browser open to manually inspect
    console.log('🔍 Keeping browser open for manual inspection (30 seconds)...');
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testJavaScriptLoading().catch(console.error);