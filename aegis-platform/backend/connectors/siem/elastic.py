"""
Elastic Stack (ELK) SIEM Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import base64

from ..base import SIEMConnector, ConnectorCapability, HealthStatus


class ElasticConnector(SIEMConnector):
    """Elastic Stack (ELK) SIEM connector"""
    
    @property
    def vendor_name(self) -> str:
        return "Elastic Stack"
    
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
        self.api_key = config.get('api_key')
        
        # Elasticsearch configuration
        self.default_index = config.get('default_index', 'logs-*')
        self.security_index = config.get('security_index', 'winlogbeat-*,filebeat-*,auditbeat-*')
        self.alerts_index = config.get('alerts_index', '.alerts-*')
        self.verify_ssl = config.get('verify_ssl', True)
        self.max_results = config.get('max_results', 10000)
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for Elasticsearch requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-Elastic-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add authentication
        if self.api_key:
            headers['Authorization'] = f'ApiKey {self.api_key}'
        elif self.username and self.password:
            credentials = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
        
        return headers
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Elasticsearch"""
        try:
            # Test cluster health endpoint
            health_url = f"{self.base_url}/_cluster/health"
            
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    # Test authentication by getting cluster info
                    info_url = f"{self.base_url}/"
                    async with self.session.get(info_url) as info_response:
                        if info_response.status == 200:
                            cluster_info = await info_response.json()
                            return {
                                'success': True,
                                'message': 'Successfully connected to Elasticsearch',
                                'details': {
                                    'cluster_name': cluster_info.get('cluster_name'),
                                    'version': cluster_info.get('version', {}).get('number'),
                                    'cluster_status': health_data.get('status'),
                                    'number_of_nodes': health_data.get('number_of_nodes'),
                                    'server_url': self.base_url
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'Authentication failed: HTTP {info_response.status}'
                            }
                elif response.status == 401:
                    return {
                        'success': False,
                        'message': 'Authentication failed - check credentials'
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
            
            # Check cluster health
            try:
                health_url = f"{self.base_url}/_cluster/health"
                async with self.session.get(health_url) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        health_details['cluster_status'] = health_data.get('status', 'unknown')
                        health_details['nodes'] = health_data.get('number_of_nodes', 0)
                    else:
                        health_details['cluster_status'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['cluster_status'] = f'error: {str(e)}'
            
            # Check index accessibility
            try:
                indices_url = f"{self.base_url}/_cat/indices/{self.security_index}?format=json"
                async with self.session.get(indices_url) as response:
                    if response.status == 200:
                        indices_data = await response.json()
                        health_details['security_indices'] = f'{len(indices_data)} indices available'
                    else:
                        health_details['security_indices'] = 'limited access'
            except Exception as e:
                health_details['security_indices'] = f'error: {str(e)}'
            
            # Test search capability
            try:
                search_result = await self._test_search()
                health_details['search_capability'] = 'available' if search_result else 'limited'
            except Exception as e:
                health_details['search_capability'] = f'error: {str(e)}'
            
            # Determine overall health
            cluster_status = health_details.get('cluster_status', 'error')
            if cluster_status in ['green', 'yellow'] and 'error' not in str(health_details.get('search_capability', '')):
                overall_health = HealthStatus.HEALTHY
            elif cluster_status == 'yellow':
                overall_health = HealthStatus.WARNING
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
            search_query = {
                "size": 1,
                "query": {"match_all": {}}
            }
            
            search_url = f"{self.base_url}/{self.default_index}/_search"
            async with self.session.post(search_url, json=search_query) as response:
                return response.status == 200
        except Exception:
            return False
    
    def _build_time_range_query(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Build Elasticsearch time range query"""
        return {
            "range": {
                "@timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat()
                }
            }
        }
    
    async def get_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve security events from Elasticsearch"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Build Elasticsearch query
            es_query = {
                "size": min(limit, self.max_results),
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": {
                    "bool": {
                        "must": [
                            self._build_time_range_query(start_time, end_time)
                        ]
                    }
                }
            }
            
            # Add custom query if provided
            if query:
                try:
                    # Try to parse as JSON for complex queries
                    custom_query = json.loads(query)
                    es_query["query"]["bool"]["must"].append(custom_query)
                except json.JSONDecodeError:
                    # Treat as simple query string
                    es_query["query"]["bool"]["must"].append({
                        "query_string": {"query": query}
                    })
            else:
                # Default security event filters
                es_query["query"]["bool"]["should"] = [
                    {"match": {"event.category": "security"}},
                    {"match": {"event.type": "authentication"}},
                    {"match": {"event.type": "access"}},
                    {"match": {"winlog.channel": "Security"}},
                    {"exists": {"field": "user.name"}},
                    {"exists": {"field": "source.ip"}}
                ]
                es_query["query"]["bool"]["minimum_should_match"] = 1
            
            # Execute search
            search_url = f"{self.base_url}/{self.security_index}/_search"
            
            async with self.session.post(search_url, json=es_query) as response:
                if response.status == 200:
                    search_result = await response.json()
                    
                    # Process events
                    events = []
                    for hit in search_result.get('hits', {}).get('hits', []):
                        source = hit['_source']
                        
                        processed_event = {
                            'id': hit['_id'],
                            'index': hit['_index'],
                            'timestamp': source.get('@timestamp'),
                            'event_category': source.get('event', {}).get('category'),
                            'event_type': source.get('event', {}).get('type'),
                            'event_action': source.get('event', {}).get('action'),
                            'host_name': source.get('host', {}).get('name'),
                            'user_name': source.get('user', {}).get('name'),
                            'source_ip': source.get('source', {}).get('ip'),
                            'destination_ip': source.get('destination', {}).get('ip'),
                            'process_name': source.get('process', {}).get('name'),
                            'file_path': source.get('file', {}).get('path'),
                            'winlog_channel': source.get('winlog', {}).get('channel'),
                            'winlog_event_id': source.get('winlog', {}).get('event_id'),
                            'message': source.get('message'),
                            'raw_data': source
                        }
                        events.append(processed_event)
                    
                    total_hits = search_result.get('hits', {}).get('total', {})
                    if isinstance(total_hits, dict):
                        total_count = total_hits.get('value', 0)
                    else:
                        total_count = total_hits
                    
                    return {
                        'success': True,
                        'events': events,
                        'total_count': total_count,
                        'returned_count': len(events),
                        'query': es_query,
                        'time_range': {
                            'start': start_time.isoformat(),
                            'end': end_time.isoformat()
                        }
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Search failed: HTTP {response.status} - {error_text}',
                        'events': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Elasticsearch events: {e}")
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
        """Retrieve security alerts from Elasticsearch"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Build Elasticsearch query for alerts
            es_query = {
                "size": min(limit, self.max_results),
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": {
                    "bool": {
                        "must": [
                            self._build_time_range_query(start_time, end_time)
                        ],
                        "should": [
                            {"match": {"event.category": "malware"}},
                            {"match": {"event.category": "intrusion_detection"}},
                            {"match": {"event.type": "alert"}},
                            {"match": {"rule.name": "*"}},
                            {"exists": {"field": "signal"}},
                            {"match": {"kibana.alert.rule.name": "*"}}
                        ],
                        "minimum_should_match": 1
                    }
                }
            }
            
            # Add severity filter
            if severity:
                severity_filter = {"match": {"event.severity": severity.lower()}}
                es_query["query"]["bool"]["must"].append(severity_filter)
            
            # Try alerts index first, then fallback to general security index
            indices_to_try = [self.alerts_index, self.security_index]
            
            for index in indices_to_try:
                try:
                    search_url = f"{self.base_url}/{index}/_search"
                    
                    async with self.session.post(search_url, json=es_query) as response:
                        if response.status == 200:
                            search_result = await response.json()
                            
                            # Process alerts
                            alerts = []
                            for hit in search_result.get('hits', {}).get('hits', []):
                                source = hit['_source']
                                
                                # Extract alert information from various possible fields
                                alert_title = (source.get('kibana', {}).get('alert', {}).get('rule', {}).get('name') or
                                             source.get('rule', {}).get('name') or
                                             source.get('signal', {}).get('rule', {}).get('name') or
                                             source.get('event', {}).get('action') or
                                             'Elasticsearch Alert')
                                
                                alert_severity = (source.get('kibana', {}).get('alert', {}).get('severity') or
                                                source.get('event', {}).get('severity') or
                                                source.get('signal', {}).get('rule', {}).get('severity') or
                                                'medium')
                                
                                processed_alert = {
                                    'id': hit['_id'],
                                    'index': hit['_index'],
                                    'title': alert_title,
                                    'description': source.get('message', source.get('event', {}).get('reason', '')),
                                    'severity': str(alert_severity).lower(),
                                    'timestamp': source.get('@timestamp'),
                                    'rule_name': source.get('rule', {}).get('name'),
                                    'rule_id': source.get('rule', {}).get('id'),
                                    'host_name': source.get('host', {}).get('name'),
                                    'user_name': source.get('user', {}).get('name'),
                                    'source_ip': source.get('source', {}).get('ip'),
                                    'destination_ip': source.get('destination', {}).get('ip'),
                                    'event_category': source.get('event', {}).get('category'),
                                    'event_type': source.get('event', {}).get('type'),
                                    'status': 'new',  # Default status
                                    'raw_data': source
                                }
                                alerts.append(processed_alert)
                            
                            total_hits = search_result.get('hits', {}).get('total', {})
                            if isinstance(total_hits, dict):
                                total_count = total_hits.get('value', 0)
                            else:
                                total_count = total_hits
                            
                            return {
                                'success': True,
                                'alerts': alerts,
                                'total_count': total_count,
                                'returned_count': len(alerts),
                                'index_used': index,
                                'query': es_query,
                                'time_range': {
                                    'start': start_time.isoformat(),
                                    'end': end_time.isoformat()
                                }
                            }
                        
                except Exception as e:
                    # Try next index
                    continue
            
            # If all indices failed
            return {
                'success': False,
                'error': 'Failed to retrieve alerts from all available indices',
                'alerts': []
            }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Elasticsearch alerts: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }