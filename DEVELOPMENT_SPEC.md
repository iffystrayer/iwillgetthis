# Aegis Risk Management Platform - Development Specification

## 1. Project Overview

### 1.1 Project Description
The Aegis Risk Management Platform is an enterprise-grade cybersecurity risk management system that provides comprehensive risk assessment, asset management, and AI-powered security analysis capabilities. The platform integrates with multiple Large Language Model (LLM) providers to automate risk analysis, evidence evaluation, and report generation.

### 1.2 Technical Architecture
- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy ORM
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Database**: SQLite (development) → MySQL 8.0+ (production)
- **AI Integration**: Multi-provider LLM system (OpenAI, Anthropic, Google, etc.)
- **Deployment**: Docker containers with docker-compose orchestration

### 1.3 Key Features
- Multi-tenant cybersecurity risk management
- Asset inventory and lifecycle management
- Comprehensive risk register with scoring
- AI-powered evidence analysis and risk assessment
- Framework compliance tracking (NIST, ISO27001, SOC2)
- Automated reporting and executive dashboards
- Role-based access control (RBAC)
- Integration with security tools (OpenVAS, OpenCTI)

## 2. Technical Requirements

### 2.1 System Requirements

#### Development Environment
- **OS**: macOS/Linux/Windows with WSL2
- **Python**: 3.11+ with virtual environment mandatory
- **Node.js**: 18+ with pnpm package manager
- **Database**: SQLite 3.35+ (development), MySQL 8.0+ (production)
- **Docker**: 24.0+ with Docker Compose v2
- **Git**: 2.30+ with conventional commits

#### Hardware Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB available space
- **Network**: Stable internet for AI provider APIs

### 2.2 Technology Stack

#### Backend Technologies
```yaml
Core Framework:
  - FastAPI 0.104+: Modern async web framework
  - Uvicorn: ASGI server with hot reload
  - SQLAlchemy 2.0+: ORM with async support
  - Alembic: Database migration management
  - Pydantic 2.5+: Data validation and serialization

Security:
  - python-jose: JWT token management
  - passlib[bcrypt]: Password hashing
  - python-multipart: File upload support
  - fastapi-limiter: Rate limiting

AI/LLM Integration:
  - openai: OpenAI GPT models
  - google-generativeai: Google Gemini
  - anthropic: Claude models
  - litellm: Universal LLM interface
  - httpx: Async HTTP client

Data Processing:
  - pandas: Data analysis
  - openpyxl: Excel file processing
  - weasyprint: PDF generation
  - beautifulsoup4: HTML parsing

Monitoring & Logging:
  - structlog: Structured logging
  - redis: Caching and session storage
  - celery: Background task processing
  - apscheduler: Task scheduling
```

#### Frontend Technologies
```yaml
Core Framework:
  - React 18.3+: UI library with hooks
  - TypeScript 5.6+: Type safety
  - Vite 6.0+: Build tool and dev server
  - React Router 6: Client-side routing

UI Framework:
  - TailwindCSS v3.4+: Utility-first CSS
  - shadcn/ui: High-quality component library
  - Radix UI: Headless UI primitives
  - Lucide React: Icon library

State Management:
  - React Query (TanStack): Server state
  - React Hook Form: Form management
  - Zustand: Client state (if needed)

Build Tools:
  - ESLint 9.15+: Code linting
  - TypeScript ESLint: TS-specific rules
  - PostCSS: CSS processing
  - Autoprefixer: CSS vendor prefixes
```

### 2.3 Database Schema

#### Core Entities
```sql
-- Users and Authentication
users: id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at
roles: id, name, description, permissions, is_active, created_at, updated_at
user_roles: user_id, role_id, assigned_at, assigned_by

-- Asset Management
assets: id, name, description, asset_type, category_id, owner_id, criticality, location, ip_address, hostname, operating_system, metadata, is_active, created_at, updated_at
asset_categories: id, name, description, parent_id, color, icon, created_at, updated_at

-- Risk Management
risks: id, title, description, category, status, likelihood, impact, risk_score, inherent_risk, residual_risk, owner_id, created_at, updated_at
risk_matrices: id, name, likelihood_scale, impact_scale, risk_levels, is_default, created_at, updated_at

-- Compliance & Frameworks
frameworks: id, name, version, description, type, is_active, created_at, updated_at
controls: id, framework_id, control_id, title, description, control_type, implementation_guidance, testing_procedures, created_at, updated_at
assessments: id, name, framework_id, scope, status, start_date, end_date, assessor_id, created_at, updated_at

-- Evidence & Documentation
evidence: id, title, description, file_path, file_type, file_size, upload_date, uploaded_by, tags, metadata, created_at, updated_at
tasks: id, title, description, type, status, priority, assignee_id, due_date, created_at, updated_at, completed_at

-- Integrations & External Data
integrations: id, name, type, config, is_active, last_sync, created_at, updated_at
vulnerability_data: id, asset_id, cve_id, severity, description, status, discovered_date, remediation_date
threat_intel_data: id, indicator, type, source, confidence, last_seen, tags, metadata
```

## 3. Development Environment Setup

### 3.1 Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd iwillgetthis

# Backend setup with virtual environment (MANDATORY)
cd aegis-platform/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend/aegis-frontend
pnpm install

# Database initialization
cd ../../backend
python init_db_complete.py
alembic upgrade head
```

### 3.2 Development Workflow

#### Port Management
- **Backend**: Random port via `$(shuf -i 10000-65535 -n 1)`
- **Frontend**: Random port via `$(shuf -i 10000-65535 -n 1)`
- **Database**: Default ports (3306 MySQL, 6379 Redis)

#### Daily Development Commands
```bash
# Backend (always in virtual environment)
cd aegis-platform/backend
source venv/bin/activate
python run_server.py --port $(shuf -i 10000-65535 -n 1)

# Frontend (separate terminal)
cd aegis-platform/frontend/aegis-frontend
pnpm run dev --port $(shuf -i 10000-65535 -n 1)

# After feature completion
python -m pytest tests/ -v  # Backend tests
npm test                    # Frontend tests
git add .
git commit -m "feat: feature description"
```

### 3.3 Environment Variables

#### Backend (.env)
```bash
# Core Application
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./aegis_development.db
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production

# AI Providers
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
AZURE_OPENAI_API_KEY=your-azure-openai-key

# External Integrations
OPENVAS_HOST=localhost
OPENCTI_URL=http://localhost:8080
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@domain.com
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API=false
VITE_ENVIRONMENT=development
```

## 4. API Specifications

### 4.1 Authentication Endpoints
```yaml
POST /api/v1/auth/login:
  summary: User authentication
  request:
    email: string
    password: string
  response:
    access_token: string
    refresh_token: string
    user: User object

POST /api/v1/auth/register:
  summary: User registration
  request:
    email: string
    username: string
    password: string
    full_name: string
  response:
    user: User object

POST /api/v1/auth/refresh:
  summary: Token refresh
  request:
    refresh_token: string
  response:
    access_token: string
```

### 4.2 Asset Management Endpoints
```yaml
GET /api/v1/assets:
  summary: List assets with filtering and pagination
  parameters:
    page: integer (default: 1)
    size: integer (default: 20)
    category: string (optional)
    criticality: string (optional)
    search: string (optional)
  response:
    items: Asset[]
    total: integer
    page: integer
    size: integer

POST /api/v1/assets:
  summary: Create new asset
  request:
    name: string
    description: string (optional)
    asset_type: string
    criticality: enum ['low', 'medium', 'high', 'critical']
    owner_id: integer (optional)
    metadata: object (optional)
  response:
    Asset object

PUT /api/v1/assets/{asset_id}:
  summary: Update asset
  request:
    Asset object (partial updates allowed)
  response:
    Asset object

DELETE /api/v1/assets/{asset_id}:
  summary: Delete asset
  response:
    success: boolean
```

### 4.3 Risk Management Endpoints
```yaml
GET /api/v1/risks:
  summary: List risks with filtering
  parameters:
    status: string (optional)
    category: string (optional)
    severity: string (optional)
    owner_id: integer (optional)
  response:
    items: Risk[]
    total: integer

POST /api/v1/risks:
  summary: Create new risk
  request:
    title: string
    description: string
    category: enum
    likelihood: integer (1-5)
    impact: integer (1-5)
    owner_id: integer
  response:
    Risk object

GET /api/v1/risks/{risk_id}/analysis:
  summary: AI-powered risk analysis
  response:
    analysis: string
    recommendations: string[]
    severity_score: float
    confidence: float
```

### 4.4 AI Service Endpoints
```yaml
POST /api/v1/ai/analyze-evidence:
  summary: Analyze uploaded evidence using AI
  request:
    file: multipart/form-data
    context: string (optional)
  response:
    summary: string
    key_findings: string[]
    risk_indicators: string[]
    compliance_gaps: string[]

