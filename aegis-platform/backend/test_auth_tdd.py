#!/usr/bin/env python3
"""
TDD Tests for Aegis Platform Authentication
Focuses on auth workflow issues identified in assessment testing
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append('.')

from main import app
from database import get_db, Base
from models.user import User, Role
from auth import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

# Create test database tables
Base.metadata.create_all(bind=engine)

class TestAuthWorkflow:
    """TDD tests for authentication workflow issues"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test client and clean database before each test"""
        self.client = TestClient(app)
        # Clean up test database
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Create test user for authentication tests
        db = TestingSessionLocal()
        try:
            test_user = User(
                email="test@aegis.com",
                username="testuser",
                full_name="Test User",
                hashed_password=get_password_hash("testpass123"),
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
        finally:
            db.close()
    
    def test_security_middleware_allows_test_requests(self):
        """Test that security middleware doesn't block legitimate test requests"""
        # RED: This should pass but currently fails due to security middleware blocking
        response = self.client.get("/health")
        assert response.status_code == 200
        # Should not have security violation logs
    
    def test_auth_login_with_valid_credentials_returns_token(self):
        """Test successful login returns access token"""
        # RED: Should return token but currently fails
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_auth_login_with_invalid_credentials_returns_401(self):
        """Test login with invalid credentials returns 401"""
        # RED: Should return 401 but currently fails due to middleware issues
        response = self.client.post("/api/v1/auth/login", json={
            "username": "invalid",
            "password": "invalid"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_protected_endpoint_without_auth_returns_401(self):
        """Test protected endpoints return 401 without authentication"""
        # RED: Should return 401 but currently fails
        response = self.client.get("/api/v1/assessments")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token_succeeds(self):
        """Test protected endpoints work with valid authentication"""
        # First, login to get token
        login_response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser", 
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Then access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/api/v1/assessments", headers=headers)
        
        # Should return 200 (or appropriate success code)
        assert response.status_code in [200, 204]
    
    def test_api_documentation_accessible(self):
        """Test that API documentation endpoints are accessible"""
        # RED: Currently failing due to middleware blocking
        response = self.client.get("/docs")
        assert response.status_code == 200
    
    def test_cors_headers_present(self):
        """Test CORS headers are properly configured"""
        # RED: Currently failing  
        response = self.client.get("/", headers={"Origin": "http://localhost:58533"})
        assert response.status_code == 200
        # Should have CORS headers for allowed origins

if __name__ == "__main__":
    pytest.main([__file__, "-v"])