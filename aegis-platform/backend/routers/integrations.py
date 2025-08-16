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


# Enhanced Enterprise Integration Endpoints

@router.get("/types")
async def get_integration_types(
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get available integration types."""
    
    # For now, return predefined integration types
    # In production, this would query the IntegrationType model
    integration_types = [
        {
            "id": "splunk",
            "name": "splunk",
            "category": "siem",
            "display_name": "Splunk Enterprise/Cloud",
            "description": "Splunk SIEM platform for security event analysis and monitoring",
            "capabilities": ["read_events", "read_alerts", "health_check"],
            "auth_methods": ["basic", "token"],
            "default_port": 8089,
            "requires_ssl": True,
            "is_enterprise": True
        },
        {
            "id": "qradar",
            "name": "qradar",
            "category": "siem",
            "display_name": "IBM QRadar SIEM",
            "description": "IBM QRadar security intelligence platform",
            "capabilities": ["read_events", "read_alerts", "health_check"],
            "auth_methods": ["token"],
            "default_port": 443,
            "requires_ssl": True,
            "is_enterprise": True
        },
        {
            "id": "sentinel",
            "name": "sentinel",
            "category": "siem",
            "display_name": "Microsoft Sentinel",
            "description": "Microsoft Azure Sentinel cloud-native SIEM",
            "capabilities": ["read_events", "read_alerts", "health_check"],
            "auth_methods": ["oauth"],
            "default_port": 443,
            "requires_ssl": True,
            "is_enterprise": True
        },
        {
            "id": "elastic",
            "name": "elastic",
            "category": "siem",
            "display_name": "Elastic Stack (ELK)",
            "description": "Elasticsearch, Logstash, and Kibana security platform",
            "capabilities": ["read_events", "read_alerts", "health_check"],
            "auth_methods": ["basic", "api_key"],
            "default_port": 9200,
            "requires_ssl": True,
            "is_enterprise": False
        },
        {
            "id": "servicenow",
            "name": "servicenow",
            "category": "grc",
            "display_name": "ServiceNow GRC",
            "description": "ServiceNow Governance, Risk, and Compliance platform",
            "capabilities": ["read_controls", "create_tickets", "update_tickets", "health_check"],
            "auth_methods": ["basic"],
            "default_port": 443,
            "requires_ssl": True,
            "is_enterprise": True
        },
        {
            "id": "archer",
            "name": "archer",
            "category": "grc",
            "display_name": "RSA Archer",
            "description": "RSA Archer governance, risk, and compliance platform",
            "capabilities": ["read_controls", "create_tickets", "health_check"],
            "auth_methods": ["basic"],
            "default_port": 443,
            "requires_ssl": True,
            "is_enterprise": True
        },
        {
            "id": "metricstream",
            "name": "metricstream",
            "category": "grc",
            "display_name": "MetricStream",
            "description": "MetricStream integrated GRC platform",
            "capabilities": ["read_controls", "create_tickets", "health_check"],
            "auth_methods": ["basic", "api_key"],
            "default_port": 443,
            "requires_ssl": True,
            "is_enterprise": True
        }
    ]
    
    if category:
        integration_types = [t for t in integration_types if t["category"] == category]
    
    return integration_types


@router.post("/connectors/create")
async def create_connector(
    connector_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create and initialize a new connector instance."""
    
    try:
        from connectors.base import connector_registry
        from models.integration import Integration, IntegrationConnector
        
        # Validate required fields
        required_fields = ['name', 'integration_type', 'endpoint_url']
        missing_fields = [field for field in required_fields if not connector_data.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Create integration record
        integration = Integration(
            name=connector_data['name'],
            integration_type=connector_data['integration_type'],
            endpoint_url=connector_data['endpoint_url'],
            username=connector_data.get('username'),
            password=connector_data.get('password'),  # TODO: Encrypt in production
            api_key=connector_data.get('api_key'),  # TODO: Encrypt in production
            auth_method=connector_data.get('auth_method', 'basic'),
            auth_config=connector_data.get('auth_config', {}),
            configuration=connector_data.get('configuration', {}),
            description=connector_data.get('description', ''),
            created_by=current_user.id
        )
        
        db.add(integration)
        db.commit()
        db.refresh(integration)
        
        # Determine connector class based on integration type
        connector_class_map = {
            'splunk': 'SplunkConnector',
            'qradar': 'QRadarConnector',
            'sentinel': 'SentinelConnector',
            'elastic': 'ElasticConnector',
            'servicenow': 'ServiceNowConnector',
            'archer': 'ArcherConnector',
            'metricstream': 'MetricStreamConnector'
        }
        
        connector_class_name = connector_class_map.get(integration.integration_type)
        if not connector_class_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported integration type: {integration.integration_type}"
            )
        
        # Create connector record
        connector = IntegrationConnector(
            integration_id=integration.id,
            connector_class=f"connectors.{integration.integration_type}.{connector_class_name}",
            connector_version="1.0",
            status="active"
        )
        
        db.add(connector)
        db.commit()
        db.refresh(connector)
        
        return {
            "success": True,
            "integration_id": integration.id,
            "connector_id": connector.id,
            "message": f"Connector {integration.name} created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connector: {str(e)}"
        )


@router.post("/connectors/{connector_id}/test")
async def test_connector(
    connector_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test a connector's connection."""
    
    try:
        from connectors.base import connector_registry
        
        # Get connector and integration
        connector = db.query(IntegrationConnector).filter(
            IntegrationConnector.id == connector_id
        ).first()
        
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found"
            )
        
        integration = connector.integration
        
        # Build configuration for connector
        config = {
            'endpoint_url': integration.endpoint_url,
            'username': integration.username,
            'password': integration.password,
            'api_key': integration.api_key,
            'auth_method': integration.auth_method,
            **integration.configuration
        }
        
        # Create connector instance
        connector_instance = await connector_registry.create_connector(
            integration.integration_type,
            config
        )
        
        if not connector_instance:
            return {
                "success": False,
                "error": "Failed to create connector instance"
            }
        
        try:
            # Test connection
            test_result = await connector_instance.test_connection()
            
            # Update connector status based on test result
            if test_result.get('success', False):
                connector.status = "active"
                connector.health_status = "healthy"
                integration.is_connected = True
                integration.health_status = "healthy"
                integration.connection_error = None
            else:
                connector.status = "error"
                connector.health_status = "error"
                integration.is_connected = False
                integration.health_status = "error"
                integration.connection_error = test_result.get('message', 'Connection test failed')
            
            connector.last_health_check = datetime.utcnow()
            integration.last_connection_test = datetime.utcnow()
            
            db.commit()
            
            return test_result
            
        finally:
            await connector_instance.cleanup()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )


@router.post("/connectors/{connector_id}/sync")
async def sync_connector_data(
    connector_id: int,
    sync_options: Dict[str, Any] = {},
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Trigger data synchronization for a connector."""
    
    try:
        # Get connector and integration
        connector = db.query(IntegrationConnector).filter(
            IntegrationConnector.id == connector_id
        ).first()
        
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found"
            )
        
        integration = connector.integration
        
        if not integration.is_connected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connector is not connected. Please test connection first."
            )
        
        # Create sync log entry
        from models.integration import IntegrationSyncLog
        
        sync_log = IntegrationSyncLog(
            connector_id=connector.id,
            sync_type=sync_options.get('sync_type', 'incremental'),
            started_at=datetime.utcnow(),
            status='running'
        )
        
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)
        
        # Start background sync task
        background_tasks.add_task(
            sync_connector_background,
            connector_id,
            sync_log.id,
            sync_options
        )
        
        return {
            "success": True,
            "sync_id": sync_log.id,
            "message": f"Data sync started for {integration.name}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start sync: {str(e)}"
        )


@router.get("/connectors/{connector_id}/status")
async def get_connector_status(
    connector_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed connector status and health information."""
    
    try:
        connector = db.query(IntegrationConnector).filter(
            IntegrationConnector.id == connector_id
        ).first()
        
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Connector not found"
            )
        
        integration = connector.integration
        
        # Get recent sync logs
        recent_syncs = db.query(IntegrationSyncLog).filter(
            IntegrationSyncLog.connector_id == connector_id
        ).order_by(IntegrationSyncLog.started_at.desc()).limit(5).all()
        
        return {
            "connector_id": connector.id,
            "integration_id": integration.id,
            "name": integration.name,
            "type": integration.integration_type,
            "status": connector.status,
            "health_status": connector.health_status,
            "is_connected": integration.is_connected,
            "last_health_check": connector.last_health_check.isoformat() if connector.last_health_check else None,
            "last_sync": connector.last_data_sync.isoformat() if connector.last_data_sync else None,
            "success_rate": connector.success_rate,
            "average_response_time": connector.average_response_time,
            "total_requests": connector.total_requests,
            "failed_requests": connector.failed_requests,
            "auto_sync_enabled": connector.auto_sync_enabled,
            "sync_frequency": connector.sync_frequency,
            "recent_syncs": [
                {
                    "id": sync.id,
                    "sync_type": sync.sync_type,
                    "status": sync.status,
                    "started_at": sync.started_at.isoformat(),
                    "completed_at": sync.completed_at.isoformat() if sync.completed_at else None,
                    "records_processed": sync.records_processed,
                    "duration_seconds": sync.duration_seconds
                }
                for sync in recent_syncs
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connector status: {str(e)}"
        )


async def sync_connector_background(connector_id: int, sync_log_id: int, sync_options: Dict[str, Any]):
    """Background task for connector data synchronization."""
    
    try:
        from database import SessionLocal
        from connectors.base import connector_registry
        from models.integration import IntegrationConnector, IntegrationSyncLog, SIEMEventData, GRCControlData
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        
        try:
            # Get connector and sync log
            connector = db.query(IntegrationConnector).filter(
                IntegrationConnector.id == connector_id
            ).first()
            
            sync_log = db.query(IntegrationSyncLog).filter(
                IntegrationSyncLog.id == sync_log_id
            ).first()
            
            if not connector or not sync_log:
                logger.error(f"Connector {connector_id} or sync log {sync_log_id} not found")
                return
            
            integration = connector.integration
            start_time = datetime.utcnow()
            
            # Build configuration
            config = {
                'endpoint_url': integration.endpoint_url,
                'username': integration.username,
                'password': integration.password,
                'api_key': integration.api_key,
                'auth_method': integration.auth_method,
                **integration.configuration
            }
            
            # Create connector instance
            connector_instance = await connector_registry.create_connector(
                integration.integration_type,
                config
            )
            
            if not connector_instance:
                sync_log.status = 'failed'
                sync_log.error_message = 'Failed to create connector instance'
                sync_log.completed_at = datetime.utcnow()
                db.commit()
                return
            
            try:
                records_processed = 0
                records_created = 0
                
                # Determine sync time range
                if sync_options.get('sync_type') == 'full':
                    start_date = datetime.utcnow() - timedelta(days=30)
                else:
                    start_date = connector.last_data_sync or datetime.utcnow() - timedelta(hours=24)
                
                end_date = datetime.utcnow()
                
                # Sync based on connector type
                if connector_instance.connector_type == 'siem':
                    # Sync events and alerts
                    events_result = await connector_instance.get_events(
                        start_date, end_date, limit=sync_options.get('limit', 1000)
                    )
                    
                    if events_result.get('success'):
                        for event in events_result.get('events', []):
                            # Store SIEM event data
                            siem_event = SIEMEventData(
                                integration_id=integration.id,
                                event_id=event.get('id'),
                                event_type='event',
                                title=event.get('title', 'SIEM Event'),
                                description=event.get('description', ''),
                                severity=event.get('severity', 'medium'),
                                source_ip=event.get('source_ip'),
                                destination_ip=event.get('destination_ip'),
                                username=event.get('username'),
                                event_time=datetime.fromisoformat(event['timestamp']) if event.get('timestamp') else datetime.utcnow(),
                                raw_event_data=event.get('raw_data', event)
                            )
                            db.add(siem_event)
                            records_created += 1
                        
                        records_processed += len(events_result.get('events', []))
                
                elif connector_instance.connector_type == 'grc':
                    # Sync controls and assessments
                    controls_result = await connector_instance.get_controls(
                        limit=sync_options.get('limit', 1000)
                    )
                    
                    if controls_result.get('success'):
                        for control in controls_result.get('controls', []):
                            # Store GRC control data
                            grc_control = GRCControlData(
                                integration_id=integration.id,
                                control_id=control.get('control_id'),
                                control_name=control.get('name'),
                                framework=control.get('framework'),
                                description=control.get('description'),
                                control_type=control.get('control_type'),
                                control_frequency=control.get('frequency'),
                                implementation_status=control.get('status'),
                                effectiveness_rating=control.get('effectiveness'),
                                risk_rating=control.get('risk_rating'),
                                control_owner=control.get('owner'),
                                raw_control_data=control.get('raw_data', control)
                            )
                            db.add(grc_control)
                            records_created += 1
                        
                        records_processed += len(controls_result.get('controls', []))
                
                # Update sync log
                sync_log.status = 'completed'
                sync_log.completed_at = datetime.utcnow()
                sync_log.records_processed = records_processed
                sync_log.records_created = records_created
                sync_log.duration_seconds = (sync_log.completed_at - sync_log.started_at).total_seconds()
                
                # Update connector
                connector.last_data_sync = datetime.utcnow()
                connector.total_requests += 1
                
                db.commit()
                
                logger.info(f"Sync completed for connector {connector_id}: {records_processed} processed, {records_created} created")
                
            finally:
                await connector_instance.cleanup()
        
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Sync failed for connector {connector_id}: {str(e)}")
        
        # Update sync log with error
        try:
            db = SessionLocal()
            sync_log = db.query(IntegrationSyncLog).filter(
                IntegrationSyncLog.id == sync_log_id
            ).first()
            
            if sync_log:
                sync_log.status = 'failed'
                sync_log.error_message = str(e)
                sync_log.completed_at = datetime.utcnow()
                db.commit()
            
            db.close()
        except Exception as db_error:
            logger.error(f"Failed to update sync log: {str(db_error)}")


@router.get("/sync-logs/{connector_id}")
async def get_sync_logs(
    connector_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get synchronization logs for a connector."""
    
    sync_logs = db.query(IntegrationSyncLog).filter(
        IntegrationSyncLog.connector_id == connector_id
    ).order_by(IntegrationSyncLog.started_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "connector_id": log.connector_id,
            "sync_type": log.sync_type,
            "status": log.status,
            "started_at": log.started_at.isoformat(),
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "records_processed": log.records_processed,
            "records_created": log.records_created,
            "records_updated": log.records_updated,
            "records_skipped": log.records_skipped,
            "duration_seconds": log.duration_seconds,
            "error_message": log.error_message
        }
        for log in sync_logs
    ]