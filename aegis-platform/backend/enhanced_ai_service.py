"""Enhanced AI Service using Multi-LLM Providers"""

import json
import logging
from typing import Dict, Any, Optional, List
from multi_llm_service import multi_llm_service
from config import settings

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """Enhanced AI service with multi-provider support"""
    
    def __init__(self):
        self.service = multi_llm_service
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the enhanced AI service"""
        if not self._initialized:
            self._initialized = await self.service.initialize()
        return self._initialized
    
    def is_enabled(self) -> bool:
        """Check if AI service is enabled"""
        return self.service.is_enabled()
    
    async def analyze_evidence(
        self,
        evidence_text: str,
        control_id: str,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze evidence document using multi-provider service"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a cybersecurity compliance expert. Analyze evidence documents and provide structured assessments."
                },
                {
                    "role": "user",
                    "content": f"""Analyze the following evidence document for control {control_id} and provide a concise summary.

Evidence Document:
{evidence_text[:4000]}

Provide your response in JSON format with these keys:
- summary: Brief summary of the evidence
- relevance: How it relates to the control requirements
- gaps: Any gaps or additional evidence needed
- assessment: Compliance assessment (Fully Compliant, Partially Compliant, Non-Compliant)
"""
                }
            ]
            
            response = await self.service.generate_completion(
                messages=messages,
                task_type="reasoning",
                preferred_provider=preferred_provider,
                response_format="json",
                max_tokens=1000,
                temperature=0.3
            )
            
            # Try to parse as JSON
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                result = {
                    "summary": response.content,
                    "relevance": "AI analysis completed",
                    "gaps": "Manual review recommended",
                    "assessment": "Requires Review"
                }
            
            # Add metadata
            result["provider_used"] = response.provider
            result["response_time"] = response.response_time
            result["cost"] = response.cost
            
            return result
            
        except Exception as e:
            logger.error(f"Evidence analysis error: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def generate_control_narrative(
        self,
        control_id: str,
        evidence_summary: str,
        control_description: str,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate control implementation narrative"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a cybersecurity compliance documentation expert. Generate professional control implementation narratives."
                },
                {
                    "role": "user",
                    "content": f"""Generate a professional control implementation narrative for cybersecurity control {control_id}.

Control Description: {control_description}
Evidence Summary: {evidence_summary}

Create a narrative that:
1. Describes how the control is implemented
2. References the supporting evidence
3. Addresses implementation details
4. Uses professional, compliance-appropriate language

Keep the narrative concise but comprehensive (200-400 words)."""
                }
            ]
            
            response = await self.service.generate_completion(
                messages=messages,
                task_type="creative",
                preferred_provider=preferred_provider,
                max_tokens=800,
                temperature=0.4
            )
            
            return {
                "narrative": response.content.strip(),
                "generated_at": "2025-07-09T03:52:19Z",
                "control_id": control_id,
                "provider_used": response.provider,
                "response_time": response.response_time,
                "cost": response.cost
            }
            
        except Exception as e:
            logger.error(f"Narrative generation error: {e}")
            return {"error": f"Narrative generation failed: {str(e)}"}
    
    async def generate_risk_statement(
        self,
        asset_name: str,
        vulnerability_data: Dict[str, Any],
        threat_intel: Dict[str, Any] = None,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate formal risk statement"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            threat_context = ""
            if threat_intel:
                threat_context = f"\nThreat Intelligence: {json.dumps(threat_intel, indent=2)}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a cybersecurity risk assessment expert. Generate formal risk statements following industry best practices."
                },
                {
                    "role": "user",
                    "content": f"""Generate a formal cybersecurity risk statement for:

Asset: {asset_name}
Vulnerability Data: {json.dumps(vulnerability_data, indent=2)}{threat_context}

Create a risk statement following this format:
"If [threat/vulnerability] occurs on [asset], then [impact] could result, potentially causing [business consequence]."

Provide your response in JSON format with these keys:
- risk_statement: The formal risk statement
- category: Risk category (Technical, Operational, Strategic, Compliance)
- likelihood: Suggested likelihood level (1-5)
- impact: Suggested impact level (1-5)
- risk_score: Initial risk score calculation
- key_factors: List of key risk factors"""
                }
            ]
            
            response = await self.service.generate_completion(
                messages=messages,
                task_type="reasoning",
                preferred_provider=preferred_provider,
                response_format="json",
                max_tokens=1000,
                temperature=0.3
            )
            
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                result = {
                    "risk_statement": response.content,
                    "category": "Technical",
                    "likelihood": 3,
                    "impact": 3,
                    "risk_score": 9,
                    "key_factors": ["Manual review required"]
                }
            
            # Add metadata
            result["provider_used"] = response.provider
            result["response_time"] = response.response_time
            result["cost"] = response.cost
            
            return result
            
        except Exception as e:
            logger.error(f"Risk statement generation error: {e}")
            return {"error": f"Risk statement generation failed: {str(e)}"}
    
    async def suggest_remediation(
        self,
        risk_description: str,
        asset_type: str,
        current_controls: List[str] = None,
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate remediation suggestions"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            controls_context = ""
            if current_controls:
                controls_context = f"\nCurrent Controls: {', '.join(current_controls)}"
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a cybersecurity remediation expert. Provide actionable, prioritized remediation recommendations."
                },
                {
                    "role": "user",
                    "content": f"""Provide cybersecurity remediation recommendations for:

Risk Description: {risk_description}
Asset Type: {asset_type}{controls_context}

Provide your response in JSON format with these keys:
- immediate_actions: Array of immediate actions (each with: action, effort_level, priority, timeline)
- short_term: Array of short-term recommendations (1-3 months)
- long_term: Array of long-term strategic improvements (3-12 months)

Each recommendation should include: action, effort_level, priority, timeline"""
                }
            ]
            
            response = await self.service.generate_completion(
                messages=messages,
                task_type="reasoning",
                preferred_provider=preferred_provider,
                response_format="json",
                max_tokens=1200,
                temperature=0.4
            )
            
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                result = {
                    "immediate_actions": [{"action": response.content, "effort_level": "Medium", "priority": "High", "timeline": "1 week"}],
                    "short_term": [],
                    "long_term": []
                }
            
            # Add metadata
            result["provider_used"] = response.provider
            result["response_time"] = response.response_time
            result["cost"] = response.cost
            
            return result
            
        except Exception as e:
            logger.error(f"Remediation suggestion error: {e}")
            return {"error": f"Remediation suggestion failed: {str(e)}"}
    
    async def generate_executive_summary(
        self,
        dashboard_metrics: Dict[str, Any],
        preferred_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate executive summary from dashboard metrics"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a CISO preparing an executive briefing. Create business-focused cybersecurity summaries for C-level audience."
                },
                {
                    "role": "user",
                    "content": f"""Generate an executive summary for cybersecurity leadership based on these metrics:

{json.dumps(dashboard_metrics, indent=2)}

Create a business-focused summary that:
1. Highlights key risk trends and posture
2. Identifies areas requiring executive attention
3. Provides actionable recommendations
4. Uses business language appropriate for C-level audience
5. Keeps it concise (200-300 words)

Provide your response in JSON format with these keys:
- overview: Current posture overview
- concerns: Key concerns requiring attention
- recommendations: Recommended actions
- investments: Investment priorities"""
                }
            ]
            
            response = await self.service.generate_completion(
                messages=messages,
                task_type="creative",
                preferred_provider=preferred_provider,
                response_format="json",
                max_tokens=1000,
                temperature=0.4
            )
            
            try:
                result = json.loads(response.content)
            except json.JSONDecodeError:
                result = {
                    "overview": response.content,
                    "concerns": "See detailed analysis",
                    "recommendations": "Continue monitoring",
                    "investments": "Strategic planning recommended"
                }
            
            # Add metadata
            result["provider_used"] = response.provider
            result["response_time"] = response.response_time
            result["cost"] = response.cost
            
            return result
            
        except Exception as e:
            logger.error(f"Executive summary generation error: {e}")
            return {"error": f"Executive summary generation failed: {str(e)}"}
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        return await self.service.get_provider_status()
    
    async def get_recommended_provider(self, task_type: str = "general") -> Optional[str]:
        """Get recommended provider for a task"""
        return await self.service.get_recommended_provider(task_type)

# Global enhanced AI service instance
enhanced_ai_service = EnhancedAIService()