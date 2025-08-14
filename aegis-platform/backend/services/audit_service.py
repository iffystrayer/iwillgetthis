"""Comprehensive audit trail logging service for tracking system activities"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import and_, or_, func, text, desc
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
import ipaddress
import hashlib
from pathlib import Path

from models.audit import AuditLog
from models.user import User
from config import settings

class AuditService:
    """Service for comprehensive audit trail logging and analysis"""
    
    def __init__(self):
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'credentials', 
            'api_key', 'private', 'confidential'
        }
        self.high_risk_events = {
            'user_created', 'user_deleted', 'role_changed', 'permission_granted',
            'permission_revoked', 'system_config_changed', 'backup_restored',
            'security_breach', 'failed_login_attempt', 'password_reset'
        }
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: str = "",
        description: str = "",
        details: Optional[Dict[str, Any]] = None,
        source: str = "system",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        risk_level: str = "medium"
    ) -> AuditLog:
        """Log an audit event with comprehensive details"""
        
        # Sanitize sensitive data
        sanitized_details = self._sanitize_details(details) if details else None
        
        # Determine risk level automatically based on event type
        if risk_level == "medium" and event_type in self.high_risk_events:
            risk_level = "high"
        
        # Create audit log entry
        audit_log = AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            action=action[:500],  # Limit action length
            description=description[:1000],  # Limit description length
            details=json.dumps(sanitized_details) if sanitized_details else None,
            source=source,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,
            risk_level=risk_level,
            timestamp=datetime.utcnow()
        )
        
        try:
            db.add(audit_log)
            db.commit()
            return audit_log
        except Exception as e:
            db.rollback()
            # Log to system logger as fallback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to log audit event: {e}")
            raise
    
    def bulk_log_events(self, db: Session, events: List[Dict[str, Any]]) -> List[AuditLog]:
        """Log multiple audit events efficiently"""
        
        audit_logs = []
        for event in events:
            # Sanitize each event
            sanitized_details = self._sanitize_details(event.get('details')) if event.get('details') else None
            
            audit_log = AuditLog(
                event_type=event.get('event_type', 'unknown'),
                entity_type=event.get('entity_type', 'unknown'),
                entity_id=event.get('entity_id'),
                user_id=event.get('user_id'),
                action=event.get('action', '')[:500],
                description=event.get('description', '')[:1000],
                details=json.dumps(sanitized_details) if sanitized_details else None,
                source=event.get('source', 'system'),
                ip_address=event.get('ip_address'),
                user_agent=event.get('user_agent', '')[:500] if event.get('user_agent') else None,
                risk_level=event.get('risk_level', 'medium'),
                timestamp=datetime.utcnow()
            )
            audit_logs.append(audit_log)
        
        try:
            db.add_all(audit_logs)
            db.commit()
            return audit_logs
        except Exception as e:
            db.rollback()
            raise
    
    def get_audit_trail(
        self,
        db: Session,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        user_id: Optional[int] = None,
        event_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Retrieve filtered audit trail with pagination"""
        
        query = db.query(AuditLog)
        
        # Apply filters
        filters = []
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            filters.append(AuditLog.entity_id == entity_id)
        if user_id is not None:
            filters.append(AuditLog.user_id == user_id)
        if event_type:
            filters.append(AuditLog.event_type == event_type)
        if risk_level:
            filters.append(AuditLog.risk_level == risk_level)
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()
        
        # Format results
        results = []
        for log in logs:
            log_data = {
                'id': log.id,
                'event_type': log.event_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'user_id': log.user_id,
                'action': log.action,
                'description': log.description,
                'source': log.source,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'risk_level': log.risk_level,
                'timestamp': log.timestamp.isoformat()
            }
            
            # Include details if requested (be careful with sensitive data)
            if include_details and log.details:
                try:
                    log_data['details'] = json.loads(log.details)
                except json.JSONDecodeError:
                    log_data['details'] = None
            
            results.append(log_data)
        
        return {
            'total_count': total_count,
            'results': results,
            'limit': limit,
            'offset': offset,
            'has_more': total_count > (offset + len(results))
        }
    
    def get_user_activity_summary(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive user activity summary"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user activities
        activities = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= start_date
            )
        ).all()
        
        # Analyze activities
        activity_by_type = {}
        activity_by_entity = {}
        risk_events = []
        daily_activity = {}
        
        for activity in activities:
            # Count by event type
            activity_by_type[activity.event_type] = activity_by_type.get(activity.event_type, 0) + 1
            
            # Count by entity type
            activity_by_entity[activity.entity_type] = activity_by_entity.get(activity.entity_type, 0) + 1
            
            # Track high-risk events
            if activity.risk_level == 'high':
                risk_events.append({
                    'event_type': activity.event_type,
                    'action': activity.action,
                    'timestamp': activity.timestamp.isoformat(),
                    'entity_type': activity.entity_type
                })
            
            # Daily activity count
            date_key = activity.timestamp.date().isoformat()
            daily_activity[date_key] = daily_activity.get(date_key, 0) + 1
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_activities': len(activities),
            'activity_by_type': activity_by_type,
            'activity_by_entity': activity_by_entity,
            'high_risk_events': risk_events,
            'high_risk_event_count': len(risk_events),
            'daily_activity': daily_activity,
            'most_active_day': max(daily_activity, key=daily_activity.get) if daily_activity else None,
            'average_daily_activity': round(len(activities) / days, 2)
        }
    
    def get_security_events(
        self,
        db: Session,
        days: int = 7,
        risk_level: str = "high"
    ) -> Dict[str, Any]:
        """Get security-related events for monitoring"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Security event types to monitor
        security_events = [
            'failed_login_attempt', 'unauthorized_access', 'permission_escalation',
            'data_export', 'system_config_changed', 'user_role_changed',
            'suspicious_activity', 'security_breach'
        ]
        
        # Get security events
        events = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                or_(
                    AuditLog.risk_level == risk_level,
                    AuditLog.event_type.in_(security_events)
                )
            )
        ).order_by(desc(AuditLog.timestamp)).all()
        
        # Analyze security events
        events_by_type = {}
        events_by_user = {}
        suspicious_ips = {}
        
        for event in events:
            # Count by event type
            events_by_type[event.event_type] = events_by_type.get(event.event_type, 0) + 1
            
            # Count by user
            if event.user_id:
                events_by_user[event.user_id] = events_by_user.get(event.user_id, 0) + 1
            
            # Track suspicious IP addresses
            if event.ip_address and event.risk_level == 'high':
                suspicious_ips[event.ip_address] = suspicious_ips.get(event.ip_address, 0) + 1
        
        # Format events for response
        formatted_events = []
        for event in events[:100]:  # Limit to latest 100
            formatted_events.append({
                'id': event.id,
                'event_type': event.event_type,
                'action': event.action,
                'description': event.description,
                'entity_type': event.entity_type,
                'user_id': event.user_id,
                'ip_address': event.ip_address,
                'risk_level': event.risk_level,
                'timestamp': event.timestamp.isoformat()
            })
        
        return {
            'period_days': days,
            'total_security_events': len(events),
            'events_by_type': events_by_type,
            'events_by_user': events_by_user,
            'suspicious_ip_addresses': suspicious_ips,
            'recent_events': formatted_events,
            'summary': {
                'high_risk_events': len([e for e in events if e.risk_level == 'high']),
                'failed_login_attempts': events_by_type.get('failed_login_attempt', 0),
                'unauthorized_access_attempts': events_by_type.get('unauthorized_access', 0),
                'config_changes': events_by_type.get('system_config_changed', 0)
            }
        }
    
    def generate_compliance_report(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate compliance audit report for regulatory requirements"""
        
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        )
        
        if entity_types:
            query = query.filter(AuditLog.entity_type.in_(entity_types))
        
        logs = query.all()
        
        # Compliance metrics
        total_events = len(logs)
        
        # Events by category
        events_by_category = {
            'data_access': 0,
            'data_modification': 0,
            'user_management': 0,
            'system_changes': 0,
            'security_events': 0
        }
        
        data_access_events = ['read', 'view', 'download', 'export']
        data_modification_events = ['create', 'update', 'delete', 'import']
        user_management_events = ['user_created', 'user_deleted', 'role_changed', 'permission_granted']
        system_events = ['system_config_changed', 'backup_created', 'backup_restored']
        security_events = ['failed_login_attempt', 'unauthorized_access', 'security_breach']
        
        for log in logs:
            if any(event in log.event_type.lower() for event in data_access_events):
                events_by_category['data_access'] += 1
            elif any(event in log.event_type.lower() for event in data_modification_events):
                events_by_category['data_modification'] += 1
            elif log.event_type in user_management_events:
                events_by_category['user_management'] += 1
            elif log.event_type in system_events:
                events_by_category['system_changes'] += 1
            elif log.event_type in security_events:
                events_by_category['security_events'] += 1
        
        # User activity analysis
        user_activities = {}
        for log in logs:
            if log.user_id:
                if log.user_id not in user_activities:
                    user_activities[log.user_id] = {'total': 0, 'high_risk': 0}
                user_activities[log.user_id]['total'] += 1
                if log.risk_level == 'high':
                    user_activities[log.user_id]['high_risk'] += 1
        
        # Data integrity checks
        data_modifications = [log for log in logs if any(event in log.event_type.lower() for event in data_modification_events)]
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days
            },
            'summary': {
                'total_events': total_events,
                'events_by_category': events_by_category,
                'unique_users': len(user_activities),
                'high_risk_events': len([log for log in logs if log.risk_level == 'high'])
            },
            'user_activity': user_activities,
            'data_integrity': {
                'total_modifications': len(data_modifications),
                'create_operations': len([log for log in data_modifications if 'create' in log.event_type.lower()]),
                'update_operations': len([log for log in data_modifications if 'update' in log.event_type.lower()]),
                'delete_operations': len([log for log in data_modifications if 'delete' in log.event_type.lower()])
            },
            'compliance_metrics': {
                'audit_coverage': round((total_events / max(1, (end_date - start_date).days)) * 100, 2),
                'security_incident_rate': round((events_by_category['security_events'] / max(1, total_events)) * 100, 2),
                'data_access_monitoring': events_by_category['data_access'] > 0,
                'user_activity_tracking': len(user_activities) > 0
            }
        }
    
    def detect_anomalous_activity(
        self,
        db: Session,
        user_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """Detect potentially anomalous user activity patterns"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user's recent activity
        recent_activities = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= start_date
            )
        ).all()
        
        # Get user's historical activity for baseline
        historical_start = start_date - timedelta(days=days * 4)  # 4x the analysis period
        historical_activities = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.timestamp >= historical_start,
                AuditLog.timestamp < start_date
            )
        ).all()
        
        anomalies = []
        
        # Activity volume anomaly
        recent_count = len(recent_activities)
        historical_avg = len(historical_activities) / max(1, (start_date - historical_start).days) * days
        
        if recent_count > historical_avg * 2:
            anomalies.append({
                'type': 'high_activity_volume',
                'description': f'Activity volume ({recent_count}) is {recent_count/max(1, historical_avg):.1f}x higher than usual',
                'severity': 'medium',
                'value': recent_count,
                'baseline': historical_avg
            })
        
        # Unusual time patterns
        recent_hours = [activity.timestamp.hour for activity in recent_activities]
        historical_hours = [activity.timestamp.hour for activity in historical_activities]
        
        if recent_hours and historical_hours:
            recent_unusual_hours = [h for h in recent_hours if h < 6 or h > 22]  # Outside business hours
            historical_unusual_hours = [h for h in historical_hours if h < 6 or h > 22]
            
            recent_unusual_ratio = len(recent_unusual_hours) / len(recent_hours)
            historical_unusual_ratio = len(historical_unusual_hours) / max(1, len(historical_hours))
            
            if recent_unusual_ratio > historical_unusual_ratio * 3:
                anomalies.append({
                    'type': 'unusual_time_pattern',
                    'description': f'High activity outside business hours ({recent_unusual_ratio:.1%} vs {historical_unusual_ratio:.1%} baseline)',
                    'severity': 'high',
                    'value': recent_unusual_ratio,
                    'baseline': historical_unusual_ratio
                })
        
        # New entity types accessed
        recent_entities = set(activity.entity_type for activity in recent_activities)
        historical_entities = set(activity.entity_type for activity in historical_activities)
        new_entities = recent_entities - historical_entities
        
        if new_entities:
            anomalies.append({
                'type': 'new_entity_access',
                'description': f'Accessing new entity types: {", ".join(new_entities)}',
                'severity': 'medium',
                'value': list(new_entities),
                'baseline': list(historical_entities)
            })
        
        # High-risk event frequency
        recent_high_risk = len([a for a in recent_activities if a.risk_level == 'high'])
        historical_high_risk = len([a for a in historical_activities if a.risk_level == 'high'])
        historical_high_risk_avg = historical_high_risk / max(1, (start_date - historical_start).days) * days
        
        if recent_high_risk > historical_high_risk_avg * 2 and recent_high_risk > 2:
            anomalies.append({
                'type': 'high_risk_activity_spike',
                'description': f'High-risk events ({recent_high_risk}) significantly above baseline ({historical_high_risk_avg:.1f})',
                'severity': 'high',
                'value': recent_high_risk,
                'baseline': historical_high_risk_avg
            })
        
        # Calculate overall risk score
        risk_score = 0
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                risk_score += 3
            elif anomaly['severity'] == 'medium':
                risk_score += 2
            else:
                risk_score += 1
        
        return {
            'user_id': user_id,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'activity_summary': {
                'recent_activities': recent_count,
                'historical_average': round(historical_avg, 1),
                'recent_high_risk_events': recent_high_risk
            },
            'anomalies': anomalies,
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score >= 6 else 'medium' if risk_score >= 3 else 'low',
            'requires_investigation': risk_score >= 6 or any(a['severity'] == 'high' for a in anomalies)
        }
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from audit log details"""
        
        if not isinstance(details, dict):
            return details
        
        sanitized = {}
        for key, value in details.items():
            key_lower = key.lower()
            
            # Check if field contains sensitive data
            if any(sensitive_field in key_lower for sensitive_field in self.sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_details(item) if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def export_audit_trail(
        self,
        db: Session,
        start_date: datetime,
        end_date: datetime,
        format: str = "json",
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Export audit trail data for external analysis or compliance"""
        
        query = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        )
        
        if entity_types:
            query = query.filter(AuditLog.entity_type.in_(entity_types))
        
        logs = query.order_by(AuditLog.timestamp).all()
        
        # Format export data
        export_data = []
        for log in logs:
            log_data = {
                'timestamp': log.timestamp.isoformat(),
                'event_type': log.event_type,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'user_id': log.user_id,
                'action': log.action,
                'description': log.description,
                'source': log.source,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'risk_level': log.risk_level
            }
            
            # Include sanitized details
            if log.details:
                try:
                    details = json.loads(log.details)
                    log_data['details'] = self._sanitize_details(details)
                except json.JSONDecodeError:
                    log_data['details'] = None
            
            export_data.append(log_data)
        
        # Generate export metadata
        metadata = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_records': len(export_data),
            'entity_types_included': entity_types or ['all'],
            'format': format,
            'checksum': hashlib.sha256(json.dumps(export_data, sort_keys=True).encode()).hexdigest()
        }
        
        return {
            'metadata': metadata,
            'data': export_data
        }

# Global audit service instance
audit_service = AuditService()