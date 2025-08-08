# Production Deployment Recovery Specification

## Executive Summary

The current production deployment has partially succeeded with core infrastructure services running, but application services are failing. This specification provides a systematic approach to resolve all issues and achieve full production deployment.

## Current State Analysis

### ✅ Successfully Running Services
- **MySQL Database** (aegis-db-prod): Healthy, port 3306
- **Redis Cache** (aegis-redis-prod): Healthy, port 6379  
- **Prometheus Monitoring** (aegis-prometheus-prod): Running, port 9091

### ❌ Failing Services
- **Backend API** (aegis-backend-prod): Restarting (Error 3)
- **Frontend Application** (aegis-frontend-prod): Not running
- **Nginx Proxy** (aegis-nginx-prod): Restarting (Error 1)
- **Grafana Dashboard** (aegis-grafana-prod): Restarting (Error 1)

## Root Cause Analysis

### Primary Issue: Port Configuration Mismatch
**CLAUDE.md Requirement**: Production must use **fixed ports 3000 (frontend) and 8000 (backend)**
**Current State**: Using random development ports, causing service discovery failures

### Secondary Issues
1. **Database Connection**: Backend likely configured for PostgreSQL but MySQL is running
2. **Service Dependencies**: Services starting before dependencies are ready
3. **Configuration Drift**: Development configurations incompatible with production environment
4. **Missing Health Checks**: Inadequate startup verification

## Recovery Strategy

### Phase 1: Port Standardization (Immediate)
**Objective**: Fix port configuration to match CLAUDE.md requirements

**Actions**:
1. Update production Docker Compose to use fixed ports:
   - Frontend: 3000
   - Backend: 8000
   - Database: 3306 (already correct)
   - Redis: 6379 (already correct)
2. Update all internal service references
3. Fix CORS configuration for production ports

### Phase 2: Service Configuration Alignment
**Objective**: Ensure all services use production-compatible configurations

**Actions**:
1. **Backend Service**:
   - Fix database connection string (PostgreSQL → MySQL)
   - Update environment variables for production
   - Add comprehensive health check endpoints
   - Configure proper logging levels

2. **Frontend Service**:
   - Update API endpoints to backend:8000
   - Set production environment variables
   - Fix nginx configuration for production

3. **Nginx Proxy**:
   - Remove development-specific SSL configurations
   - Configure proper upstream services
   - Add health check endpoints

### Phase 3: Database Integration
**Objective**: Ensure backend connects properly to MySQL

**Actions**:
1. Update backend database configuration
2. Run database initialization scripts
3. Verify schema compatibility
4. Test database connectivity

### Phase 4: Service Orchestration
**Objective**: Ensure services start in correct order with proper health checks

**Actions**:
1. Add comprehensive health checks
2. Configure service dependencies
3. Add retry mechanisms
4. Implement graceful startup sequences

### Phase 5: Comprehensive Testing
**Objective**: Verify all endpoints work in production environment

**Actions**:
1. **API Endpoint Testing**:
   - Authentication endpoints
   - CRUD operations for all entities
   - File upload/download
   - WebSocket connections (if any)

2. **Integration Testing**:
   - Frontend-backend communication
   - Database operations
   - Cache functionality
   - Monitoring metrics

3. **End-to-End Testing**:
   - User workflows
   - Admin operations
   - Error handling
   - Performance validation

## Implementation Plan

### Step 1: Stop Current Deployment
```bash
cd /Users/ifiokmoses/code/iwillgetthis/aegis-platform
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod down -v
```

### Step 2: Fix Port Configuration
Update `docker/docker-compose.prod.yml`:
- Frontend: Map to port 3000
- Backend: Map to port 8000
- Update all internal references

### Step 3: Fix Backend Database Configuration
Update backend environment variables:
- Change from PostgreSQL to MySQL connection string
- Fix database connection parameters

### Step 4: Rebuild Images
```bash
# Rebuild with production configurations
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod build --no-cache
```

### Step 5: Deploy with Proper Orchestration
```bash
# Deploy services in correct order
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod up -d db redis
# Wait for healthy status
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod up -d backend
# Wait for healthy status  
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod up -d frontend nginx
# Deploy monitoring
docker-compose -f docker/docker-compose.prod.yml --env-file docker/.env.prod up -d prometheus grafana
```

### Step 6: Comprehensive Endpoint Testing
Execute test suite covering:
- Health endpoints: `/health`, `/metrics`
- Authentication: `/api/v1/auth/login`, `/api/v1/auth/logout`
- Core entities: Users, Assets, Risks, Assessments, Tasks, Evidence, Reports
- File operations: Upload, download, processing
- Admin functions: User management, system configuration

### Step 7: Performance Validation
- Response time verification (< 2s for API calls)
- Concurrent user testing
- Database query performance
- Memory and CPU utilization

## Success Criteria

### Technical Requirements
- [ ] All services running with status "healthy"
- [ ] Backend accessible on port 8000 with `/health` returning 200
- [ ] Frontend accessible on port 3000 with homepage loading
- [ ] Database connectivity verified
- [ ] All API endpoints responding correctly
- [ ] Authentication flow working end-to-end
- [ ] File upload/download functional
- [ ] Monitoring dashboards accessible

### Performance Requirements
- [ ] API response times < 2 seconds
- [ ] Frontend load time < 5 seconds
- [ ] Database queries < 1 second average
- [ ] Memory usage < 80% on all services
- [ ] CPU usage < 70% under normal load

### Integration Requirements
- [ ] Frontend-backend communication working
- [ ] Database transactions completing successfully
- [ ] Cache invalidation functioning
- [ ] Logging aggregation operational
- [ ] Monitoring metrics being collected

## Risk Mitigation

### Data Safety
- Database backup before any schema changes
- Volume persistence for production data
- Rollback procedures documented

### Service Continuity
- Health check mechanisms
- Automatic restart policies
- Service dependency management
- Graceful shutdown procedures

### Monitoring
- Application metrics collection
- Error rate monitoring
- Performance tracking
- Alert configuration

## Post-Deployment Verification

### Automated Tests
- Playwright E2E test suite execution
- API integration test suite
- Database connectivity tests
- Performance benchmark tests

### Manual Validation
- User registration and login flow
- CRUD operations for each entity type
- File upload and processing
- Report generation functionality
- Admin dashboard access

## Next Steps After Recovery

1. **CI/CD Pipeline Setup**: Automate deployment process
2. **Production Monitoring**: Set up alerts and dashboards
3. **Backup Strategy**: Implement automated backups
4. **Security Hardening**: SSL/TLS, security headers, access controls
5. **Performance Optimization**: Query optimization, caching strategy
6. **Documentation Update**: Deployment procedures, troubleshooting guides

## Timeline

- **Phase 1-2**: 2-3 hours (Configuration fixes)
- **Phase 3-4**: 1-2 hours (Database and orchestration)
- **Phase 5**: 2-3 hours (Comprehensive testing)
- **Total**: 5-8 hours for complete recovery and validation

This systematic approach ensures that the production deployment becomes reliable and maintainable, preventing future "starting from scratch" scenarios when moving from development to production.