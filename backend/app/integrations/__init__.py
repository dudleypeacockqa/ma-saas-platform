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

from .crm.salesforce import SalesforceIntegration
from .crm.hubspot import HubSpotIntegration
from .crm.pipedrive import PipedriveIntegration
from .crm.dynamics import DynamicsIntegration

from .communication.teams import TeamsIntegration
from .communication.slack import SlackIntegration
from .communication.zoom import ZoomIntegration
from .communication.email import EmailIntegration

from .financial.banking import BankingAPIIntegration
from .financial.payment import PaymentProcessingIntegration
from .financial.fx import FXRateIntegration
from .financial.escrow import EscrowIntegration

from .legal.docusign import DocuSignIntegration
from .legal.compliance import ComplianceIntegration
from .legal.legal_research import LegalResearchIntegration

from .services.marketplace import ProfessionalServicesMarketplace
from .services.network import ServiceProviderNetwork

from .automation.zapier import ZapierIntegration
from .automation.power_automate import PowerAutomateIntegration
from .automation.workflow_builder import WorkflowBuilder

from .api.platform import DeveloperPlatform
from .api.sdk import SDKGenerator
from .api.marketplace import AppMarketplace

__all__ = [
    # Core
    "IntegrationManager",
    "IntegrationStatus",
    "DataSyncManager",
    "WebhookManager",
    "get_integration_manager",

    # CRM & Sales
    "SalesforceIntegration",
    "HubSpotIntegration",
    "PipedriveIntegration",
    "DynamicsIntegration",

    # Communication
    "TeamsIntegration",
    "SlackIntegration",
    "ZoomIntegration",
    "EmailIntegration",

    # Financial
    "BankingAPIIntegration",
    "PaymentProcessingIntegration",
    "FXRateIntegration",
    "EscrowIntegration",

    # Legal
    "DocuSignIntegration",
    "ComplianceIntegration",
    "LegalResearchIntegration",

    # Professional Services
    "ProfessionalServicesMarketplace",
    "ServiceProviderNetwork",

    # Automation
    "ZapierIntegration",
    "PowerAutomateIntegration",
    "WorkflowBuilder",

    # API Platform
    "DeveloperPlatform",
    "SDKGenerator",
    "AppMarketplace"
]