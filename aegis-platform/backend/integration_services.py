"""Integration services for external security tools"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from xml.etree import ElementTree
import base64
from datetime import datetime
import json

from config import settings

logger = logging.getLogger(__name__)

class OpenVASService:
    """Service for OpenVAS vulnerability scanner integration"""
    
    def __init__(self):
        self.enabled = settings.ENABLE_OPENVAS
        self.host = settings.OPENVAS_HOST
        self.username = settings.OPENVAS_USERNAME
        self.password = settings.OPENVAS_PASSWORD
        self.port = settings.OPENVAS_PORT or 9392
        
        if self.enabled and not all([self.host, self.username, self.password]):
            logger.warning("OpenVAS integration enabled but missing configuration")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if OpenVAS integration is enabled"""
        return self.enabled
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenVAS server"""
        if not self.is_enabled():
            return {"status": "disabled", "message": "OpenVAS integration not configured"}
        
        try:
            # Basic connection test
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                auth = aiohttp.BasicAuth(self.username, self.password)
                url = f"https://{self.host}:{self.port}/"
                
                async with session.get(url, auth=auth, ssl=False) as response:
                    if response.status == 200:
                        return {"status": "connected", "message": "OpenVAS connection successful"}
                    else:
                        return {"status": "error", "message": f"HTTP {response.status}"}
        
        except Exception as e:
            logger.error(f"OpenVAS connection test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_scan_results(self, target_ip: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get vulnerability scan results from OpenVAS"""
        if not self.is_enabled():
            return []
        
        try:
            # Mock scan results for demo purposes
            # In real implementation, this would query OpenVAS API
            mock_results = [
                {
                    "id": "vuln-001",
                    "name": "Unpatched Apache HTTP Server",
                    "severity": "High",
                    "cvss_score": 7.5,
                    "cve_id": "CVE-2024-1234",
                    "host": target_ip or "192.168.1.100",
                    "port": "80/tcp",
                    "description": "The Apache HTTP Server is vulnerable to a remote code execution flaw.",
                    "solution": "Update Apache HTTP Server to the latest version.",
                    "detected_at": datetime.now().isoformat(),
                    "category": "Web Server"
                },
                {
                    "id": "vuln-002",
                    "name": "Weak SSL/TLS Configuration",
                    "severity": "Medium",
                    "cvss_score": 5.3,
                    "cve_id": None,
                    "host": target_ip or "192.168.1.100",
                    "port": "443/tcp",
                    "description": "The SSL/TLS configuration allows weak cipher suites.",
                    "solution": "Configure stronger cipher suites and disable weak protocols.",
                    "detected_at": datetime.now().isoformat(),
                    "category": "SSL/TLS"
                }
            ]
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Failed to get OpenVAS scan results: {e}")
            return []
    
    async def start_scan(self, target_ip: str, scan_name: str) -> Dict[str, Any]:
        """Start a new vulnerability scan"""
        if not self.is_enabled():
            return {"status": "error", "message": "OpenVAS not enabled"}
        
        try:
            # Mock scan initiation
            scan_id = f"scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            return {
                "status": "started",
                "scan_id": scan_id,
                "target": target_ip,
                "scan_name": scan_name,
                "message": "Vulnerability scan initiated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to start OpenVAS scan: {e}")
            return {"status": "error", "message": str(e)}

class OpenCTIService:
    """Service for OpenCTI threat intelligence integration"""
    
    def __init__(self):
        self.enabled = settings.ENABLE_OPENCTI
        self.url = settings.OPENCTI_URL
        self.token = settings.OPENCTI_TOKEN
        
        if self.enabled and not all([self.url, self.token]):
            logger.warning("OpenCTI integration enabled but missing configuration")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if OpenCTI integration is enabled"""
        return self.enabled
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenCTI server"""
        if not self.is_enabled():
            return {"status": "disabled", "message": "OpenCTI integration not configured"}
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                # Test GraphQL endpoint
                query = {
                    "query": "query { me { name } }"
                }
                
                async with session.post(f"{self.url}/graphql", json=query) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "data" in data and "me" in data["data"]:
                            return {"status": "connected", "message": "OpenCTI connection successful"}
                    
                    return {"status": "error", "message": f"HTTP {response.status}"}
        
        except Exception as e:
            logger.error(f"OpenCTI connection test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_threat_intel(self, search_term: str) -> List[Dict[str, Any]]:
        """Get threat intelligence data from OpenCTI"""
        if not self.is_enabled():
            return []
        
        try:
            # Mock threat intelligence data
            mock_intel = [
                {
                    "id": "threat-001",
                    "name": "APT29 (Cozy Bear)",
                    "type": "threat-actor",
                    "description": "Russian state-sponsored threat group",
                    "targets": ["Government", "Healthcare", "Technology"],
                    "ttps": ["Spear Phishing", "Credential Harvesting", "Lateral Movement"],
                    "confidence": 85,
                    "last_seen": "2025-07-01",
                    "severity": "High"
                },
                {
                    "id": "malware-001",
                    "name": "Cobalt Strike",
                    "type": "malware",
                    "description": "Post-exploitation framework commonly used by threat actors",
                    "capabilities": ["Command and Control", "Lateral Movement", "Persistence"],
                    "indicators": ["beacon.exe", "specific network signatures"],
                    "confidence": 90,
                    "last_seen": "2025-07-05",
                    "severity": "High"
                }
            ]
            
            # Filter results based on search term
            if search_term:
                filtered_intel = [
                    intel for intel in mock_intel 
                    if search_term.lower() in intel["name"].lower() or 
                       search_term.lower() in intel["description"].lower()
                ]
                return filtered_intel
            
            return mock_intel
            
        except Exception as e:
            logger.error(f"Failed to get OpenCTI threat intelligence: {e}")
            return []
    
    async def get_indicators(self, indicator_type: str = None) -> List[Dict[str, Any]]:
        """Get indicators of compromise from OpenCTI"""
        if not self.is_enabled():
            return []
        
        try:
            # Mock IOC data
            mock_indicators = [
                {
                    "id": "ioc-001",
                    "type": "ip-address",
                    "value": "192.168.100.50",
                    "description": "Known C2 server",
                    "confidence": 80,
                    "valid_until": "2025-08-01",
                    "tags": ["malware", "c2"]
                },
                {
                    "id": "ioc-002",
                    "type": "domain",
                    "value": "malicious-domain.com",
                    "description": "Phishing domain",
                    "confidence": 95,
                    "valid_until": "2025-07-20",
                    "tags": ["phishing", "credential-theft"]
                },
                {
                    "id": "ioc-003",
                    "type": "file-hash",
                    "value": "d41d8cd98f00b204e9800998ecf8427e",
                    "description": "Malware sample hash",
                    "confidence": 90,
                    "valid_until": "2025-12-31",
                    "tags": ["malware", "trojan"]
                }
            ]
            
            if indicator_type:
                filtered_indicators = [
                    ioc for ioc in mock_indicators 
                    if ioc["type"] == indicator_type
                ]
                return filtered_indicators
            
            return mock_indicators
            
        except Exception as e:
            logger.error(f"Failed to get OpenCTI indicators: {e}")
            return []

class EmailService:
    """Service for email notifications and reporting"""
    
    def __init__(self):
        self.enabled = settings.ENABLE_EMAIL
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.FROM_EMAIL
        
        if self.enabled and not all([self.smtp_host, self.from_email]):
            logger.warning("Email service enabled but missing configuration")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if email service is enabled"""
        return self.enabled
    
    async def send_notification(self, to_email: str, subject: str, body: str, 
                              html_body: str = None) -> Dict[str, Any]:
        """Send email notification"""
        if not self.is_enabled():
            return {"status": "disabled", "message": "Email service not configured"}
        
        try:
            # Mock email sending for demo
            logger.info(f"Email notification sent to {to_email}: {subject}")
            
            return {
                "status": "sent",
                "to": to_email,
                "subject": subject,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_report(self, to_emails: List[str], report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send automated report via email"""
        if not self.is_enabled():
            return {"status": "disabled", "message": "Email service not configured"}
        
        try:
            subject = f"Aegis Security Report - {report_data.get('title', 'Weekly Report')}"
            
            # Generate email body from report data
            body = f"""
            Security Report Summary
            
            Report Period: {report_data.get('period', 'N/A')}
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Key Metrics:
            - Total Assets: {report_data.get('assets', {}).get('total', 0)}
            - Active Risks: {report_data.get('risks', {}).get('total', 0)}
            - Open Tasks: {report_data.get('tasks', {}).get('open', 0)}
            
            For detailed information, please access the Aegis platform.
            """
            
            results = []
            for email in to_emails:
                result = await self.send_notification(email, subject, body)
                results.append(result)
            
            return {
                "status": "sent",
                "recipients": len(to_emails),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to send report: {e}")
            return {"status": "error", "message": str(e)}

# Global service instances
openvas_service = OpenVASService()
opencti_service = OpenCTIService()
email_service = EmailService()