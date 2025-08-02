from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import httpx
import json
from datetime import datetime

from database import get_db
from models.user import User
from models.integration import Integration, VulnerabilityData, ThreatIntelData
from models.asset import Asset
from models.audit import AuditLog
from auth import get_current_active_user
from config import settings

router = APIRouter()


@router.get("/")
async def get_integrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all configured integrations."""
    
    integrations = db.query(Integration).filter(Integration.is_active == True).all()
    
    return [
        {
            "id": integration.id,
            "name": integration.name,
            "type": integration.integration_type,
            "is_connected": integration.is_connected,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "last_connection_test": integration.last_connection_test.isoformat() if integration.last_connection_test else None,
            "connection_error": integration.connection_error
        }
        for integration in integrations
    ]


@router.post("/openvas/configure")
async def configure_openvas(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Configure OpenVAS integration."""
    
    # Check if OpenVAS integration already exists
    existing = db.query(Integration).filter(
        Integration.integration_type == "openvas",
        Integration.is_active == True
    ).first()
    
    if existing:
        # Update existing configuration
        existing.endpoint_url = config.get("host")
        existing.username = config.get("username")
        existing.password = config.get("password")  # In production, encrypt this
        existing.configuration = config
        integration = existing
    else:
        # Create new integration
        integration = Integration(
            name="OpenVAS Scanner",
            integration_type="openvas",
            endpoint_url=config.get("host"),
            username=config.get("username"),
            password=config.get("password"),  # In production, encrypt this
            configuration=config,
            created_by=current_user.id
        )
        db.add(integration)
    
    db.commit()
    db.refresh(integration)
    
    return {"message": "OpenVAS integration configured successfully", "integration_id": integration.id}


@router.post("/opencti/configure")
async def configure_opencti(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Configure OpenCTI integration."""
    
    # Check if OpenCTI integration already exists
    existing = db.query(Integration).filter(
        Integration.integration_type == "opencti",
        Integration.is_active == True
    ).first()
    
    if existing:
        # Update existing configuration
        existing.endpoint_url = config.get("url")
        existing.api_key = config.get("token")  # In production, encrypt this
        existing.configuration = config
        integration = existing
    else:
        # Create new integration
        integration = Integration(
            name="OpenCTI Threat Intelligence",
            integration_type="opencti",
            endpoint_url=config.get("url"),
            api_key=config.get("token"),  # In production, encrypt this
            configuration=config,
            created_by=current_user.id
        )
        db.add(integration)
    
    db.commit()
    db.refresh(integration)
    
    return {"message": "OpenCTI integration configured successfully", "integration_id": integration.id}


@router.post("/test-connection/{integration_id}")
async def test_integration_connection(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test connection to an integration."""
    
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    try:
        if integration.integration_type == "openvas":
            # Test OpenVAS connection
            result = await test_openvas_connection(integration)
        elif integration.integration_type == "opencti":
            # Test OpenCTI connection
            result = await test_opencti_connection(integration)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown integration type: {integration.integration_type}"
            )
        
        # Update integration status
        integration.is_connected = result["success"]
        integration.last_connection_test = datetime.utcnow()
        integration.connection_error = None if result["success"] else result.get("error")
        
        db.commit()
        
        return result
        
    except Exception as e:
        integration.is_connected = False
        integration.last_connection_test = datetime.utcnow()
        integration.connection_error = str(e)
        db.commit()
        
        return {"success": False, "error": str(e)}


async def test_openvas_connection(integration: Integration) -> Dict[str, Any]:
    """Test OpenVAS connection."""
    try:
        # Simulate OpenVAS connection test
        # In real implementation, you would use the OpenVAS API
        if not integration.endpoint_url:
            return {"success": False, "error": "No endpoint URL configured"}
        
        # Simulate successful connection
        return {
            "success": True,
            "message": "Successfully connected to OpenVAS (simulated)",
            "version": "22.4",  # Simulated version
            "capabilities": ["vulnerability_scanning", "asset_discovery"]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def test_opencti_connection(integration: Integration) -> Dict[str, Any]:
    """Test OpenCTI connection."""
    try:
        if not integration.endpoint_url or not integration.api_key:
            return {"success": False, "error": "Missing endpoint URL or API token"}
        
        # Simulate OpenCTI connection test
        # In production, you would make actual GraphQL calls
        return {
            "success": True,
            "message": "Successfully connected to OpenCTI (simulated)",
            "user": {"id": "user123", "name": "Test User"}
        }
                
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/sync/{integration_id}")
async def sync_integration_data(
    integration_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Sync data from an integration."""
    
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if not integration.is_connected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration is not connected. Please test connection first."
        )
    
    # Start background sync task
    if integration.integration_type == "openvas":
        background_tasks.add_task(sync_openvas_data, integration.id, db)
    elif integration.integration_type == "opencti":
        background_tasks.add_task(sync_opencti_data, integration.id, db)
    
    return {"message": f"Data sync started for {integration.name}"}


async def sync_openvas_data(integration_id: int, db: Session):
    """Background task to sync OpenVAS vulnerability data."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        return
    
    try:
        # Simulate OpenVAS data sync
        # In real implementation, you would call OpenVAS API to get scan results
        
        # Get all assets for correlation
        assets = db.query(Asset).filter(Asset.is_active == True).all()
        
        # Simulate vulnerability data
        sample_vulnerabilities = [
            {
                "vulnerability_id": "CVE-2023-1234",
                "title": "Remote Code Execution in Apache",
                "description": "Critical vulnerability allowing remote code execution",
                "severity": "critical",
                "cvss_score": 9.8,
                "port": "80",
                "service": "HTTP"
            },
            {
                "vulnerability_id": "CVE-2023-5678",
                "title": "SQL Injection in Web Application",
                "description": "SQL injection vulnerability in login form",
                "severity": "high",
                "cvss_score": 8.1,
                "port": "443",
                "service": "HTTPS"
            }
        ]
        
        for asset in assets[:2]:  # Limit to first 2 assets for demo
            for vuln_data in sample_vulnerabilities:
                # Create vulnerability record
                vulnerability = VulnerabilityData(
                    integration_id=integration.id,
                    asset_id=asset.id,
                    vulnerability_id=vuln_data["vulnerability_id"],
                    title=vuln_data["title"],
                    description=vuln_data["description"],
                    severity=vuln_data["severity"],
                    cvss_score=vuln_data["cvss_score"],
                    port=vuln_data["port"],
                    service=vuln_data["service"],
                    scan_date=datetime.utcnow(),
                    scanner_name="OpenVAS"
                )
                db.add(vulnerability)
        
        # Update integration sync status
        integration.last_sync = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        integration.connection_error = f"Sync failed: {str(e)}"
        db.commit()


async def sync_opencti_data(integration_id: int, db: Session):
    """Background task to sync OpenCTI threat intelligence data."""
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        return
    
    try:
        # Simulate OpenCTI data sync
        # In real implementation, you would call OpenCTI GraphQL API
        
        sample_threats = [
            {
                "threat_name": "APT29",
                "description": "Advanced persistent threat group",
                "threat_actor": "APT29",
                "indicator_type": "ip",
                "indicator_value": "192.168.1.100",
                "severity": "high",
                "confidence_level": "high"
            },
            {
                "threat_name": "Lazarus Group",
                "description": "North Korean state-sponsored group",
                "threat_actor": "Lazarus Group",
                "indicator_type": "domain",
                "indicator_value": "malicious-domain.com",
                "severity": "critical",
                "confidence_level": "medium"
            }
        ]
        
        for threat_data in sample_threats:
            threat_intel = ThreatIntelData(
                integration_id=integration.id,
                intel_type="actor",
                indicator_type=threat_data["indicator_type"],
                indicator_value=threat_data["indicator_value"],
                threat_name=threat_data["threat_name"],
                description=threat_data["description"],
                threat_actor=threat_data["threat_actor"],
                confidence_level=threat_data["confidence_level"],
                severity=threat_data["severity"],
                first_seen=datetime.utcnow()
            )
            db.add(threat_intel)
        
        # Update integration sync status
        integration.last_sync = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        integration.connection_error = f"Sync failed: {str(e)}"
        db.commit()


@router.get("/vulnerabilities")
async def get_vulnerability_data(
    asset_id: int = None,
    severity: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get vulnerability data from integrations."""
    
    query = db.query(VulnerabilityData)
    
    if asset_id:
        query = query.filter(VulnerabilityData.asset_id == asset_id)
    
    if severity:
        query = query.filter(VulnerabilityData.severity == severity)
    
    vulnerabilities = query.order_by(VulnerabilityData.scan_date.desc()).limit(100).all()
    
    return [
        {
            "id": vuln.id,
            "vulnerability_id": vuln.vulnerability_id,
            "title": vuln.title,
            "severity": vuln.severity,
            "cvss_score": vuln.cvss_score,
            "asset_id": vuln.asset_id,
            "scan_date": vuln.scan_date.isoformat() if vuln.scan_date else None,
            "status": vuln.status
        }
        for vuln in vulnerabilities
    ]


@router.get("/threat-intelligence")
async def get_threat_intelligence(
    threat_actor: str = None,
    severity: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get threat intelligence data from integrations."""
    
    query = db.query(ThreatIntelData)
    
    if threat_actor:
        query = query.filter(ThreatIntelData.threat_actor.contains(threat_actor))
    
    if severity:
        query = query.filter(ThreatIntelData.severity == severity)
    
    threats = query.order_by(ThreatIntelData.created_at.desc()).limit(100).all()
    
    return [
        {
            "id": threat.id,
            "threat_name": threat.threat_name,
            "threat_actor": threat.threat_actor,
            "indicator_type": threat.indicator_type,
            "indicator_value": threat.indicator_value,
            "severity": threat.severity,
            "confidence_level": threat.confidence_level,
            "created_at": threat.created_at.isoformat()
        }
        for threat in threats
    ]