# Developer Guide - Aegis Risk Management Platform

## Overview

This guide provides comprehensive information for developers contributing to the Aegis Risk Management Platform. It covers development environment setup, coding standards, contribution processes, and best practices for both frontend and backend development.

## Development Environment Setup

### Prerequisites

#### System Requirements
- **Operating System**: macOS, Linux, or Windows 10/11
- **Memory**: 16GB RAM minimum (32GB recommended)
- **Storage**: 50GB available space
- **Network**: Reliable internet connection for dependency downloads

#### Required Software
- **Git**: Version 2.30 or higher
- **Node.js**: Version 18.x or higher (LTS recommended)
- **Python**: Version 3.9 or higher
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### Backend Development Setup

#### Python Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-org/aegis-platform.git
cd aegis-platform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
vim .env
```

Required environment variables:
```bash
# Database Configuration
DATABASE_URL=sqlite:///./aegis_development.db

# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# AI Provider Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Development Settings
DEBUG=True
DEVELOPMENT_MODE=True
LOG_LEVEL=DEBUG
```

#### Database Setup
```bash
# Initialize database
python init_db_complete.py

# Run migrations
alembic upgrade head

# Seed development data (optional)
python scripts/seed_dev_data.py
```

#### Running Backend Development Server
```bash
# Start development server
python run_server.py --port 8001 --reload

# Alternative with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Development Setup

#### Node.js Environment Setup
```bash
# Navigate to frontend directory
cd aegis-platform/frontend/aegis-frontend

# Install dependencies
pnpm install

# Copy environment template
cp .env.example .env.local
```

Required environment variables:
```bash
# API Configuration
VITE_API_URL=http://localhost:8001/api/v1
VITE_USE_MOCK_API=false

# Development Settings
VITE_ENVIRONMENT=development
VITE_LOG_LEVEL=debug
```

#### Running Frontend Development Server
```bash
# Start development server with random port
pnpm run dev --port $(shuf -i 10000-65535 -n 1)

# Or with specific port
pnpm run dev --port 3001
```

### Docker Development Environment

#### Complete Stack Setup
```bash
# From project root directory
cd aegis-platform

# Build and start all services
docker-compose -f docker/docker-compose.dev.yml up --build

# Run in detached mode
docker-compose -f docker/docker-compose.dev.yml up -d

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.dev.yml down
```

#### Development Docker Configuration
```yaml
# docker/docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.dev
    ports:
      - "8001:8000"
    volumes:
      - ../backend:/app
      - /app/venv
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:password@db:5432/aegis_dev
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ../frontend/aegis-frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3001:3000"
    volumes:
      - ../frontend/aegis-frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: aegis_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Project Structure

### Backend Structure
```
backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── ai_providers/              # LLM provider implementations
│   ├── base.py               # Abstract base provider
│   ├── openai_provider.py    # OpenAI implementation
│   └── anthropic_provider.py # Anthropic implementation
├── models/                    # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py               # User authentication model
│   ├── asset.py              # Asset management model
│   ├── risk.py               # Risk assessment model
│   └── compliance.py         # Compliance framework model
├── routers/                   # FastAPI route handlers
│   ├── auth.py               # Authentication endpoints
│   ├── assets.py             # Asset management endpoints
│   ├── risks.py              # Risk management endpoints
│   └── compliance.py         # Compliance endpoints
├── schemas/                   # Pydantic validation schemas
│   ├── auth.py               # Authentication schemas
│   ├── asset.py              # Asset schemas
│   └── risk.py               # Risk schemas
├── services/                  # Business logic services
│   ├── auth_service.py       # Authentication service
│   ├── risk_service.py       # Risk calculation service
│   └── compliance_service.py # Compliance management
├── utils/                     # Utility functions
│   ├── database.py           # Database utilities
│   ├── security.py           # Security utilities
│   └── logging.py            # Logging configuration
├── tests/                     # Test files
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── conftest.py           # Test configuration
├── main.py                    # FastAPI application
├── config.py                  # Configuration management
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
└── run_server.py             # Development server runner
```

### Frontend Structure
```
frontend/aegis-frontend/
├── public/                    # Static assets
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # shadcn/ui components
│   │   ├── forms/           # Form components
│   │   ├── charts/          # Chart components
│   │   └── dialogs/         # Dialog components
│   ├── pages/               # Application pages
│   │   ├── auth/            # Authentication pages
│   │   ├── dashboard/       # Dashboard pages
│   │   ├── risks/           # Risk management pages
│   │   └── assets/          # Asset management pages
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication hook
│   │   ├── useApi.ts        # API interaction hook
│   │   └── useLocalStorage.ts # Local storage hook
│   ├── lib/                 # Utility libraries
│   │   ├── api.ts           # API client
│   │   ├── auth.ts          # Authentication utilities
│   │   └── utils.ts         # General utilities
│   ├── types/               # TypeScript type definitions
│   │   ├── auth.ts          # Authentication types
│   │   ├── api.ts           # API response types
│   │   └── common.ts        # Common types
│   ├── styles/              # Global styles
│   └── main.tsx             # Application entry point
├── tests/                   # Test files
│   ├── components/          # Component tests
│   ├── pages/               # Page tests
│   ├── utils/               # Utility tests
│   └── setup.ts             # Test setup
├── playwright/              # E2E tests
│   ├── tests/               # Test files
│   └── playwright.config.ts # Playwright configuration
├── package.json             # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## Coding Standards

