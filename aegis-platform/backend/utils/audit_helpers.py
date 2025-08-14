"""Helper utilities for audit trail logging throughout the application"""

import functools
import json
from typing import Callable, Dict, Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session

from services.audit_service import audit_service

def log_user_action(
    event_type: str,
    entity_type: str,
    action: str,
    description: str = "",
    risk_level: str = "medium"
):
    """Decorator to automatically log user actions"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract common parameters from function arguments
            db: Optional[Session] = None
            current_user = None
            request: Optional[Request] = None
            entity_id: Optional[int] = None
            
            # Look for standard FastAPI dependency injection parameters
            for arg in args:
                if hasattr(arg, 'query'):  # Session object
                    db = arg
                elif hasattr(arg, 'id') and hasattr(arg, 'email'):  # User object
                    current_user = arg
                elif hasattr(arg, 'url') and hasattr(arg, 'client'):  # Request object
                    request = arg
            
            # Look in kwargs
            if 'db' in kwargs:
                db = kwargs['db']
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
            if 'request' in kwargs:
                request = kwargs['request']
            
            # Look for entity ID in kwargs (common patterns)
            for key in ['id', 'entity_id', 'user_id', 'risk_id', 'asset_id']:
                if key in kwargs and isinstance(kwargs[key], int):
                    entity_id = kwargs[key]
                    break
            
            # Execute the function
            try:
                result = await func(*args, **kwargs)
                
                # Log successful action
                if db and current_user:
                    client_ip = request.client.host if request and request.client else None
                    user_agent = request.headers.get("user-agent") if request else None
                    
                    audit_service.log_event(
                        db=db,
                        event_type=event_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        user_id=current_user.id,
                        action=action,
                        description=f"{description} - Success",
                        source="api",
                        ip_address=client_ip,
                        user_agent=user_agent,
                        risk_level=risk_level
                    )
                
                return result
                
            except Exception as e:
                # Log failed action
                if db and current_user:
                    client_ip = request.client.host if request and request.client else None
                    user_agent = request.headers.get("user-agent") if request else None
                    
                    audit_service.log_event(
                        db=db,
                        event_type=event_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        user_id=current_user.id,
                        action=action,
                        description=f"{description} - Failed: {str(e)[:200]}",
                        details={"error": str(e), "error_type": type(e).__name__},
                        source="api",
                        ip_address=client_ip,
                        user_agent=user_agent,
                        risk_level="high"  # Failed operations are high risk
                    )
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

def log_system_event(
    db: Session,
    event_type: str,
    entity_type: str,
    action: str,
    description: str,
    entity_id: Optional[int] = None,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    risk_level: str = "medium"
):
    """Helper function to log system events"""
    
    try:
        audit_service.log_event(
            db=db,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action,
            description=description,
            details=details,
            source="system",
            risk_level=risk_level
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log system event: {e}")

def log_security_event(
    db: Session,
    event_type: str,
    action: str,
    description: str,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log security events"""
    
    try:
        audit_service.log_event(
            db=db,
            event_type=event_type,
            entity_type="security",
            entity_id=None,
            user_id=user_id,
            action=action,
            description=description,
            details=details,
            source="security_system",
            ip_address=ip_address,
            user_agent=user_agent,
            risk_level="high"  # Security events are always high risk
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log security event: {e}")

def log_data_access(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    user_id: int,
    sensitive_data: bool = False,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log data access events"""
    
    risk_level = "high" if sensitive_data else "low"
    
    try:
        audit_service.log_event(
            db=db,
            event_type="data_access",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action,
            description=f"Data access - {action} {entity_type} ID {entity_id}",
            details=details,
            source="api",
            risk_level=risk_level
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log data access event: {e}")

def log_configuration_change(
    db: Session,
    config_type: str,
    action: str,
    description: str,
    user_id: int,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log configuration changes"""
    
    config_details = details or {}
    if old_value is not None:
        config_details["old_value"] = old_value
    if new_value is not None:
        config_details["new_value"] = new_value
    
    try:
        audit_service.log_event(
            db=db,
            event_type="configuration_change",
            entity_type="system_config",
            entity_id=None,
            user_id=user_id,
            action=action,
            description=f"Configuration change - {config_type}: {description}",
            details=config_details,
            source="admin_interface",
            risk_level="high"  # Config changes are high risk
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log configuration change: {e}")

def log_bulk_operation(
    db: Session,
    operation_type: str,
    entity_type: str,
    user_id: int,
    item_count: int,
    success_count: int,
    failure_count: int,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log bulk operations"""
    
    bulk_details = details or {}
    bulk_details.update({
        "total_items": item_count,
        "successful": success_count,
        "failed": failure_count,
        "success_rate": round((success_count / max(1, item_count)) * 100, 2)
    })
    
    # Determine risk level based on failure rate
    failure_rate = failure_count / max(1, item_count)
    if failure_rate > 0.5:
        risk_level = "high"
    elif failure_rate > 0.1:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    try:
        audit_service.log_event(
            db=db,
            event_type="bulk_operation",
            entity_type=entity_type,
            entity_id=None,
            user_id=user_id,
            action=f"Bulk {operation_type}",
            description=f"Bulk {operation_type} of {entity_type} - {success_count}/{item_count} successful",
            details=bulk_details,
            source="api",
            risk_level=risk_level
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log bulk operation: {e}")

def log_integration_event(
    db: Session,
    integration_name: str,
    event_type: str,
    action: str,
    description: str,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log integration events"""
    
    risk_level = "low" if success else "medium"
    status = "Success" if success else "Failed"
    
    try:
        audit_service.log_event(
            db=db,
            event_type=event_type,
            entity_type="integration",
            entity_id=None,
            user_id=None,  # System-driven
            action=f"{integration_name} - {action}",
            description=f"{integration_name} integration - {description} - {status}",
            details=details,
            source="integration",
            risk_level=risk_level
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to log integration event: {e}")

# Decorator for high-risk operations
def audit_high_risk_operation(
    event_type: str,
    entity_type: str,
    action: str,
    description: str
):
    """Decorator for high-risk operations that require detailed logging"""
    return log_user_action(
        event_type=event_type,
        entity_type=entity_type,
        action=action,
        description=description,
        risk_level="high"
    )

# Decorator for administrative operations
def audit_admin_operation(
    action: str,
    description: str
):
    """Decorator for administrative operations"""
    return log_user_action(
        event_type="admin_action",
        entity_type="system",
        action=action,
        description=description,
        risk_level="high"
    )