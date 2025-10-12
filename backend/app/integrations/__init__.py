"""
Comprehensive Integration Ecosystem
Making the platform the central hub for all M&A activities
"""

from .core.integration_manager import (
    IntegrationManager,
    IntegrationStatus,
    DataSyncManager,
    WebhookManager,
    get_integration_manager
)

# CRM Integrations (only import what exists)
try:
    from .crm.salesforce import SalesforceIntegration
except ImportError:
    SalesforceIntegration = None

try:
    from .crm.hubspot import HubSpotIntegration
except ImportError:
    HubSpotIntegration = None

# from .crm.pipedrive import PipedriveIntegration  # Not implemented yet
# from .crm.dynamics import DynamicsIntegration  # Not implemented yet

# Communication Integrations (only import what exists)
try:
    from .communication.teams import TeamsIntegration
except ImportError:
    TeamsIntegration = None

try:
    from .communication.slack import SlackIntegration
except ImportError:
    SlackIntegration = None

# from .communication.zoom import ZoomIntegration  # Not implemented yet
# from .communication.email import EmailIntegration  # Not implemented yet

# Financial Integrations - Not implemented yet
# from .financial.banking import BankingAPIIntegration
# from .financial.payment import PaymentProcessingIntegration
# from .financial.fx import FXRateIntegration
# from .financial.escrow import EscrowIntegration

# Legal Integrations - Not implemented yet
# from .legal.docusign import DocuSignIntegration
# from .legal.compliance import ComplianceIntegration
# from .legal.legal_research import LegalResearchIntegration

# Services - Not implemented yet
# from .services.marketplace import ProfessionalServicesMarketplace
# from .services.network import ServiceProviderNetwork

# Automation - Not implemented yet
# from .automation.zapier import ZapierIntegration
# from .automation.power_automate import PowerAutomateIntegration
# from .automation.workflow_builder import WorkflowBuilder

# API Platform - Not implemented yet
# from .api.platform import DeveloperPlatform
# from .api.sdk import SDKGenerator
# from .api.marketplace import AppMarketplace

__all__ = [
    # Core
    "IntegrationManager",
    "IntegrationStatus",
    "DataSyncManager",
    "WebhookManager",
    "get_integration_manager",
]

# Add optional integrations if they loaded successfully
if SalesforceIntegration:
    __all__.append("SalesforceIntegration")
if HubSpotIntegration:
    __all__.append("HubSpotIntegration")
if TeamsIntegration:
    __all__.append("TeamsIntegration")
if SlackIntegration:
    __all__.append("SlackIntegration")