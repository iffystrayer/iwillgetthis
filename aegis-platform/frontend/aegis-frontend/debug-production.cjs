const { chromium } = require('playwright');

async function debugProductionFrontend() {
  console.log('🔍 Debugging Production Frontend at http://localhost:42361');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500,
    devtools: true
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Track all console messages
  const allMessages = [];
  page.on('console', msg => {
    allMessages.push(`[${msg.type().toUpperCase()}] ${msg.text()}`);
  });
  
  // Track network requests
  const networkRequests = [];
  page.on('request', request => {
    networkRequests.push(`${request.method()} ${request.url()}`);
  });
  
  // Track failed requests
  const failedRequests = [];
  page.on('requestfailed', request => {
    failedRequests.push(`❌ FAILED: ${request.method()} ${request.url()} - ${request.failure().errorText}`);
  });
  
  try {
    console.log('📍 Navigating to production frontend...');
    await page.goto('http://localhost:42361', { waitUntil: 'networkidle' });
    
    console.log('\n🌐 Network Requests Made:');
    networkRequests.forEach(req => console.log('  ', req));
    
    console.log('\n💬 All Console Messages:');
    allMessages.forEach(msg => console.log('  ', msg));
    
    console.log('\n❌ Failed Requests:');
    if (failedRequests.length === 0) {
      console.log('   None - all requests successful! ✅');
    } else {
      failedRequests.forEach(req => console.log('  ', req));
    }
    
    // Check JavaScript environment
    const jsEnvironment = await page.evaluate(() => {
      return {
        hasReact: typeof window.React !== 'undefined',
        hasReactDOM: typeof window.ReactDOM !== 'undefined',
        hasVite: typeof window.__vite_plugin_react_preamble_installed__ !== 'undefined',
        scripts: Array.from(document.querySelectorAll('script')).map(s => ({
          src: s.src,
          type: s.type,
          hasContent: s.innerHTML.length > 0
        })),
        stylesheets: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href),
        rootHtml: document.getElementById('root').innerHTML,
        bodyHtml: document.body.innerHTML.substring(0, 500) + '...'
      };
    });
    
    console.log('\n🔧 JavaScript Environment:');
    console.log('   React available:', jsEnvironment.hasReact);
    console.log('   ReactDOM available:', jsEnvironment.hasReactDOM);
    console.log('   Vite detected:', jsEnvironment.hasVite);
    console.log('   Root div content:', jsEnvironment.rootHtml || '(empty)');
    
    console.log('\n📜 Scripts loaded:');
    jsEnvironment.scripts.forEach((script, i) => {
      console.log(`   ${i+1}. ${script.src || '(inline)'} [${script.type || 'text/javascript'}] ${script.hasContent ? '(has content)' : '(no content)'}`);
    });
    
    console.log('\n🎨 Stylesheets loaded:');
    jsEnvironment.stylesheets.forEach((css, i) => {
      console.log(`   ${i+1}. ${css}`);
    });
    
    // Wait longer to see if React eventually mounts
    console.log('\n⏳ Waiting 10 seconds for React to potentially mount...');
    await page.waitForTimeout(10000);
    
    const finalCheck = await page.evaluate(() => {
      return {
        rootContent: document.getElementById('root').innerHTML,
        hasAnyReactElements: document.querySelector('[data-reactroot]') !== null ||
                           document.getElementById('root').children.length > 0,
        globalReact: typeof window.React !== 'undefined'
      };
    });
    
    console.log('\n📊 Final Status:');
    console.log('   Root has content:', finalCheck.rootContent.length > 0);
    console.log('   React elements present:', finalCheck.hasAnyReactElements);
    console.log('   Global React available:', finalCheck.globalReact);
    
    if (finalCheck.rootContent.length > 0) {
      console.log('   Root content preview:', finalCheck.rootContent.substring(0, 200) + '...');
    }
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser will stay open for 30 seconds for manual inspection...');
    await page.waitForTimeout(30000);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

debugProductionFrontend().catch(console.error);