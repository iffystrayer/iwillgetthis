# Testing Guide

## Overview

This document outlines comprehensive testing strategies and procedures for the Aegis Risk Management Platform. Our testing approach ensures system reliability, security, and performance while maintaining high code quality and user experience.

## Testing Philosophy

### Testing Pyramid
We follow the testing pyramid approach:
- **Unit Tests (70%)**: Fast, isolated component tests
- **Integration Tests (20%)**: Service interaction tests
- **End-to-End Tests (10%)**: Complete user workflow tests

### Testing Principles
1. **Test-Driven Development (TDD)**: Write tests before implementation
2. **Continuous Testing**: Automated tests run on every commit
3. **Risk-Based Testing**: Focus on high-risk, high-value features
4. **Regression Prevention**: Comprehensive test coverage prevents bugs
5. **Performance Awareness**: Monitor performance impact in tests

## Test Environment Setup

### Development Environment

#### Backend Testing Setup
```bash
cd aegis-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with dev packages
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install httpx  # For async HTTP testing
pip install factory-boy  # For test data factories
pip install faker  # For fake data generation
```

#### Frontend Testing Setup
```bash
cd aegis-platform/frontend/aegis-frontend

# Install dependencies
npm install

# Install testing dependencies (if not already in package.json)
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event vitest jsdom
npm install --save-dev @playwright/test  # For E2E testing
```

#### Test Database Setup
```bash
# Backend test database
export TEST_DATABASE_URL="sqlite:///./test.db"
python -c "from database import Base; from sqlalchemy import create_engine; engine = create_engine('sqlite:///./test.db'); Base.metadata.create_all(engine)"
```

### Testing Tools and Frameworks

#### Backend Testing Stack
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and stubbing
- **factory-boy**: Test data factories
- **faker**: Synthetic data generation
- **httpx**: HTTP client for API testing
- **SQLAlchemy**: Database testing utilities

#### Frontend Testing Stack
- **Vitest**: Unit and integration testing
- **React Testing Library**: Component testing
- **Jest DOM**: DOM testing utilities
- **User Event**: User interaction simulation
- **Playwright**: End-to-end testing
- **MSW (Mock Service Worker)**: API mocking

## Testing Strategies

### Unit Testing

#### Backend Unit Tests
Test individual functions, classes, and modules in isolation.

```python
# tests/test_models/test_asset.py
import pytest
from sqlalchemy.orm import Session
from models.asset import Asset, AssetType, AssetCriticality
from tests.factories import AssetFactory, UserFactory

class TestAssetModel:
    
    def test_create_asset_with_required_fields(self, db_session: Session):
        """Test asset creation with minimum required fields."""
        asset_data = {
            "name": "Test Server",
            "asset_type": AssetType.SERVER,
            "criticality": AssetCriticality.HIGH
        }
        
        asset = Asset(**asset_data)
        db_session.add(asset)
        db_session.commit()
        
        assert asset.id is not None
        assert asset.name == "Test Server"
        assert asset.asset_type == AssetType.SERVER
        assert asset.created_at is not None
    
    def test_asset_string_representation(self):
        """Test asset string representation."""
        asset = AssetFactory(name="Test Server")
        assert str(asset) == "Test Server"
    
    def test_asset_validation_invalid_ip(self):
        """Test asset validation with invalid IP address."""
        with pytest.raises(ValueError, match="Invalid IP address format"):
            Asset(
                name="Test Server",
                asset_type=AssetType.SERVER,
                ip_address="invalid.ip"
            )
    
    @pytest.mark.parametrize("criticality,expected_score", [
        (AssetCriticality.LOW, 1),
        (AssetCriticality.MEDIUM, 2),
        (AssetCriticality.HIGH, 3),
        (AssetCriticality.CRITICAL, 4)
    ])
    def test_criticality_score_mapping(self, criticality, expected_score):
        """Test criticality to score mapping."""
        asset = AssetFactory(criticality=criticality)
        assert asset.get_criticality_score() == expected_score
```

#### Service Layer Testing
```python
# tests/test_services/test_asset_service.py
import pytest
from unittest.mock import Mock, patch
from services.asset_service import AssetService
from schemas.asset import AssetCreateRequest
from models.asset import AssetType, AssetCriticality
from tests.factories import AssetFactory, UserFactory

class TestAssetService:
    
    @pytest.fixture
    def asset_service(self, db_session):
        return AssetService(db_session)
    
    @pytest.fixture
    def mock_audit_service(self):
        with patch('services.asset_service.audit_service') as mock:
            yield mock
    
    async def test_create_asset_success(self, asset_service, mock_audit_service):
        """Test successful asset creation."""
        user = UserFactory()
        asset_data = AssetCreateRequest(
            name="New Server",
            asset_type=AssetType.SERVER,
            criticality=AssetCriticality.HIGH
        )
        
        asset = await asset_service.create_asset(asset_data, user.id)
        
        assert asset.name == "New Server"
        assert asset.created_by == user.id
        mock_audit_service.log_action.assert_called_once()
    
    async def test_create_asset_duplicate_name(self, asset_service):
        """Test asset creation with duplicate name."""
        # Create existing asset
        existing_asset = AssetFactory(name="Duplicate Server")
        
        asset_data = AssetCreateRequest(
            name="Duplicate Server",
            asset_type=AssetType.SERVER
        )
        
        with pytest.raises(ValueError, match="Asset name already exists"):
            await asset_service.create_asset(asset_data, 1)
    
    async def test_get_assets_by_criticality(self, asset_service):
        """Test filtering assets by criticality."""
        # Create test assets
        AssetFactory.create_batch(3, criticality=AssetCriticality.HIGH)
        AssetFactory.create_batch(2, criticality=AssetCriticality.LOW)
        
        high_assets = await asset_service.get_assets_by_criticality(
            AssetCriticality.HIGH
        )
        
        assert len(high_assets) == 3
        assert all(asset.criticality == AssetCriticality.HIGH for asset in high_assets)
```

#### Frontend Unit Tests
```typescript
// src/components/AssetForm/AssetForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import AssetForm from './AssetForm';
import { AssetType, AssetCriticality } from '../../types/asset';

// Mock API calls
vi.mock('../../lib/api', () => ({
  createAsset: vi.fn(),
  updateAsset: vi.fn()
}));

describe('AssetForm', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders form fields correctly', () => {
    render(
      <AssetForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel} 
      />
    );
    
    expect(screen.getByLabelText(/asset name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/asset type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/criticality/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });
  
  it('validates required fields', async () => {
    const user = userEvent.setup();
    
    render(
      <AssetForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Try to submit without filling required fields
    await user.click(screen.getByRole('button', { name: /save/i }));
    
    expect(await screen.findByText(/asset name is required/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
  
  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    
    render(
      <AssetForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel} 
      />
    );
    
    // Fill form fields
    await user.type(screen.getByLabelText(/asset name/i), 'Test Server');
    await user.selectOptions(screen.getByLabelText(/asset type/i), AssetType.SERVER);
    await user.selectOptions(screen.getByLabelText(/criticality/i), AssetCriticality.HIGH);
    
    // Submit form
    await user.click(screen.getByRole('button', { name: /save/i }));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Server',
        asset_type: AssetType.SERVER,
        criticality: AssetCriticality.HIGH
      });
    });
  });
  
  it('handles IP address validation', async () => {
    const user = userEvent.setup();
    
    render(
      <AssetForm 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel} 
      />
    );
    
    const ipInput = screen.getByLabelText(/ip address/i);
    
    // Enter invalid IP
    await user.type(ipInput, 'invalid.ip');
    await user.tab(); // Trigger validation
    
    expect(await screen.findByText(/invalid ip address format/i)).toBeInTheDocument();
    
    // Clear and enter valid IP
    await user.clear(ipInput);
    await user.type(ipInput, '192.168.1.100');
    
    expect(screen.queryByText(/invalid ip address format/i)).not.toBeInTheDocument();
  });
});
```

### Integration Testing

#### API Integration Tests
Test complete API endpoints with database interactions.

