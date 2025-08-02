from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import logging

from config import settings
from database import engine, Base
from enhanced_ai_service import enhanced_ai_service
from routers import (
    auth, users, assets, frameworks, assessments, 
    risks, tasks, evidence, integrations, reports, 
    dashboards, ai_services
)
from health import router as health_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


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
        # In development, we might want to continue even if database fails
        if not settings.DEBUG:
            raise
        print("⚠️  Continuing in development mode...")
    
    # Initialize Enhanced AI Service with Multi-Provider Support (optional)
    print("🤖 Initializing Enhanced AI Service...")
    try:
        ai_initialized = await enhanced_ai_service.initialize()
        if ai_initialized:
            print("✅ Enhanced AI Service initialized successfully")
            # Get provider status
            provider_status = await enhanced_ai_service.get_provider_status()
            enabled_providers = [name for name, status in provider_status.items() if status.get("enabled", False)]
            print(f"✅ Active AI providers: {', '.join(enabled_providers) if enabled_providers else 'None (using demo mode)'}")
        else:
            print("⚠️  Enhanced AI Service initialization failed - AI features will run in demo mode")
    except Exception as e:
        print(f"⚠️  Enhanced AI Service initialization error: {e}")
        print("⚠️  AI features will run in demo mode")
    
    print("🎯 Aegis Platform startup complete!")
    yield
    
    # Shutdown
    print("🛑 Aegis Platform shutdown")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Cybersecurity Risk Management Platform with AI-powered features",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["localhost", "127.0.0.1", "frontend"]
    )

# Include health check router first (no auth required)
app.include_router(health_router)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(frameworks.router, prefix="/api/v1/frameworks", tags=["Frameworks"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(risks.router, prefix="/api/v1/risks", tags=["Risks"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["Evidence"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["Integrations"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(dashboards.router, prefix="/api/v1/dashboards", tags=["Dashboards"])
app.include_router(ai_services.router, prefix="/api/v1/ai", tags=["AI Services"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Aegis Risk Management Platform",
        "version": settings.APP_VERSION,
        "description": "Enterprise Cybersecurity Risk Management Platform",
        "features": [
            "Asset Management",
            "Risk Assessment",
            "Compliance Frameworks (NIST CSF, CIS Controls)",
            "Task Management & POA&M",
            "Evidence Management",
            "AI-Powered Analytics",
            "External Integrations (OpenVAS, OpenCTI)",
            "Automated Reporting"
        ],
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/api", tags=["API Info"])
async def api_info():
    return {
        "api_version": "v1",
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "authentication": "/api/v1/auth",
            "users": "/api/v1/users",
            "assets": "/api/v1/assets",
            "risks": "/api/v1/risks",
            "assessments": "/api/v1/assessments",
            "tasks": "/api/v1/tasks",
            "evidence": "/api/v1/evidence",
            "reports": "/api/v1/reports",
            "frameworks": "/api/v1/frameworks",
            "dashboards": "/api/v1/dashboards",
            "ai_services": "/api/v1/ai",
            "integrations": "/api/v1/integrations"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )