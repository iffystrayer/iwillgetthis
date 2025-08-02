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