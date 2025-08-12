"""
Metrics collection middleware for automatic HTTP request tracking
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from metrics import metrics_collector
import logging

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically collect HTTP request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        
        # Normalize endpoint path (remove IDs and dynamic parts)
        normalized_path = self._normalize_path(path)
        
        response = None
        status_code = 500  # Default to error
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            logger.error(f"Request failed: {method} {path} - {str(e)}")
            metrics_collector.record_error('http_middleware', type(e).__name__)
            raise
        
        finally:
            # Record metrics regardless of success/failure
            duration = time.time() - start_time
            metrics_collector.record_http_request(
                method=method,
                endpoint=normalized_path,
                status_code=status_code,
                duration=duration
            )
            
            # Log slow requests
            if duration > 2.0:
                logger.warning(f"Slow request: {method} {normalized_path} took {duration:.2f}s")
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """Normalize URL path to reduce cardinality of metrics"""
        
        # Skip metrics endpoint to avoid recursive metrics
        if path == '/metrics' or path.startswith('/health'):
            return path
        
        # Common patterns to normalize
        normalizations = [
            # Replace numeric IDs with placeholder
            (r'/\d+', '/{id}'),
            # Replace UUIDs with placeholder
            (r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}'),
            # Replace email addresses
            (r'/[\w\.-]+@[\w\.-]+\.\w+', '/{email}'),
        ]
        
        import re
        normalized = path
        for pattern, replacement in normalizations:
            normalized = re.sub(pattern, replacement, normalized)
        
        # Limit path length to prevent excessive cardinality
        if len(normalized) > 100:
            normalized = normalized[:100] + '...'
        
        return normalized