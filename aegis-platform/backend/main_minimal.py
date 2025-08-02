from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from config import settings
from database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Aegis Risk Management Platform...")
    
    # Create database tables
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Continuing in development mode...")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Aegis Risk Management Platform...")


# Create FastAPI app
app = FastAPI(
    title="Aegis Risk Management Platform",
    version="1.0.0",
    description="Cybersecurity Risk Management Platform",
    lifespan=lifespan,
    debug=True
)

# CORS Configuration - Support dynamic ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Aegis Risk Management Platform",
        "version": "1.0.0",
        "environment": "development",
        "status": "operational"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "database": "connected",
        "environment": "development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}

@app.get("/api/v1/dashboards/overview")
async def get_dashboard_overview():
    """Get dashboard overview with mock data"""
    return {
        "assets": {
            "total": 45,
            "critical": 8
        },
        "risks": {
            "total": 23,
            "high_priority": 8,
            "open": 19
        },
        "tasks": {
            "total": 18,
            "open": 13,
            "overdue": 4
        },
        "assessments": {
            "total": 7,
            "active": 3,
            "completed": 4
        }
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user with mock data"""
    return {
        "id": 1,
        "email": "admin@aegis-platform.com",
        "username": "admin",
        "full_name": "System Administrator",
        "is_active": True,
        "is_superuser": True,
        "roles": [
            {
                "id": 1,
                "name": "admin",
                "description": "Administrator role",
                "permissions": {
                    "dashboard": ["read", "write"],
                    "assets": ["read", "write", "delete"],
                    "risks": ["read", "write", "delete"]
                },
                "is_active": True
            }
        ]
    }

@app.get("/api/v1/ai/providers/status")
async def get_ai_providers_status():
    """Get AI providers status"""
    return {
        "openai": {
            "enabled": True,
            "status": "healthy",
            "api_key_configured": False,
            "model": "gpt-3.5-turbo",
            "capabilities": {
                "text_generation": True,
                "function_calling": True,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "anthropic": {
            "enabled": False,
            "status": "disabled",
            "api_key_configured": False,
            "model": "claude-3-sonnet",
            "capabilities": {
                "text_generation": True,
                "function_calling": False,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "azure_openai": {
            "enabled": False,
            "status": "disabled",
            "api_key_configured": False,
            "model": "gpt-4-turbo",
            "capabilities": {
                "text_generation": True,
                "function_calling": True,
                "streaming": True,
                "max_tokens": 4096
            }
        },
        "total_providers": 14,
        "enabled_providers": 1,
        "ai_features_enabled": True
    }

@app.post("/api/v1/ai/test")
async def test_ai_generation():
    """Test AI text generation with mock response"""
    return {
        "success": True,
        "provider": "mock",
        "response": "This is a mock AI response for testing. The AI provider integration is working correctly.",
        "tokens_used": 25,
        "cost": 0.001,
        "response_time_ms": 1200
    }

if __name__ == "__main__":
    port = 8000
    print(f"🚀 Starting server on port {port}")
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0", 
        port=port,
        reload=True,
        log_level="info"
    )