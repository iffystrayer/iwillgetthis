# Frontend Dev-to-Prod Issue Analysis Specification

## Problem Statement
The React frontend works perfectly in development but shows a blank page in production with the error: 
`Cannot read properties of undefined (reading 'createContext')`

## Known Facts
✅ **Working in Development:**
- Development server runs on `npm run dev`
- React components render correctly
- All functionality works as expected
- Using Vite dev server

❌ **Broken in Production:**
- Blank page with JavaScript error
- All assets load successfully (200 status codes)
- No network request failures
- React never mounts to DOM
- Error occurs during ES module execution

## Key Differences to Investigate

### 1. **Environment Comparison**
| Aspect | Development (Docker) | Production (Docker) |
|--------|---------------------|---------------------|
| Server | Vite dev server | nginx static server |
| Build | Hot reload, source maps | Optimized build, minified |
| Modules | Direct ES modules | Bundled and chunked |
| Dockerfile | Dockerfile (dev mode) | Dockerfile.prod |
| Port | Random dev port | Port 42361 |

### 2. **Investigation Plan**

#### Phase 1: Compare Docker Configurations
- [ ] Examine development Dockerfile vs Dockerfile.prod
- [ ] Compare nginx configuration between dev and prod
- [ ] Check environment variables and build args
- [ ] Verify file serving and MIME types

#### Phase 2: Build Process Analysis  
- [ ] Compare Vite dev server output vs production build
- [ ] Analyze module chunking and bundling differences
- [ ] Check if build process is corrupting React exports
- [ ] Verify ES module structure in build artifacts

#### Phase 3: Server Configuration Analysis
- [ ] Compare Vite dev server behavior vs nginx
- [ ] Check HTTP headers affecting ES module loading
- [ ] Verify MIME types for JavaScript files
- [ ] Test alternative static servers

#### Phase 4: Module Loading Deep Dive
- [ ] Analyze module dependency order
- [ ] Check for circular dependencies
- [ ] Verify React export structure in bundles
- [ ] Test module preloading behavior

## Diagnostic Tests to Run

### Test 1: Development Environment Verification
```bash
# Start development server
npm run dev --port $(shuf -i 10000-65535 -n 1)

# Test in browser
curl -I http://localhost:[port]
```

### Test 2: Local Production Build Test
```bash
# Build and serve locally
npm run build
npx serve dist --port $(shuf -i 10000-65535 -n 1)

# Test in browser
curl -I http://localhost:[port]
```

### Test 3: Module Structure Analysis
```bash
# Analyze main bundle structure
head -50 dist/assets/index-*.js
head -50 dist/assets/react-vendor-*.js

# Check import dependencies
grep -n "import.*createContext" dist/assets/*.js
```

### Test 4: nginx vs Alternative Server
```bash
# Test with different static server
python -m http.server 8000 --directory dist
```

## Expected Outcomes & Actions

### If Dev Still Works + Local Prod Build Works
**Root Cause:** Docker/nginx configuration issue
**Action:** Fix nginx configuration or container setup

### If Dev Still Works + Local Prod Build Fails  
**Root Cause:** Vite build configuration issue
**Action:** Fix build process, chunk strategy, or module bundling

### If Dev Fails
**Root Cause:** Source code issue introduced
**Action:** Revert to last working commit and identify breaking change

### If Local Prod Build Works + Docker Fails
**Root Cause:** Docker environment issue
**Action:** Fix container configuration, file permissions, or nginx setup

## Resolution Strategy

1. **Systematic Testing:** Execute all diagnostic tests in order
2. **Binary Search:** Isolate the exact point where functionality breaks
3. **Environment Parity:** Ensure production closely matches working development
4. **Minimal Changes:** Make the smallest possible change to fix the issue
5. **Verification:** Confirm fix works with comprehensive testing

## Success Criteria
- [ ] React application loads in production
- [ ] No JavaScript console errors
- [ ] All components render correctly
- [ ] Full functionality restored
- [ ] Backend API communication works
- [ ] Production deployment is stable

## Rollback Plan
If fixes break other functionality:
1. Revert to last known working Docker image
2. Document all attempted changes
3. Implement alternative approach
4. Test thoroughly before deployment

---
**Next Steps:** Execute Phase 1 tests to confirm current development status