```python
# tests/test_api/test_asset_endpoints.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from tests.factories import UserFactory, AssetFactory, RoleFactory
from tests.utils import create_test_token

class TestAssetEndpoints:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def admin_user(self, db_session: Session):
        admin_role = RoleFactory(name="Admin")
        user = UserFactory()
        # Assign admin role to user
        return user
    
    @pytest.fixture
    def auth_headers(self, admin_user):
        token = create_test_token(admin_user.id)
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_asset_success(self, client, auth_headers):
        """Test successful asset creation via API."""
        asset_data = {
            "name": "API Test Server",
            "asset_type": "server",
            "criticality": "high",
            "description": "Test server created via API"
        }
        
        response = client.post(
            "/api/v1/assets",
            json=asset_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == asset_data["name"]
        assert data["data"]["asset_type"] == asset_data["asset_type"]
    
    def test_create_asset_validation_error(self, client, auth_headers):
        """Test asset creation with validation errors."""
        invalid_data = {
            "name": "",  # Empty name
            "asset_type": "invalid_type",  # Invalid enum
            "ip_address": "invalid.ip"  # Invalid IP format
        }
        
        response = client.post(
            "/api/v1/assets",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "validation" in data["error"]["message"].lower()
        assert len(data["error"]["details"]) > 0
    
    def test_get_asset_by_id(self, client, auth_headers, db_session):
        """Test retrieving asset by ID."""
        asset = AssetFactory()
        db_session.commit()
        
        response = client.get(
            f"/api/v1/assets/{asset.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == asset.id
        assert data["data"]["name"] == asset.name
    
    def test_get_asset_not_found(self, client, auth_headers):
        """Test retrieving non-existent asset."""
        response = client.get(
            "/api/v1/assets/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"].lower()
    
    def test_list_assets_pagination(self, client, auth_headers, db_session):
        """Test asset listing with pagination."""
        # Create multiple assets
        AssetFactory.create_batch(25)
        db_session.commit()
        
        # Test first page
        response = client.get(
            "/api/v1/assets?page=1&per_page=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 10
        assert data["pagination"]["total"] == 25
        assert data["pagination"]["has_next"] is True
    
    def test_update_asset_success(self, client, auth_headers, db_session):
        """Test successful asset update."""
        asset = AssetFactory(name="Original Name")
        db_session.commit()
        
        update_data = {
            "name": "Updated Name",
            "description": "Updated description"
        }
        
        response = client.patch(
            f"/api/v1/assets/{asset.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["description"] == "Updated description"
    
    def test_delete_asset_success(self, client, auth_headers, db_session):
        """Test successful asset deletion."""
        asset = AssetFactory()
        db_session.commit()
        
        response = client.delete(
            f"/api/v1/assets/{asset.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify asset is deleted
        get_response = client.get(
            f"/api/v1/assets/{asset.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
```

#### Database Integration Tests
```python
# tests/test_repositories/test_asset_repository.py
import pytest
from sqlalchemy.orm import Session
from repositories.asset_repository import AssetRepository
from models.asset import Asset, AssetType, AssetCriticality
from tests.factories import AssetFactory, AssetCategoryFactory

class TestAssetRepository:
    
    @pytest.fixture
    def asset_repository(self, db_session: Session):
        return AssetRepository(db_session)
    
    async def test_create_asset(self, asset_repository):
        """Test asset creation through repository."""
        asset_data = {
            "name": "Repository Test Server",
            "asset_type": AssetType.SERVER,
            "criticality": AssetCriticality.HIGH
        }
        
        asset = await asset_repository.create(asset_data)
        
        assert asset.id is not None
        assert asset.name == "Repository Test Server"
    
    async def test_find_by_criticality(self, asset_repository, db_session):
        """Test finding assets by criticality."""
        # Create test assets
        AssetFactory(criticality=AssetCriticality.CRITICAL)
        AssetFactory(criticality=AssetCriticality.HIGH)
        AssetFactory(criticality=AssetCriticality.CRITICAL)
        db_session.commit()
        
        critical_assets = await asset_repository.find_by_criticality(
            AssetCriticality.CRITICAL
        )
        
        assert len(critical_assets) == 2
        assert all(asset.criticality == AssetCriticality.CRITICAL for asset in critical_assets)
    
    async def test_search_assets(self, asset_repository, db_session):
        """Test asset search functionality."""
        # Create test assets
        AssetFactory(name="Web Server 01", description="Primary web server")
        AssetFactory(name="Database Server", description="MySQL database")
        AssetFactory(name="File Server", description="File storage server")
        db_session.commit()
        
        # Search by name
        web_assets = await asset_repository.search("web")
        assert len(web_assets) == 1
        assert "web" in web_assets[0].name.lower()
        
        # Search by description
        server_assets = await asset_repository.search("server")
        assert len(server_assets) == 3
```

