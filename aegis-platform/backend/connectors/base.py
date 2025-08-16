"""
Base connector architecture for enterprise integrations
"""

import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ConnectorStatus(Enum):
    """Connector status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class HealthStatus(Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


class SyncResult(Enum):
    """Synchronization result enumeration"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    NO_DATA = "no_data"


class ConnectorCapability(Enum):
    """Connector capability enumeration"""
    READ_EVENTS = "read_events"
    WRITE_EVENTS = "write_events"
    READ_ALERTS = "read_alerts"
    CREATE_TICKETS = "create_tickets"
    UPDATE_TICKETS = "update_tickets"
    READ_CONTROLS = "read_controls"
    SYNC_USERS = "sync_users"
    HEALTH_CHECK = "health_check"


class BaseConnector(ABC):
    """
    Abstract base class for all integration connectors
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(f"connectors.{self.name}")
        self.session: Optional[aiohttp.ClientSession] = None
        self._capabilities = set()
        self._status = ConnectorStatus.INACTIVE
        self._health_status = HealthStatus.UNKNOWN
        self._last_error: Optional[str] = None
        
    @property
    @abstractmethod
    def connector_type(self) -> str:
        """Return the type of this connector (siem, grc, vulnerability, etc.)"""
        pass
    
    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """Return the vendor name (Splunk, ServiceNow, QRadar, etc.)"""
        pass
    
    @property
    @abstractmethod
    def supported_capabilities(self) -> List[ConnectorCapability]:
        """Return list of capabilities this connector supports"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the external system
        
        Returns:
            Dict containing test results with keys:
            - success: bool
            - message: str
            - details: Dict[str, Any]
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform detailed health check
        
        Returns:
            Dict containing health information
        """
        pass
    
    async def initialize(self) -> bool:
        """
        Initialize the connector
        
        Returns:
            True if initialization successful
        """
        try:
            # Create HTTP session with timeout and retry configuration
            timeout = aiohttp.ClientTimeout(
                total=self.config.get('timeout', 30),
                connect=self.config.get('connect_timeout', 10)
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._get_default_headers()
            )
            
            # Test connection
            connection_result = await self.test_connection()
            if connection_result.get('success', False):
                self._status = ConnectorStatus.ACTIVE
                self._health_status = HealthStatus.HEALTHY
                self.logger.info(f"Connector {self.name} initialized successfully")
                return True
            else:
                self._status = ConnectorStatus.ERROR
                self._health_status = HealthStatus.ERROR
                self._last_error = connection_result.get('message', 'Connection test failed')
                self.logger.error(f"Connector {self.name} initialization failed: {self._last_error}")
                return False
                
        except Exception as e:
            self._status = ConnectorStatus.ERROR
            self._health_status = HealthStatus.ERROR
            self._last_error = str(e)
            self.logger.error(f"Error initializing connector {self.name}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default HTTP headers for requests"""
        headers = {
            'User-Agent': f'Aegis-Platform-Connector/{self.name}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add authentication headers based on auth method
        auth_method = self.config.get('auth_method', 'basic')
        
        if auth_method == 'token' and 'api_key' in self.config:
            headers['Authorization'] = f"Bearer {self.config['api_key']}"
        elif auth_method == 'api_key' and 'api_key' in self.config:
            headers['X-API-Key'] = self.config['api_key']
        
        return headers
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request with error handling and retries
        """
        if not self.session:
            raise Exception("Connector not initialized")
        
        max_retries = self.config.get('max_retries', 3)
        retry_delay = self.config.get('retry_delay', 1)
        
        for attempt in range(max_retries + 1):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status < 400:
                        return response
                    elif response.status in [429, 503, 504]:  # Rate limit or server error
                        if attempt < max_retries:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                            continue
                    
                    response.raise_for_status()
                    
            except asyncio.TimeoutError:
                if attempt < max_retries:
                    self.logger.warning(f"Request timeout, retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(retry_delay)
                    continue
                raise Exception("Request timeout after retries")
            
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"Request failed, retry {attempt + 1}/{max_retries}: {e}")
                    await asyncio.sleep(retry_delay)
                    continue
                raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get current connector status"""
        return {
            'status': self._status.value,
            'health_status': self._health_status.value,
            'last_error': self._last_error,
            'capabilities': [cap.value for cap in self.supported_capabilities]
        }


class SIEMConnector(BaseConnector):
    """Base class for SIEM connectors"""
    
    @property
    def connector_type(self) -> str:
        return "siem"
    
    @abstractmethod
    async def get_events(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        query: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Retrieve security events from SIEM
        
        Args:
            start_time: Start time for event query
            end_time: End time for event query (defaults to now)
            query: Optional query filter
            limit: Maximum number of events to retrieve
            
        Returns:
            Dict containing events and metadata
        """
        pass
    
    @abstractmethod
    async def get_alerts(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        severity: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Retrieve security alerts from SIEM
        
        Args:
            start_time: Start time for alert query
            end_time: End time for alert query (defaults to now)
            severity: Optional severity filter
            limit: Maximum number of alerts to retrieve
            
        Returns:
            Dict containing alerts and metadata
        """
        pass
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create alert in SIEM (if supported)
        
        Args:
            alert_data: Alert information
            
        Returns:
            Dict containing creation result
        """
        raise NotImplementedError("Create alert not supported by this connector")


class GRCConnector(BaseConnector):
    """Base class for GRC connectors"""
    
    @property
    def connector_type(self) -> str:
        return "grc"
    
    @abstractmethod
    async def get_controls(
        self,
        framework: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Retrieve compliance controls from GRC system
        
        Args:
            framework: Optional framework filter (NIST, ISO27001, etc.)
            status: Optional status filter
            limit: Maximum number of controls to retrieve
            
        Returns:
            Dict containing controls and metadata
        """
        pass
    
    @abstractmethod
    async def get_assessments(
        self,
        control_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Retrieve assessment results from GRC system
        
        Args:
            control_id: Optional control ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of assessments to retrieve
            
        Returns:
            Dict containing assessments and metadata
        """
        pass
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create ticket/task in GRC system (if supported)
        
        Args:
            ticket_data: Ticket information
            
        Returns:
            Dict containing creation result
        """
        raise NotImplementedError("Create ticket not supported by this connector")
    
    async def update_control_status(
        self,
        control_id: str,
        status: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update control status in GRC system (if supported)
        
        Args:
            control_id: Control identifier
            status: New status
            comments: Optional comments
            
        Returns:
            Dict containing update result
        """
        raise NotImplementedError("Update control status not supported by this connector")


class ConnectorRegistry:
    """Registry for managing available connectors"""
    
    def __init__(self):
        self._connectors: Dict[str, type] = {}
        self._instances: Dict[str, BaseConnector] = {}
    
    def register(self, connector_class: type):
        """Register a connector class"""
        if not issubclass(connector_class, BaseConnector):
            raise ValueError("Connector must inherit from BaseConnector")
        
        name = connector_class.__name__
        self._connectors[name] = connector_class
        logger.info(f"Registered connector: {name}")
    
    def get_connector_class(self, name: str) -> Optional[type]:
        """Get connector class by name"""
        return self._connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """List all registered connector names"""
        return list(self._connectors.keys())
    
    async def create_connector(
        self,
        connector_name: str,
        config: Dict[str, Any]
    ) -> Optional[BaseConnector]:
        """Create and initialize a connector instance"""
        connector_class = self.get_connector_class(connector_name)
        if not connector_class:
            logger.error(f"Unknown connector: {connector_name}")
            return None
        
        try:
            connector = connector_class(config)
            if await connector.initialize():
                self._instances[f"{connector_name}_{id(connector)}"] = connector
                return connector
            else:
                await connector.cleanup()
                return None
        except Exception as e:
            logger.error(f"Failed to create connector {connector_name}: {e}")
            return None
    
    async def cleanup_all(self):
        """Cleanup all connector instances"""
        for connector in self._instances.values():
            await connector.cleanup()
        self._instances.clear()


# Global connector registry
connector_registry = ConnectorRegistry()