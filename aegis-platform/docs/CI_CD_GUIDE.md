# Aegis Platform CI/CD Guide

## Overview

This guide covers the complete Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Aegis Risk Management Platform. The pipeline is built using GitHub Actions and provides automated testing, security scanning, building, and deployment capabilities.

## CI/CD Architecture

```mermaid
graph TD
    A[Developer Push/PR] --> B[Code Quality Checks]
    B --> C[Automated Testing]
    C --> D[Security Scanning]
    D --> E[Container Building]
    E --> F[Staging Deployment]
    F --> G[E2E Testing]
    G --> H[Production Deployment]
    H --> I[Monitoring & Alerts]
    
    J[Scheduled Security Scans] --> D
    K[Manual Deployment Trigger] --> F
```

## Pipeline Components

### 1. Code Quality Analysis (`code-quality` job)

Runs on every push and pull request to ensure code quality standards.

**Backend Quality Checks:**
- **Black**: Code formatting validation
- **isort**: Import statement organization
- **Flake8**: Python linting and style checking
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking

**Frontend Quality Checks:**
- **ESLint**: JavaScript/TypeScript linting
- **TypeScript**: Type checking
- **npm audit**: Dependency vulnerability scanning

### 2. Automated Testing

#### Backend Tests (`backend-tests` job)
- **Framework**: pytest with coverage reporting
- **Services**: PostgreSQL and Redis test databases
- **Coverage**: Uploads to Codecov for tracking
- **Environment**: Isolated test environment with test secrets

#### Frontend Tests (`frontend-tests` job)
- **Framework**: Jest with React Testing Library
- **Coverage**: Uploads to Codecov for tracking
- **Type Checking**: TypeScript validation

#### End-to-End Tests (`e2e-tests` job)
- **Framework**: Playwright for browser automation
- **Scope**: Full application stack testing
- **Browsers**: Chromium (configurable for additional browsers)
- **Environment**: Docker-based full stack deployment

### 3. Security Testing (`security-tests` job)

Comprehensive security validation running on main branch or when explicitly requested:

- **Rate Limiting**: Validates API rate limiting implementation
- **Security Headers**: Checks for proper security headers
- **Input Validation**: Tests against common attack patterns
- **Authentication**: Validates auth security measures
- **SSL/TLS**: Checks certificate and configuration
- **Network Security**: Basic port scanning and vulnerability checks

### 4. Container Image Building (`build-images` job)

**Multi-platform Builds:**
- Linux AMD64 and ARM64 support
- Automated tagging based on branch/commit
- Layer caching for faster builds
- Push to GitHub Container Registry (GHCR)

**Image Tags:**
- `latest`: Latest main branch build
- `develop`: Latest develop branch build
- `{branch}-{sha}`: Branch-specific builds
- `pr-{number}`: Pull request builds

### 5. Container Security Scanning (`container-security-scan` job)

**Tools Used:**
- **Trivy**: Comprehensive vulnerability scanning
- **Results**: Uploaded to GitHub Security tab (SARIF format)
- **Coverage**: Both backend and frontend images

### 6. Deployment Stages

#### Staging Deployment (`deploy-staging`)
- **Trigger**: Develop branch merges or manual trigger
- **Environment**: `staging` GitHub environment
- **Validation**: Automated smoke tests
- **Notifications**: Slack alerts with deployment status

#### Production Deployment (`deploy-production`)
- **Trigger**: Main branch merges or manual trigger with approval
- **Environment**: `production` GitHub environment (requires approval)
- **Pre-deployment**: Automated backup creation
- **Validation**: Comprehensive smoke tests and monitoring verification
- **Notifications**: Slack alerts to production deployment channel

## GitHub Actions Workflows

### Main CI/CD Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main`, `develop`, or feature branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch with environment selection

**Jobs Flow:**
1. `code-quality` → Quality analysis and linting
2. `backend-tests` → Python/FastAPI testing  
3. `frontend-tests` → React/TypeScript testing
4. `e2e-tests` → Full stack integration testing
5. `security-tests` → Security validation (conditional)
6. `build-images` → Container image building
7. `container-security-scan` → Image vulnerability scanning
8. `deploy-staging` → Staging environment deployment
9. `deploy-production` → Production deployment (with approval)
10. `cleanup` → Post-deployment cleanup and reporting

### Security Scanning Workflow (`.github/workflows/security-scan.yml`)

**Triggers:**
- Daily scheduled scan (2 AM UTC)
- Push to main branch
- Pull requests to main
- Manual trigger with scan type selection

**Scan Types:**
- **Dependencies**: Vulnerability scanning of Python/Node.js dependencies
- **Code Analysis**: Static code analysis with CodeQL
- **Containers**: Container image vulnerability scanning  
- **Infrastructure**: Docker/nginx/shell script security analysis
- **Secrets**: Detection of leaked secrets and credentials

## Deployment Script (`scripts/deploy.sh`)

### Features
- **Multi-environment support**: development, staging, production
- **Dry-run capability**: Preview changes without deployment
- **Automated backups**: Pre-deployment backup creation
- **Rollback support**: Automatic rollback on deployment failure
- **Health checks**: Service readiness validation
- **Smoke testing**: Basic functionality verification

### Usage Examples

```bash
# Deploy to staging (default)
./scripts/deploy.sh

# Deploy specific version to production
./scripts/deploy.sh -e production -t v1.2.3

# Dry run deployment to staging
./scripts/deploy.sh -e staging --dry-run

# Deploy without backup or rollback (emergency)
./scripts/deploy.sh -e production -b -r
```

## Environment Configuration

### Required Secrets