### Python Backend Standards

#### Code Style
- **PEP 8**: Follow Python Enhancement Proposal 8 styling guidelines
- **Black**: Use Black code formatter with 88-character line length
- **isort**: Use isort for import sorting
- **flake8**: Use flake8 for linting with custom configuration

#### Code Quality Tools Configuration
```ini
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = alembic/
```

#### Type Hints
```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel

# Function type hints
def calculate_risk_score(
    likelihood: int, 
    impact: int,
    controls: Optional[List[str]] = None
) -> float:
    """Calculate risk score based on likelihood and impact."""
    if controls is None:
        controls = []
    
    base_score = likelihood * impact
    control_reduction = len(controls) * 0.1
    
    return max(0.0, base_score - control_reduction)

# Class type hints
class RiskAssessment(BaseModel):
    asset_id: str
    likelihood: int
    impact: int
    controls: List[str]
    calculated_score: Optional[float] = None
```

#### Error Handling Patterns
```python
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

async def create_risk(risk_data: RiskCreate) -> Risk:
    """Create a new risk with proper error handling."""
    try:
        # Validate input data
        if risk_data.likelihood < 1 or risk_data.likelihood > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Likelihood must be between 1 and 5"
            )
        
        # Create risk object
        risk = Risk(**risk_data.dict())
        db.add(risk)
        await db.commit()
        await db.refresh(risk)
        
        logger.info(f"Created risk {risk.id} for asset {risk.asset_id}")
        return risk
        
    except SQLAlchemyError as e:
        logger.error(f"Database error creating risk: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### TypeScript Frontend Standards

#### Code Style Configuration
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off"
  }
}
```

#### Component Patterns
```typescript
// components/RiskCard.tsx
import { FC, memo } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface RiskCardProps {
  risk: Risk;
  onEdit?: (risk: Risk) => void;
  onDelete?: (riskId: string) => void;
  className?: string;
}

export const RiskCard: FC<RiskCardProps> = memo(({
  risk,
  onEdit,
  onDelete,
  className = ''
}) => {
  const handleEdit = (): void => {
    onEdit?.(risk);
  };

  const handleDelete = (): void => {
    if (window.confirm('Are you sure you want to delete this risk?')) {
      onDelete?.(risk.id);
    }
  };

  const getSeverityColor = (score: number): string => {
    if (score >= 15) return 'destructive';
    if (score >= 10) return 'warning';
    if (score >= 5) return 'secondary';
    return 'default';
  };

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="text-sm font-medium">{risk.title}</h3>
        <Badge variant={getSeverityColor(risk.riskScore)}>
          {risk.riskScore}
        </Badge>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground mb-2">
          {risk.description}
        </p>
        <div className="flex justify-between text-xs">
          <span>Owner: {risk.owner}</span>
          <span>Due: {risk.dueDate}</span>
        </div>
        <div className="flex gap-2 mt-2">
          <button
            onClick={handleEdit}
            className="text-xs text-blue-600 hover:underline"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="text-xs text-red-600 hover:underline"
          >
            Delete
          </button>
        </div>
      </CardContent>
    </Card>
  );
});

RiskCard.displayName = 'RiskCard';
```