POST /api/v1/ai/generate-risk-statement:
  summary: Generate risk statement using AI
  request:
    asset_id: integer
    threat_scenario: string
    context: string (optional)
  response:
    risk_statement: string
    likelihood_assessment: string
    impact_assessment: string
    recommendations: string[]

GET /api/v1/ai/providers:
  summary: List available AI providers and their status
  response:
    providers: AIProvider[]
    default_provider: string
    health_status: object
```

## 5. Testing Requirements

### 5.1 Testing Strategy
- **Unit Tests**: 80%+ code coverage requirement
- **Integration Tests**: API endpoint testing
- **End-to-End Tests**: Critical user workflows
- **Regression Tests**: Mandatory after every feature
- **Security Tests**: Authentication and authorization

### 5.2 Backend Testing
```bash
# Test structure
tests/
├── unit/
│   ├── test_models.py
│   ├── test_ai_providers.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/
│   ├── test_api_auth.py
│   ├── test_api_assets.py
│   ├── test_api_risks.py
│   └── test_database.py
└── e2e/
    ├── test_user_workflows.py
    └── test_ai_integration.py

# Run tests
python -m pytest tests/ -v --cov=. --cov-report=html
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
```

### 5.3 Frontend Testing
```bash
# Test structure
src/
├── __tests__/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   └── utils/
├── components/
│   └── __tests__/
└── pages/
    └── __tests__/

# Run tests
npm test                    # All tests
npm run test:unit          # Unit tests only
npm run test:integration   # Integration tests
npm run test:e2e          # End-to-end tests
npm run test:coverage     # Coverage report
```

### 5.4 Test Data Management
```python
# Backend test fixtures
@pytest.fixture
def test_user():
    return User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password_here"
    )

@pytest.fixture
def test_asset():
    return Asset(
        name="Test Server",
        asset_type="server",
        criticality="high",
        location="Data Center 1"
    )

# Mock AI responses for testing
@pytest.fixture
def mock_ai_response():
    return {
        "analysis": "Test analysis result",
        "risk_score": 0.75,
        "recommendations": ["Test recommendation 1", "Test recommendation 2"]
    }
```

## 6. Code Quality & Standards

### 6.1 Code Style Guidelines

#### Python (Backend)
```python
# Use type hints everywhere
def create_risk(risk_data: RiskCreate, user_id: int) -> Risk:
    """Create a new risk with proper validation."""
    
# Follow PEP 8 with 100 character line limit
# Use black code formatter
# Use isort for import sorting
# Use mypy for type checking

# Error handling pattern
try:
    result = await some_async_operation()
    return result
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

#### TypeScript (Frontend)
```typescript
// Strict type definitions
interface RiskData {
  id: number;
  title: string;
  description?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
}

// Component props with proper typing
interface RiskCardProps {
  risk: RiskData;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

// Use proper error boundaries
const RiskCard: React.FC<RiskCardProps> = ({ risk, onEdit, onDelete }) => {
  // Component implementation
};
```

### 6.2 Git Workflow
```bash
# Branch naming
feature/risk-assessment-automation
bugfix/dashboard-rendering-issue
hotfix/security-vulnerability-patch

# Commit message format (Conventional Commits)
feat: add AI-powered risk analysis endpoint
fix: resolve database connection timeout issue
docs: update API documentation for authentication
test: add unit tests for risk scoring algorithm
refactor: optimize database queries for asset management

# Required workflow
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "feat: implement new feature"
python -m pytest tests/ -v  # Must pass
npm test                    # Must pass
git push origin feature/new-feature
# Create pull request
```

### 6.3 Security Requirements
- **Input Validation**: All user inputs validated with Pydantic schemas
- **SQL Injection Prevention**: Use SQLAlchemy ORM exclusively
- **XSS Prevention**: Sanitize all user-generated content
- **CSRF Protection**: Implement CSRF tokens for state-changing operations
- **Rate Limiting**: Implement rate limiting on all public endpoints
- **Dependency Scanning**: Regular security audits of dependencies
- **Secret Management**: Never commit secrets; use environment variables

## 7. AI Integration Specifications

