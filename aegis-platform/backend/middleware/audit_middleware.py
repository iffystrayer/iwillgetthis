"""Middleware for automatic audit trail logging"""

import json
import time
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import logging

from services.audit_service import audit_service
from database import get_db

logger = logging.getLogger(__name__)

class AuditMiddleware:
    """Middleware to automatically capture and log significant application events"""
    
    def __init__(self):
        # Events that should be automatically logged
        self.logged_methods = {'POST', 'PUT', 'DELETE', 'PATCH'}
        
        # Paths to exclude from automatic logging
        self.excluded_paths = {
            '/health', '/metrics', '/docs', '/redoc', '/openapi.json',
            '/api/v1/auth/verify-token',  # Too frequent
            '/api/v1/search/suggestions'  # Too frequent
        }
        
        # Map HTTP methods to event types
        self.method_to_event_type = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }
        
        # Sensitive fields to redact from request/response logging
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'credentials', 
            'authorization', 'cookie', 'session'
        }
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(path in str(request.url.path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Skip if method is not in logged methods
        if request.method not in self.logged_methods:
            return await call_next(request)
        
        start_time = time.time()
        
        # Extract request information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Try to get user information from request state
        user_id = getattr(request.state, 'user_id', None) if hasattr(request.state, 'user_id') else None
        
        # Extract path components to determine entity information
        entity_type, entity_id = self._extract_entity_info(request.url.path)
        
        # Capture request body (if reasonable size)
        request_body = None
        if request.headers.get("content-length"):
            try:
                content_length = int(request.headers["content-length"])
                if content_length < 10000:  # Only capture if less than 10KB
                    body = await request.body()
                    if body:
                        try:
                            request_body = json.loads(body.decode())
                            # Sanitize sensitive data
                            request_body = self._sanitize_data(request_body)
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            request_body = {"raw_body_size": len(body)}
            except (ValueError, TypeError):
                pass
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Determine if we should log this event
        should_log = self._should_log_request(request, response)
        
        if should_log:
            # Capture response information (for successful operations)
            response_info = None
            if 200 <= response.status_code < 300:
                response_info = {
                    "status_code": response.status_code,
                    "processing_time_ms": round(process_time * 1000, 2)
                }
            
            # Determine risk level based on operation and status
            risk_level = self._determine_risk_level(request, response)
            
            # Create audit log entry
            try:
                # Use a database session for logging
                db = next(get_db())
                try:
                    event_type = self.method_to_event_type.get(request.method, 'action')
                    
                    # Build description
                    description = f"{request.method} {request.url.path}"
                    if response.status_code >= 400:
                        description += f" - Failed ({response.status_code})"
                    elif response.status_code >= 300:
                        description += f" - Redirected ({response.status_code})"
                    else:
                        description += " - Success"
                    
                    # Build details
                    details = {
                        "method": request.method,
                        "path": str(request.url.path),
                        "query_params": dict(request.query_params) if request.query_params else None,
                        "status_code": response.status_code,
                        "processing_time_ms": round(process_time * 1000, 2),
                        "user_agent": user_agent[:200] if user_agent else None
                    }
                    
                    if request_body:
                        details["request_data"] = request_body
                    
                    if response_info:
                        details["response_info"] = response_info
                    
                    audit_service.log_event(
                        db=db,
                        event_type=event_type,
                        entity_type=entity_type or 'system',
                        entity_id=entity_id,
                        user_id=user_id,
                        action=f"{request.method} {entity_type or 'endpoint'}",
                        description=description,
                        details=details,
                        source="api",
                        ip_address=client_ip,
                        user_agent=user_agent,
                        risk_level=risk_level
                    )
                    
                except Exception as e:
                    logger.warning(f"Failed to log audit event: {e}")
                finally:
                    db.close()
                    
            except Exception as e:
                logger.warning(f"Failed to get database session for audit logging: {e}")
        
        return response
    
    def _extract_entity_info(self, path: str) -> tuple[Optional[str], Optional[int]]:
        """Extract entity type and ID from API path"""
        
        # Remove leading /api/v1/ if present
        clean_path = path.replace('/api/v1/', '')
        path_parts = clean_path.strip('/').split('/')
        
        if not path_parts or path_parts[0] == '':
            return None, None
        
        entity_type = path_parts[0]
        entity_id = None
        
        # Look for numeric ID in the path
        for part in path_parts[1:]:
            try:
                entity_id = int(part)
                break
            except ValueError:
                continue
        
        # Map common endpoint names to entity types
        entity_mapping = {
            'users': 'user',
            'assets': 'asset',
            'risks': 'risk',
            'assessments': 'assessment',
            'evidence': 'evidence',
            'tasks': 'task',
            'frameworks': 'framework',
            'reports': 'report',
            'notifications': 'notification',
            'auth': 'authentication',
            'dashboards': 'dashboard'
        }
        
        return entity_mapping.get(entity_type, entity_type), entity_id
    
    def _should_log_request(self, request: Request, response: Response) -> bool:
        """Determine if this request should be logged"""
        
        # Always log failed requests (4xx, 5xx)
        if response.status_code >= 400:
            return True
        
        # Always log successful write operations
        if request.method in {'POST', 'PUT', 'DELETE', 'PATCH'} and 200 <= response.status_code < 300:
            return True
        
        # Log authentication events
        if 'auth' in request.url.path:
            return True
        
        # Log admin operations
        if any(admin_path in request.url.path for admin_path in ['/admin/', '/system/']):
            return True
        
        return False
    
    def _determine_risk_level(self, request: Request, response: Response) -> str:
        """Determine risk level based on request and response"""
        
        # High risk: Failed authentication, delete operations, admin operations
        if response.status_code == 401 or response.status_code == 403:
            return "high"
        
        if request.method == 'DELETE' and response.status_code < 300:
            return "high"
        
        if any(admin_path in request.url.path for admin_path in ['/admin/', '/system/', '/config']):
            return "high"
        
        # Medium risk: Failed operations, write operations
        if response.status_code >= 400:
            return "medium"
        
        if request.method in {'POST', 'PUT', 'PATCH'} and response.status_code < 300:
            return "medium"
        
        # Low risk: Everything else
        return "low"
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove sensitive information from data"""
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                key_lower = key.lower()
                if any(sensitive in key_lower for sensitive in self.sensitive_fields):
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        
        else:
            return data

# Middleware instance
audit_middleware = AuditMiddleware()