"""
Splunk SIEM Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from ..base import SIEMConnector, ConnectorCapability, HealthStatus


class SplunkConnector(SIEMConnector):
    """Splunk Enterprise/Cloud connector"""
    
    @property
    def vendor_name(self) -> str:
        return "Splunk"
    
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
        self.username = config.get('username')
        self.password = config.get('password')
        self.token = config.get('api_token')
        self.app = config.get('app', 'search')
        self.owner = config.get('owner', 'admin')
        
        # Splunk-specific configuration
        self.search_timeout = config.get('search_timeout', 300)  # 5 minutes
        self.max_results = config.get('max_results', 10000)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for Splunk requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-Splunk-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        return headers
    
    async def _authenticate(self) -> str:
        """Authenticate with Splunk and get session key"""
        if self.token:
            return self.token
        
        if not self.username or not self.password:
            raise Exception("Username/password or token required for Splunk authentication")
        
        auth_url = f"{self.base_url}/services/auth/login"
        auth_data = {
            'username': self.username,
            'password': self.password,
            'output_mode': 'json'
        }
        
        try:
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    result = await response.json()
                    session_key = result.get('sessionKey')
                    if session_key:
                        return session_key
                    else:
                        raise Exception("No session key in authentication response")
                else:
                    raise Exception(f"Authentication failed: HTTP {response.status}")
        except Exception as e:
            self.logger.error(f"Splunk authentication error: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Splunk"""
        try:
            # Test authentication
            session_key = await self._authenticate()
            
            # Test server info endpoint
            info_url = f"{self.base_url}/services/server/info"
            headers = {'Authorization': f'Splunk {session_key}'}
            
            async with self.session.get(info_url, headers=headers) as response:
                if response.status == 200:
                    info_data = await response.text()
                    # Parse XML response for server info
                    try:
                        root = ET.fromstring(info_data)
                        version = "Unknown"
                        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                            for content in entry.findall('.//{http://www.w3.org/2005/Atom}content'):
                                for key in content.findall('.//s:key[@name="version"]', {'s': 'http://dev.splunk.com/ns/rest'}):
                                    version = key.text
                                    break
                        
                        return {
                            'success': True,
                            'message': 'Successfully connected to Splunk',
                            'details': {
                                'version': version,
                                'server_url': self.base_url,
                                'app': self.app
                            }
                        }
                    except ET.ParseError:
                        return {
                            'success': True,
                            'message': 'Connected to Splunk (version info unavailable)',
                            'details': {'server_url': self.base_url}
                        }
                else:
                    return {
                        'success': False,
                        'message': f'Server info request failed: HTTP {response.status}'
                    }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform detailed health check"""
        try:
            session_key = await self._authenticate()
            health_details = {'authentication': 'success'}
            
            # Check server status
            try:
                status_url = f"{self.base_url}/services/server/status"
                headers = {'Authorization': f'Splunk {session_key}'}
                
                async with self.session.get(status_url, headers=headers) as response:
                    if response.status == 200:
                        health_details['server_status'] = 'healthy'
                    else:
                        health_details['server_status'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['server_status'] = f'error: {str(e)}'
            
            # Test basic search capability
            try:
                search_result = await self._test_search()
                health_details['search_capability'] = 'available' if search_result else 'limited'
            except Exception as e:
                health_details['search_capability'] = f'error: {str(e)}'
            
            # Determine overall health
            if all(status != 'error' for status in health_details.values() if isinstance(status, str)):
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
    
    async def _test_search(self) -> bool:
        """Test basic search functionality"""
        try:
            # Simple search to test capability
            search_query = "| head 1"
            result = await self._execute_search(search_query, max_results=1)
            return len(result.get('events', [])) >= 0
        except Exception:
            return False
    
    async def _execute_search(
        self,
        search_query: str,
        earliest_time: Optional[str] = None,
        latest_time: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a Splunk search"""
        session_key = await self._authenticate()
        
        # Create search job
        search_url = f"{self.base_url}/services/search/jobs"
        headers = {'Authorization': f'Splunk {session_key}'}
        
        search_data = {
            'search': search_query,
            'output_mode': 'json',
            'exec_mode': 'blocking',  # Wait for search to complete
            'max_count': max_results or self.max_results
        }
        
        if earliest_time:
            search_data['earliest_time'] = earliest_time
        if latest_time:
            search_data['latest_time'] = latest_time
        
        # Execute search
        async with self.session.post(search_url, headers=headers, data=search_data) as response:
            if response.status != 201:
                raise Exception(f"Search creation failed: HTTP {response.status}")
            
            search_result = await response.json()
            job_id = search_result.get('sid')
            
            if not job_id:
                raise Exception("No search job ID returned")
        
        # Get search results
        results_url = f"{self.base_url}/services/search/jobs/{job_id}/results"
        results_params = {'output_mode': 'json', 'count': max_results or self.max_results}
        
        async with self.session.get(results_url, headers=headers, params=results_params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Results retrieval failed: HTTP {response.status}")
    
    async def get_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve security events from Splunk"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Format times for Splunk
            earliest_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            latest_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Build search query
            if query:
                search_query = f"search {query}"
            else:
                # Default search for security events
                search_query = 'search index=main OR index=security sourcetype=*security* OR sourcetype=*alert*'
            
            # Add time range
            search_query += f" earliest={earliest_time} latest={latest_time}"
            
            # Execute search
            result = await self._execute_search(
                search_query,
                earliest_time=earliest_time,
                latest_time=latest_time,
                max_results=limit
            )
            
            # Process results
            events = []
            for event in result.get('results', []):
                processed_event = {
                    'id': event.get('_raw', '')[:50],  # Use truncated raw as ID
                    'timestamp': event.get('_time'),
                    'source': event.get('source'),
                    'sourcetype': event.get('sourcetype'),
                    'host': event.get('host'),
                    'index': event.get('index'),
                    'raw_data': event.get('_raw'),
                    'fields': {k: v for k, v in event.items() if not k.startswith('_')}
                }
                events.append(processed_event)
            
            return {
                'success': True,
                'events': events,
                'total_count': len(events),
                'query': search_query,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Splunk events: {e}")
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
        """Retrieve security alerts from Splunk"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Format times for Splunk
            earliest_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            latest_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            # Build search query for alerts
            search_query = 'search index=main OR index=security sourcetype=*alert* OR tag=alert'
            
            if severity:
                search_query += f' severity={severity}'
            
            # Execute search
            result = await self._execute_search(
                search_query,
                earliest_time=earliest_time,
                latest_time=latest_time,
                max_results=limit
            )
            
            # Process alerts
            alerts = []
            for alert in result.get('results', []):
                processed_alert = {
                    'id': alert.get('alert_id', alert.get('_raw', '')[:50]),
                    'title': alert.get('alert_name', alert.get('title', 'Unknown Alert')),
                    'description': alert.get('description', alert.get('_raw')),
                    'severity': alert.get('severity', alert.get('priority', 'medium')),
                    'timestamp': alert.get('_time'),
                    'source': alert.get('source'),
                    'host': alert.get('host'),
                    'status': alert.get('status', 'new'),
                    'raw_data': alert
                }
                alerts.append(processed_alert)
            
            return {
                'success': True,
                'alerts': alerts,
                'total_count': len(alerts),
                'query': search_query,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Splunk alerts: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }