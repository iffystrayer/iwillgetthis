const { chromium } = require('playwright');

async function deepDebugFrontend() {
  console.log('🔬 Deep Debugging Frontend Module Loading');
  
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture all errors including unhandled promise rejections
  const errors = [];
  page.on('pageerror', error => {
    errors.push({
      type: 'pageerror',
      message: error.message,
      stack: error.stack
    });
    console.log(`❌ PAGE ERROR: ${error.message}`);
  });
  
  // Capture console messages
  const messages = [];
  page.on('console', msg => {
    const message = {
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    };
    messages.push(message);
    console.log(`[${msg.type().toUpperCase()}] ${msg.text()}`);
  });
  
  // Track script loading
  const scripts = [];
  page.on('response', response => {
    if (response.url().includes('.js')) {
      scripts.push({
        url: response.url(),
        status: response.status(),
        headers: response.headers()
      });
    }
  });
  
  try {
    // Enable network domain for detailed network monitoring
    await page.goto('http://localhost:42361');
    
    // Wait and try to manually execute React code
    await page.waitForTimeout(5000);
    
    console.log('\n🧪 Manual Module Import Test:');
    
    // Try to manually import and execute React
    const manualTest = await page.evaluate(async () => {
      try {
        // Try to access React directly from module scope
        const result = {
          windowReact: typeof window.React,
          windowReactDOM: typeof window.ReactDOM,
          modules: Object.keys(window).filter(key => key.includes('react') || key.includes('React')),
        };
        
        // Try to manually import React
        try {
          const reactImport = await import('./assets/react-vendor-B391mDFM.js');
          result.manualImport = {
            success: true,
            keys: Object.keys(reactImport),
            hasDefault: 'default' in reactImport,
            defaultType: typeof reactImport.default
          };
        } catch (importError) {
          result.manualImport = {
            success: false,
            error: importError.message
          };
        }
        
        return result;
      } catch (error) {
        return {
          error: error.message,
          stack: error.stack
        };
      }
    });
    
    console.log('Manual test result:', JSON.stringify(manualTest, null, 2));
    
    // Check if there are any pending promises or module loading issues
    const moduleStatus = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll('script[type="module"]'));
      return {
        moduleScripts: scripts.map(s => ({
          src: s.src,
          defer: s.defer,
          async: s.async,
          loaded: s.readyState || 'unknown',
          hasError: s.onerror !== null
        })),
        documentReady: document.readyState,
        hasModules: 'import' in document.createElement('script'),
        moduleSupport: window.navigator ? window.navigator.modules : undefined
      };
    });
    
    console.log('\n📊 Module Status:', JSON.stringify(moduleStatus, null, 2));
    console.log('\n📜 Script Loading Status:');
    scripts.forEach(script => {
      console.log(`  ${script.status} ${script.url}`);
    });
    
    console.log('\n💬 All Messages:');
    messages.forEach(msg => {
      console.log(`  [${msg.type}] ${msg.text} (${JSON.stringify(msg.location)})`);
    });
    
    console.log('\n❌ All Errors:');
    if (errors.length === 0) {
      console.log('  No JavaScript errors captured');
    } else {
      errors.forEach(error => {
        console.log(`  ${error.type}: ${error.message}`);
        if (error.stack) {
          console.log(`    Stack: ${error.stack.split('\n')[0]}`);
        }
      });
    }
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Keeping browser open for 60 seconds for manual inspection...');
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('❌ Deep debug failed:', error.message);
  } finally {
    await browser.close();
  }
}

deepDebugFrontend().catch(console.error);