#### Hook Patterns
```typescript
// hooks/useRisks.ts
import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Risk, RiskFilters } from '@/types/risk';

interface UseRisksReturn {
  risks: Risk[];
  loading: boolean;
  error: Error | null;
  filters: RiskFilters;
  setFilters: (filters: RiskFilters) => void;
  createRisk: (risk: Partial<Risk>) => Promise<Risk>;
  updateRisk: (id: string, risk: Partial<Risk>) => Promise<Risk>;
  deleteRisk: (id: string) => Promise<void>;
  refetch: () => void;
}

export const useRisks = (initialFilters: RiskFilters = {}): UseRisksReturn => {
  const [filters, setFilters] = useState<RiskFilters>(initialFilters);
  const queryClient = useQueryClient();

  const {
    data: risks = [],
    isLoading: loading,
    error,
    refetch
  } = useQuery({
    queryKey: ['risks', filters],
    queryFn: () => api.risks.list(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const createMutation = useMutation({
    mutationFn: (risk: Partial<Risk>) => api.risks.create(risk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, risk }: { id: string; risk: Partial<Risk> }) =>
      api.risks.update(id, risk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.risks.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
    },
  });

  const createRisk = useCallback(
    async (risk: Partial<Risk>): Promise<Risk> => {
      return createMutation.mutateAsync(risk);
    },
    [createMutation]
  );

  const updateRisk = useCallback(
    async (id: string, risk: Partial<Risk>): Promise<Risk> => {
      return updateMutation.mutateAsync({ id, risk });
    },
    [updateMutation]
  );

  const deleteRisk = useCallback(
    async (id: string): Promise<void> => {
      return deleteMutation.mutateAsync(id);
    },
    [deleteMutation]
  );

  return {
    risks,
    loading,
    error,
    filters,
    setFilters,
    createRisk,
    updateRisk,
    deleteRisk,
    refetch
  };
};
```

## Testing Standards

### Backend Testing

#### Unit Testing with pytest
```python
# tests/unit/test_risk_service.py
import pytest
from unittest.mock import Mock, patch
from services.risk_service import RiskService
from models.risk import Risk

class TestRiskService:
    @pytest.fixture
    def risk_service(self):
        return RiskService()
    
    @pytest.fixture
    def sample_risk_data(self):
        return {
            'title': 'Test Risk',
            'description': 'Test Description',
            'likelihood': 3,
            'impact': 4,
            'asset_id': 'asset-123'
        }
    
    def test_calculate_risk_score(self, risk_service):
        """Test risk score calculation"""
        score = risk_service.calculate_risk_score(
            likelihood=3, 
            impact=4, 
            controls=['control1', 'control2']
        )
        
        # Base score: 3 * 4 = 12
        # Control reduction: 2 * 0.1 = 0.2
        # Expected: 12 - 0.2 = 11.8
        assert score == 11.8
    
    def test_calculate_risk_score_no_controls(self, risk_service):
        """Test risk score calculation without controls"""
        score = risk_service.calculate_risk_score(likelihood=3, impact=4)
        assert score == 12.0
    
    @patch('services.risk_service.db')
    async def test_create_risk(self, mock_db, risk_service, sample_risk_data):
        """Test risk creation"""
        mock_risk = Mock(spec=Risk)
        mock_risk.id = 'risk-123'
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        with patch.object(Risk, '__init__', return_value=None):
            with patch.object(risk_service, 'calculate_risk_score', return_value=12.0):
                result = await risk_service.create_risk(sample_risk_data)
                
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
```

#### Integration Testing
```python
# tests/integration/test_risk_api.py
import pytest
from fastapi.testclient import TestClient
from main import app
from tests.conftest import test_db

client = TestClient(app)

class TestRiskAPI:
    def test_create_risk_success(self, auth_headers):
        """Test successful risk creation"""
        risk_data = {
            'title': 'Integration Test Risk',
            'description': 'Test risk for integration',
            'likelihood': 3,
            'impact': 4,
            'asset_id': 'asset-123'
        }
        
        response = client.post(
            '/api/v1/risks',
            json=risk_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data['title'] == risk_data['title']
        assert 'id' in data
        assert 'created_at' in data
    
    def test_get_risks_with_filters(self, auth_headers):
        """Test risk retrieval with filters"""
        response = client.get(
            '/api/v1/risks?severity=high&status=open',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        for risk in data:
            assert risk['status'] == 'open'
            assert risk['risk_score'] >= 10  # High severity threshold
```

