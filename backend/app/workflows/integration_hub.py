"""
Integration Hub - Sprint 14
Advanced integration management, API connectors, and data transformation for external systems
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
import aiohttp
from collections import defaultdict, deque

class IntegrationType(Enum):
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    SOAP = "soap"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    CLOUD_STORAGE = "cloud_storage"

class AuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    BASIC = "basic"
    CUSTOM = "custom"

class SyncDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

class SyncStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

class TransformationType(Enum):
    MAPPING = "mapping"
    FILTERING = "filtering"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    VALIDATION = "validation"
    FORMATTING = "formatting"

@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    integration_id: str
    name: str
    description: str
    integration_type: IntegrationType
    auth_type: AuthType
    endpoint_url: str
    auth_config: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Optional[int] = None
    timeout: int = 30
    retry_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DataMapping:
    """Data field mapping configuration"""
    mapping_id: str
    source_field: str
    target_field: str
    transformation: Optional[str] = None
    default_value: Optional[Any] = None
    required: bool = False
    validation_rules: List[str] = field(default_factory=list)

@dataclass
class SyncConfiguration:
    """Synchronization configuration"""
    sync_id: str
    integration_id: str
    name: str
    direction: SyncDirection
    source_endpoint: str
    target_endpoint: str
    mappings: List[DataMapping] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None  # Cron expression
    batch_size: int = 100
    enabled: bool = True

@dataclass
class SyncExecution:
    """Record of a sync execution"""
    execution_id: str
    sync_id: str
    status: SyncStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_success: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)

@dataclass
class APIRequest:
    """API request configuration"""
    method: str
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Any] = None
    timeout: int = 30

@dataclass
class APIResponse:
    """API response data"""
    status_code: int
    headers: Dict[str, str]
    data: Any
    response_time: float
    error: Optional[str] = None

class APIConnector:
    """Generic API connector for external systems"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = None
        self.auth_token = None
        self.rate_limiter = {}
        self.request_history = deque(maxlen=1000)

    async def initialize(self):
        """Initialize the connector"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers=self.config.headers
        )

        # Authenticate if required
        if self.config.auth_type != AuthType.NONE:
            await self._authenticate()

    async def _authenticate(self):
        """Handle authentication"""
        if self.config.auth_type == AuthType.OAUTH2:
            await self._oauth2_authenticate()
        elif self.config.auth_type == AuthType.API_KEY:
            self._setup_api_key_auth()
        elif self.config.auth_type == AuthType.BEARER_TOKEN:
            self._setup_bearer_token_auth()

    async def _oauth2_authenticate(self):
        """OAuth2 authentication flow"""
        auth_config = self.config.auth_config

        token_url = auth_config.get("token_url")
        client_id = auth_config.get("client_id")
        client_secret = auth_config.get("client_secret")
        scope = auth_config.get("scope", "")

        if not all([token_url, client_id, client_secret]):
            raise ValueError("OAuth2 configuration incomplete")

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }

        async with self.session.post(token_url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                self.auth_token = token_data.get("access_token")

                # Update headers with token
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
            else:
                raise Exception(f"OAuth2 authentication failed: {response.status}")

    def _setup_api_key_auth(self):
        """Setup API key authentication"""
        api_key = self.config.auth_config.get("api_key")
        header_name = self.config.auth_config.get("header_name", "X-API-Key")

        if api_key:
            self.session.headers.update({header_name: api_key})

    def _setup_bearer_token_auth(self):
        """Setup bearer token authentication"""
        token = self.config.auth_config.get("token")
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make an API request with rate limiting and error handling"""
        if not self.session:
            await self.initialize()

        # Apply rate limiting
        await self._apply_rate_limit()

        start_time = datetime.now()

        try:
            async with self.session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                params=request.params,
                json=request.data if request.method in ["POST", "PUT", "PATCH"] else None,
                timeout=request.timeout
            ) as response:

                response_time = (datetime.now() - start_time).total_seconds()

                # Parse response data
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    data = await response.json()
                else:
                    data = await response.text()

                api_response = APIResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    data=data,
                    response_time=response_time
                )

                # Log request
                self.request_history.append({
                    "timestamp": start_time.isoformat(),
                    "method": request.method,
                    "url": request.url,
                    "status_code": response.status,
                    "response_time": response_time
                })

                return api_response

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            return APIResponse(
                status_code=0,
                headers={},
                data=None,
                response_time=response_time,
                error=str(e)
            )

    async def _apply_rate_limit(self):
        """Apply rate limiting"""
        if not self.config.rate_limit:
            return

        now = datetime.now()
        minute_key = now.strftime("%Y-%m-%d-%H-%M")

        if minute_key not in self.rate_limiter:
            self.rate_limiter[minute_key] = 0

        if self.rate_limiter[minute_key] >= self.config.rate_limit:
            # Wait until next minute
            sleep_time = 60 - now.second
            await asyncio.sleep(sleep_time)

        self.rate_limiter[minute_key] += 1

        # Clean up old entries
        cutoff = (now - timedelta(minutes=5)).strftime("%Y-%m-%d-%H-%M")
        keys_to_remove = [k for k in self.rate_limiter.keys() if k < cutoff]
        for key in keys_to_remove:
            del self.rate_limiter[key]

    async def test_connection(self) -> Dict[str, Any]:
        """Test the API connection"""
        try:
            # Make a simple GET request to test connectivity
            test_request = APIRequest(
                method="GET",
                url=self.config.endpoint_url,
                timeout=10
            )

            response = await self.make_request(test_request)

            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time": response.response_time,
                "error": response.error
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """Close the connector"""
        if self.session:
            await self.session.close()

class DataTransformer:
    """Handles data transformation and mapping"""

    def __init__(self):
        self.transformation_functions = {}
        self._register_default_transformations()

    def transform_data(self, data: Any, mappings: List[DataMapping]) -> Dict[str, Any]:
        """Transform data using mappings"""
        result = {}

        for mapping in mappings:
            try:
                # Get source value
                source_value = self._get_nested_value(data, mapping.source_field)

                # Apply transformation if specified
                if mapping.transformation:
                    source_value = self._apply_transformation(
                        source_value, mapping.transformation
                    )

                # Use default value if source is None
                if source_value is None and mapping.default_value is not None:
                    source_value = mapping.default_value

                # Validate if required
                if mapping.required and source_value is None:
                    raise ValueError(f"Required field {mapping.source_field} is missing")

                # Apply validation rules
                for rule in mapping.validation_rules:
                    if not self._validate_value(source_value, rule):
                        raise ValueError(f"Validation failed for {mapping.source_field}: {rule}")

                # Set target value
                self._set_nested_value(result, mapping.target_field, source_value)

            except Exception as e:
                # Log transformation error
                print(f"Transformation error for {mapping.source_field}: {e}")

        return result

    def _get_nested_value(self, data: Any, field_path: str) -> Any:
        """Get value from nested data structure"""
        if not field_path:
            return data

        keys = field_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            else:
                return None

            if current is None:
                break

        return current

    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Set value in nested data structure"""
        keys = field_path.split(".")
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Apply transformation function to value"""
        if transformation in self.transformation_functions:
            return self.transformation_functions[transformation](value)

        # Handle basic transformations
        if transformation == "upper":
            return str(value).upper() if value is not None else None
        elif transformation == "lower":
            return str(value).lower() if value is not None else None
        elif transformation == "trim":
            return str(value).strip() if value is not None else None
        elif transformation.startswith("format:"):
            format_str = transformation[7:]
            return format_str.format(value) if value is not None else None

        return value

    def _validate_value(self, value: Any, rule: str) -> bool:
        """Validate value against rule"""
        if rule == "not_empty":
            return value is not None and str(value).strip() != ""
        elif rule == "numeric":
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
        elif rule.startswith("min_length:"):
            min_len = int(rule.split(":")[1])
            return len(str(value)) >= min_len if value is not None else False
        elif rule.startswith("max_length:"):
            max_len = int(rule.split(":")[1])
            return len(str(value)) <= max_len if value is not None else False

        return True

    def _register_default_transformations(self):
        """Register default transformation functions"""
        self.transformation_functions = {
            "to_date": lambda x: datetime.fromisoformat(str(x)) if x else None,
            "to_string": lambda x: str(x) if x is not None else "",
            "to_int": lambda x: int(x) if x is not None else 0,
            "to_float": lambda x: float(x) if x is not None else 0.0,
        }

class IntegrationHub:
    """Central hub for managing all integrations"""

    def __init__(self):
        self.integrations = {}
        self.connectors = {}
        self.sync_configs = {}
        self.data_transformer = DataTransformer()
        self.sync_executions = {}
        self.integration_stats = {
            "integrations_created": 0,
            "sync_executions": 0,
            "data_records_processed": 0
        }

    async def create_integration(self, name: str, description: str,
                               integration_type: IntegrationType,
                               endpoint_url: str, auth_type: AuthType,
                               auth_config: Optional[Dict[str, Any]] = None) -> str:
        """Create a new integration"""
        integration_id = f"int_{uuid.uuid4().hex[:8]}"

        config = IntegrationConfig(
            integration_id=integration_id,
            name=name,
            description=description,
            integration_type=integration_type,
            auth_type=auth_type,
            endpoint_url=endpoint_url,
            auth_config=auth_config or {}
        )

        self.integrations[integration_id] = config
        self.integration_stats["integrations_created"] += 1

        return integration_id

    async def get_connector(self, integration_id: str) -> Optional[APIConnector]:
        """Get or create a connector for an integration"""
        if integration_id not in self.integrations:
            return None

        if integration_id not in self.connectors:
            config = self.integrations[integration_id]
            connector = APIConnector(config)
            await connector.initialize()
            self.connectors[integration_id] = connector

        return self.connectors[integration_id]

    async def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test an integration connection"""
        connector = await self.get_connector(integration_id)
        if not connector:
            return {"success": False, "error": "Integration not found"}

        return await connector.test_connection()

    async def create_sync(self, integration_id: str, name: str,
                         direction: SyncDirection, source_endpoint: str,
                         target_endpoint: str, mappings: List[DataMapping]) -> str:
        """Create a data synchronization configuration"""
        sync_id = f"sync_{uuid.uuid4().hex[:8]}"

        sync_config = SyncConfiguration(
            sync_id=sync_id,
            integration_id=integration_id,
            name=name,
            direction=direction,
            source_endpoint=source_endpoint,
            target_endpoint=target_endpoint,
            mappings=mappings
        )

        self.sync_configs[sync_id] = sync_config
        return sync_id

    async def execute_sync(self, sync_id: str) -> str:
        """Execute a data synchronization"""
        if sync_id not in self.sync_configs:
            raise ValueError(f"Sync configuration {sync_id} not found")

        sync_config = self.sync_configs[sync_id]
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"

        execution = SyncExecution(
            execution_id=execution_id,
            sync_id=sync_id,
            status=SyncStatus.ACTIVE,
            started_at=datetime.now()
        )

        self.sync_executions[execution_id] = execution

        try:
            # Get connector
            connector = await self.get_connector(sync_config.integration_id)
            if not connector:
                raise Exception("Integration connector not available")

            # Fetch source data
            source_request = APIRequest(
                method="GET",
                url=sync_config.source_endpoint
            )

            source_response = await connector.make_request(source_request)

            if source_response.status_code >= 400:
                raise Exception(f"Source fetch failed: {source_response.error}")

            # Transform data
            source_data = source_response.data
            if isinstance(source_data, list):
                transformed_records = []
                for record in source_data:
                    transformed = self.data_transformer.transform_data(
                        record, sync_config.mappings
                    )
                    transformed_records.append(transformed)
                    execution.records_processed += 1
            else:
                transformed_records = self.data_transformer.transform_data(
                    source_data, sync_config.mappings
                )
                execution.records_processed = 1

            # Send to target (if outbound or bidirectional)
            if sync_config.direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                target_request = APIRequest(
                    method="POST",
                    url=sync_config.target_endpoint,
                    data=transformed_records
                )

                target_response = await connector.make_request(target_request)

                if target_response.status_code < 400:
                    execution.records_success = execution.records_processed
                else:
                    execution.records_failed = execution.records_processed
                    execution.error_message = target_response.error

            execution.status = SyncStatus.ACTIVE if execution.records_failed == 0 else SyncStatus.ERROR
            execution.completed_at = datetime.now()

            self.integration_stats["sync_executions"] += 1
            self.integration_stats["data_records_processed"] += execution.records_processed

        except Exception as e:
            execution.status = SyncStatus.ERROR
            execution.error_message = str(e)
            execution.completed_at = datetime.now()

        return execution_id

    def get_integrations(self) -> List[IntegrationConfig]:
        """Get all integrations"""
        return list(self.integrations.values())

    def get_sync_configs(self) -> List[SyncConfiguration]:
        """Get all sync configurations"""
        return list(self.sync_configs.values())

    def get_sync_executions(self, sync_id: Optional[str] = None) -> List[SyncExecution]:
        """Get sync executions"""
        executions = list(self.sync_executions.values())

        if sync_id:
            executions = [e for e in executions if e.sync_id == sync_id]

        return executions

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            **self.integration_stats,
            "active_integrations": len(self.integrations),
            "active_syncs": len([s for s in self.sync_configs.values() if s.enabled]),
            "active_connectors": len(self.connectors)
        }

# Singleton instance
_integration_hub_instance: Optional[IntegrationHub] = None

def get_integration_hub() -> IntegrationHub:
    """Get the singleton Integration Hub instance"""
    global _integration_hub_instance
    if _integration_hub_instance is None:
        _integration_hub_instance = IntegrationHub()
    return _integration_hub_instance