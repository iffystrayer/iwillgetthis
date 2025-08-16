"""
ServiceNow GRC Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import base64

from ..base import GRCConnector, ConnectorCapability, HealthStatus


class ServiceNowConnector(GRCConnector):
    """ServiceNow GRC platform connector"""
    
    @property
    def vendor_name(self) -> str:
        return "ServiceNow"
    
    @property
    def supported_capabilities(self) -> List[ConnectorCapability]:
        return [
            ConnectorCapability.READ_CONTROLS,
            ConnectorCapability.CREATE_TICKETS,
            ConnectorCapability.UPDATE_TICKETS,
            ConnectorCapability.HEALTH_CHECK
        ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.instance_url = config.get('endpoint_url', '').rstrip('/')
        self.username = config.get('username')
        self.password = config.get('password')
        
        # ServiceNow specific configuration
        self.api_version = config.get('api_version', 'v1')
        self.table_prefix = config.get('table_prefix', 'x_aegis_')
        
        # Table names for different GRC objects
        self.controls_table = config.get('controls_table', 'grc_control')
        self.assessments_table = config.get('assessments_table', 'grc_assessment')
        self.incidents_table = config.get('incidents_table', 'incident')
        self.tasks_table = config.get('tasks_table', 'task')
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for ServiceNow requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-ServiceNow-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.username and self.password:
            credentials = base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()
            headers['Authorization'] = f'Basic {credentials}'
        
        return headers
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to ServiceNow"""
        try:
            if not self.username or not self.password:
                return {
                    'success': False,
                    'message': 'Username and password required for ServiceNow authentication'
                }
            
            # Test system properties endpoint to verify connection and auth
            system_url = f"{self.instance_url}/api/now/table/sys_properties"
            params = {
                'sysparm_query': 'name=glide.product.description',
                'sysparm_limit': '1'
            }
            
            async with self.session.get(system_url, params=params) as response:
                if response.status == 200:
                    system_data = await response.json()
                    
                    # Get instance information
                    info_url = f"{self.instance_url}/api/now/table/sys_properties"
                    info_params = {
                        'sysparm_query': 'name=glide.buildnumber^ORname=glide.war',
                        'sysparm_limit': '10'
                    }
                    
                    async with self.session.get(info_url, params=info_params) as info_response:
                        if info_response.status == 200:
                            info_data = await info_response.json()
                            build_info = {}
                            for prop in info_data.get('result', []):
                                build_info[prop.get('name', '')] = prop.get('value', '')
                            
                            return {
                                'success': True,
                                'message': 'Successfully connected to ServiceNow',
                                'details': {
                                    'instance_url': self.instance_url,
                                    'build_number': build_info.get('glide.buildnumber', 'Unknown'),
                                    'version': build_info.get('glide.war', 'Unknown'),
                                    'api_version': self.api_version
                                }
                            }
                        else:
                            return {
                                'success': True,
                                'message': 'Connected to ServiceNow (version info unavailable)'
                            }
                elif response.status == 401:
                    return {
                        'success': False,
                        'message': 'Authentication failed - check username and password'
                    }
                elif response.status == 403:
                    return {
                        'success': False,
                        'message': 'Access denied - check user permissions'
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
            
            # Check authentication and system access
            try:
                system_url = f"{self.instance_url}/api/now/table/sys_properties"
                params = {'sysparm_limit': '1'}
                
                async with self.session.get(system_url, params=params) as response:
                    if response.status == 200:
                        health_details['authentication'] = 'success'
                        health_details['api_access'] = 'available'
                    else:
                        health_details['authentication'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['authentication'] = f'error: {str(e)}'
            
            # Check GRC table access
            try:
                controls_url = f"{self.instance_url}/api/now/table/{self.controls_table}"
                params = {'sysparm_limit': '1'}
                
                async with self.session.get(controls_url, params=params) as response:
                    if response.status == 200:
                        health_details['grc_controls'] = 'accessible'
                    elif response.status == 404:
                        health_details['grc_controls'] = 'table_not_found'
                    else:
                        health_details['grc_controls'] = 'limited_access'
            except Exception as e:
                health_details['grc_controls'] = f'error: {str(e)}'
            
            # Check incident table access
            try:
                incidents_url = f"{self.instance_url}/api/now/table/{self.incidents_table}"
                params = {'sysparm_limit': '1'}
                
                async with self.session.get(incidents_url, params=params) as response:
                    if response.status == 200:
                        health_details['incident_management'] = 'accessible'
                    else:
                        health_details['incident_management'] = 'limited_access'
            except Exception as e:
                health_details['incident_management'] = f'error: {str(e)}'
            
            # Determine overall health
            if health_details.get('authentication') == 'success' and health_details.get('api_access') == 'available':
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
        """Retrieve compliance controls from ServiceNow"""
        try:
            # Build query parameters
            query_parts = []
            
            if framework:
                query_parts.append(f'framework={framework}')
            
            if status:
                query_parts.append(f'state={status}')
            
            params = {
                'sysparm_limit': str(limit),
                'sysparm_fields': 'sys_id,number,short_description,description,framework,control_type,frequency,state,owner,last_assessment_date,next_assessment_date,effectiveness,risk_rating'
            }
            
            if query_parts:
                params['sysparm_query'] = '^'.join(query_parts)
            
            controls_url = f"{self.instance_url}/api/now/table/{self.controls_table}"
            
            async with self.session.get(controls_url, params=params) as response:
                if response.status == 200:
                    controls_data = await response.json()
                    
                    # Process controls
                    controls = []
                    for control in controls_data.get('result', []):
                        processed_control = {
                            'id': control.get('sys_id'),
                            'control_id': control.get('number'),
                            'name': control.get('short_description'),
                            'description': control.get('description'),
                            'framework': control.get('framework'),
                            'control_type': control.get('control_type'),
                            'frequency': control.get('frequency'),
                            'status': control.get('state'),
                            'owner': control.get('owner'),
                            'last_assessment_date': control.get('last_assessment_date'),
                            'next_assessment_date': control.get('next_assessment_date'),
                            'effectiveness': control.get('effectiveness'),
                            'risk_rating': control.get('risk_rating'),
                            'raw_data': control
                        }
                        controls.append(processed_control)
                    
                    return {
                        'success': True,
                        'controls': controls,
                        'total_count': len(controls),
                        'table_used': self.controls_table,
                        'query': params.get('sysparm_query', 'all')
                    }
                elif response.status == 404:
                    return {
                        'success': False,
                        'error': f'Controls table {self.controls_table} not found',
                        'controls': []
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'controls': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving ServiceNow controls: {e}")
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
        """Retrieve assessment results from ServiceNow"""
        try:
            # Build query parameters
            query_parts = []
            
            if control_id:
                query_parts.append(f'control={control_id}')
            
            if start_date:
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
                query_parts.append(f'assessment_date>={start_str}')
            
            if end_date:
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
                query_parts.append(f'assessment_date<={end_str}')
            
            params = {
                'sysparm_limit': str(limit),
                'sysparm_fields': 'sys_id,number,control,assessment_date,assessor,result,score,findings,recommendations,evidence,status'
            }
            
            if query_parts:
                params['sysparm_query'] = '^'.join(query_parts)
            
            assessments_url = f"{self.instance_url}/api/now/table/{self.assessments_table}"
            
            async with self.session.get(assessments_url, params=params) as response:
                if response.status == 200:
                    assessments_data = await response.json()
                    
                    # Process assessments
                    assessments = []
                    for assessment in assessments_data.get('result', []):
                        processed_assessment = {
                            'id': assessment.get('sys_id'),
                            'assessment_id': assessment.get('number'),
                            'control_id': assessment.get('control'),
                            'assessment_date': assessment.get('assessment_date'),
                            'assessor': assessment.get('assessor'),
                            'result': assessment.get('result'),
                            'score': assessment.get('score'),
                            'findings': assessment.get('findings'),
                            'recommendations': assessment.get('recommendations'),
                            'evidence': assessment.get('evidence'),
                            'status': assessment.get('status'),
                            'raw_data': assessment
                        }
                        assessments.append(processed_assessment)
                    
                    return {
                        'success': True,
                        'assessments': assessments,
                        'total_count': len(assessments),
                        'table_used': self.assessments_table,
                        'query': params.get('sysparm_query', 'all')
                    }
                elif response.status == 404:
                    return {
                        'success': False,
                        'error': f'Assessments table {self.assessments_table} not found',
                        'assessments': []
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'assessments': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving ServiceNow assessments: {e}")
            return {
                'success': False,
                'error': str(e),
                'assessments': []
            }
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ticket/task in ServiceNow"""
        try:
            # Determine table based on ticket type
            ticket_type = ticket_data.get('type', 'task').lower()
            
            if ticket_type in ['incident', 'security_incident']:
                table_name = self.incidents_table
            else:
                table_name = self.tasks_table
            
            # Map Aegis ticket data to ServiceNow fields
            snow_data = {
                'short_description': ticket_data.get('title', ticket_data.get('summary', 'Aegis Platform Ticket')),
                'description': ticket_data.get('description', ''),
                'priority': self._map_priority(ticket_data.get('priority', 'medium')),
                'urgency': self._map_urgency(ticket_data.get('urgency', 'medium')),
                'state': '1',  # New
                'caller_id': ticket_data.get('requester'),
                'assigned_to': ticket_data.get('assigned_to'),
                'category': ticket_data.get('category', 'Security'),
                'subcategory': ticket_data.get('subcategory', 'Risk Management')
            }
            
            # Add incident-specific fields if applicable
            if ticket_type in ['incident', 'security_incident']:
                snow_data.update({
                    'impact': self._map_impact(ticket_data.get('impact', 'medium')),
                    'severity': self._map_severity(ticket_data.get('severity', 'medium')),
                    'incident_state': '1'  # New
                })
            
            # Remove None values
            snow_data = {k: v for k, v in snow_data.items() if v is not None}
            
            create_url = f"{self.instance_url}/api/now/table/{table_name}"
            
            async with self.session.post(create_url, json=snow_data) as response:
                if response.status == 201:
                    result_data = await response.json()
                    created_ticket = result_data.get('result', {})
                    
                    return {
                        'success': True,
                        'ticket_id': created_ticket.get('sys_id'),
                        'ticket_number': created_ticket.get('number'),
                        'table': table_name,
                        'url': f"{self.instance_url}/{table_name}.do?sys_id={created_ticket.get('sys_id')}",
                        'details': created_ticket
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ticket creation failed: HTTP {response.status} - {error_text}'
                    }
        
        except Exception as e:
            self.logger.error(f"Error creating ServiceNow ticket: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _map_priority(self, aegis_priority: str) -> str:
        """Map Aegis priority to ServiceNow priority"""
        priority_map = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        return priority_map.get(aegis_priority.lower(), '3')
    
    def _map_urgency(self, aegis_urgency: str) -> str:
        """Map Aegis urgency to ServiceNow urgency"""
        urgency_map = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        return urgency_map.get(aegis_urgency.lower(), '3')
    
    def _map_impact(self, aegis_impact: str) -> str:
        """Map Aegis impact to ServiceNow impact"""
        impact_map = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        return impact_map.get(aegis_impact.lower(), '3')
    
    def _map_severity(self, aegis_severity: str) -> str:
        """Map Aegis severity to ServiceNow severity"""
        severity_map = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        return severity_map.get(aegis_severity.lower(), '3')
    
    async def update_control_status(
        self,
        control_id: str,
        status: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update control status in ServiceNow"""
        try:
            update_data = {
                'state': status
            }
            
            if comments:
                update_data['work_notes'] = comments
            
            update_url = f"{self.instance_url}/api/now/table/{self.controls_table}/{control_id}"
            
            async with self.session.patch(update_url, json=update_data) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    return {
                        'success': True,
                        'control_id': control_id,
                        'updated_status': status,
                        'details': result_data.get('result', {})
                    }
                elif response.status == 404:
                    return {
                        'success': False,
                        'error': f'Control {control_id} not found'
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Update failed: HTTP {response.status} - {error_text}'
                    }
        
        except Exception as e:
            self.logger.error(f"Error updating ServiceNow control: {e}")
            return {
                'success': False,
                'error': str(e)
            }