### End-to-End Testing

#### Playwright E2E Tests
Complete user workflow testing across the entire application.

```typescript
// tests/e2e/asset-management.spec.ts
import { test, expect } from '@playwright/test';
import { loginAsAdmin, createTestAsset, deleteTestAsset } from './utils/helpers';

test.describe('Asset Management', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.goto('/assets');
  });
  
  test('should create new asset successfully', async ({ page }) => {
    // Navigate to asset creation form
    await page.click('text=Add Asset');
    await expect(page.locator('h1')).toContainText('Create Asset');
    
    // Fill asset form
    await page.fill('[data-testid="asset-name"]', 'E2E Test Server');
    await page.selectOption('[data-testid="asset-type"]', 'server');
    await page.selectOption('[data-testid="criticality"]', 'high');
    await page.fill('[data-testid="description"]', 'Server created by E2E test');
    await page.fill('[data-testid="ip-address"]', '192.168.1.100');
    
    // Submit form
    await page.click('[data-testid="save-button"]');
    
    // Verify success
    await expect(page.locator('.toast-success')).toContainText('Asset created successfully');
    await expect(page).toHaveURL(/\/assets\/\d+/);
    await expect(page.locator('h1')).toContainText('E2E Test Server');
  });
  
  test('should validate form fields', async ({ page }) => {
    await page.click('text=Add Asset');
    
    // Try to submit empty form
    await page.click('[data-testid="save-button"]');
    
    // Check validation messages
    await expect(page.locator('[data-testid="name-error"]')).toContainText('Asset name is required');
    await expect(page.locator('[data-testid="type-error"]')).toContainText('Asset type is required');
    
    // Enter invalid IP address
    await page.fill('[data-testid="ip-address"]', 'invalid.ip');
    await page.blur('[data-testid="ip-address"]');
    await expect(page.locator('[data-testid="ip-error"]')).toContainText('Invalid IP address format');
  });
  
  test('should edit existing asset', async ({ page }) => {
    // Create test asset first
    const assetId = await createTestAsset(page, 'Asset to Edit');
    
    // Navigate to edit page
    await page.goto(`/assets/${assetId}/edit`);
    await expect(page.locator('h1')).toContainText('Edit Asset');
    
    // Update asset name
    await page.fill('[data-testid="asset-name"]', 'Updated Asset Name');
    await page.fill('[data-testid="description"]', 'Updated description');
    
    // Save changes
    await page.click('[data-testid="save-button"]');
    
    // Verify update
    await expect(page.locator('.toast-success')).toContainText('Asset updated successfully');
    await expect(page.locator('h1')).toContainText('Updated Asset Name');
    
    // Cleanup
    await deleteTestAsset(page, assetId);
  });
  
  test('should filter assets by type and criticality', async ({ page }) => {
    // Create diverse test assets
    await createTestAsset(page, 'Critical Server', 'server', 'critical');
    await createTestAsset(page, 'High Workstation', 'workstation', 'high');
    await createTestAsset(page, 'Medium Server', 'server', 'medium');
    
    await page.goto('/assets');
    
    // Filter by server type
    await page.selectOption('[data-testid="type-filter"]', 'server');
    await page.waitForSelector('[data-testid="asset-card"]');
    
    const serverAssets = page.locator('[data-testid="asset-card"]');
    await expect(serverAssets).toHaveCount(2);
    
    // Add criticality filter
    await page.selectOption('[data-testid="criticality-filter"]', 'critical');
    await page.waitForSelector('[data-testid="asset-card"]');
    
    const criticalServers = page.locator('[data-testid="asset-card"]');
    await expect(criticalServers).toHaveCount(1);
    await expect(criticalServers.first()).toContainText('Critical Server');
  });
  
  test('should search assets', async ({ page }) => {
    // Create test assets
    await createTestAsset(page, 'Production Database', 'database', 'critical');
    await createTestAsset(page, 'Development Server', 'server', 'low');
    
    await page.goto('/assets');
    
    // Search for 'database'
    await page.fill('[data-testid="search-input"]', 'database');
    await page.press('[data-testid="search-input"]', 'Enter');
    
    await page.waitForSelector('[data-testid="asset-card"]');
    const searchResults = page.locator('[data-testid="asset-card"]');
    await expect(searchResults).toHaveCount(1);
    await expect(searchResults).toContainText('Production Database');
  });
  
  test('should handle asset deletion', async ({ page }) => {
    // Create test asset
    const assetId = await createTestAsset(page, 'Asset to Delete');
    
    await page.goto(`/assets/${assetId}`);
    
    // Delete asset
    await page.click('[data-testid="delete-button"]');
    
    // Confirm deletion in modal
    await page.click('[data-testid="confirm-delete"]');
    
    // Verify deletion
    await expect(page.locator('.toast-success')).toContainText('Asset deleted successfully');
    await expect(page).toHaveURL('/assets');
  });
});

// Risk Assessment E2E Tests
test.describe('Risk Assessment Workflow', () => {
  
  test('should complete full risk assessment flow', async ({ page }) => {
    await loginAsAdmin(page);
    
    // Create asset for risk assessment
    const assetId = await createTestAsset(page, 'Risk Assessment Server');
    
    // Navigate to risk creation
    await page.goto('/risks/create');
    
    // Fill risk form
    await page.fill('[data-testid="risk-title"]', 'Unpatched Vulnerability Risk');
    await page.fill('[data-testid="risk-description"]', 'Critical vulnerability requires patching');
    await page.selectOption('[data-testid="risk-category"]', 'technical');
    await page.selectOption('[data-testid="asset-select"]', assetId.toString());
    
    // Set risk scores
    await page.selectOption('[data-testid="likelihood"]', '4');
    await page.selectOption('[data-testid="impact"]', '5');
    
    // Submit risk
    await page.click('[data-testid="save-risk"]');
    
    // Verify risk creation
    await expect(page.locator('.toast-success')).toContainText('Risk created successfully');
    const riskUrl = page.url();
    const riskId = riskUrl.match(/\/risks\/(\d+)/)?.[1];
    
    // Create remediation task
    await page.click('[data-testid="create-task"]');
    await page.fill('[data-testid="task-title"]', 'Apply Security Patch');
    await page.fill('[data-testid="task-description"]', 'Apply latest security patches');
    await page.selectOption('[data-testid="priority"]', 'critical');
    await page.click('[data-testid="save-task"]');
    
    // Verify task creation
    await expect(page.locator('.toast-success')).toContainText('Task created successfully');
    await expect(page.locator('[data-testid="task-list"]')).toContainText('Apply Security Patch');
    
    // Update task progress
    await page.click('[data-testid="edit-task"]');
    await page.fill('[data-testid="progress"]', '50');
    await page.fill('[data-testid="task-comment"]', 'Patch installation in progress');
    await page.click('[data-testid="update-task"]');
    
    // Verify progress update
    await expect(page.locator('[data-testid="progress-bar"]')).toContainText('50%');
    
    // Complete task
    await page.click('[data-testid="complete-task"]');
    await page.fill('[data-testid="completion-notes"]', 'Patches applied successfully');
    await page.click('[data-testid="confirm-completion"]');
    
    // Update risk status
    await page.selectOption('[data-testid="risk-status"]', 'mitigated');
    await page.click('[data-testid="update-status"]');
    
    // Verify risk mitigation
    await expect(page.locator('[data-testid="risk-status"]')).toContainText('Mitigated');
    await expect(page.locator('.toast-success')).toContainText('Risk status updated');
  });
});
```

