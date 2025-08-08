# Comprehensive Dev vs Prod Configuration Analysis

## 1. Dockerfile Differences

### Development (Dockerfile)
```dockerfile
FROM node:18-alpine AS builder
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install
COPY . .
RUN pnpm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
HEALTHCHECK CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
```

### Production (Dockerfile.prod)
```dockerfile
FROM node:18-alpine as builder
ARG VITE_API_URL=https://api.aegis.yourdomain.com/api/v1
ARG VITE_ENVIRONMENT=production
ARG VITE_USE_MOCK_API=false

COPY package*.json ./
RUN npm ci --silent                    # ← npm instead of pnpm
ENV NODE_ENV=production
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_ENVIRONMENT=${VITE_ENVIRONMENT}
ENV VITE_USE_MOCK_API=${VITE_USE_MOCK_API}
RUN npm run build                      # ← npm instead of pnpm

FROM nginx:1.25-alpine as production
# Complex nginx configuration inline
EXPOSE 80                              # ← port 80 instead of 3000
HEALTHCHECK CMD curl -f http://localhost:80/health || exit 1
```

## 2. nginx Configuration Differences

### Development (nginx.conf)
```nginx
server {
    listen 3000;                       # ← Port 3000
    server_name localhost;
    
    # Specific assets handling
    location /assets/ {                # ← Critical: specific /assets/ handling
        try_files $uri =404;
    }
    
    # SPA routing
    location / {
        try_files $uri /index.html;    # ← Simple fallback
    }
}
```

### Production (Dockerfile.prod inline)
```nginx
server {
    listen 80;                         # ← Port 80
    server_name _;
    
    # Generic static files handling
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA routing  
    location / {
        try_files $uri $uri/ /index.html;  # ← Different pattern with $uri/
    }
}
```

## 3. Build Process Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| Package Manager | pnpm | npm |
| Install Command | `pnpm install` | `npm ci --silent` |
| Build Command | `pnpm run build` | `npm run build` |
| Build Args | None | VITE_API_URL, VITE_ENVIRONMENT, VITE_USE_MOCK_API |
| NODE_ENV | Not set | production |

## 4. Environment Variables

### Development
- No build-time environment variables
- Uses defaults from vite.config.ts or .env files

### Production  
- `VITE_API_URL` (build arg)
- `VITE_ENVIRONMENT=production` (build arg)
- `VITE_USE_MOCK_API=false` (build arg)
- `NODE_ENV=production` (ENV)

## 5. nginx Features Differences

### Development nginx.conf
- Basic configuration
- Port 3000
- Simple gzip settings
- **Critical: Specific `/assets/` location block**
- Simple try_files pattern

### Production nginx (inline)
- Advanced configuration with performance optimizations
- Port 80
- Advanced gzip with multiple MIME types
- Security headers
- Cache control for static files
- **Missing: Specific `/assets/` handling**
- Different try_files pattern

## 6. Key Suspected Issues

### Issue #1: Missing /assets/ Location Block
**Development has:**
```nginx
location /assets/ {
    try_files $uri =404;
}
```

**Production missing this**, relies on generic static file handling.

### Issue #2: Different try_files Pattern
**Development:**
```nginx
try_files $uri /index.html;
```

**Production:**
```nginx
try_files $uri $uri/ /index.html;
```

### Issue #3: Package Manager Differences
- Dev: pnpm (uses pnpm-lock.yaml, different module resolution)
- Prod: npm (uses package-lock.json, different resolution)

### Issue #4: MIME Type Configuration
**Development:** Uses default nginx MIME types
**Production:** Has explicit MIME types in inline config

## 7. Most Likely Root Cause

The **missing `/assets/` location block** in production is the most likely culprit:

1. ES modules are served from `/assets/` directory
2. Development nginx specifically handles `/assets/` requests  
3. Production relies on generic pattern matching
4. This could cause incorrect MIME types or request routing for JavaScript modules

## 8. Testing Strategy

### Test 1: Use Dev nginx config in Prod build
- Build with pnpm (like dev)  
- Use dev nginx.conf (with /assets/ block)
- Keep prod environment variables

### Test 2: Check MIME types
- Compare Content-Type headers between dev and prod
- Verify JavaScript files are served as `application/javascript`

### Test 3: Check file serving
- Verify `/assets/` files are accessible in both environments
- Test direct access to JavaScript modules

## 9. Fix Priority

1. **High Priority:** Add `/assets/` location block to production nginx config
2. **Medium Priority:** Align try_files patterns
3. **Low Priority:** Consider standardizing package manager
4. **Monitor:** Environment variable differences (likely not the issue)