### Frontend Testing

#### Component Testing with React Testing Library
```typescript
// tests/components/RiskCard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { RiskCard } from '@/components/RiskCard';
import { Risk } from '@/types/risk';

const mockRisk: Risk = {
  id: 'risk-1',
  title: 'Test Risk',
  description: 'Test Description',
  likelihood: 3,
  impact: 4,
  riskScore: 12,
  owner: 'john.doe@company.com',
  dueDate: '2024-12-31',
  status: 'open',
  assetId: 'asset-1'
};

describe('RiskCard', () => {
  it('renders risk information correctly', () => {
    render(<RiskCard risk={mockRisk} />);
    
    expect(screen.getByText('Test Risk')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
    expect(screen.getByText(/Owner: john.doe@company.com/)).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', async () => {
    const onEdit = vi.fn();
    render(<RiskCard risk={mockRisk} onEdit={onEdit} />);
    
    fireEvent.click(screen.getByText('Edit'));
    
    await waitFor(() => {
      expect(onEdit).toHaveBeenCalledWith(mockRisk);
    });
  });

  it('shows confirmation dialog and calls onDelete', async () => {
    const onDelete = vi.fn();
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    
    render(<RiskCard risk={mockRisk} onDelete={onDelete} />);
    
    fireEvent.click(screen.getByText('Delete'));
    
    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this risk?');
      expect(onDelete).toHaveBeenCalledWith('risk-1');
    });
  });

  it('applies correct severity color based on risk score', () => {
    const highRisk = { ...mockRisk, riskScore: 16 };
    const { rerender } = render(<RiskCard risk={highRisk} />);
    
    expect(screen.getByText('16')).toHaveClass('bg-destructive');
    
    const mediumRisk = { ...mockRisk, riskScore: 8 };
    rerender(<RiskCard risk={mediumRisk} />);
    
    expect(screen.getByText('8')).toHaveClass('bg-secondary');
  });
});
```

#### E2E Testing with Playwright
```typescript
// playwright/tests/risk-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Risk Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[data-testid=email]', 'test@company.com');
    await page.fill('[data-testid=password]', 'testpassword');
    await page.click('[data-testid=login-button]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should create a new risk', async ({ page }) => {
    await page.goto('/risks');
    
    // Click create risk button
    await page.click('[data-testid=create-risk-button]');
    
    // Fill risk form
    await page.fill('[data-testid=risk-title]', 'E2E Test Risk');
    await page.fill('[data-testid=risk-description]', 'Risk created by E2E test');
    await page.selectOption('[data-testid=likelihood-select]', '3');
    await page.selectOption('[data-testid=impact-select]', '4');
    await page.selectOption('[data-testid=asset-select]', 'asset-1');
    
    // Submit form
    await page.click('[data-testid=submit-risk]');
    
    // Verify risk appears in list
    await expect(page.locator('[data-testid=risk-card]').first()).toBeVisible();
    await expect(page.getByText('E2E Test Risk')).toBeVisible();
  });

  test('should filter risks by severity', async ({ page }) => {
    await page.goto('/risks');
    
    // Apply high severity filter
    await page.selectOption('[data-testid=severity-filter]', 'high');
    
    // Wait for filtered results
    await page.waitForLoadState('networkidle');
    
    // Verify all visible risks are high severity
    const riskScores = await page.locator('[data-testid=risk-score]').allTextContents();
    for (const score of riskScores) {
      expect(parseInt(score)).toBeGreaterThanOrEqual(15);
    }
  });
});
```

## Git Workflow and Contribution Process

### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature development branches
- **hotfix/**: Critical production fixes
- **release/**: Release preparation branches

### Commit Message Format
```bash
# Format: <type>(<scope>): <subject>

# Types:
feat: new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructuring
test: adding tests
chore: maintenance

# Examples:
feat(risk): add risk scoring algorithm
fix(auth): resolve JWT token expiration issue
docs(api): update endpoint documentation
test(components): add RiskCard component tests
```

### Pull Request Process

#### PR Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass (if applicable)
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] Any dependent changes have been merged and published
```

#### Code Review Guidelines
1. **Functionality**: Does the code work as expected?
2. **Code Quality**: Is the code clean, readable, and maintainable?
3. **Performance**: Are there any performance implications?
4. **Security**: Are there any security vulnerabilities?
5. **Testing**: Are there adequate tests for the changes?
6. **Documentation**: Is the documentation updated?

### Pre-commit Hooks Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.40.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        types: [file]
        additional_dependencies:
          - eslint@8.40.0
          - '@typescript-eslint/eslint-plugin@5.59.0'
          - '@typescript-eslint/parser@5.59.0'
```

## Performance Guidelines

### Backend Performance

#### Database Optimization
```python
# Efficient database queries
from sqlalchemy.orm import selectinload, joinedload

# Use eager loading for relationships
risks = session.query(Risk).options(
    selectinload(Risk.assets),
    selectinload(Risk.controls),
    joinedload(Risk.owner)
).filter(Risk.status == 'open').all()

# Use pagination for large datasets
def get_risks_paginated(page: int = 1, limit: int = 50):
    offset = (page - 1) * limit
    return session.query(Risk).offset(offset).limit(limit).all()

# Use database indexes
class Risk(Base):
    __tablename__ = 'risks'
    
    id = Column(String, primary_key=True)
    status = Column(String, index=True)  # Indexed for filtering
    risk_score = Column(Float, index=True)  # Indexed for sorting
    created_at = Column(DateTime, index=True)  # Indexed for time queries
```

#### Caching Strategies
```python
# Redis caching implementation
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)  # Cache for 10 minutes
async def get_risk_analytics():
    """Get risk analytics with caching"""
    # Expensive analytics calculation
    return calculate_risk_metrics()
```

### Frontend Performance

#### Component Optimization
```typescript
// Memoization for expensive calculations
import { useMemo, memo } from 'react';

interface RiskAnalyticsProps {
  risks: Risk[];
}

export const RiskAnalytics: React.FC<RiskAnalyticsProps> = memo(({ risks }) => {
  const analytics = useMemo(() => {
    // Expensive calculation only runs when risks change
    return calculateRiskAnalytics(risks);
  }, [risks]);

  return (
    <div>
      <div>High Risk Count: {analytics.highRiskCount}</div>
      <div>Average Score: {analytics.averageScore}</div>
    </div>
  );
});

// Virtual scrolling for large lists
import { VariableSizeList as List } from 'react-window';

const RiskList: React.FC<{ risks: Risk[] }> = ({ risks }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <RiskCard risk={risks[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={risks.length}
      itemSize={() => 120}
    >
      {Row}
    </List>
  );
};
```

#### Bundle Optimization
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'd3'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
});
```

## Security Guidelines

### Input Validation
```python
# Pydantic schema validation
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class RiskCreate(BaseModel):
    title: str
    description: str
    likelihood: int
    impact: int
    owner: EmailStr
    
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()
    
    @validator('likelihood', 'impact')
    def score_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Score must be between 1 and 5')
        return v
```

### Authentication and Authorization
```python
# JWT token validation
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
            
        return await get_user_by_id(user_id)
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

## Deployment and DevOps

### Docker Configuration

#### Multi-stage Dockerfile for Backend
```dockerfile
# Dockerfile
FROM python:3.9-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Make sure scripts are executable
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Multi-stage Dockerfile for Frontend
```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN pnpm run build

FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_aegis
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
          
      - name: Run linting
        run: |
          cd backend
          black --check .
          isort --check-only .
          flake8 .
          
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=. --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/aegis-frontend/package-lock.json
          
      - name: Install dependencies
        run: |
          cd frontend/aegis-frontend
          npm ci
          
      - name: Run linting
        run: |
          cd frontend/aegis-frontend
          npm run lint
          npm run type-check
          
      - name: Run unit tests
        run: |
          cd frontend/aegis-frontend
          npm test -- --coverage
          
      - name: Run E2E tests
        run: |
          cd frontend/aegis-frontend
          npx playwright install
          npm run test:e2e

  build-and-deploy:
    needs: [backend-tests, frontend-tests]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker images
        run: |
          docker build -t aegis-backend:latest ./backend
          docker build -t aegis-frontend:latest ./frontend/aegis-frontend
          
          # Push to registry (example)
          # docker tag aegis-backend:latest registry.company.com/aegis-backend:latest
          # docker push registry.company.com/aegis-backend:latest
```

---

**Last Updated**: August 6, 2025  
**Version**: 1.0  
**Applies To**: Aegis Platform v1.0+