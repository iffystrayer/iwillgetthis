"""AI Service for LLM-powered features"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered features using Azure OpenAI"""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if settings.ENABLE_AI_FEATURES and settings.AZURE_OPENAI_API_KEY:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                self.enabled = True
                logger.info("AI Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI Service: {e}")
                self.enabled = False
        else:
            logger.info("AI Service disabled - missing configuration")
    
    def is_enabled(self) -> bool:
        """Check if AI service is enabled and configured"""
        return self.enabled
    
    async def analyze_evidence(self, evidence_text: str, control_id: str) -> Dict[str, Any]:
        """Analyze evidence document and provide summary for a specific control"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            prompt = f"""
            You are a cybersecurity compliance expert. Analyze the following evidence document 
            for control {control_id} and provide a concise summary of how it addresses the control requirements.
            
            Evidence Document:
            {evidence_text[:4000]}  # Limit to avoid token limits
            
            Please provide:
            1. A brief summary of the evidence
            2. How it relates to the control requirements
            3. Any gaps or additional evidence needed
            4. A compliance assessment (Fully Compliant, Partially Compliant, Non-Compliant)
            
            Respond in JSON format with keys: summary, relevance, gaps, assessment
            """
            
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity compliance expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to plain text
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {
                    "summary": content,
                    "relevance": "AI analysis completed",
                    "gaps": "Manual review recommended",
                    "assessment": "Requires Review"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Evidence analysis error: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def generate_control_narrative(self, control_id: str, evidence_summary: str, 
                                       control_description: str) -> Dict[str, Any]:
        """Generate a control implementation narrative based on evidence"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            prompt = f"""
            Generate a professional control implementation narrative for cybersecurity control {control_id}.
            
            Control Description: {control_description}
            Evidence Summary: {evidence_summary}
            
            Create a narrative that:
            1. Describes how the control is implemented
            2. References the supporting evidence
            3. Addresses any implementation details
            4. Uses professional, compliance-appropriate language
            
            Keep the narrative concise but comprehensive (200-400 words).
            """
            
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity compliance documentation expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            narrative = response.choices[0].message.content.strip()
            
            return {
                "narrative": narrative,
                "generated_at": "2025-07-09T03:39:17Z",
                "control_id": control_id
            }
            
        except Exception as e:
            logger.error(f"Narrative generation error: {e}")
            return {"error": f"Narrative generation failed: {str(e)}"}
    
    async def generate_risk_statement(self, asset_name: str, vulnerability_data: Dict[str, Any], 
                                    threat_intel: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a formal risk statement using technical data and threat intelligence"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            threat_context = ""
            if threat_intel:
                threat_context = f"Threat Intelligence: {json.dumps(threat_intel, indent=2)}"
            
            prompt = f"""
            Generate a formal cybersecurity risk statement for the following scenario:
            
            Asset: {asset_name}
            Vulnerability Data: {json.dumps(vulnerability_data, indent=2)}
            {threat_context}
            
            Create a risk statement that follows this format:
            "If [threat/vulnerability] occurs on [asset], then [impact] could result, 
            potentially causing [business consequence]."
            
            Also provide:
            1. Risk category (Technical, Operational, Strategic, Compliance)
            2. Suggested likelihood level (1-5)
            3. Suggested impact level (1-5)
            4. Initial risk score calculation
            5. Key risk factors
            
            Respond in JSON format with keys: risk_statement, category, likelihood, impact, 
            risk_score, key_factors
            """
            
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity risk assessment expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {
                    "risk_statement": content,
                    "category": "Technical",
                    "likelihood": 3,
                    "impact": 3,
                    "risk_score": 9,
                    "key_factors": ["Manual review required"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Risk statement generation error: {e}")
            return {"error": f"Risk statement generation failed: {str(e)}"}
    
    async def suggest_remediation(self, risk_description: str, asset_type: str, 
                                current_controls: List[str] = None) -> Dict[str, Any]:
        """Generate remediation suggestions for a given risk"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            controls_context = ""
            if current_controls:
                controls_context = f"Current Controls: {', '.join(current_controls)}"
            
            prompt = f"""
            Provide cybersecurity remediation recommendations for the following risk:
            
            Risk Description: {risk_description}
            Asset Type: {asset_type}
            {controls_context}
            
            Provide:
            1. Immediate actions (quick wins)
            2. Short-term recommendations (1-3 months)
            3. Long-term strategic improvements (3-12 months)
            4. Estimated effort level for each recommendation
            5. Priority ranking
            
            Respond in JSON format with keys: immediate_actions, short_term, long_term, 
            each containing arrays of objects with: action, effort_level, priority, timeline
            """
            
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity remediation expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {
                    "immediate_actions": [{"action": content, "effort_level": "Medium", "priority": "High", "timeline": "1 week"}],
                    "short_term": [],
                    "long_term": []
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Remediation suggestion error: {e}")
            return {"error": f"Remediation suggestion failed: {str(e)}"}
    
    async def generate_executive_summary(self, dashboard_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an executive summary from dashboard metrics"""
        if not self.is_enabled():
            return {"error": "AI service not available"}
        
        try:
            prompt = f"""
            Generate an executive summary for cybersecurity leadership based on these metrics:
            
            {json.dumps(dashboard_metrics, indent=2)}
            
            Create a business-focused summary that:
            1. Highlights key risk trends and posture
            2. Identifies areas requiring executive attention
            3. Provides actionable recommendations
            4. Uses business language appropriate for C-level audience
            5. Keeps it concise (200-300 words)
            
            Structure the summary with:
            - Current Posture Overview
            - Key Concerns
            - Recommended Actions
            - Investment Priorities
            
            Respond in JSON format with keys: overview, concerns, recommendations, investments
            """
            
            response = self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "You are a CISO preparing an executive briefing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {
                    "overview": content,
                    "concerns": "See detailed analysis",
                    "recommendations": "Continue monitoring",
                    "investments": "Strategic planning recommended"
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Executive summary generation error: {e}")
            return {"error": f"Executive summary generation failed: {str(e)}"}

# Global AI service instance
ai_service = AIService()