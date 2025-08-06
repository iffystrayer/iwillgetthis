# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Aegis Risk Management Platform - a comprehensive, enterprise-grade cybersecurity risk management system with AI-powered security analysis capabilities. The platform integrates multiple LLM providers for automated risk assessment and evidence analysis.

## Project Structure

```
aegis-platform/
├── backend/              # FastAPI Python backend
│   ├── ai_providers/     # Multi-LLM provider implementations (14+ providers)
│   ├── models/          # SQLAlchemy database models  
│   ├── routers/         # FastAPI route handlers
│   ├── schemas/         # Pydantic data validation schemas
│   ├── alembic/         # Database migrations
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Comprehensive configuration management
│   └── run_server.py    # Direct server runner for debugging
├── frontend/aegis-frontend/  # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components (using shadcn/ui)
│   │   ├── pages/       # Application pages
│   │   ├── lib/         # API clients and utilities
│   │   ├── hooks/       # React hooks
│   │   └── types/       # TypeScript type definitions
├── docker/              # Docker compose configuration
└── docs/               # Additional documentation
```

## Development Commands

### Frontend (React + TypeScript + Vite)
```bash
cd aegis-platform/frontend/aegis-frontend

# Install dependencies and start development server (uses random port)
pnpm run dev --port $(shuf -i 10000-65535 -n 1)

# Build for production
pnpm run build

# Lint code
pnpm run lint

# Preview production build (uses random port)
pnpm run preview --port $(shuf -i 10000-65535 -n 1)

# Run regression tests (includes unit tests, E2E tests, and linting)
npm run test:regression

# Run individual test suites
npm run test:unit         # Unit tests
npm run test:e2e          # Playwright E2E tests
npm test                  # Combined unit + E2E tests
```

### Backend (FastAPI + Python)
```bash
cd aegis-platform/backend

# Always use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server (uses random port)
python run_server.py --port $(shuf -i 10000-65535 -n 1)

# Alternative with uvicorn directly (uses random port)
uvicorn main:app --host 0.0.0.0 --port $(shuf -i 10000-65535 -n 1) --reload

# Initialize database
python init_db_complete.py

# Run database migrations
alembic upgrade head

# Run regression tests
python -m pytest tests/ -v
```

### Docker Deployment
```bash
cd aegis-platform

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## Development Workflow

### Required Workflow Steps
1. **Virtual Environment**: Always activate Python virtual environment before any Python operations
2. **Random Ports**: Use random 5-digit TCP ports (10000-65535) to avoid conflicts
3. **Never launch app with ports 3000 and 8000. Use unique random 5-digit numbered ports instead**
4. **Regression Testing**: Run both backend and frontend regression tests after every feature implementation
5. **Playwright Testing**: Run Playwright E2E tests to verify UI functionality and prevent regressions
6. **Commit Always**: Commit all changes immediately after completing features
7. **No Permission Prompts**: Do not prompt for permissions except for file system manipulations

### Git Workflow
```bash
# After every feature completion
git add .
git commit -m "feat: description of feature"

# Run regression tests before pushing
python -m pytest tests/ -v                    # Backend tests
npm test                                       # Frontend unit tests  
npx playwright test                            # E2E UI functionality tests
npx playwright test button-functionality.spec.ts  # Button regression tests

git push origin main
```

## Architecture & Key Components

### Backend Architecture
- **FastAPI**: Modern async Python web framework with automatic OpenAPI docs
- **SQLAlchemy**: ORM with comprehensive models for cybersecurity risk management
- **Multi-LLM Service**: Modular AI provider system supporting 14+ LLM providers with automatic failover
- **Database**: SQLite (development) → MySQL (production) with Alembic migrations
- **Authentication**: JWT-based with role-based access control (Admin, Analyst, ReadOnly)

### Frontend Architecture  
- **React 18**: Modern functional components with hooks
- **TypeScript**: Full type safety throughout the application
- **TailwindCSS + shadcn/ui**: Professional UI component library
- **React Router**: Client-side routing for SPA
- **Axios**: HTTP client with mock API fallback system
- **React Query**: Server state management and caching

### Core Domain Models
The application manages cybersecurity risk through these key entities:
- **Assets**: Organizational assets with risk categorization
- **Risks**: Risk register with scoring and prioritization
- **Frameworks**: Security frameworks (NIST, ISO27001, etc.)
- **Assessments**: Security assessments and control evaluations
- **Evidence**: Supporting documentation and proof
- **Tasks**: Risk remediation and compliance tasks
- **Reports**: Automated risk reporting and dashboards

### AI/LLM Integration
- **Multi-Provider Support**: OpenAI, Azure OpenAI, Google Gemini, Anthropic Claude, LiteLLM, OpenRouter, Together AI, DeepSeek, Cohere, Mistral, Hugging Face, Ollama, LM Studio, Text Generation WebUI
- **AI-Powered Features**: Evidence analysis, risk statement generation, control narrative generation, remediation suggestions, executive summaries
- **Failover System**: Automatic provider switching with performance monitoring
- **Cost Tracking**: Provider usage and cost optimization

## Configuration

### Environment Variables
Key configuration is managed through environment variables in `backend/config.py`:

**Core Application:**
- `DATABASE_URL`: SQLite file path for development, MySQL connection string for production
- `SECRET_KEY` / `JWT_SECRET_KEY`: Security keys for authentication
- `CORS_ORIGINS`: Allowed frontend origins

**Database Migration Path:**
- Development: `sqlite:///./aegis_development.db`
- Production: `mysql://user:password@host:port/database`

**AI Providers:**
- `DEFAULT_LLM_PROVIDER`: Primary LLM provider (defaults to "openai")
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.: Provider API keys
- `ENABLE_*_PROVIDER`: Feature flags for each provider

**External Integrations:**
- `OPENVAS_HOST`, `OPENCTI_URL`: Vulnerability scanners and threat intelligence
- `AZURE_CLIENT_ID`: Microsoft Entra ID authentication

### API Configuration
- Frontend API client supports both real backend and comprehensive mock API system
- Mock API automatically activated when `VITE_USE_MOCK_API=true` or backend unavailable
- Base URL: Random port assignment for development, fixed ports for production

## Development Notes

### Virtual Environment Management
- **Always Required**: All Python operations must use virtual environment
- **Setup**: `python -m venv venv && source venv/bin/activate`
- **Verification**: `which python` should point to venv directory

### Database Management
- **Development**: SQLite database file (`aegis_development.db`)
- **Production**: MySQL with connection pooling and transactions
- **Migration Path**: Alembic handles schema changes between SQLite and MySQL
- **Commands**: 
  - `alembic revision --autogenerate -m "description"`
  - `alembic upgrade head`

### Port Management
- **Development**: Always use random ports (10000-65535) via `$(shuf -i 10000-65535 -n 1)`
- **Frontend**: Update VITE_API_URL to match backend port
- **Backend**: Update CORS_ORIGINS to match frontend port

### AI Provider Development
- New providers should extend `backend/ai_providers/base.py`
- Provider registration happens in `backend/multi_llm_service.py`
- Each provider supports health checks, cost tracking, and performance monitoring

### Frontend Development
- Uses shadcn/ui component library - avoid creating custom components when shadcn alternatives exist
- API calls should use the `@/lib/api.ts` client which handles mock/real API switching
- Type definitions in `@/types/` should be kept in sync with backend schemas

### Testing Strategy
- **Regression Tests**: Must run after every feature completion
- **Backend**: `python -m pytest tests/ -v` in virtual environment
- **Frontend Unit**: `npm test` for component and integration tests
- **E2E Testing**: `npx playwright test` for full user workflow verification
- **Button Regression**: `npx playwright test button-functionality.spec.ts` for UI interaction verification
- **Integration**: End-to-end testing with real AI providers (when API keys available)

### Playwright Testing Guidelines
- Run after every UI feature implementation
- Verify button functionality doesn't regress
- Test complete user workflows (login → navigation → actions)
- Capture screenshots for visual verification
- Automated testing prevents manual testing issues from recurring

## Common Issues

### Backend Issues
- **Virtual Environment**: Ensure `source venv/bin/activate` before any Python commands
- **Database Connection**: SQLite file permissions for development, MySQL connectivity for production
- **AI Provider Failures**: Check API keys and provider health endpoints
- **Port Conflicts**: Always use random port assignment

### Frontend Issues  
- **API Connection**: Frontend automatically falls back to mock API if backend unavailable
- **Build Errors**: Ensure all environment variables are set correctly
- **Port Conflicts**: Use random port assignment for development servers
- **Type Errors**: Keep TypeScript types in sync with backend Pydantic schemas

## Security Considerations

- Never commit API keys or secrets to the repository
- All AI provider integrations support secure credential management
- JWT tokens are httpOnly cookies for security
- File uploads are validated and sanitized
- Database queries use SQLAlchemy ORM to prevent injection attacks
- Virtual environment isolation prevents system-wide package conflicts

## Memories

### Workflow Management
- remember to fix the assessment workflow