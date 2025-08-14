"""Advanced document intelligence service for AI-powered evidence analysis"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
from pathlib import Path
import hashlib
import mimetypes
from io import BytesIO

try:
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
except ImportError:
    PyPDF2 = None
    docx = None
    Image = None
    pytesseract = None

from sqlalchemy.orm import Session
from fastapi import UploadFile

from enhanced_ai_service import enhanced_ai_service
from models.evidence import Evidence
from models.risks import Risk
from models.assessments import Assessment

logger = logging.getLogger(__name__)

class DocumentIntelligenceService:
    """Service for AI-powered document analysis and intelligence extraction"""
    
    def __init__(self):
        self.supported_mime_types = {
            'application/pdf': 'pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/msword': 'doc',
            'text/plain': 'txt',
            'application/json': 'json',
            'text/csv': 'csv',
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/tiff': 'tiff',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
        }
        
        # Document analysis templates
        self.analysis_templates = {
            'security_policy': {
                'keywords': ['security', 'policy', 'procedure', 'compliance', 'controls', 'governance'],
                'analysis_prompt': """Analyze this security policy document and extract:
1. Policy scope and objectives
2. Key security controls and requirements
3. Compliance frameworks referenced
4. Risk mitigation strategies
5. Implementation guidelines
6. Monitoring and review procedures"""
            },
            'risk_assessment': {
                'keywords': ['risk', 'assessment', 'threat', 'vulnerability', 'impact', 'likelihood'],
                'analysis_prompt': """Analyze this risk assessment document and extract:
1. Identified risks and threats
2. Risk ratings and scores
3. Impact assessments
4. Likelihood evaluations
5. Risk mitigation measures
6. Residual risk levels"""
            },
            'audit_report': {
                'keywords': ['audit', 'finding', 'recommendation', 'compliance', 'deficiency', 'observation'],
                'analysis_prompt': """Analyze this audit report and extract:
1. Audit scope and objectives
2. Key findings and observations
3. Compliance gaps identified
4. Recommendations for improvement
5. Risk levels associated with findings
6. Implementation timelines"""
            },
            'incident_report': {
                'keywords': ['incident', 'breach', 'event', 'response', 'impact', 'timeline'],
                'analysis_prompt': """Analyze this incident report and extract:
1. Incident type and classification
2. Timeline of events
3. Impact assessment
4. Root cause analysis
5. Response actions taken
6. Lessons learned and improvements"""
            },
            'compliance_evidence': {
                'keywords': ['compliance', 'evidence', 'control', 'requirement', 'standard', 'framework'],
                'analysis_prompt': """Analyze this compliance evidence document and extract:
1. Compliance framework or standard addressed
2. Specific controls or requirements covered
3. Evidence type and quality
4. Implementation status
5. Gaps or deficiencies noted
6. Remediation recommendations"""
            },
            'technical_report': {
                'keywords': ['technical', 'configuration', 'vulnerability', 'scan', 'assessment', 'testing'],
                'analysis_prompt': """Analyze this technical report and extract:
1. Technical systems or components assessed
2. Vulnerabilities or weaknesses identified
3. Configuration issues found
4. Risk levels and CVSS scores
5. Remediation recommendations
6. Testing methodology used"""
            }
        }
    
    async def analyze_document(
        self,
        db: Session,
        file_content: bytes,
        filename: str,
        evidence_id: Optional[int] = None,
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Comprehensive document analysis with AI-powered intelligence extraction"""
        
        try:
            # Extract basic document metadata
            file_hash = hashlib.sha256(file_content).hexdigest()
            file_size = len(file_content)
            mime_type = mimetypes.guess_type(filename)[0]
            
            # Extract text content from document
            text_content = await self._extract_text_content(file_content, filename, mime_type)
            
            if not text_content or len(text_content.strip()) < 50:
                return {
                    "success": False,
                    "error": "Unable to extract sufficient text content for analysis",
                    "metadata": {
                        "filename": filename,
                        "file_size": file_size,
                        "file_hash": file_hash,
                        "mime_type": mime_type
                    }
                }
            
            # Determine document type if not provided
            if not analysis_type:
                analysis_type = await self._classify_document_type(text_content)
            
            # Perform AI-powered analysis
            analysis_results = await self._perform_ai_analysis(text_content, analysis_type, filename)
            
            # Extract key entities and relationships
            entities = await self._extract_entities(text_content)
            
            # Generate document summary
            summary = await self._generate_summary(text_content, analysis_type)
            
            # Assess document quality and completeness
            quality_assessment = await self._assess_document_quality(text_content, analysis_type)
            
            # Extract actionable insights
            insights = await self._extract_actionable_insights(text_content, analysis_results)
            
            # Compile comprehensive analysis results
            analysis_result = {
                "success": True,
                "analysis_id": f"analysis_{file_hash[:16]}_{int(datetime.now().timestamp())}",
                "metadata": {
                    "filename": filename,
                    "file_size": file_size,
                    "file_hash": file_hash,
                    "mime_type": mime_type,
                    "analysis_type": analysis_type,
                    "analyzed_at": datetime.now().isoformat(),
                    "text_length": len(text_content)
                },
                "document_classification": {
                    "primary_type": analysis_type,
                    "confidence": analysis_results.get("classification_confidence", 0.8),
                    "detected_frameworks": self._detect_compliance_frameworks(text_content),
                    "document_maturity": quality_assessment.get("maturity_level", "unknown")
                },
                "content_analysis": analysis_results,
                "summary": summary,
                "entities": entities,
                "quality_assessment": quality_assessment,
                "actionable_insights": insights,
                "risk_indicators": await self._identify_risk_indicators(text_content),
                "compliance_mappings": await self._map_compliance_requirements(text_content),
                "recommendations": await self._generate_recommendations(analysis_results, analysis_type)
            }
            
            # If linked to evidence, update evidence record
            if evidence_id:
                await self._update_evidence_analysis(db, evidence_id, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_id": f"failed_{int(datetime.now().timestamp())}",
                "metadata": {
                    "filename": filename,
                    "analyzed_at": datetime.now().isoformat()
                }
            }
    
    async def _extract_text_content(self, file_content: bytes, filename: str, mime_type: str) -> str:
        """Extract text content from various document types"""
        
        try:
            if mime_type == 'application/pdf' and PyPDF2:
                return await self._extract_pdf_text(file_content)
            elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] and docx:
                return await self._extract_docx_text(file_content)
            elif mime_type in ['text/plain', 'application/json', 'text/csv']:
                return file_content.decode('utf-8', errors='ignore')
            elif mime_type and mime_type.startswith('image/') and pytesseract:
                return await self._extract_image_text(file_content)
            else:
                # Fallback: try to decode as text
                return file_content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.warning(f"Text extraction failed for {filename}: {e}")
            # Final fallback
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return ""
    
    async def _extract_pdf_text(self, file_content: bytes) -> str:
        """Extract text from PDF files"""
        if not PyPDF2:
            return ""
        
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"=== Page {page_num + 1} ===\n{page_text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from PDF page {page_num + 1}: {e}")
                    continue
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""
    
    async def _extract_docx_text(self, file_content: bytes) -> str:
        """Extract text from DOCX files"""
        if not docx:
            return ""
        
        try:
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"DOCX text extraction failed: {e}")
            return ""
    
    async def _extract_image_text(self, file_content: bytes) -> str:
        """Extract text from images using OCR"""
        if not (Image and pytesseract):
            return ""
        
        try:
            image = Image.open(BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    async def _classify_document_type(self, text_content: str) -> str:
        """Classify document type based on content analysis"""
        
        text_lower = text_content.lower()
        max_score = 0
        best_type = 'general'
        
        for doc_type, template in self.analysis_templates.items():
            score = sum(1 for keyword in template['keywords'] if keyword in text_lower)
            if score > max_score:
                max_score = score
                best_type = doc_type
        
        # Use AI for more sophisticated classification if available
        try:
            ai_classification = await enhanced_ai_service.classify_document(
                text_content[:2000],  # First 2000 chars for classification
                list(self.analysis_templates.keys())
            )
            if ai_classification and ai_classification.get('type'):
                return ai_classification['type']
        except Exception as e:
            logger.warning(f"AI classification failed: {e}")
        
        return best_type
    
    async def _perform_ai_analysis(self, text_content: str, analysis_type: str, filename: str) -> Dict[str, Any]:
        """Perform AI-powered document analysis"""
        
        template = self.analysis_templates.get(analysis_type, self.analysis_templates['compliance_evidence'])
        
        try:
            # Use enhanced AI service for deep analysis
            analysis_prompt = f"""
            Document: {filename}
            Type: {analysis_type}
            
            {template['analysis_prompt']}
            
            Document Content:
            {text_content[:4000]}  # Limit content for analysis
            
            Please provide a structured analysis in JSON format with the following sections:
            - key_findings: List of main findings or observations
            - risk_factors: Identified risk factors and their severity
            - compliance_status: Compliance assessment where applicable
            - gaps_identified: Any gaps or deficiencies found
            - recommendations: Specific recommendations for improvement
            - classification_confidence: Confidence score (0-1) for document classification
            """
            
            ai_response = await enhanced_ai_service.analyze_document(analysis_prompt)
            
            if ai_response and isinstance(ai_response, dict):
                return ai_response
            else:
                # Parse AI response if it's a string
                try:
                    return json.loads(ai_response) if isinstance(ai_response, str) else {}
                except:
                    return {"ai_analysis": ai_response}
                    
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            
        # Fallback analysis
        return {
            "key_findings": ["Analysis completed with basic text processing"],
            "risk_factors": [],
            "compliance_status": "requires_review",
            "gaps_identified": [],
            "recommendations": ["Manual review recommended for comprehensive analysis"],
            "classification_confidence": 0.6
        }
    
    async def _extract_entities(self, text_content: str) -> Dict[str, List[str]]:
        """Extract key entities from document text"""
        
        # Basic entity extraction patterns
        entities = {
            "frameworks": [],
            "controls": [],
            "risks": [],
            "systems": [],
            "dates": [],
            "people": [],
            "organizations": []
        }
        
        # Framework detection
        frameworks = ['nist', 'iso 27001', 'cis controls', 'pci dss', 'hipaa', 'gdpr', 'sox', 'fisma']
        text_lower = text_content.lower()
        
        for framework in frameworks:
            if framework in text_lower:
                entities["frameworks"].append(framework.upper())
        
        # Control ID patterns (basic)
        import re
        control_patterns = [
            r'\b[A-Z]{2,4}-\d{1,3}\b',  # AC-1, SC-7, etc.
            r'\b\d+\.\d+\.\d+\b',       # 1.1.1, 2.3.4, etc.
            r'\bControl\s+[A-Z0-9-]+\b' # Control AC-1, etc.
        ]
        
        for pattern in control_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            entities["controls"].extend(matches)
        
        # Try AI-powered entity extraction if available
        try:
            ai_entities = await enhanced_ai_service.extract_entities(text_content[:3000])
            if ai_entities and isinstance(ai_entities, dict):
                for key, values in ai_entities.items():
                    if key in entities and isinstance(values, list):
                        entities[key].extend(values)
        except Exception as e:
            logger.warning(f"AI entity extraction failed: {e}")
        
        # Remove duplicates and clean up
        for key in entities:
            entities[key] = list(set(entities[key]))
            
        return entities
    
    async def _generate_summary(self, text_content: str, analysis_type: str) -> str:
        """Generate document summary"""
        
        try:
            # Use AI for intelligent summarization
            summary_prompt = f"""
            Please provide a concise summary of this {analysis_type} document in 2-3 paragraphs:
            
            {text_content[:3000]}
            
            Focus on:
            - Main purpose and scope
            - Key findings or requirements
            - Critical information for stakeholders
            """
            
            ai_summary = await enhanced_ai_service.generate_summary(summary_prompt)
            if ai_summary:
                return ai_summary
                
        except Exception as e:
            logger.warning(f"AI summarization failed: {e}")
        
        # Fallback: basic summary
        sentences = text_content.split('.')[:5]  # First 5 sentences
        return '. '.join(sentence.strip() for sentence in sentences if sentence.strip()) + '.'
    
    async def _assess_document_quality(self, text_content: str, analysis_type: str) -> Dict[str, Any]:
        """Assess document quality and completeness"""
        
        quality_metrics = {
            "completeness_score": 0.0,
            "clarity_score": 0.0,
            "structure_score": 0.0,
            "maturity_level": "basic",
            "issues": [],
            "strengths": []
        }
        
        text_length = len(text_content)
        
        # Basic completeness assessment
        if text_length < 500:
            quality_metrics["completeness_score"] = 0.3
            quality_metrics["issues"].append("Document appears to be very short or incomplete")
        elif text_length < 2000:
            quality_metrics["completeness_score"] = 0.6
        else:
            quality_metrics["completeness_score"] = 0.9
        
        # Structure assessment (presence of sections, headings)
        structure_indicators = ['introduction', 'scope', 'objective', 'summary', 'conclusion', 'recommendation']
        structure_score = sum(1 for indicator in structure_indicators if indicator in text_content.lower()) / len(structure_indicators)
        quality_metrics["structure_score"] = structure_score
        
        # Maturity level assessment
        if quality_metrics["completeness_score"] >= 0.8 and structure_score >= 0.5:
            quality_metrics["maturity_level"] = "advanced"
        elif quality_metrics["completeness_score"] >= 0.6 and structure_score >= 0.3:
            quality_metrics["maturity_level"] = "intermediate"
        else:
            quality_metrics["maturity_level"] = "basic"
        
        return quality_metrics
    
    async def _extract_actionable_insights(self, text_content: str, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable insights from document analysis"""
        
        insights = []
        
        # Extract from AI analysis results
        if analysis_results.get('recommendations'):
            for rec in analysis_results['recommendations']:
                insights.append({
                    "type": "recommendation",
                    "priority": "medium",
                    "description": rec,
                    "category": "improvement"
                })
        
        if analysis_results.get('gaps_identified'):
            for gap in analysis_results['gaps_identified']:
                insights.append({
                    "type": "gap",
                    "priority": "high",
                    "description": gap,
                    "category": "remediation"
                })
        
        if analysis_results.get('risk_factors'):
            for risk in analysis_results['risk_factors']:
                insights.append({
                    "type": "risk_factor",
                    "priority": "high",
                    "description": risk,
                    "category": "risk_management"
                })
        
        return insights
    
    async def _identify_risk_indicators(self, text_content: str) -> List[Dict[str, Any]]:
        """Identify risk indicators in the document"""
        
        risk_indicators = []
        text_lower = text_content.lower()
        
        # Risk keyword patterns
        high_risk_keywords = ['critical', 'severe', 'urgent', 'immediate', 'breach', 'failure', 'non-compliant']
        medium_risk_keywords = ['significant', 'moderate', 'attention', 'concern', 'weakness']
        low_risk_keywords = ['minor', 'low', 'informational', 'advisory']
        
        for keyword in high_risk_keywords:
            if keyword in text_lower:
                risk_indicators.append({
                    "level": "high",
                    "indicator": keyword,
                    "context": "keyword_detection"
                })
        
        for keyword in medium_risk_keywords:
            if keyword in text_lower:
                risk_indicators.append({
                    "level": "medium",
                    "indicator": keyword,
                    "context": "keyword_detection"
                })
        
        return risk_indicators
    
    async def _map_compliance_requirements(self, text_content: str) -> Dict[str, List[str]]:
        """Map document content to compliance requirements"""
        
        compliance_mappings = {
            "NIST_CSF": [],
            "ISO_27001": [],
            "CIS_Controls": [],
            "PCI_DSS": [],
            "HIPAA": [],
            "GDPR": []
        }
        
        text_lower = text_content.lower()
        
        # Basic mapping based on keyword detection
        if 'nist' in text_lower or 'cybersecurity framework' in text_lower:
            compliance_mappings["NIST_CSF"].append("Framework referenced in document")
        
        if 'iso 27001' in text_lower or 'information security management' in text_lower:
            compliance_mappings["ISO_27001"].append("Standard referenced in document")
        
        return {k: v for k, v in compliance_mappings.items() if v}
    
    async def _generate_recommendations(self, analysis_results: Dict[str, Any], analysis_type: str) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis results"""
        
        recommendations = []
        
        # Based on document type and analysis results
        if analysis_type == 'security_policy':
            recommendations.append({
                "category": "policy_improvement",
                "priority": "medium",
                "title": "Regular Policy Review",
                "description": "Establish regular review cycles for security policies to ensure they remain current and effective"
            })
        
        elif analysis_type == 'risk_assessment':
            recommendations.append({
                "category": "risk_management",
                "priority": "high",
                "title": "Risk Monitoring",
                "description": "Implement continuous monitoring for identified high-risk areas"
            })
        
        # Add quality-based recommendations
        if analysis_results.get('gaps_identified'):
            recommendations.append({
                "category": "documentation",
                "priority": "medium",
                "title": "Address Documentation Gaps",
                "description": "Review and address identified gaps in documentation for completeness"
            })
        
        return recommendations
    
    async def _update_evidence_analysis(self, db: Session, evidence_id: int, analysis_result: Dict[str, Any]) -> None:
        """Update evidence record with analysis results"""
        
        try:
            evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
            if evidence:
                # Update evidence metadata with analysis results
                if not evidence.metadata:
                    evidence.metadata = {}
                
                evidence.metadata.update({
                    "ai_analysis": {
                        "analysis_id": analysis_result.get("analysis_id"),
                        "document_type": analysis_result.get("document_classification", {}).get("primary_type"),
                        "summary": analysis_result.get("summary"),
                        "quality_score": analysis_result.get("quality_assessment", {}).get("completeness_score"),
                        "risk_indicators_count": len(analysis_result.get("risk_indicators", [])),
                        "insights_count": len(analysis_result.get("actionable_insights", [])),
                        "analyzed_at": analysis_result.get("metadata", {}).get("analyzed_at")
                    }
                })
                
                # Update evidence description if it's generic
                if evidence.description in ['', 'Evidence file', 'Uploaded evidence']:
                    summary = analysis_result.get("summary", "")
                    if summary and len(summary) > 50:
                        evidence.description = summary[:200] + "..." if len(summary) > 200 else summary
                
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to update evidence analysis: {e}")
            db.rollback()
    
    def _detect_compliance_frameworks(self, text_content: str) -> List[str]:
        """Detect compliance frameworks mentioned in the document"""
        
        frameworks = []
        text_lower = text_content.lower()
        
        framework_patterns = {
            'NIST CSF': ['nist cybersecurity framework', 'nist csf', 'cybersecurity framework'],
            'ISO 27001': ['iso 27001', 'iso/iec 27001', 'information security management'],
            'CIS Controls': ['cis controls', 'center for internet security', 'cis critical security controls'],
            'PCI DSS': ['pci dss', 'payment card industry', 'pci compliance'],
            'HIPAA': ['hipaa', 'health insurance portability'],
            'GDPR': ['gdpr', 'general data protection regulation'],
            'SOX': ['sarbanes-oxley', 'sox compliance'],
            'FISMA': ['fisma', 'federal information security']
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                frameworks.append(framework)
        
        return frameworks
    
    async def batch_analyze_evidence(self, db: Session, evidence_ids: List[int]) -> Dict[str, Any]:
        """Batch analyze multiple evidence documents"""
        
        results = {
            "total_processed": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "analysis_summaries": [],
            "batch_insights": {
                "common_frameworks": [],
                "risk_distribution": {},
                "quality_overview": {},
                "recommendations": []
            }
        }
        
        try:
            for evidence_id in evidence_ids:
                try:
                    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
                    if not evidence or not evidence.file_path:
                        results["failed_analyses"] += 1
                        continue
                    
                    # Read file content
                    if os.path.exists(evidence.file_path):
                        with open(evidence.file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Analyze document
                        analysis_result = await self.analyze_document(
                            db=db,
                            file_content=file_content,
                            filename=evidence.file_name or f"evidence_{evidence_id}",
                            evidence_id=evidence_id
                        )
                        
                        if analysis_result.get("success"):
                            results["successful_analyses"] += 1
                            results["analysis_summaries"].append({
                                "evidence_id": evidence_id,
                                "filename": evidence.file_name,
                                "document_type": analysis_result.get("document_classification", {}).get("primary_type"),
                                "summary": analysis_result.get("summary", "")[:200]
                            })
                        else:
                            results["failed_analyses"] += 1
                    else:
                        results["failed_analyses"] += 1
                        
                except Exception as e:
                    logger.error(f"Failed to analyze evidence {evidence_id}: {e}")
                    results["failed_analyses"] += 1
                
                results["total_processed"] += 1
            
            # Generate batch insights
            results["batch_insights"] = await self._generate_batch_insights(db, evidence_ids)
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def _generate_batch_insights(self, db: Session, evidence_ids: List[int]) -> Dict[str, Any]:
        """Generate insights from batch analysis results"""
        
        insights = {
            "common_frameworks": [],
            "risk_distribution": {"high": 0, "medium": 0, "low": 0},
            "quality_overview": {"advanced": 0, "intermediate": 0, "basic": 0},
            "recommendations": []
        }
        
        try:
            # Query evidence with AI analysis metadata
            evidence_list = db.query(Evidence).filter(Evidence.id.in_(evidence_ids)).all()
            
            framework_counts = {}
            quality_counts = {"advanced": 0, "intermediate": 0, "basic": 0}
            
            for evidence in evidence_list:
                if evidence.metadata and evidence.metadata.get('ai_analysis'):
                    ai_data = evidence.metadata['ai_analysis']
                    
                    # Count quality levels
                    quality_score = ai_data.get('quality_score', 0)
                    if quality_score >= 0.8:
                        quality_counts['advanced'] += 1
                    elif quality_score >= 0.6:
                        quality_counts['intermediate'] += 1
                    else:
                        quality_counts['basic'] += 1
            
            insights["quality_overview"] = quality_counts
            
            # Generate recommendations based on batch analysis
            if quality_counts['basic'] > quality_counts['advanced']:
                insights["recommendations"].append({
                    "category": "documentation_quality",
                    "description": "Consider improving documentation quality across evidence collection"
                })
            
            if len(evidence_ids) > 10:
                insights["recommendations"].append({
                    "category": "evidence_management",
                    "description": "Large evidence collection detected - consider implementing evidence categorization and indexing"
                })
            
        except Exception as e:
            logger.error(f"Failed to generate batch insights: {e}")
        
        return insights

# Global service instance
document_intelligence_service = DocumentIntelligenceService()