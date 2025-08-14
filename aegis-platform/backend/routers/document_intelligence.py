"""API endpoints for AI-powered document intelligence and evidence analysis"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from auth import get_current_user
from models.users import User
from models.evidence import Evidence
from services.document_intelligence_service import document_intelligence_service
from utils.audit_helpers import log_user_action, log_system_event
from schemas.evidence import EvidenceResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for API responses
class DocumentAnalysisRequest(BaseModel):
    analysis_type: Optional[str] = Field(None, description="Type of document analysis to perform")
    include_entities: bool = Field(True, description="Whether to extract entities from the document")
    include_quality_assessment: bool = Field(True, description="Whether to assess document quality")
    include_compliance_mapping: bool = Field(True, description="Whether to map compliance requirements")

class DocumentAnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    metadata: Dict[str, Any]
    document_classification: Optional[Dict[str, Any]] = None
    content_analysis: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None
    quality_assessment: Optional[Dict[str, Any]] = None
    actionable_insights: Optional[List[Dict[str, Any]]] = None
    risk_indicators: Optional[List[Dict[str, Any]]] = None
    compliance_mappings: Optional[Dict[str, List[str]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    evidence_ids: List[int] = Field(..., description="List of evidence IDs to analyze")
    analysis_type: Optional[str] = Field(None, description="Type of analysis to perform on all documents")

class BatchAnalysisResponse(BaseModel):
    total_processed: int
    successful_analyses: int
    failed_analyses: int
    analysis_summaries: List[Dict[str, Any]]
    batch_insights: Dict[str, Any]
    error: Optional[str] = None

class DocumentClassificationResponse(BaseModel):
    document_type: str
    confidence: float
    detected_frameworks: List[str]
    suggested_analysis_type: str

@router.post("/analyze-upload", response_model=DocumentAnalysisResponse)
@log_user_action(
    event_type="document_analysis",
    entity_type="document",
    action="analyze_upload",
    description="Analyze uploaded document with AI"
)
async def analyze_uploaded_document(
    file: UploadFile = File(...),
    analysis_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze an uploaded document with AI-powered intelligence extraction"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file size (limit to 50MB)
    file_content = await file.read()
    if len(file_content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large (max 50MB)")
    
    try:
        # Perform document analysis
        analysis_result = await document_intelligence_service.analyze_document(
            db=db,
            file_content=file_content,
            filename=file.filename,
            analysis_type=analysis_type
        )
        
        # Log analysis event
        log_system_event(
            db=db,
            event_type="document_analysis",
            entity_type="document",
            action="analyze_upload",
            description=f"Document analysis completed for {file.filename}",
            user_id=current_user.id,
            details={
                "filename": file.filename,
                "file_size": len(file_content),
                "analysis_type": analysis_type,
                "success": analysis_result.get("success", False),
                "analysis_id": analysis_result.get("analysis_id")
            }
        )
        
        return DocumentAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.post("/analyze-evidence/{evidence_id}", response_model=DocumentAnalysisResponse)
@log_user_action(
    event_type="evidence_analysis",
    entity_type="evidence",
    action="analyze_ai",
    description="Analyze evidence document with AI"
)
async def analyze_evidence_document(
    evidence_id: int,
    analysis_request: DocumentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze an existing evidence document with AI-powered intelligence extraction"""
    
    # Get evidence record
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    # Check file exists
    if not evidence.file_path or not os.path.exists(evidence.file_path):
        raise HTTPException(status_code=400, detail="Evidence file not found on disk")
    
    try:
        # Read file content
        with open(evidence.file_path, 'rb') as f:
            file_content = f.read()
        
        # Perform document analysis
        analysis_result = await document_intelligence_service.analyze_document(
            db=db,
            file_content=file_content,
            filename=evidence.file_name or f"evidence_{evidence_id}",
            evidence_id=evidence_id,
            analysis_type=analysis_request.analysis_type
        )
        
        # Log analysis event
        log_system_event(
            db=db,
            event_type="evidence_analysis",
            entity_type="evidence",
            action="analyze_ai",
            description=f"AI analysis completed for evidence {evidence_id}",
            user_id=current_user.id,
            entity_id=evidence_id,
            details={
                "evidence_id": evidence_id,
                "filename": evidence.file_name,
                "analysis_type": analysis_request.analysis_type,
                "success": analysis_result.get("success", False),
                "analysis_id": analysis_result.get("analysis_id")
            }
        )
        
        return DocumentAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Evidence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence analysis failed: {str(e)}")

@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
@log_user_action(
    event_type="batch_analysis",
    entity_type="evidence",
    action="batch_analyze",
    description="Batch analyze multiple evidence documents",
    risk_level="medium"
)
async def batch_analyze_evidence(
    batch_request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch analyze multiple evidence documents with AI-powered intelligence extraction"""
    
    if len(batch_request.evidence_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 documents can be analyzed in a single batch")
    
    # Verify evidence exists
    existing_evidence = db.query(Evidence).filter(Evidence.id.in_(batch_request.evidence_ids)).all()
    existing_ids = [e.id for e in existing_evidence]
    missing_ids = set(batch_request.evidence_ids) - set(existing_ids)
    
    if missing_ids:
        raise HTTPException(
            status_code=400, 
            detail=f"Evidence not found for IDs: {list(missing_ids)}"
        )
    
    try:
        # Perform batch analysis
        batch_result = await document_intelligence_service.batch_analyze_evidence(
            db=db,
            evidence_ids=batch_request.evidence_ids
        )
        
        # Log batch analysis event
        log_system_event(
            db=db,
            event_type="batch_analysis",
            entity_type="evidence",
            action="batch_analyze",
            description=f"Batch analysis completed for {len(batch_request.evidence_ids)} evidence documents",
            user_id=current_user.id,
            details={
                "evidence_count": len(batch_request.evidence_ids),
                "successful_analyses": batch_result.get("successful_analyses", 0),
                "failed_analyses": batch_result.get("failed_analyses", 0),
                "analysis_type": batch_request.analysis_type
            }
        )
        
        return BatchAnalysisResponse(**batch_result)
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.post("/classify-document", response_model=DocumentClassificationResponse)
async def classify_document_type(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Classify document type and suggest analysis approach"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Read first part of file for classification
    file_content = await file.read(8192)  # First 8KB for classification
    
    try:
        # Extract text for classification
        text_content = await document_intelligence_service._extract_text_content(
            file_content, file.filename, file.content_type
        )
        
        if not text_content or len(text_content.strip()) < 50:
            raise HTTPException(status_code=400, detail="Unable to extract text for classification")
        
        # Classify document
        doc_type = await document_intelligence_service._classify_document_type(text_content)
        
        # Detect frameworks
        frameworks = document_intelligence_service._detect_compliance_frameworks(text_content)
        
        # Calculate confidence (simplified)
        confidence = 0.8  # This would be more sophisticated in a real implementation
        
        return DocumentClassificationResponse(
            document_type=doc_type,
            confidence=confidence,
            detected_frameworks=frameworks,
            suggested_analysis_type=doc_type
        )
        
    except Exception as e:
        logger.error(f"Document classification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document classification failed: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analysis result by analysis ID"""
    
    # In a real implementation, you'd store analysis results in the database
    # For now, return a placeholder response
    return JSONResponse(
        content={
            "message": "Analysis result retrieval not yet implemented",
            "analysis_id": analysis_id
        },
        status_code=501
    )

@router.get("/evidence/{evidence_id}/analysis")
async def get_evidence_analysis(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI analysis results for an evidence document"""
    
    # Get evidence record
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    # Extract AI analysis from metadata
    ai_analysis = None
    if evidence.metadata and evidence.metadata.get('ai_analysis'):
        ai_analysis = evidence.metadata['ai_analysis']
    
    return JSONResponse(
        content={
            "evidence_id": evidence_id,
            "has_analysis": ai_analysis is not None,
            "analysis": ai_analysis,
            "last_analyzed": ai_analysis.get("analyzed_at") if ai_analysis else None
        }
    )

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats for document analysis"""
    
    return JSONResponse(
        content={
            "supported_formats": {
                "documents": [
                    {"extension": ".pdf", "mime_type": "application/pdf", "description": "PDF documents"},
                    {"extension": ".docx", "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "description": "Word documents"},
                    {"extension": ".txt", "mime_type": "text/plain", "description": "Plain text files"},
                    {"extension": ".csv", "mime_type": "text/csv", "description": "CSV files"},
                    {"extension": ".json", "mime_type": "application/json", "description": "JSON files"}
                ],
                "images": [
                    {"extension": ".jpg", "mime_type": "image/jpeg", "description": "JPEG images (OCR)"},
                    {"extension": ".png", "mime_type": "image/png", "description": "PNG images (OCR)"},
                    {"extension": ".tiff", "mime_type": "image/tiff", "description": "TIFF images (OCR)"}
                ],
                "spreadsheets": [
                    {"extension": ".xlsx", "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "description": "Excel spreadsheets"},
                    {"extension": ".xls", "mime_type": "application/vnd.ms-excel", "description": "Legacy Excel files"}
                ]
            },
            "analysis_types": [
                {"type": "security_policy", "description": "Security policies and procedures"},
                {"type": "risk_assessment", "description": "Risk assessment reports"},
                {"type": "audit_report", "description": "Audit findings and reports"},
                {"type": "incident_report", "description": "Security incident reports"},
                {"type": "compliance_evidence", "description": "Compliance evidence and documentation"},
                {"type": "technical_report", "description": "Technical assessment reports"}
            ],
            "features": [
                "Text extraction from multiple formats",
                "AI-powered content analysis",
                "Entity extraction (frameworks, controls, risks)",
                "Document quality assessment",
                "Compliance framework mapping",
                "Risk indicator identification",
                "Actionable insights generation",
                "Batch processing support"
            ]
        }
    )

@router.get("/analysis-templates")
async def get_analysis_templates():
    """Get available analysis templates and their descriptions"""
    
    templates = document_intelligence_service.analysis_templates
    
    template_info = []
    for template_type, template_data in templates.items():
        template_info.append({
            "type": template_type,
            "keywords": template_data["keywords"],
            "description": template_data["analysis_prompt"][:200] + "..." if len(template_data["analysis_prompt"]) > 200 else template_data["analysis_prompt"]
        })
    
    return JSONResponse(
        content={
            "available_templates": template_info,
            "total_templates": len(templates)
        }
    )

@router.post("/reanalyze-evidence/{evidence_id}")
@log_user_action(
    event_type="evidence_reanalysis",
    entity_type="evidence",
    action="reanalyze",
    description="Re-analyze evidence with updated AI models"
)
async def reanalyze_evidence(
    evidence_id: int,
    analysis_request: DocumentAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Re-analyze an evidence document with updated AI models or different analysis type"""
    
    # Get evidence record
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    # Check if file exists
    if not evidence.file_path or not os.path.exists(evidence.file_path):
        raise HTTPException(status_code=400, detail="Evidence file not found on disk")
    
    try:
        # Add re-analysis task to background
        background_tasks.add_task(
            _background_reanalyze_evidence,
            db,
            evidence_id,
            analysis_request.analysis_type,
            current_user.id
        )
        
        return JSONResponse(
            content={
                "message": "Evidence re-analysis started in background",
                "evidence_id": evidence_id,
                "status": "processing"
            }
        )
        
    except Exception as e:
        logger.error(f"Evidence re-analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Re-analysis failed: {str(e)}")

async def _background_reanalyze_evidence(
    db: Session,
    evidence_id: int,
    analysis_type: Optional[str],
    user_id: int
):
    """Background task for evidence re-analysis"""
    
    try:
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if evidence and evidence.file_path and os.path.exists(evidence.file_path):
            
            with open(evidence.file_path, 'rb') as f:
                file_content = f.read()
            
            # Clear previous analysis from metadata
            if evidence.metadata and evidence.metadata.get('ai_analysis'):
                evidence.metadata['ai_analysis']['previous_analysis'] = evidence.metadata['ai_analysis'].copy()
            
            # Perform new analysis
            analysis_result = await document_intelligence_service.analyze_document(
                db=db,
                file_content=file_content,
                filename=evidence.file_name or f"evidence_{evidence_id}",
                evidence_id=evidence_id,
                analysis_type=analysis_type
            )
            
            # Log completion
            log_system_event(
                db=db,
                event_type="evidence_reanalysis",
                entity_type="evidence",
                action="reanalyze_complete",
                description=f"Evidence re-analysis completed for {evidence_id}",
                user_id=user_id,
                entity_id=evidence_id,
                details={
                    "success": analysis_result.get("success", False),
                    "analysis_id": analysis_result.get("analysis_id")
                }
            )
            
    except Exception as e:
        logger.error(f"Background re-analysis failed for evidence {evidence_id}: {e}")
        
        # Log failure
        log_system_event(
            db=db,
            event_type="evidence_reanalysis",
            entity_type="evidence",
            action="reanalyze_failed",
            description=f"Evidence re-analysis failed for {evidence_id}: {str(e)}",
            user_id=user_id,
            entity_id=evidence_id,
            details={"error": str(e)},
            risk_level="medium"
        )