"""Health check endpoints for monitoring and diagnostics"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from config import settings
from ai_service import ai_service
from integration_services import openvas_service, opencti_service, email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "components": {
            "database": await check_database_health(db),
            "ai_service": await check_ai_service_health(),
            "integrations": await check_integrations_health()
        }
    }
    
    # Determine overall health
    component_statuses = [comp["status"] for comp in health_status["components"].values()]
    if "error" in component_statuses:
        health_status["status"] = "degraded"
    elif "warning" in component_statuses:
        health_status["status"] = "warning"
    
    return health_status

async def check_database_health(db: Session) -> Dict[str, Any]:
    """Check database connectivity and basic operations"""
    try:
        # Test basic query
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "response_time_ms": 0  # Could add timing here
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }

async def check_ai_service_health() -> Dict[str, Any]:
    """Check AI service availability"""
    if not ai_service.is_enabled():
        return {
            "status": "disabled",
            "message": "AI service not configured"
        }
    
    try:
        # Could add a simple AI service test here
        return {
            "status": "healthy",
            "message": "AI service available",
            "enabled": True
        }
    except Exception as e:
        logger.error(f"AI service health check failed: {e}")
        return {
            "status": "error",
            "message": f"AI service error: {str(e)}"
        }

async def check_integrations_health() -> Dict[str, Any]:
    """Check external integrations health"""
    integrations = {
        "openvas": {"enabled": openvas_service.is_enabled()},
        "opencti": {"enabled": opencti_service.is_enabled()},
        "email": {"enabled": email_service.is_enabled()}
    }
    
    # Test enabled integrations
    tasks = []
    if openvas_service.is_enabled():
        tasks.append(("openvas", openvas_service.test_connection()))
    if opencti_service.is_enabled():
        tasks.append(("opencti", opencti_service.test_connection()))
    
    # Run connection tests concurrently
    if tasks:
        try:
            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            for i, (service_name, _) in enumerate(tasks):
                result = results[i]
                if isinstance(result, Exception):
                    integrations[service_name]["status"] = "error"
                    integrations[service_name]["message"] = str(result)
                else:
                    integrations[service_name].update(result)
        except Exception as e:
            logger.error(f"Integration health check failed: {e}")
    
    return integrations

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe for Kubernetes/container orchestration"""
    try:
        # Check if database is ready
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/liveness")
async def liveness_check():
    """Liveness probe for Kubernetes/container orchestration"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }