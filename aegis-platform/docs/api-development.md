# API Development Standards and Best Practices

## Overview

This document outlines the API development standards, patterns, and best practices for the Aegis Risk Management Platform. All API development should follow these guidelines to ensure consistency, maintainability, and quality.

## Architecture Overview

### FastAPI Framework
- **Framework**: FastAPI with Python 3.11+
- **Async Support**: All endpoints support asynchronous operations
- **Automatic Documentation**: OpenAPI/Swagger documentation generated automatically
- **Type Safety**: Full Pydantic model validation for request/response data

### API Structure
```
backend/
├── routers/           # API route handlers organized by domain
├── schemas/          # Pydantic request/response schemas
├── models/           # SQLAlchemy database models
├── dependencies/     # Shared dependencies and middleware
├── auth.py          # Authentication and authorization
└── main.py          # FastAPI application setup
```

## API Design Standards

### RESTful Design Principles

#### Resource Naming
- Use **plural nouns** for resource collections: `/api/v1/assets`, `/api/v1/risks`
- Use **kebab-case** for multi-word resources: `/api/v1/user-roles`
- Avoid verbs in URLs - use HTTP methods instead

#### HTTP Methods
```python
# Resource Collections
GET    /api/v1/assets           # List all assets
POST   /api/v1/assets           # Create new asset
GET    /api/v1/assets/{id}      # Get specific asset
PUT    /api/v1/assets/{id}      # Update entire asset
PATCH  /api/v1/assets/{id}      # Partially update asset
DELETE /api/v1/assets/{id}      # Delete asset

# Sub-resources
GET    /api/v1/assets/{id}/risks    # Get risks for asset
POST   /api/v1/assets/{id}/risks    # Create risk for asset
```

#### Status Codes
Use appropriate HTTP status codes:
```python
# Success Codes
200 OK          # Successful GET, PUT, PATCH
201 Created     # Successful POST
204 No Content  # Successful DELETE

# Client Error Codes
400 Bad Request       # Invalid request data
401 Unauthorized      # Authentication required
403 Forbidden         # Insufficient permissions
404 Not Found         # Resource doesn't exist
409 Conflict          # Resource conflict (duplicate)
422 Unprocessable     # Validation errors

# Server Error Codes
500 Internal Server Error  # Unexpected server error
```

### API Versioning

#### URL Path Versioning
```python
# Current approach
/api/v1/assets
/api/v1/risks

# Future versions
/api/v2/assets  # Major breaking changes
```

#### Version Management
- **v1**: Current stable version
- **Backward Compatibility**: Maintain for at least 2 major versions
- **Deprecation**: 6-month notice before removal
- **Documentation**: Version-specific documentation

## Request/Response Patterns

### Standard Response Format

#### Success Response
```json
{
  "success": true,
  "data": {
    // Response data object or array
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Paginated Response
```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Request Validation

#### Pydantic Schemas
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class AssetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    asset_type: AssetType
    criticality: AssetCriticality
    ip_address: Optional[str] = Field(None, regex=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class AssetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    asset_type: AssetType
    criticality: AssetCriticality
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
```

## Authentication & Authorization

### JWT Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)) -> User:
    """Extract and validate current user from JWT token."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Permission-Based Authorization
```python
from functools import wraps
from fastapi import HTTPException

def require_permission(permission: str):
    """Decorator to check user permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission required: {permission}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in endpoints
@router.post("/assets")
@require_permission("create_asset")
async def create_asset(
    asset_data: AssetCreateRequest,
    current_user: User = Depends(get_current_user)
):
    # Implementation
```

## Database Integration

### SQLAlchemy Patterns

#### Model Relationships
```python
class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey("asset_categories.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    category = relationship("AssetCategory", back_populates="assets")
    creator = relationship("User", foreign_keys=[created_by])
    risks = relationship("Risk", back_populates="asset")
```

#### Repository Pattern
```python
class AssetRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, asset_data: AssetCreateRequest, user_id: int) -> Asset:
        """Create a new asset."""
        asset = Asset(**asset_data.dict(), created_by=user_id)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset
    
    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID."""
        return self.db.query(Asset).filter(Asset.id == asset_id).first()
    
    async def list_paginated(self, page: int = 1, per_page: int = 20) -> PaginatedResponse:
        """Get paginated list of assets."""
        query = self.db.query(Asset)
        total = query.count()
        
        assets = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return PaginatedResponse(
            items=assets,
            page=page,
            per_page=per_page,
            total=total,
            pages=(total + per_page - 1) // per_page
        )
```

### Database Transactions
```python
from sqlalchemy.orm import Session
from contextlib import contextmanager

@contextmanager
def db_transaction(db: Session):
    """Database transaction context manager."""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# Usage
async def create_asset_with_risks(asset_data: AssetCreateRequest, db: Session):
    with db_transaction(db):
        # Create asset
        asset = Asset(**asset_data.dict())
        db.add(asset)
        db.flush()  # Get asset ID
        
        # Create related risks
        for risk_data in asset_data.risks:
            risk = Risk(**risk_data.dict(), asset_id=asset.id)
            db.add(risk)
```

## Error Handling

### Exception Hierarchy
```python
class APIException(Exception):
    """Base API exception."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

class ValidationError(APIException):
    def __init__(self, message: str, field: str = None):
        super().__init__(message, 422, "VALIDATION_ERROR")
        self.field = field

class NotFoundError(APIException):
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with ID {identifier} not found"
        super().__init__(message, 404, "NOT_FOUND")

class PermissionError(APIException):
    def __init__(self, permission: str):
        message = f"Permission required: {permission}"
        super().__init__(message, 403, "PERMISSION_DENIED")
```

### Global Exception Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": [
                    {
                        "field": error["loc"][-1],
                        "message": error["msg"]
                    }
                    for error in exc.errors()
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Testing Standards

### Unit Tests
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

class TestAssetEndpoints:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
        return User(id=1, email="test@example.com", is_active=True)
    
    def test_create_asset_success(self, client, mock_user):
        """Test successful asset creation."""
        asset_data = {
            "name": "Test Server",
            "asset_type": "server",
            "criticality": "high"
        }
        
        with patch('dependencies.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/assets", json=asset_data)
        
        assert response.status_code == 201
        assert response.json()["success"] is True
        assert response.json()["data"]["name"] == asset_data["name"]
    
    def test_create_asset_validation_error(self, client, mock_user):
        """Test asset creation with invalid data."""
        asset_data = {
            "name": "",  # Invalid: empty name
            "asset_type": "invalid_type"  # Invalid: bad enum value
        }
        
        with patch('dependencies.get_current_user', return_value=mock_user):
            response = client.post("/api/v1/assets", json=asset_data)
        
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert "validation" in response.json()["error"]["message"].lower()
```

### Integration Tests
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestAssetIntegration:
    
    def test_asset_crud_operations(self, test_db, client):
        """Test complete asset CRUD operations."""
        # Create asset
        asset_data = {"name": "Integration Test Server", "asset_type": "server"}
        create_response = client.post("/api/v1/assets", json=asset_data)
        assert create_response.status_code == 201
        asset_id = create_response.json()["data"]["id"]
        
        # Read asset
        get_response = client.get(f"/api/v1/assets/{asset_id}")
        assert get_response.status_code == 200
        assert get_response.json()["data"]["name"] == asset_data["name"]
        
        # Update asset
        update_data = {"name": "Updated Server Name"}
        update_response = client.patch(f"/api/v1/assets/{asset_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["data"]["name"] == update_data["name"]
        
        # Delete asset
        delete_response = client.delete(f"/api/v1/assets/{asset_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/assets/{asset_id}")
        assert get_response.status_code == 404
```

## Performance Guidelines

### Query Optimization
```python
# Use explicit joins to avoid N+1 queries
def get_assets_with_risks(db: Session):
    return db.query(Asset)\
        .options(joinedload(Asset.risks))\
        .options(joinedload(Asset.category))\
        .all()

# Use pagination for large datasets
def get_paginated_assets(db: Session, page: int = 1, per_page: int = 20):
    return db.query(Asset)\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()
```

### Caching Strategy
```python
from functools import lru_cache
import redis

# In-memory caching for reference data
@lru_cache(maxsize=100)
def get_asset_categories():
    """Cache asset categories (rarely change)."""
    return db.query(AssetCategory).filter(AssetCategory.is_active == True).all()

# Redis caching for session data
redis_client = redis.Redis()

def cache_user_permissions(user_id: int, permissions: list):
    """Cache user permissions for 1 hour."""
    redis_client.setex(
        f"user_permissions:{user_id}", 
        3600, 
        json.dumps(permissions)
    )
```

### Async Operations
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def bulk_asset_processing(asset_ids: List[int]):
    """Process multiple assets concurrently."""
    
    async def process_single_asset(asset_id: int):
        # CPU-intensive processing
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                executor, 
                perform_asset_analysis, 
                asset_id
            )
    
    # Process assets concurrently
    tasks = [process_single_asset(asset_id) for asset_id in asset_ids]
    results = await asyncio.gather(*tasks)
    return results
```

## Documentation Standards

### OpenAPI Documentation
```python
@router.post(
    "/assets",
    response_model=AssetResponse,
    status_code=201,
    summary="Create new asset",
    description="Create a new asset in the system with the provided details.",
    responses={
        201: {"description": "Asset created successfully"},
        400: {"description": "Invalid request data"},
        401: {"description": "Authentication required"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"}
    }
)
async def create_asset(
    asset: AssetCreateRequest = Body(
        ...,
        example={
            "name": "Web Server 01",
            "description": "Primary web application server",
            "asset_type": "server",
            "criticality": "high"
        }
    ),
    current_user: User = Depends(get_current_user)
) -> AssetResponse:
    """
    Create a new asset.
    
    - **name**: Asset name (required)
    - **description**: Asset description (optional)
    - **asset_type**: Type of asset from predefined types
    - **criticality**: Business criticality level
    """
    # Implementation
```

### Code Documentation
```python
def calculate_risk_score(likelihood: int, impact: int, matrix_id: int) -> float:
    """
    Calculate risk score based on likelihood, impact, and risk matrix.
    
    Args:
        likelihood (int): Likelihood score (1-5)
        impact (int): Impact score (1-5)
        matrix_id (int): Risk matrix ID for scoring methodology
    
    Returns:
        float: Calculated risk score
    
    Raises:
        ValueError: If likelihood or impact is out of valid range
        NotFoundError: If risk matrix is not found
    
    Example:
        >>> calculate_risk_score(4, 5, 1)
        20.0
    """
    if not 1 <= likelihood <= 5 or not 1 <= impact <= 5:
        raise ValueError("Likelihood and impact must be between 1 and 5")
    
    # Implementation details...
```

## Security Best Practices

### Input Sanitization
```python
import html
import re
from typing import str

def sanitize_text_input(text: str) -> str:
    """Sanitize text input to prevent XSS and injection attacks."""
    if not text:
        return ""
    
    # HTML escape
    text = html.escape(text.strip())
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', text)
    
    return text

# Use in Pydantic validators
class AssetCreateRequest(BaseModel):
    name: str
    description: Optional[str]
    
    @validator('name', 'description')
    def sanitize_text_fields(cls, v):
        return sanitize_text_input(v) if v else v
```

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/assets")
@limiter.limit("10/minute")  # 10 requests per minute
async def create_asset(request: Request, asset_data: AssetCreateRequest):
    # Implementation
```

### SQL Injection Prevention
```python
# GOOD: Use parameterized queries
def get_assets_by_name(db: Session, name: str):
    return db.query(Asset).filter(Asset.name == name).all()

# GOOD: Use SQLAlchemy ORM
def search_assets(db: Session, search_term: str):
    return db.query(Asset).filter(
        Asset.name.ilike(f"%{search_term}%")
    ).all()

# BAD: Never use string formatting for queries
def bad_search_assets(db: Session, search_term: str):
    query = f"SELECT * FROM assets WHERE name LIKE '%{search_term}%'"
    return db.execute(query).fetchall()  # SQL injection vulnerability!
```

## Deployment & Monitoring

### Health Checks
```python
@router.get("/health")
async def health_check():
    """System health check endpoint."""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        # Check external services
        # ... additional checks
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Logging Standards
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in endpoints
@router.post("/assets")
async def create_asset(asset_data: AssetCreateRequest, current_user: User = Depends(get_current_user)):
    logger.info(
        "Asset creation initiated",
        user_id=current_user.id,
        asset_name=asset_data.name,
        asset_type=asset_data.asset_type
    )
    
    try:
        asset = await asset_service.create(asset_data, current_user.id)
        logger.info(
            "Asset created successfully",
            user_id=current_user.id,
            asset_id=asset.id,
            asset_name=asset.name
        )
        return asset
    except Exception as e:
        logger.error(
            "Asset creation failed",
            user_id=current_user.id,
            asset_name=asset_data.name,
            error=str(e),
            exc_info=True
        )
        raise
```

## Change Management

### API Versioning Strategy
1. **Backward Compatible Changes** (patch version):
   - Adding optional fields
   - Adding new endpoints
   - Improving error messages

2. **Minor Breaking Changes** (minor version):
   - Changing response formats
   - Adding required fields
   - Changing validation rules

3. **Major Breaking Changes** (major version):
   - Removing endpoints
   - Changing URL structure
   - Removing response fields

### Deprecation Process
1. **Announce**: Document deprecation in API docs
2. **Warning Headers**: Add `X-API-Deprecation-Warning` headers
3. **Migration Guide**: Provide clear migration instructions
4. **Sunset Date**: Set clear removal timeline (minimum 6 months)
5. **Remove**: Remove deprecated functionality after sunset

## Conclusion

Following these API development standards ensures:

- **Consistency**: Uniform API design across all endpoints
- **Maintainability**: Clear code structure and documentation
- **Security**: Robust authentication, authorization, and input validation
- **Performance**: Optimized database queries and caching strategies
- **Reliability**: Comprehensive testing and error handling
- **Scalability**: Async operations and proper resource management

For questions or clarifications on these standards, refer to the development team or create an issue in the project repository.