### 7.1 Multi-Provider Architecture
```python
# Provider interface
class BaseLLMProvider:
    def __init__(self, config: ProviderConfig):
        self.config = config
        
    async def generate_text(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError
        
    async def health_check(self) -> bool:
        raise NotImplementedError
        
    def get_cost_estimate(self, tokens: int) -> float:
        raise NotImplementedError

# Provider registration
providers = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'google': GoogleProvider,
    'azure_openai': AzureOpenAIProvider,
    # ... 14+ providers total
}
```

### 7.2 AI Use Cases
- **Evidence Analysis**: Document summarization and key finding extraction
- **Risk Assessment**: Automated risk scoring based on threat intelligence
- **Control Gap Analysis**: Compliance framework gap identification
- **Remediation Planning**: Automated mitigation strategy generation
- **Executive Reporting**: Business-focused risk summaries

### 7.3 Provider Failover Logic
```python
async def generate_with_failover(prompt: str, providers: List[str]) -> str:
    for provider_name in providers:
        try:
            provider = get_provider(provider_name)
            if await provider.health_check():
                return await provider.generate_text(prompt)
        except Exception as e:
            logger.warning(f"Provider {provider_name} failed: {e}")
            continue
    raise Exception("All providers failed")
```

## 8. Deployment Specifications

### 8.1 Docker Configuration
```yaml
# docker-compose.yml structure
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/aegis
    depends_on:
      - db
      - redis
    
  frontend:
    build: ./frontend/aegis-frontend
    environment:
      - VITE_API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    
  db:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=aegis
      - MYSQL_USER=aegis_user
      - MYSQL_PASSWORD=secure_password
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
```

### 8.2 Production Requirements
- **Database**: MySQL 8.0+ with connection pooling
- **Caching**: Redis for session storage and API caching
- **Load Balancing**: Nginx reverse proxy for high availability
- **SSL/TLS**: HTTPS everywhere with valid certificates
- **Monitoring**: Prometheus + Grafana for metrics
- **Logging**: Centralized logging with ELK stack
- **Backup**: Automated database backups with point-in-time recovery

### 8.3 Performance Requirements
- **API Response Time**: < 200ms for standard operations
- **AI Analysis Time**: < 30 seconds for document analysis
- **Database Query Time**: < 100ms for complex queries
- **Concurrent Users**: Support 100+ concurrent users
- **File Upload**: Support files up to 50MB
- **Database Size**: Optimize for 1M+ records per table

## 9. Monitoring & Observability

### 9.1 Logging Strategy
```python
# Structured logging with context
import structlog

logger = structlog.get_logger(__name__)

# In API endpoints
logger.info(
    "Risk analysis completed",
    user_id=user.id,
    risk_id=risk.id,
    provider_used="openai",
    analysis_duration_ms=1250,
    confidence_score=0.85
)

# Error logging with context
logger.error(
    "AI provider failed",
    provider="anthropic",
    error_type="rate_limit",
    retry_count=3,
    user_id=user.id
)
```

### 9.2 Metrics Collection
- **Business Metrics**: Risk assessments completed, evidence analyzed
- **Technical Metrics**: API response times, database query performance
- **AI Metrics**: Provider usage, token consumption, cost tracking
- **Security Metrics**: Failed login attempts, unauthorized access
- **Infrastructure Metrics**: CPU/memory usage, disk space, network traffic

### 9.3 Health Checks
```python
# Comprehensive health check endpoint
@router.get("/health")
async def health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "ai_providers": await check_ai_providers(),
        "external_integrations": await check_external_apis()
    }
    
    overall_status = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow(),
        "checks": checks,
        "version": app_version
    }
```

## 10. Documentation Requirements

### 10.1 API Documentation
- **OpenAPI/Swagger**: Auto-generated from FastAPI
- **Interactive Docs**: Available at `/docs` and `/redoc`
- **Postman Collection**: Exportable API collection
- **Code Examples**: Request/response examples in multiple languages

### 10.2 User Documentation
- **Admin Guide**: System administration and configuration
- **User Manual**: End-user feature documentation
- **API Guide**: Developer integration documentation
- **Deployment Guide**: Production deployment instructions

### 10.3 Developer Documentation
- **Architecture Overview**: System design and component interaction
- **Development Setup**: Environment configuration and setup
- **Contributing Guide**: Code contribution guidelines
- **Troubleshooting**: Common issues and solutions

This specification serves as the comprehensive guide for developing, testing, and deploying the Aegis Risk Management Platform. All development work should follow these specifications to ensure consistency, quality, and maintainability.