**GitHub Repository Secrets:**
```bash
# Container Registry
GITHUB_TOKEN                    # Auto-provided by GitHub

# AWS Deployment (if using)
AWS_ACCESS_KEY_ID              # AWS access key
AWS_SECRET_ACCESS_KEY          # AWS secret key

# Notifications
SLACK_WEBHOOK_URL              # Slack webhook for notifications

# Application Configuration  
VITE_API_URL                   # Frontend API URL override

# Database & External Services
DATABASE_URL                   # Production database connection
OPENAI_API_KEY                # OpenAI API key for production
ANTHROPIC_API_KEY             # Anthropic API key for production

# Security Scanning
GITLEAKS_LICENSE              # GitLeaks license (optional)
```

### Environment Files

Create environment-specific configuration files:

**`.env.staging`:**
```env
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=postgresql://user:pass@staging-db:5432/aegis_staging
CORS_ORIGINS=["https://staging.aegis.example.com"]
RATE_LIMIT_ENABLED=true
SSL_REDIRECT=true
```

**`.env.production`:**
```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/aegis_production
CORS_ORIGINS=["https://aegis.example.com"]
RATE_LIMIT_ENABLED=true
SSL_REDIRECT=true
BACKUP_ENCRYPTION_KEY=your-production-backup-key
```

## Security Best Practices

### Secret Management
- Use GitHub Secrets for sensitive configuration
- Never commit secrets to the repository
- Rotate secrets regularly (quarterly recommended)
- Use different secrets for each environment

### Image Security
- Multi-stage builds to minimize attack surface
- Regular base image updates
- Vulnerability scanning on every build
- Signed container images (future enhancement)

### Deployment Security
- Approval requirements for production deployments
- Automated backups before production deployments
- Rollback capabilities on deployment failure
- Health checks and smoke testing

### Access Control
- GitHub environment protection rules
- Required reviews for production deployments
- Branch protection rules on main/develop
- Audit logging of all deployment activities

## Monitoring and Observability

### Deployment Monitoring
- **Health Checks**: Automated service health validation
- **Smoke Tests**: Basic functionality verification  
- **Performance Tests**: Response time and throughput validation
- **Integration Tests**: External service connectivity verification

### Notifications
- **Slack Integration**: Deployment status notifications
- **Email Alerts**: Critical failure notifications (configurable)
- **Dashboard Updates**: Deployment tracking in monitoring systems

### Metrics and Logging
- **Deployment Success Rate**: Track deployment success/failure rates
- **Deployment Duration**: Monitor deployment time trends
- **Rollback Frequency**: Track rollback occurrences
- **Security Scan Results**: Track vulnerability trends

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check build logs
gh run list --workflow=ci.yml
gh run view [run-id] --log

# Local build testing
docker build -t test-build ./backend
docker build -t test-build ./frontend/aegis-frontend
```

#### Test Failures
```bash
# Run tests locally
cd backend && python -m pytest tests/ -v
cd frontend/aegis-frontend && npm test

# Debug E2E tests
cd frontend/aegis-frontend && npx playwright test --debug
```

#### Deployment Failures
```bash
# Check deployment logs
./scripts/deploy.sh -e staging --dry-run

# Manual rollback
./scripts/restore-system.sh

# Service debugging
docker-compose logs backend
docker-compose logs frontend
```

#### Security Scan Issues
```bash
# Run security scans locally
./scripts/security-test.sh
./scripts/configure-security.sh test

# Check vulnerability reports
gh run view [run-id] --log-failed
```

### Debug Commands

```bash
# Check service health
curl http://localhost:30641/health
curl http://localhost:58533

# View container logs
docker-compose logs --tail=100 backend
docker-compose logs --tail=100 frontend

# Check database connectivity
docker-compose exec backend python -c "from database import engine; engine.connect()"

# Validate configuration
docker-compose config
nginx -t -c ./nginx/nginx-production.conf
```

## Maintenance

### Regular Tasks
- **Weekly**: Review security scan results
- **Monthly**: Update dependencies and base images
- **Quarterly**: Rotate secrets and certificates
- **Annually**: Review and update CI/CD pipeline

### Pipeline Updates
- Keep GitHub Actions versions updated
- Monitor for new security scanning tools
- Update deployment strategies based on lessons learned
- Optimize build times and resource usage

### Performance Optimization
- **Caching**: Optimize Docker layer caching
- **Parallelization**: Run independent jobs in parallel
- **Resource Limits**: Configure appropriate resource limits
- **Cleanup**: Regular cleanup of old artifacts and images

## Best Practices Summary

1. **Security First**: Security scanning on every commit
2. **Test Everything**: Comprehensive automated testing
3. **Fast Feedback**: Quick failure detection and notification
4. **Safe Deployments**: Automated backups and rollback capabilities
5. **Observability**: Comprehensive monitoring and logging
6. **Documentation**: Keep deployment procedures documented
7. **Regular Updates**: Keep tools and dependencies updated
8. **Review Process**: Required reviews for production changes

## Getting Started

1. **Fork/Clone Repository**: Set up local development environment
2. **Configure Secrets**: Add required secrets to GitHub repository
3. **Test Locally**: Run tests and deployment scripts locally
4. **Create Feature Branch**: Follow GitFlow branching strategy
5. **Submit Pull Request**: Automated testing will run
6. **Deploy to Staging**: Merge to develop branch triggers staging deployment
7. **Production Deployment**: Merge to main branch for production deployment

## Support and Resources

- **Documentation**: `/docs` directory contains comprehensive guides
- **Scripts**: `/scripts` directory contains automation tools
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Monitoring**: Check monitoring dashboards for deployment status
- **Logs**: Use centralized logging for troubleshooting

For additional support, contact the platform engineering team or refer to the troubleshooting section above.