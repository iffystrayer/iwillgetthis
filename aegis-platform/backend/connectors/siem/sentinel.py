"""
Microsoft Sentinel SIEM Connector
"""

import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from ..base import SIEMConnector, ConnectorCapability, HealthStatus


class SentinelConnector(SIEMConnector):
    """Microsoft Sentinel (Azure Sentinel) connector"""
    
    @property
    def vendor_name(self) -> str:
        return "Microsoft Sentinel"
    
    @property
    def supported_capabilities(self) -> List[ConnectorCapability]:
        return [
            ConnectorCapability.READ_EVENTS,
            ConnectorCapability.READ_ALERTS,
            ConnectorCapability.HEALTH_CHECK
        ]
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.subscription_id = config.get('subscription_id')
        self.resource_group = config.get('resource_group')
        self.workspace_name = config.get('workspace_name')
        self.tenant_id = config.get('tenant_id')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        
        # Azure API configuration
        self.azure_base_url = "https://management.azure.com"
        self.log_analytics_base = "https://api.loganalytics.io"
        self.api_version = config.get('api_version', '2020-01-01')
        
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for Sentinel requests"""
        return {
            'User-Agent': 'Aegis-Platform-Sentinel-Connector',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def _get_access_token(self) -> str:
        """Get Azure AD access token"""
        # Check if we have a valid token
        if (self._access_token and self._token_expires and 
            datetime.now() < self._token_expires - timedelta(minutes=5)):
            return self._access_token
        
        # Get new token
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://management.azure.com/.default'
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        async with self.session.post(token_url, data=token_data, headers=headers) as response:
            if response.status == 200:
                token_response = await response.json()
                self._access_token = token_response['access_token']
                expires_in = token_response.get('expires_in', 3600)
                self._token_expires = datetime.now() + timedelta(seconds=expires_in)
                return self._access_token
            else:
                error_text = await response.text()
                raise Exception(f"Token acquisition failed: HTTP {response.status} - {error_text}")
    
    async def _get_log_analytics_token(self) -> str:
        """Get token for Log Analytics API"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://api.loganalytics.io/.default'
        }
        
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        async with self.session.post(token_url, data=token_data, headers=headers) as response:
            if response.status == 200:
                token_response = await response.json()
                return token_response['access_token']
            else:
                error_text = await response.text()
                raise Exception(f"Log Analytics token acquisition failed: HTTP {response.status} - {error_text}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Microsoft Sentinel"""
        try:
            # Validate required configuration
            required_fields = ['subscription_id', 'resource_group', 'workspace_name', 
                             'tenant_id', 'client_id', 'client_secret']
            missing_fields = [field for field in required_fields if not getattr(self, field)]
            
            if missing_fields:
                return {
                    'success': False,
                    'message': f'Missing required configuration: {", ".join(missing_fields)}'
                }
            
            # Test Azure AD authentication
            access_token = await self._get_access_token()
            
            # Test workspace access
            workspace_url = (f"{self.azure_base_url}/subscriptions/{self.subscription_id}/"
                           f"resourceGroups/{self.resource_group}/providers/"
                           f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {'api-version': self.api_version}
            
            async with self.session.get(workspace_url, headers=headers, params=params) as response:
                if response.status == 200:
                    workspace_info = await response.json()
                    return {
                        'success': True,
                        'message': 'Successfully connected to Microsoft Sentinel',
                        'details': {
                            'workspace_id': workspace_info.get('properties', {}).get('customerId'),
                            'workspace_name': self.workspace_name,
                            'resource_group': self.resource_group,
                            'subscription_id': self.subscription_id
                        }
                    }
                elif response.status == 401:
                    return {
                        'success': False,
                        'message': 'Authentication failed - check client credentials'
                    }
                elif response.status == 404:
                    return {
                        'success': False,
                        'message': 'Workspace not found - check subscription, resource group, and workspace name'
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'message': f'Connection test failed: HTTP {response.status} - {error_text}'
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
                access_token = await self._get_access_token()
                health_details['authentication'] = 'success'
            except Exception as e:
                health_details['authentication'] = f'error: {str(e)}'
            
            # Check workspace access
            try:
                workspace_url = (f"{self.azure_base_url}/subscriptions/{self.subscription_id}/"
                               f"resourceGroups/{self.resource_group}/providers/"
                               f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}")
                
                headers = {'Authorization': f'Bearer {access_token}'}
                params = {'api-version': self.api_version}
                
                async with self.session.get(workspace_url, headers=headers, params=params) as response:
                    if response.status == 200:
                        health_details['workspace_access'] = 'available'
                    else:
                        health_details['workspace_access'] = f'error_http_{response.status}'
            except Exception as e:
                health_details['workspace_access'] = f'error: {str(e)}'
            
            # Check Log Analytics API access
            try:
                log_token = await self._get_log_analytics_token()
                health_details['log_analytics_api'] = 'available'
            except Exception as e:
                health_details['log_analytics_api'] = f'error: {str(e)}'
            
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
    
    async def _execute_kql_query(self, query: str) -> Dict[str, Any]:
        """Execute KQL query against Log Analytics"""
        log_token = await self._get_log_analytics_token()
        
        # Get workspace ID first
        workspace_id = await self._get_workspace_id()
        
        query_url = f"{self.log_analytics_base}/v1/workspaces/{workspace_id}/query"
        
        headers = {
            'Authorization': f'Bearer {log_token}',
            'Content-Type': 'application/json'
        }
        
        query_data = {'query': query}
        
        async with self.session.post(query_url, headers=headers, json=query_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"KQL query failed: HTTP {response.status} - {error_text}")
    
    async def _get_workspace_id(self) -> str:
        """Get the workspace ID (customer ID)"""
        access_token = await self._get_access_token()
        
        workspace_url = (f"{self.azure_base_url}/subscriptions/{self.subscription_id}/"
                        f"resourceGroups/{self.resource_group}/providers/"
                        f"Microsoft.OperationalInsights/workspaces/{self.workspace_name}")
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'api-version': self.api_version}
        
        async with self.session.get(workspace_url, headers=headers, params=params) as response:
            if response.status == 200:
                workspace_info = await response.json()
                return workspace_info['properties']['customerId']
            else:
                error_text = await response.text()
                raise Exception(f"Failed to get workspace ID: HTTP {response.status} - {error_text}")
    
    async def get_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Retrieve security events from Sentinel"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Format times for KQL
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Build KQL query
            if query:
                kql_query = query
            else:
                # Default query for security events
                kql_query = '''
                SecurityEvent
                | where TimeGenerated >= datetime({start_time}) and TimeGenerated <= datetime({end_time})
                | limit {limit}
                | project TimeGenerated, Computer, Account, EventID, Activity, LogonType, IpAddress, WorkstationName, ProcessName, CommandLine
                '''.format(start_time=start_time_str, end_time=end_time_str, limit=limit)
            
            # Execute query
            result = await self._execute_kql_query(kql_query)
            
            # Process results
            events = []
            if 'tables' in result and result['tables']:
                table = result['tables'][0]
                columns = [col['name'] for col in table.get('columns', [])]
                
                for row in table.get('rows', []):
                    event_data = dict(zip(columns, row))
                    
                    processed_event = {
                        'id': f"{event_data.get('Computer', '')}_{event_data.get('EventID', '')}_{event_data.get('TimeGenerated', '')}",
                        'timestamp': event_data.get('TimeGenerated'),
                        'computer': event_data.get('Computer'),
                        'account': event_data.get('Account'),
                        'event_id': event_data.get('EventID'),
                        'activity': event_data.get('Activity'),
                        'logon_type': event_data.get('LogonType'),
                        'ip_address': event_data.get('IpAddress'),
                        'workstation': event_data.get('WorkstationName'),
                        'process': event_data.get('ProcessName'),
                        'command_line': event_data.get('CommandLine'),
                        'raw_data': event_data
                    }
                    events.append(processed_event)
            
            return {
                'success': True,
                'events': events,
                'total_count': len(events),
                'query': kql_query,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Sentinel events: {e}")
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
        """Retrieve security alerts from Sentinel"""
        try:
            if end_time is None:
                end_time = datetime.now()
            
            # Format times for KQL
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Build KQL query for security alerts
            kql_query = '''
            SecurityAlert
            | where TimeGenerated >= datetime({start_time}) and TimeGenerated <= datetime({end_time})
            '''.format(start_time=start_time_str, end_time=end_time_str)
            
            if severity:
                # Map severity levels
                severity_map = {
                    'low': 'Low',
                    'medium': 'Medium', 
                    'high': 'High',
                    'critical': 'High'  # Sentinel uses High for critical
                }
                mapped_severity = severity_map.get(severity.lower(), severity)
                kql_query += f' | where AlertSeverity == "{mapped_severity}"'
            
            kql_query += f'''
            | limit {limit}
            | project TimeGenerated, AlertName, AlertSeverity, Description, CompromisedEntity, RemediationSteps, ExtendedProperties, Entities
            '''
            
            # Execute query
            result = await self._execute_kql_query(kql_query)
            
            # Process results
            alerts = []
            if 'tables' in result and result['tables']:
                table = result['tables'][0]
                columns = [col['name'] for col in table.get('columns', [])]
                
                for row in table.get('rows', []):
                    alert_data = dict(zip(columns, row))
                    
                    processed_alert = {
                        'id': f"{alert_data.get('AlertName', '')}_{alert_data.get('TimeGenerated', '')}",
                        'title': alert_data.get('AlertName', 'Sentinel Alert'),
                        'description': alert_data.get('Description', ''),
                        'severity': alert_data.get('AlertSeverity', 'Medium').lower(),
                        'timestamp': alert_data.get('TimeGenerated'),
                        'compromised_entity': alert_data.get('CompromisedEntity'),
                        'remediation_steps': alert_data.get('RemediationSteps'),
                        'extended_properties': alert_data.get('ExtendedProperties'),
                        'entities': alert_data.get('Entities'),
                        'status': 'new',  # Default status
                        'raw_data': alert_data
                    }
                    alerts.append(processed_alert)
            
            return {
                'success': True,
                'alerts': alerts,
                'total_count': len(alerts),
                'query': kql_query,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error retrieving Sentinel alerts: {e}")
            return {
                'success': False,
                'error': str(e),
                'alerts': []
            }