"""
Prometheus metrics collection for Aegis Platform
Provides comprehensive application and business metrics
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
import time
import psutil
import logging
from typing import Optional
from sqlalchemy import text
from database import get_db
from contextlib import contextmanager

# Application Info
app_info = Info('aegis_app', 'Aegis Platform Application Info')
app_info.info({
    'version': '2.0.0',
    'component': 'aegis-backend',
    'environment': 'production'
})

# HTTP Metrics
http_requests_total = Counter(
    'aegis_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'aegis_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database Metrics
database_connections_active = Gauge(
    'aegis_database_connections_active',
    'Number of active database connections'
)

database_query_duration_seconds = Histogram(
    'aegis_database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

database_queries_total = Counter(
    'aegis_database_queries_total',
    'Total database queries',
    ['operation', 'status']
)

# Authentication Metrics
auth_attempts_total = Counter(
    'aegis_auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

active_sessions = Gauge(
    'aegis_active_sessions',
    'Number of active user sessions'
)

# Business Logic Metrics
risks_created_total = Counter(
    'aegis_risks_created_total',
    'Total risks created'
)

assessments_completed_total = Counter(
    'aegis_assessments_completed_total',
    'Total assessments completed'
)

tasks_created_total = Counter(
    'aegis_tasks_created_total',
    'Total tasks created'
)

evidence_uploaded_total = Counter(
    'aegis_evidence_uploaded_total',
    'Total evidence files uploaded'
)

# AI/LLM Metrics
ai_requests_total = Counter(
    'aegis_ai_requests_total',
    'Total AI/LLM requests',
    ['provider', 'operation', 'status']
)

ai_request_duration_seconds = Histogram(
    'aegis_ai_request_duration_seconds',
    'AI request duration in seconds',
    ['provider', 'operation']
)

ai_tokens_consumed_total = Counter(
    'aegis_ai_tokens_consumed_total',
    'Total AI tokens consumed',
    ['provider', 'model']
)

# System Resource Metrics
system_cpu_percent = Gauge(
    'aegis_system_cpu_percent',
    'System CPU usage percentage'
)

system_memory_bytes = Gauge(
    'aegis_system_memory_bytes',
    'System memory usage in bytes',
    ['type']
)

system_disk_bytes = Gauge(
    'aegis_system_disk_bytes',
    'System disk usage in bytes',
    ['device', 'type']
)

# Application Health Metrics
health_check_duration_seconds = Histogram(
    'aegis_health_check_duration_seconds',
    'Health check duration in seconds',
    ['component']
)

background_tasks_active = Gauge(
    'aegis_background_tasks_active',
    'Number of active background tasks'
)

# Error Metrics
application_errors_total = Counter(
    'aegis_application_errors_total',
    'Total application errors',
    ['component', 'error_type']
)

# Security Metrics
failed_login_attempts_total = Counter(
    'aegis_failed_login_attempts_total',
    'Total failed login attempts',
    ['ip_address', 'reason']
)

security_events_total = Counter(
    'aegis_security_events_total',
    'Total security events',
    ['event_type', 'severity']
)


class MetricsCollector:
    """Centralized metrics collection class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        http_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_auth_attempt(self, method: str, status: str):
        """Record authentication attempt"""
        auth_attempts_total.labels(method=method, status=status).inc()
    
    def record_failed_login(self, ip_address: str, reason: str):
        """Record failed login attempt"""
        failed_login_attempts_total.labels(ip_address=ip_address, reason=reason).inc()
    
    def record_database_query(self, operation: str, duration: float, status: str = 'success'):
        """Record database query metrics"""
        database_queries_total.labels(operation=operation, status=status).inc()
        database_query_duration_seconds.labels(operation=operation).observe(duration)
    
    def record_ai_request(self, provider: str, operation: str, duration: float, status: str, tokens: int = 0, model: str = ''):
        """Record AI/LLM request metrics"""
        ai_requests_total.labels(provider=provider, operation=operation, status=status).inc()
        ai_request_duration_seconds.labels(provider=provider, operation=operation).observe(duration)
        if tokens > 0 and model:
            ai_tokens_consumed_total.labels(provider=provider, model=model).inc(tokens)
    
    def record_business_event(self, event_type: str):
        """Record business logic events"""
        if event_type == 'risk_created':
            risks_created_total.inc()
        elif event_type == 'assessment_completed':
            assessments_completed_total.inc()
        elif event_type == 'task_created':
            tasks_created_total.inc()
        elif event_type == 'evidence_uploaded':
            evidence_uploaded_total.inc()
    
    def record_error(self, component: str, error_type: str):
        """Record application error"""
        application_errors_total.labels(component=component, error_type=error_type).inc()
    
    def record_security_event(self, event_type: str, severity: str):
        """Record security event"""
        security_events_total.labels(event_type=event_type, severity=severity).inc()
    
    def update_active_sessions(self, count: int):
        """Update active sessions gauge"""
        active_sessions.set(count)
    
    def update_background_tasks(self, count: int):
        """Update background tasks gauge"""
        background_tasks_active.set(count)
    
    def update_database_connections(self):
        """Update database connection metrics"""
        try:
            # This would need to be implemented based on your connection pool
            # For now, using a placeholder
            database_connections_active.set(10)  # Placeholder
        except Exception as e:
            self.logger.error(f"Failed to update database connection metrics: {e}")
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_bytes.labels(type='used').set(memory.used)
            system_memory_bytes.labels(type='available').set(memory.available)
            system_memory_bytes.labels(type='total').set(memory.total)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            system_disk_bytes.labels(device='root', type='used').set(disk.used)
            system_disk_bytes.labels(device='root', type='free').set(disk.free)
            system_disk_bytes.labels(device='root', type='total').set(disk.total)
            
        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")
    
    @contextmanager
    def time_database_operation(self, operation: str):
        """Context manager to time database operations"""
        start_time = time.time()
        status = 'success'
        try:
            yield
        except Exception as e:
            status = 'error'
            raise
        finally:
            duration = time.time() - start_time
            self.record_database_query(operation, duration, status)
    
    @contextmanager
    def time_health_check(self, component: str):
        """Context manager to time health check operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            health_check_duration_seconds.labels(component=component).observe(duration)


# Global metrics collector instance
metrics_collector = MetricsCollector()

# Metrics router
router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    
    # Update system metrics before serving
    metrics_collector.update_system_metrics()
    metrics_collector.update_database_connections()
    
    # Generate and return metrics
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/health/metrics")
async def health_metrics():
    """Health check with basic metrics"""
    
    with metrics_collector.time_health_check('api'):
        # Basic health information with metrics
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "metrics_enabled": True,
            "collectors": {
                "http_requests": True,
                "database_queries": True,
                "auth_attempts": True,
                "ai_requests": True,
                "system_resources": True,
                "business_events": True
            }
        }