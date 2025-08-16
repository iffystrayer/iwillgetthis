"""
MetricStream GRC Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import base64

from ..base import GRCConnector, ConnectorCapability, HealthStatus


class MetricStreamConnector(GRCConnector):
    """MetricStream GRC platform connector"""
    
    @property
    def vendor_name(self) -> str:
        return "MetricStream"
    
    @property
    def supported_capabilities(self) -> List[ConnectorCapability]:
        return [
            ConnectorCapability.READ_CONTROLS,
            ConnectorCapability.CREATE_TICKETS,
            ConnectorCapability.HEALTH_CHECK
        ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('endpoint_url', '').rstrip('/')
        self.username = config.get('username')
        self.password = config.get('password')
        self.api_key = config.get('api_key')
        
        # MetricStream specific configuration
        self.api_version = config.get('api_version', 'v1')
        self.tenant_id = config.get('tenant_id')
        
        # Module paths
        self.controls_path = config.get('controls_path', '/api/controls')
        self.assessments_path = config.get('assessments_path', '/api/assessments')
        self.issues_path = config.get('issues_path', '/api/issues')
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for MetricStream requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-MetricStream-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        elif self.username and self.password:
            credentials = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
        
        if self.tenant_id:
            headers['X-Tenant-ID'] = self.tenant_id
        
        return headers
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to MetricStream"""
        try:
            # Check authentication method
            if not self.api_key and not (self.username and self.password):
                return {
                    'success': False,
                    'message': 'API key or username/password required for MetricStream authentication'
                }
            
            # Test system health endpoint
            health_url = f"{self.base_url}/api/health"
            
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    health_data = await response.json()
                    
                    # Test API access with a simple query
                    test_url = f"{self.base_url}{self.controls_path}"
                    test_params = {'limit': '1'}
                    
                    async with self.session.get(test_url, params=test_params) as test_response:
                        if test_response.status == 200:
                            return {
                                'success': True,
                                'message': 'Successfully connected to MetricStream',
                                'details': {
                                    'api_version': self.api_version,
                                    'tenant_id': self.tenant_id,
                                    'server_url': self.base_url,
                                    'system_status': health_data.get('status', 'unknown')
                                }
                            }
                        elif test_response.status == 401:
                            return {
                                'success': False,
                                'message': 'Authentication failed - check API key or credentials'
                            }
                        elif test_response.status == 403:
                            return {
                                'success': False,
                                'message': 'Access denied - check permissions'
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'API access test failed: HTTP {test_response.status}'
                            }
                elif response.status == 404:
                    # Health endpoint might not exist, try direct API test
                    test_url = f"{self.base_url}{self.controls_path}"
                    test_params = {'limit': '1'}
                    
                    async with self.session.get(test_url, params=test_params) as test_response:
                        if test_response.status == 200:
                            return {
                                'success': True,
                                'message': 'Successfully connected to MetricStream',
                                'details': {
                                    'api_version': self.api_version,
                                    'tenant_id': self.tenant_id,
                                    'server_url': self.base_url
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'message': f'Connection test failed: HTTP {test_response.status}'
                            }
                else:
                    return {
                        'success': False,
                        'message': f'Health check failed: HTTP {response.status}'
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
            
            # Check API connectivity
            try:
                test_url = f"{self.base_url}{self.controls_path}"
                test_params = {'limit': '1'}
                
                async with self.session.get(test_url, params=test_params) as response:
                    if response.status == 200:
                        health_details['api_connectivity'] = 'available'
                        health_details['authentication'] = 'success'
                    elif response.status == 401:
                        health_details['api_connectivity'] = 'available'
                        health_details['authentication'] = 'failed'
                    else:
                        health_details['api_connectivity'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['api_connectivity'] = f'error: {str(e)}'
            
            # Check controls module access
            try:
                controls_url = f"{self.base_url}{self.controls_path}"
                params = {'limit': '1'}
                
                async with self.session.get(controls_url, params=params) as response:
                    if response.status == 200:
                        health_details['controls_module'] = 'accessible'
                    else:
                        health_details['controls_module'] = 'limited_access'
            except Exception as e:
                health_details['controls_module'] = f'error: {str(e)}'
            
            # Check assessments module access
            try:
                assessments_url = f"{self.base_url}{self.assessments_path}"
                params = {'limit': '1'}
                
                async with self.session.get(assessments_url, params=params) as response:
                    if response.status == 200:
                        health_details['assessments_module'] = 'accessible'
                    else:
                        health_details['assessments_module'] = 'limited_access'
            except Exception as e:
                health_details['assessments_module'] = f'error: {str(e)}'
            
            # Determine overall health
            if (health_details.get('api_connectivity') == 'available' and 
                health_details.get('authentication') == 'success'):
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
    
    async def get_controls(
        self,
        framework: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve compliance controls from MetricStream"""
        try:
            controls_url = f"{self.base_url}{self.controls_path}"
            
            # Build query parameters
            params = {
                'limit': str(limit),
                'offset': '0'
            }
            
            # Add filters
            filters = []
            if framework:
                filters.append(f'framework={framework}')
            if status:
                filters.append(f'status={status}')
            
            if filters:
                params['filter'] = '&'.join(filters)
            
            async with self.session.get(controls_url, params=params) as response:
                if response.status == 200:
                    controls_data = await response.json()
                    
                    # Process controls - adapt to MetricStream response format
                    controls = []
                    data_list = controls_data.get('data', controls_data.get('controls', []))
                    
                    for control in data_list:
                        processed_control = {
                            'id': control.get('id') or control.get('controlId'),
                            'control_id': control.get('controlNumber') or control.get('reference'),
                            'name': control.get('name') or control.get('title'),
                            'description': control.get('description'),
                            'framework': control.get('framework') or control.get('standard'),
                            'control_type': control.get('type') or control.get('controlType'),
                            'frequency': control.get('testingFrequency') or control.get('frequency'),
                            'status': control.get('status'),
                            'owner': control.get('owner') or control.get('responsible'),
                            'last_assessment_date': control.get('lastAssessmentDate'),
                            'next_assessment_date': control.get('nextAssessmentDate'),
                            'effectiveness': control.get('effectiveness') or control.get('rating'),
                            'risk_rating': control.get('riskRating') or control.get('risk'),
                            'raw_data': control
                        }
                        controls.append(processed_control)
                    
                    total_count = controls_data.get('totalCount', len(controls))
                    
                    return {
                        'success': True,
                        'controls': controls,
                        'total_count': total_count,
                        'returned_count': len(controls),
                        'filters': params.get('filter', 'none')
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'controls': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving MetricStream controls: {e}")
            return {
                'success': False,
                'error': str(e),
                'controls': []
            }
    
    async def get_assessments(
        self,
        control_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve assessment results from MetricStream"""
        try:
            assessments_url = f"{self.base_url}{self.assessments_path}"
            
            # Build query parameters
            params = {
                'limit': str(limit),
                'offset': '0'
            }
            
            # Add filters
            filters = []
            if control_id:
                filters.append(f'controlId={control_id}')
            if start_date:
                filters.append(f'assessmentDate>={start_date.strftime("%Y-%m-%d")}')
            if end_date:
                filters.append(f'assessmentDate<={end_date.strftime("%Y-%m-%d")}')
            
            if filters:
                params['filter'] = '&'.join(filters)
            
            async with self.session.get(assessments_url, params=params) as response:
                if response.status == 200:
                    assessments_data = await response.json()
                    
                    # Process assessments
                    assessments = []
                    data_list = assessments_data.get('data', assessments_data.get('assessments', []))
                    
                    for assessment in data_list:
                        processed_assessment = {
                            'id': assessment.get('id') or assessment.get('assessmentId'),
                            'assessment_id': assessment.get('assessmentNumber') or assessment.get('reference'),
                            'control_id': assessment.get('controlId') or assessment.get('relatedControl'),
                            'assessment_date': assessment.get('assessmentDate') or assessment.get('date'),
                            'assessor': assessment.get('assessor') or assessment.get('performer'),
                            'result': assessment.get('result') or assessment.get('outcome'),
                            'score': assessment.get('score') or assessment.get('rating'),
                            'findings': assessment.get('findings') or assessment.get('observations'),
                            'recommendations': assessment.get('recommendations') or assessment.get('actions'),
                            'evidence': assessment.get('evidence') or assessment.get('documentation'),
                            'status': assessment.get('status'),
                            'raw_data': assessment
                        }
                        assessments.append(processed_assessment)
                    
                    total_count = assessments_data.get('totalCount', len(assessments))
                    
                    return {
                        'success': True,
                        'assessments': assessments,
                        'total_count': total_count,
                        'returned_count': len(assessments),
                        'filters': params.get('filter', 'none')
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'assessments': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving MetricStream assessments: {e}")
            return {
                'success': False,
                'error': str(e),
                'assessments': []
            }
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ticket/issue in MetricStream"""
        try:
            issues_url = f"{self.base_url}{self.issues_path}"
            
            # Map Aegis ticket data to MetricStream format
            metricstream_data = {
                'title': ticket_data.get('title', ticket_data.get('summary', 'Aegis Platform Issue')),
                'description': ticket_data.get('description', ''),
                'priority': ticket_data.get('priority', 'Medium').title(),
                'severity': ticket_data.get('severity', 'Medium').title(),
                'status': 'New',
                'category': ticket_data.get('category', 'Security'),
                'subcategory': ticket_data.get('subcategory', 'Risk Management'),
                'assignee': ticket_data.get('assigned_to'),
                'requester': ticket_data.get('requester'),
                'dueDate': ticket_data.get('due_date'),
                'tags': ticket_data.get('tags', [])
            }
            
            # Remove None values
            metricstream_data = {k: v for k, v in metricstream_data.items() if v is not None}
            
            async with self.session.post(issues_url, json=metricstream_data) as response:
                if response.status in [200, 201]:
                    result_data = await response.json()
                    
                    # Extract issue information
                    issue_data = result_data.get('data', result_data)
                    issue_id = issue_data.get('id') or issue_data.get('issueId')
                    issue_number = issue_data.get('number') or issue_data.get('reference')
                    
                    return {
                        'success': True,
                        'ticket_id': issue_id,
                        'ticket_number': issue_number,
                        'url': f"{self.base_url}/issues/{issue_id}",
                        'details': issue_data
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ticket creation failed: HTTP {response.status} - {error_text}'
                    }
        
        except Exception as e:
            self.logger.error(f"Error creating MetricStream ticket: {e}")
            return {
                'success': False,
                'error': str(e)
            }