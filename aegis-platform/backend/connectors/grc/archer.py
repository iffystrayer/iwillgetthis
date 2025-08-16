"""
RSA Archer GRC Connector
"""

import aiohttp
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from ..base import GRCConnector, ConnectorCapability, HealthStatus


class ArcherConnector(GRCConnector):
    """RSA Archer GRC platform connector"""
    
    @property
    def vendor_name(self) -> str:
        return "RSA Archer"
    
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
        self.instance_name = config.get('instance_name', 'default')
        
        # Archer specific configuration
        self.api_version = config.get('api_version', '6.0')
        self.domain = config.get('domain', '')
        
        # Application IDs for different GRC modules
        self.controls_app_id = config.get('controls_app_id', '75')  # Common default for Controls
        self.risks_app_id = config.get('risks_app_id', '73')  # Common default for Risks
        self.incidents_app_id = config.get('incidents_app_id', '86')  # Common default for Incidents
        
        self._session_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for Archer requests"""
        headers = {
            'User-Agent': 'Aegis-Platform-Archer-Connector',
            'Accept': 'application/json,application/xml',
            'Content-Type': 'application/json'
        }
        
        if self._session_token:
            headers['Authorization'] = f'Archer session-id={self._session_token}'
        
        return headers
    
    async def _authenticate(self) -> str:
        """Authenticate with Archer and get session token"""
        # Check if we have a valid token
        if (self._session_token and self._token_expires and 
            datetime.now() < self._token_expires - timedelta(minutes=5)):
            return self._session_token
        
        auth_url = f"{self.base_url}/platformapi/core/security/login"
        
        auth_data = {
            "InstanceName": self.instance_name,
            "Username": self.username,
            "UserDomain": self.domain,
            "Password": self.password
        }
        
        headers = {'Content-Type': 'application/json'}
        
        async with self.session.post(auth_url, json=auth_data, headers=headers) as response:
            if response.status == 200:
                auth_response = await response.json()
                
                if auth_response.get('IsSuccessful', False):
                    self._session_token = auth_response.get('RequestedObject', {}).get('SessionToken')
                    # Archer sessions typically last 20 minutes
                    self._token_expires = datetime.now() + timedelta(minutes=18)
                    return self._session_token
                else:
                    error_msg = auth_response.get('ValidationMessages', [{}])[0].get('ValidationMessage', 'Authentication failed')
                    raise Exception(f"Archer authentication failed: {error_msg}")
            else:
                error_text = await response.text()
                raise Exception(f"Authentication request failed: HTTP {response.status} - {error_text}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to RSA Archer"""
        try:
            if not all([self.username, self.password, self.instance_name]):
                return {
                    'success': False,
                    'message': 'Username, password, and instance name required for Archer authentication'
                }
            
            # Test authentication
            session_token = await self._authenticate()
            
            # Test system information endpoint
            info_url = f"{self.base_url}/platformapi/core/system/about"
            
            async with self.session.get(info_url) as response:
                if response.status == 200:
                    system_info = await response.json()
                    
                    return {
                        'success': True,
                        'message': 'Successfully connected to RSA Archer',
                        'details': {
                            'instance_name': self.instance_name,
                            'version': system_info.get('RequestedObject', {}).get('Version', 'Unknown'),
                            'api_version': self.api_version,
                            'server_url': self.base_url
                        }
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
            
            # Check authentication
            try:
                session_token = await self._authenticate()
                health_details['authentication'] = 'success'
            except Exception as e:
                health_details['authentication'] = f'error: {str(e)}'
            
            # Check system status
            try:
                status_url = f"{self.base_url}/platformapi/core/system/about"
                async with self.session.get(status_url) as response:
                    if response.status == 200:
                        health_details['system_status'] = 'healthy'
                    else:
                        health_details['system_status'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['system_status'] = f'error: {str(e)}'
            
            # Check application access
            try:
                apps_url = f"{self.base_url}/platformapi/core/system/application"
                async with self.session.get(apps_url) as response:
                    if response.status == 200:
                        health_details['application_access'] = 'available'
                    else:
                        health_details['application_access'] = 'limited'
            except Exception as e:
                health_details['application_access'] = f'error: {str(e)}'
            
            # Determine overall health
            if health_details.get('authentication') == 'success' and health_details.get('system_status') == 'healthy':
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
        """Retrieve compliance controls from Archer"""
        try:
            session_token = await self._authenticate()
            
            # Build search criteria
            search_criteria = {
                "MaxReturnedRecords": limit,
                "Module": "Core",
                "IsDesc": True,
                "SortType": "Desc"
            }
            
            # Add filters if specified
            if framework or status:
                field_criteria = []
                
                if framework:
                    field_criteria.append({
                        "FieldName": "Framework",
                        "FieldValue": framework,
                        "SearchType": "Equals"
                    })
                
                if status:
                    field_criteria.append({
                        "FieldName": "Status",
                        "FieldValue": status,
                        "SearchType": "Equals"
                    })
                
                search_criteria["FieldCriteria"] = field_criteria
            
            search_url = f"{self.base_url}/platformapi/core/content/search"
            search_params = {
                "applicationId": self.controls_app_id
            }
            
            async with self.session.post(search_url, json=search_criteria, params=search_params) as response:
                if response.status == 200:
                    search_result = await response.json()
                    
                    if not search_result.get('IsSuccessful', False):
                        return {
                            'success': False,
                            'error': 'Archer search failed',
                            'controls': []
                        }
                    
                    # Process controls
                    controls = []
                    records = search_result.get('RequestedObject', {}).get('Records', [])
                    
                    for record in records:
                        # Extract field values
                        field_contents = record.get('FieldContents', {})
                        
                        processed_control = {
                            'id': record.get('ContentId'),
                            'control_id': self._extract_field_value(field_contents, 'Control ID'),
                            'name': self._extract_field_value(field_contents, 'Control Name'),
                            'description': self._extract_field_value(field_contents, 'Description'),
                            'framework': self._extract_field_value(field_contents, 'Framework'),
                            'control_type': self._extract_field_value(field_contents, 'Control Type'),
                            'frequency': self._extract_field_value(field_contents, 'Testing Frequency'),
                            'status': self._extract_field_value(field_contents, 'Status'),
                            'owner': self._extract_field_value(field_contents, 'Control Owner'),
                            'last_assessment_date': self._extract_field_value(field_contents, 'Last Assessment Date'),
                            'effectiveness': self._extract_field_value(field_contents, 'Effectiveness Rating'),
                            'risk_rating': self._extract_field_value(field_contents, 'Risk Rating'),
                            'raw_data': record
                        }
                        controls.append(processed_control)
                    
                    return {
                        'success': True,
                        'controls': controls,
                        'total_count': len(controls),
                        'application_id': self.controls_app_id,
                        'search_criteria': search_criteria
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'controls': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Archer controls: {e}")
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
        """Retrieve assessment results from Archer"""
        try:
            session_token = await self._authenticate()
            
            # Build search criteria for assessments
            search_criteria = {
                "MaxReturnedRecords": limit,
                "Module": "Core",
                "IsDesc": True,
                "SortType": "Desc"
            }
            
            # Add filters
            field_criteria = []
            
            if control_id:
                field_criteria.append({
                    "FieldName": "Related Control",
                    "FieldValue": control_id,
                    "SearchType": "Equals"
                })
            
            if start_date:
                field_criteria.append({
                    "FieldName": "Assessment Date",
                    "FieldValue": start_date.strftime('%m/%d/%Y'),
                    "SearchType": "GreaterThanOrEqual"
                })
            
            if end_date:
                field_criteria.append({
                    "FieldName": "Assessment Date",
                    "FieldValue": end_date.strftime('%m/%d/%Y'),
                    "SearchType": "LessThanOrEqual"
                })
            
            if field_criteria:
                search_criteria["FieldCriteria"] = field_criteria
            
            # Use assessments application (often part of controls or separate app)
            assessment_app_id = config.get('assessments_app_id', self.controls_app_id)
            
            search_url = f"{self.base_url}/platformapi/core/content/search"
            search_params = {
                "applicationId": assessment_app_id
            }
            
            async with self.session.post(search_url, json=search_criteria, params=search_params) as response:
                if response.status == 200:
                    search_result = await response.json()
                    
                    if not search_result.get('IsSuccessful', False):
                        return {
                            'success': False,
                            'error': 'Archer assessment search failed',
                            'assessments': []
                        }
                    
                    # Process assessments
                    assessments = []
                    records = search_result.get('RequestedObject', {}).get('Records', [])
                    
                    for record in records:
                        field_contents = record.get('FieldContents', {})
                        
                        processed_assessment = {
                            'id': record.get('ContentId'),
                            'assessment_id': self._extract_field_value(field_contents, 'Assessment ID'),
                            'control_id': self._extract_field_value(field_contents, 'Related Control'),
                            'assessment_date': self._extract_field_value(field_contents, 'Assessment Date'),
                            'assessor': self._extract_field_value(field_contents, 'Assessor'),
                            'result': self._extract_field_value(field_contents, 'Assessment Result'),
                            'score': self._extract_field_value(field_contents, 'Score'),
                            'findings': self._extract_field_value(field_contents, 'Findings'),
                            'recommendations': self._extract_field_value(field_contents, 'Recommendations'),
                            'evidence': self._extract_field_value(field_contents, 'Evidence'),
                            'status': self._extract_field_value(field_contents, 'Status'),
                            'raw_data': record
                        }
                        assessments.append(processed_assessment)
                    
                    return {
                        'success': True,
                        'assessments': assessments,
                        'total_count': len(assessments),
                        'application_id': assessment_app_id,
                        'search_criteria': search_criteria
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'API request failed: HTTP {response.status} - {error_text}',
                        'assessments': []
                    }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Archer assessments: {e}")
            return {
                'success': False,
                'error': str(e),
                'assessments': []
            }
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ticket/record in Archer"""
        try:
            session_token = await self._authenticate()
            
            # Determine application ID based on ticket type
            ticket_type = ticket_data.get('type', 'incident').lower()
            
            if ticket_type == 'risk':
                app_id = self.risks_app_id
            elif ticket_type == 'incident':
                app_id = self.incidents_app_id
            else:
                app_id = self.incidents_app_id  # Default to incidents
            
            # Map Aegis ticket data to Archer fields
            field_contents = {}
            
            # Common fields
            if 'title' in ticket_data:
                field_contents['Title'] = ticket_data['title']
            
            if 'description' in ticket_data:
                field_contents['Description'] = ticket_data['description']
            
            if 'priority' in ticket_data:
                field_contents['Priority'] = ticket_data['priority'].title()
            
            if 'severity' in ticket_data:
                field_contents['Severity'] = ticket_data['severity'].title()
            
            if 'assigned_to' in ticket_data:
                field_contents['Assigned To'] = ticket_data['assigned_to']
            
            if 'category' in ticket_data:
                field_contents['Category'] = ticket_data['category']
            
            # Set default status
            field_contents['Status'] = 'New'
            
            create_data = {
                "FieldContents": field_contents
            }
            
            create_url = f"{self.base_url}/platformapi/core/content"
            create_params = {
                "applicationId": app_id
            }
            
            async with self.session.post(create_url, json=create_data, params=create_params) as response:
                if response.status == 201:
                    result_data = await response.json()
                    
                    if result_data.get('IsSuccessful', False):
                        content_id = result_data.get('RequestedObject', {}).get('Id')
                        
                        return {
                            'success': True,
                            'ticket_id': content_id,
                            'application_id': app_id,
                            'url': f"{self.base_url}/Default.aspx?requestUrl=..%2FGenericContent%2FRecord.aspx%3Fid%3D{content_id}%26moduleId%3D{app_id}",
                            'details': result_data.get('RequestedObject', {})
                        }
                    else:
                        error_msgs = result_data.get('ValidationMessages', [])
                        error_text = '; '.join([msg.get('ValidationMessage', '') for msg in error_msgs])
                        return {
                            'success': False,
                            'error': f'Ticket creation failed: {error_text}'
                        }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f'Ticket creation failed: HTTP {response.status} - {error_text}'
                    }
        
        except Exception as e:
            self.logger.error(f"Error creating Archer ticket: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_field_value(self, field_contents: Dict[str, Any], field_name: str) -> Optional[str]:
        """Extract field value from Archer field contents"""
        for field_id, field_data in field_contents.items():
            if isinstance(field_data, dict):
                if field_data.get('FieldName') == field_name:
                    return field_data.get('Value')
                elif field_data.get('Name') == field_name:
                    return field_data.get('Value')
        return None