"""Enhanced AI Services Router with Multi-Provider Support"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models.user import User
from enhanced_ai_service import enhanced_ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Services"])

class EvidenceAnalysisRequest(BaseModel):
    evidence_text: str
    control_id: str
    preferred_provider: Optional[str] = None

class ControlNarrativeRequest(BaseModel):
    control_id: str
    evidence_summary: str
    control_description: str
    preferred_provider: Optional[str] = None

class RiskStatementRequest(BaseModel):
    asset_name: str
    vulnerability_data: Dict[str, Any]
    threat_intel: Optional[Dict[str, Any]] = None
    preferred_provider: Optional[str] = None

class RemediationRequest(BaseModel):
    risk_description: str
    asset_type: str
    current_controls: Optional[List[str]] = None
    preferred_provider: Optional[str] = None

class ExecutiveSummaryRequest(BaseModel):
    dashboard_metrics: Dict[str, Any]
    preferred_provider: Optional[str] = None

class ProviderTestRequest(BaseModel):
    provider_name: str
    test_message: str = "Hello, this is a test message."

# Core AI Features
@router.get("/status")
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """Get AI service status"""
    return {
        "enabled": enhanced_ai_service.is_enabled(),
        "status": "available" if enhanced_ai_service.is_enabled() else "unavailable",
        "multi_provider": True
    }

@router.post("/analyze-evidence")
async def analyze_evidence(
    request: EvidenceAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze evidence document for compliance control"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await enhanced_ai_service.analyze_evidence(
            evidence_text=request.evidence_text,
            control_id=request.control_id,
            preferred_provider=request.preferred_provider
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Evidence analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-narrative")
async def generate_control_narrative(
    request: ControlNarrativeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate control implementation narrative"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await enhanced_ai_service.generate_control_narrative(
            control_id=request.control_id,
            evidence_summary=request.evidence_summary,
            control_description=request.control_description,
            preferred_provider=request.preferred_provider
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Narrative generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-risk-statement")
async def generate_risk_statement(
    request: RiskStatementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate formal risk statement"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await enhanced_ai_service.generate_risk_statement(
            asset_name=request.asset_name,
            vulnerability_data=request.vulnerability_data,
            threat_intel=request.threat_intel,
            preferred_provider=request.preferred_provider
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Risk statement generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-remediation")
async def suggest_remediation(
    request: RemediationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate remediation suggestions"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await enhanced_ai_service.suggest_remediation(
            risk_description=request.risk_description,
            asset_type=request.asset_type,
            current_controls=request.current_controls,
            preferred_provider=request.preferred_provider
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Remediation suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-executive-summary")
async def generate_executive_summary(
    request: ExecutiveSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate executive summary from dashboard metrics"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        result = await enhanced_ai_service.generate_executive_summary(
            dashboard_metrics=request.dashboard_metrics,
            preferred_provider=request.preferred_provider
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Executive summary generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Provider Management Endpoints
@router.get("/providers/status")
async def get_providers_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of all LLM providers"""
    try:
        return await enhanced_ai_service.get_provider_status()
    except Exception as e:
        logger.error(f"Provider status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/recommended")
async def get_recommended_provider(
    task_type: str = "general",
    current_user: User = Depends(get_current_user)
):
    """Get recommended provider for a task type"""
    try:
        provider = await enhanced_ai_service.get_recommended_provider(task_type)
        return {
            "recommended_provider": provider,
            "task_type": task_type
        }
    except Exception as e:
        logger.error(f"Provider recommendation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/providers/test")
async def test_provider(
    request: ProviderTestRequest,
    current_user: User = Depends(get_current_user)
):
    """Test a specific provider"""
    try:
        if not enhanced_ai_service.is_enabled():
            raise HTTPException(status_code=503, detail="AI service not available")
        
        # Simple test completion
        messages = [
            {"role": "user", "content": request.test_message}
        ]
        
        response = await enhanced_ai_service.service.generate_completion(
            messages=messages,
            preferred_provider=request.provider_name,
            max_tokens=50,
            temperature=0.7
        )
        
        return {
            "provider": response.provider,
            "test_successful": True,
            "response": response.content,
            "response_time": response.response_time,
            "cost": response.cost,
            "usage": response.usage
        }
        
    except Exception as e:
        logger.error(f"Provider test error: {e}")
        return {
            "provider": request.provider_name,
            "test_successful": False,
            "error": str(e)
        }

@router.get("/providers/capabilities/{provider_name}")
async def get_provider_capabilities(
    provider_name: str,
    current_user: User = Depends(get_current_user)
):
    """Get capabilities of a specific provider"""
    try:
        status = await enhanced_ai_service.get_provider_status()
        
        if provider_name not in status:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return {
            "provider": provider_name,
            "capabilities": status[provider_name].get("capabilities", {}),
            "status": status[provider_name].get("status", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Provider capabilities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/summary")
async def get_usage_summary(
    current_user: User = Depends(get_current_user)
):
    """Get AI usage summary across all providers"""
    try:
        status = await enhanced_ai_service.get_provider_status()
        
        total_requests = sum(p.get("requests_count", 0) for p in status.values())
        total_cost = sum(p.get("total_cost", 0) for p in status.values())
        avg_success_rate = sum(p.get("success_rate", 0) for p in status.values()) / len(status) if status else 0
        
        return {
            "total_requests": total_requests,
            "total_cost": round(total_cost, 4),
            "average_success_rate": round(avg_success_rate, 2),
            "active_providers": len([p for p in status.values() if p.get("enabled", False)]),
            "provider_breakdown": status
        }
        
    except Exception as e:
        logger.error(f"Usage summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))