### Performance Testing

#### Load Testing
```python
# tests/performance/test_api_load.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import httpx
import pytest

class TestAPIPerformance:
    
    @pytest.fixture
    def api_client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000")
    
    async def test_asset_list_performance(self, api_client):
        """Test asset listing endpoint performance."""
        
        # Warm up
        await api_client.get("/api/v1/assets")
        
        # Performance test
        start_time = time.time()
        tasks = []
        
        for _ in range(100):  # 100 concurrent requests
            task = api_client.get("/api/v1/assets?per_page=20")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Assertions
        assert all(response.status_code == 200 for response in responses)
        
        total_time = end_time - start_time
        avg_response_time = total_time / 100
        
        # Performance thresholds
        assert avg_response_time < 0.5, f"Average response time {avg_response_time}s exceeds 0.5s threshold"
        assert total_time < 10, f"Total time {total_time}s exceeds 10s threshold"
    
    async def test_database_query_performance(self, db_session):
        """Test database query performance."""
        from models.asset import Asset
        
        # Create test data
        assets = []
        for i in range(1000):
            assets.append(Asset(name=f"Asset {i}", asset_type="server"))
        
        db_session.bulk_save_objects(assets)
        db_session.commit()
        
        # Test query performance
        start_time = time.time()
        
        # Complex query with joins
        results = db_session.query(Asset)\
            .join(AssetCategory)\
            .filter(Asset.criticality == 'high')\
            .order_by(Asset.created_at.desc())\
            .limit(50)\
            .all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Performance assertion
        assert query_time < 0.1, f"Query time {query_time}s exceeds 0.1s threshold"
```

#### Memory and Resource Testing
```python
# tests/performance/test_memory_usage.py
import psutil
import pytest
from memory_profiler import profile

class TestMemoryUsage:
    
    @profile
    def test_large_dataset_memory_usage(self, db_session):
        """Test memory usage with large datasets."""
        from models.asset import Asset
        
        # Monitor process memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        assets = []
        for i in range(10000):
            assets.append(Asset(
                name=f"Asset {i}",
                description=f"Description for asset {i}" * 10,
                asset_type="server"
            ))
        
        db_session.bulk_save_objects(assets)
        db_session.commit()
        
        # Check memory after operation
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 100, f"Memory increase {memory_increase}MB exceeds 100MB threshold"
    
    def test_api_memory_leak(self, client):
        """Test for memory leaks in API endpoints."""
        import gc
        
        process = psutil.Process()
        
        memory_readings = []
        for i in range(100):
            # Make API requests
            response = client.get("/api/v1/assets")
            assert response.status_code == 200
            
            # Force garbage collection
            gc.collect()
            
            # Record memory usage
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_readings.append(memory_mb)
        
        # Check for memory growth trend
        first_quarter = sum(memory_readings[:25]) / 25
        last_quarter = sum(memory_readings[-25:]) / 25
        
        memory_growth = last_quarter - first_quarter
        
        # Memory should not grow significantly
        assert memory_growth < 10, f"Memory growth {memory_growth}MB indicates potential leak"
```

### Security Testing

#### Authentication and Authorization Tests
```python
# tests/security/test_auth.py
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from main import app

class TestAuthentication:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without authentication."""
        response = client.get("/api/v1/assets")
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client):
        """Test accessing endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid.token"}
        response = client.get("/api/v1/assets", headers=headers)
        assert response.status_code == 401
    
    def test_access_with_expired_token(self, client):
        """Test accessing endpoint with expired token."""
        # Create expired token
        expired_token = jwt.encode(
            {"user_id": 1, "exp": 1234567890},  # Past timestamp
            "secret_key",
            algorithm="HS256"
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/assets", headers=headers)
        assert response.status_code == 401
    
    def test_role_based_access_control(self, client):
        """Test role-based access control."""
        readonly_token = create_test_token(user_id=1, roles=["ReadOnly"])
        admin_token = create_test_token(user_id=2, roles=["Admin"])
        
        # ReadOnly user cannot create assets
        readonly_headers = {"Authorization": f"Bearer {readonly_token}"}
        response = client.post(
            "/api/v1/assets",
            json={"name": "Test", "asset_type": "server"},
            headers=readonly_headers
        )
        assert response.status_code == 403
        
        # Admin user can create assets
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/assets",
            json={"name": "Test", "asset_type": "server"},
            headers=admin_headers
        )
        assert response.status_code == 201
```

#### Input Validation Security Tests
```python
# tests/security/test_input_validation.py
import pytest
from fastapi.testclient import TestClient

class TestInputValidation:
    
    def test_sql_injection_prevention(self, client, auth_headers):
        """Test SQL injection attack prevention."""
        malicious_payloads = [
            "'; DROP TABLE assets; --",
            "1' OR '1'='1",
            "'; SELECT * FROM users; --"
        ]
        
        for payload in malicious_payloads:
            # Try SQL injection in search parameter
            response = client.get(
                f"/api/v1/assets/search?q={payload}",
                headers=auth_headers
            )
            
            # Should not return 500 error or expose database structure
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                # Should return safe, empty results
                data = response.json()
                assert isinstance(data.get("data"), list)
    
    def test_xss_prevention(self, client, auth_headers):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for payload in xss_payloads:
            # Try XSS in asset name
            response = client.post(
                "/api/v1/assets",
                json={
                    "name": payload,
                    "asset_type": "server",
                    "description": payload
                },
                headers=auth_headers
            )
            
            if response.status_code == 201:
                # If created, verify content is sanitized
                data = response.json()
                assert "<script>" not in data["data"]["name"]
                assert "javascript:" not in data["data"]["description"]
    
    def test_file_upload_security(self, client, auth_headers):
        """Test file upload security."""
        # Test malicious file types
        malicious_files = [
            ("malicious.exe", b"MZ\x90\x00"),  # Executable
            ("malicious.php", b"<?php system($_GET['cmd']); ?>"),  # PHP script
            ("malicious.html", b"<script>alert('xss')</script>")  # HTML with script
        ]
        
        for filename, content in malicious_files:
            files = {"file": (filename, content, "application/octet-stream")}
            response = client.post(
                "/api/v1/evidence/upload",
                files=files,
                headers=auth_headers
            )
            
            # Should reject dangerous file types
            assert response.status_code in [400, 415, 422]
```

## Test Data Management

### Test Factories
```python
# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from models.user import User, Role
from models.asset import Asset, AssetType, AssetCriticality
from models.risk import Risk, RiskCategory, RiskStatus
from tests.database import TestSessionLocal

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = TestSessionLocal
        sqlalchemy_session_persistence = "commit"

class RoleFactory(BaseFactory):
    class Meta:
        model = Role
    
    name = factory.Sequence(lambda n: f"Role{n}")
    description = factory.Faker("sentence")
    permissions = factory.LazyFunction(lambda: '["view_user", "view_asset"]')

class UserFactory(BaseFactory):
    class Meta:
        model = User
    
    email = factory.Faker("email")
    username = factory.Sequence(lambda n: f"user{n}")
    full_name = factory.Faker("name")
    hashed_password = factory.LazyFunction(lambda: "$2b$12$dummy.hash")
    is_active = True
    is_verified = True
    department = factory.Faker("company")
    job_title = factory.Faker("job")

class AssetFactory(BaseFactory):
    class Meta:
        model = Asset
    
    name = factory.Sequence(lambda n: f"Asset{n}")
    description = factory.Faker("sentence")
    asset_type = factory.Faker("random_element", elements=[e.value for e in AssetType])
    criticality = factory.Faker("random_element", elements=[e.value for e in AssetCriticality])
    ip_address = factory.Faker("ipv4")
    hostname = factory.Faker("hostname")
    operating_system = factory.Faker("random_element", elements=["Ubuntu 22.04", "CentOS 8", "Windows Server 2019"])
    location = factory.Faker("city")
    environment = factory.Faker("random_element", elements=["production", "staging", "development"])

class RiskFactory(BaseFactory):
    class Meta:
        model = Risk
    
    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    category = factory.Faker("random_element", elements=[e.value for e in RiskCategory])
    status = factory.Faker("random_element", elements=[e.value for e in RiskStatus])
    inherent_likelihood = factory.Faker("random_int", min=1, max=5)
    inherent_impact = factory.Faker("random_int", min=1, max=5)
    asset = factory.SubFactory(AssetFactory)
```

### Test Utilities
```python
# tests/utils.py
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.user import User

def create_test_token(user_id: int, roles: list = None) -> str:
    """Create JWT token for testing."""
    payload = {
        "user_id": user_id,
        "roles": roles or ["Admin"],
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, "test_secret", algorithm="HS256")

def create_test_user(db: Session, **kwargs) -> User:
    """Create test user with default values."""
    defaults = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": "$2b$12$dummy.hash",
        "is_active": True,
        "is_verified": True
    }
    defaults.update(kwargs)
    
    user = User(**defaults)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def cleanup_test_data(db: Session, model_class, **filters):
    """Clean up test data by model and filters."""
    query = db.query(model_class)
    for key, value in filters.items():
        query = query.filter(getattr(model_class, key) == value)
    
    query.delete()
    db.commit()
```

## Test Execution and CI/CD

### Local Test Execution

#### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_models/  # Unit tests
pytest tests/test_api/     # Integration tests
pytest tests/performance/  # Performance tests
pytest tests/security/     # Security tests

# Run with markers
pytest -m "unit"           # Run only unit tests
pytest -m "integration"    # Run only integration tests
pytest -m "slow"           # Run slow tests
pytest -m "not slow"       # Skip slow tests

# Parallel execution
pytest -n auto             # Auto-detect CPU cores
pytest -n 4                # Use 4 processes
```

#### Frontend Tests
```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run specific test files
npm test -- AssetForm.test.tsx
npm test -- --watch       # Watch mode for development
```

### Continuous Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
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
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        cd backend
        pytest tests/test_models/ tests/test_services/ -v --cov=.
    
    - name: Run integration tests
      run: |
        cd backend
        pytest tests/test_api/ tests/test_repositories/ -v
        
    - name: Run security tests
      run: |
        cd backend
        pytest tests/security/ -v
    
    - name: Upload coverage reports
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
    
    - name: Run unit tests
      run: |
        cd frontend/aegis-frontend
        npm run test:coverage
    
    - name: Run E2E tests
      run: |
        cd frontend/aegis-frontend
        npx playwright install --with-deps
        npm run test:e2e

  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install locust
    
    - name: Run performance tests
      run: |
        cd backend
        pytest tests/performance/ -v --maxfail=1
```

### Test Reporting

#### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Generate XML coverage report for CI
pytest --cov=. --cov-report=xml

# Set coverage thresholds
pytest --cov=. --cov-fail-under=80
```

#### Test Results Dashboard
```python
# conftest.py - Custom test reporting
import pytest
import json
from datetime import datetime

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config.test_results = []

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        config = item.config
        test_result = {
            "test": item.nodeid,
            "outcome": report.outcome,
            "duration": report.duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        config.test_results.append(test_result)

def pytest_sessionfinish(session, exitstatus):
    # Save test results for dashboard
    with open("test_results.json", "w") as f:
        json.dump(session.config.test_results, f, indent=2)
```

## Best Practices

### Test Organization
1. **Clear Test Structure**: Organize tests by feature/domain
2. **Descriptive Names**: Use clear, descriptive test method names
3. **Test Independence**: Each test should run independently
4. **Data Isolation**: Clean up test data between tests
5. **Mock External Dependencies**: Mock third-party services

### Test Writing Guidelines
1. **AAA Pattern**: Arrange, Act, Assert
2. **One Assertion per Test**: Focus on single behavior
3. **Edge Cases**: Test boundary conditions and edge cases
4. **Error Scenarios**: Test error handling and validation
5. **Performance Considerations**: Include performance assertions

### Maintenance and Evolution
1. **Regular Review**: Review and update tests regularly
2. **Test Coverage**: Maintain high test coverage (>80%)
3. **Flaky Test Management**: Identify and fix flaky tests
4. **Test Performance**: Monitor and optimize slow tests
5. **Documentation**: Keep test documentation up to date

## Conclusion

This comprehensive testing guide provides the foundation for maintaining high-quality, reliable software. By following these practices and continuously improving our testing approach, we ensure the Aegis Risk Management Platform meets the highest standards of security, performance, and reliability.

For questions about testing practices or to contribute improvements, please refer to the development team or create an issue in the project repository.