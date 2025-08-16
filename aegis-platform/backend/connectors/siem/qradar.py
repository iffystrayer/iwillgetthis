"""
IBM QRadar SIEM Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from ..base import SIEMConnector, ConnectorCapability, HealthStatus


class QRadarConnector(SIEMConnector):
    """IBM QRadar SIEM connector"""
    
    @property
    def vendor_name(self) -> str:
        return "IBM QRadar"
    
    @property
    def supported_capabilities(self) -> List[ConnectorCapability]:
        return [
            ConnectorCapability.READ_EVENTS,
            ConnectorCapability.READ_ALERTS,
            ConnectorCapability.HEALTH_CHECK
        ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('endpoint_url', '').rstrip('/')
        self.api_token = config.get('api_token')
        self.version = config.get('api_version', '11.0')  # QRadar API version
        
        # QRadar-specific configuration
        self.verify_ssl = config.get('verify_ssl', True)
        self.max_events = config.get('max_events', 10000)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for QRadar requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-QRadar-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Version': self.version
        }
        
        if self.api_token:
            headers['SEC'] = self.api_token
        
        return headers
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to QRadar"""
        try:
            if not self.api_token:
                return {
                    'success': False,
                    'message': 'API token required for QRadar authentication'
                }
            
            # Test system information endpoint
            system_url = f"{self.base_url}/api/system/about"
            
            async with self.session.get(system_url) as response:
                if response.status == 200:
                    system_info = await response.json()
                    return {
                        'success': True,
                        'message': 'Successfully connected to QRadar',
                        'details': {
                            'version': system_info.get('release_name', 'Unknown'),
                            'external_version': system_info.get('external_version'),
                            'api_version': self.version,
                            'server_url': self.base_url
                        }
                    }
                elif response.status == 401:
                    return {
                        'success': False,
                        'message': 'Authentication failed - invalid API token'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Connection test failed: HTTP {response.status}'
                    }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform detailed health check"""
        try:
            health_details = {}
            
            # Check system health
            try:
                system_url = f"{self.base_url}/api/system/about"
                async with self.session.get(system_url) as response:
                    if response.status == 200:
                        health_details['system_status'] = 'healthy'
                        system_info = await response.json()
                        health_details['version'] = system_info.get('release_name', 'Unknown')
                    else:
                        health_details['system_status'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['system_status'] = f'error: {str(e)}'
            
            # Check API capabilities
            try:
                capabilities_url = f"{self.base_url}/api/help/capabilities"
                async with self.session.get(capabilities_url) as response:
                    if response.status == 200:
                        health_details['api_capabilities'] = 'available'
                    else:
                        health_details['api_capabilities'] = 'limited'
            except Exception as e:
                health_details['api_capabilities'] = f'error: {str(e)}'
            
            # Test events access
            try:
                # Try to get a small number of recent events
                events_url = f"{self.base_url}/api/siem/events"
                params = {'limit': 1}
                async with self.session.get(events_url, params=params) as response:
                    if response.status == 200:
                        health_details['events_access'] = 'available'
                    else:
                        health_details['events_access'] = 'limited'
            except Exception as e:
                health_details['events_access'] = f'error: {str(e)}'
            
            # Determine overall health
            if all('error' not in str(status) for status in health_details.values()):
                overall_health = HealthStatus.HEALTHY
            else:
                overall_health = HealthStatus.ERROR
            
            return {
                'status': overall_health.value,
                'details': health_details,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'status': HealthStatus.ERROR.value,
                'details': {'error': str(e)},
                'timestamp': datetime.now().isoformat()
            }
    
    def _datetime_to_qradar_timestamp(self, dt: datetime) -> int:
        """Convert datetime to QRadar timestamp (milliseconds since epoch)"""
        return int(dt.timestamp() * 1000)
    
    async def get_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve security events from QRadar"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Convert times to QRadar format
            start_timestamp = self._datetime_to_qradar_timestamp(start_time)
            end_timestamp = self._datetime_to_qradar_timestamp(end_time)
            
            # Build query parameters
            params = {
                'filter': f'starttime >= {start_timestamp} and starttime <= {end_timestamp}',
                'limit': min(limit, self.max_events),
                'fields': 'qid,starttime,devicetime,sourceip,destinationip,username,eventdirection,eventcount,logsourcename,category,severity,credibility,relevance,protocolid,sourceport,destinationport'
            }
            
            if query:
                # Add custom filter to existing filter
                params['filter'] += f' and ({query})'
            
            events_url = f"{self.base_url}/api/siem/events"
            
            async with self.session.get(events_url, params=params) as response:
                if response.status == 200:
                    events_data = await response.json()
                    
                    # Process events
                    events = []
                    for event in events_data:
                        processed_event = {
                            'id': event.get('qid', ''),
                            'timestamp': datetime.fromtimestamp(event.get('starttime', 0) / 1000).isoformat(),
                            'device_time': datetime.fromtimestamp(event.get('devicetime', 0) / 1000).isoformat(),
                            'source_ip': event.get('sourceip'),
                            'destination_ip': event.get('destinationip'),
                            'username': event.get('username'),
                            'direction': event.get('eventdirection'),
                            'event_count': event.get('eventcount', 1),
                            'log_source': event.get('logsourcename'),
                            'category': event.get('category'),
                            'severity': event.get('severity'),
                            'credibility': event.get('credibility'),
                            'relevance': event.get('relevance'),
                            'protocol': event.get('protocolid'),
                            'source_port': event.get('sourceport'),
                            'destination_port': event.get('destinationport'),
                            'raw_data': event
                        }
                        events.append(processed_event)
                    
                    return {
                        'success': True,
                        'events': events,
                        'total_count': len(events),
                        'query_filter': params['filter'],
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        }
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'events': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving QRadar events: {e}")
            return {
                'success': False,
                'error': str(e),
                'events': []
            }
    
    async def get_alerts(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve security alerts/offenses from QRadar"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Convert times to QRadar format
            start_timestamp = self._datetime_to_qradar_timestamp(start_time)
            end_timestamp = self._datetime_to_qradar_timestamp(end_time)
            
            # Build query parameters for offenses (QRadar's alert equivalent)
            params = {
                'filter': f'start_time >= {start_timestamp} and start_time <= {end_timestamp}',
                'limit': min(limit, self.max_events),
                'fields': 'id,description,status,start_time,last_updated_time,offense_type,severity,magnitude,credibility,relevance,source_count,local_destination_count,remote_destination_count,categories,source_network,destination_networks'
            }
            
            # Add severity filter if specified
            if severity:
                severity_map = {
                    'low': '1,2,3',
                    'medium': '4,5,6',
                    'high': '7,8',
                    'critical': '9,10'
                }
                if severity.lower() in severity_map:
                    params['filter'] += f' and severity in ({severity_map[severity.lower()]})'
            
            offenses_url = f"{self.base_url}/api/siem/offenses"
            
            async with self.session.get(offenses_url, params=params) as response:
                if response.status == 200:
                    offenses_data = await response.json()
                    
                    # Process offenses as alerts
                    alerts = []
                    for offense in offenses_data:
                        # Map QRadar severity (1-10) to standard severity levels
                        qradar_severity = offense.get('severity', 5)
                        if qradar_severity <= 3:
                            severity_level = 'low'
                        elif qradar_severity <= 6:
                            severity_level = 'medium'
                        elif qradar_severity <= 8:
                            severity_level = 'high'
                        else:
                            severity_level = 'critical'
                        
                        processed_alert = {
                            'id': str(offense.get('id', '')),
                            'title': offense.get('description', 'QRadar Offense'),
                            'description': offense.get('description', ''),
                            'severity': severity_level,
                            'status': offense.get('status', 'OPEN'),
                            'timestamp': datetime.fromtimestamp(offense.get('start_time', 0) / 1000).isoformat(),
                            'last_updated': datetime.fromtimestamp(offense.get('last_updated_time', 0) / 1000).isoformat(),
                            'offense_type': offense.get('offense_type'),
                            'magnitude': offense.get('magnitude'),
                            'credibility': offense.get('credibility'),
                            'relevance': offense.get('relevance'),
                            'source_count': offense.get('source_count', 0),
                            'categories': offense.get('categories', []),
                            'source_network': offense.get('source_network'),
                            'destination_networks': offense.get('destination_networks', []),
                            'raw_data': offense
                        }
                        alerts.append(processed_alert)
                    
                    return {
                        'success': True,
                        'alerts': alerts,
                        'total_count': len(alerts),
                        'query_filter': params['filter'],
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        }
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'alerts': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving QRadar alerts: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }