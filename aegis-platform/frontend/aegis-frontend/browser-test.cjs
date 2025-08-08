const { chromium } = require('playwright');

async function testBrowserModuleSupport() {
  console.log('🌐 Testing Browser Module Support');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Test basic browser capabilities
  const capabilities = await page.evaluate(() => {
    // Test ES module support
    const supportsModules = 'noModule' in HTMLScriptElement.prototype;
    const dynamicImportSupport = typeof window.eval === 'function' ? (() => {
      try {
        window.eval('() => import("data:text/javascript,export default 1")');
        return true;
      } catch {
        return false;
      }
    })() : false;
    
    return {
      userAgent: navigator.userAgent,
      supportsModules,
      dynamicImportSupport,
      es6Support: (() => {
        try {
          eval('() => {}');
          return true;
        } catch {
          return false;
        }
      })(),
      moduleScriptSupport: 'supports' in HTMLLinkElement.prototype && 
                          document.createElement('link').supports('modulepreload')
    };
  });
  
  console.log('Browser Capabilities:', JSON.stringify(capabilities, null, 2));
  
  // Test loading a simple module
  console.log('\n🧪 Testing Simple Module Loading...');
  
  await page.setContent(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Module Test</title>
    </head>
    <body>
      <div id="test">Loading...</div>
      <script type="module">
        document.getElementById('test').textContent = 'Module loaded successfully!';
        console.log('Simple module executed');
      </script>
    </body>
    </html>
  `);
  
  await page.waitForTimeout(2000);
  
  const testResult = await page.evaluate(() => {
    return {
      testContent: document.getElementById('test').textContent,
      hasConsoleMessage: true // We'll capture this separately
    };
  });
  
  console.log('Simple Module Test:', testResult);
  
  // Now test the actual production URL but with error capture
  console.log('\n🔗 Testing Production URL with Enhanced Error Capture...');
  
  const errors = [];
  const promises = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`❌ CONSOLE ERROR: ${msg.text()}`);
    } else {
      console.log(`[${msg.type().toUpperCase()}] ${msg.text()}`);
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.message);
    console.log(`❌ PAGE ERROR: ${error.message}`);
  });
  
  page.on('requestfailed', req => {
    console.log(`❌ REQUEST FAILED: ${req.url()} - ${req.failure()?.errorText}`);
  });
  
  await page.goto('http://localhost:42361');
  await page.waitForTimeout(5000);
  
  console.log('\n📋 Final Error Summary:');
  if (errors.length === 0) {
    console.log('  ✅ No page errors detected');
  } else {
    errors.forEach(error => console.log(`  ❌ ${error}`));
  }
  
  console.log('\nKeeping browser open for 30 seconds...');
  await page.waitForTimeout(30000);
  
  await browser.close();
}

testBrowserModuleSupport().catch(console.error);