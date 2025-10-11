"""
Pydantic schemas for Deal API validation and serialization.
Story 1.1: Deal Creation API - Schema Implementation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from pydantic.functional_validators import BeforeValidator


# Enums matching the SQLAlchemy models
class DealStageEnum(str, Enum):
    """Deal pipeline stages"""
    SOURCING = "sourcing"
    INITIAL_REVIEW = "initial_review"
    NDA_EXECUTION = "nda_execution"
    PRELIMINARY_ANALYSIS = "preliminary_analysis"
    VALUATION = "valuation"
    DUE_DILIGENCE = "due_diligence"
    NEGOTIATION = "negotiation"
    LOI_DRAFTING = "loi_drafting"
    DOCUMENTATION = "documentation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    ON_HOLD = "on_hold"


class DealTypeEnum(str, Enum):
    """Types of M&A transactions"""
    ACQUISITION = "acquisition"
    MERGER = "merger"
    DIVESTITURE = "divestiture"
    JOINT_VENTURE = "joint_venture"
    MANAGEMENT_BUYOUT = "management_buyout"
    LEVERAGED_BUYOUT = "leveraged_buyout"
    ASSET_PURCHASE = "asset_purchase"
    STOCK_PURCHASE = "stock_purchase"
    STRATEGIC_INVESTMENT = "strategic_investment"
    MINORITY_INVESTMENT = "minority_investment"


class DealPriorityEnum(str, Enum):
    """Deal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Base schemas
class DealBase(BaseModel):
    """Base Deal schema with common fields"""

    # Basic Information
    title: str = Field(..., min_length=1, max_length=255, description="Deal title")
    code_name: Optional[str] = Field(None, max_length=100, description="Internal confidential name")
    deal_type: DealTypeEnum = Field(DealTypeEnum.ACQUISITION, description="Type of M&A transaction")
    stage: DealStageEnum = Field(DealStageEnum.SOURCING, description="Current deal stage")
    priority: DealPriorityEnum = Field(DealPriorityEnum.MEDIUM, description="Deal priority")

    # Target Company Information
    target_company_name: str = Field(..., min_length=1, max_length=255)
    target_company_website: Optional[str] = Field(None, max_length=500)
    target_company_description: Optional[str] = None
    target_industry: Optional[str] = Field(None, max_length=100)
    target_country: Optional[str] = Field(None, max_length=2, pattern="^[A-Z]{2}$")
    target_employees: Optional[int] = Field(None, gt=0)
    target_headquarters_location: Optional[str] = Field(None, max_length=255)
    target_founded_year: Optional[int] = Field(None, ge=1800, le=datetime.now().year)

    # Financial Information
    deal_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deal_currency: str = Field("USD", pattern="^[A-Z]{3}$")
    enterprise_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    equity_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    debt_assumed: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    # Probability and Risk
    probability_of_close: int = Field(50, ge=0, le=100)
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")

    # Important Dates
    initial_contact_date: Optional[date] = None
    nda_signed_date: Optional[date] = None
    loi_signed_date: Optional[date] = None
    expected_close_date: Optional[date] = None

    # Strategic Information
    executive_summary: Optional[str] = None
    investment_thesis: Optional[str] = None
    strategic_rationale: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list, max_length=50)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    @field_validator('deal_currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Ensure currency is uppercase"""
        return v.upper()

    @model_validator(mode='after')
    def validate_dates(self) -> 'DealBase':
        """Validate date relationships"""
        if self.nda_signed_date and self.initial_contact_date:
            if self.nda_signed_date < self.initial_contact_date:
                raise ValueError("NDA signed date cannot be before initial contact date")

        if self.loi_signed_date and self.nda_signed_date:
            if self.loi_signed_date < self.nda_signed_date:
                raise ValueError("LOI signed date cannot be before NDA signed date")

        return self


class DealCreate(DealBase):
    """Schema for creating a new deal"""

    # Team
    deal_lead_id: Optional[UUID] = None
    sponsor_id: Optional[UUID] = None

    # Additional fields for creation
    is_confidential: bool = Field(True, description="Whether deal is confidential")
    next_steps: Optional[str] = None
    next_milestone_date: Optional[date] = None
    next_milestone_description: Optional[str] = Field(None, max_length=500)


class DealUpdate(BaseModel):
    """Schema for updating an existing deal"""

    # All fields are optional for partial updates
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    code_name: Optional[str] = Field(None, max_length=100)
    deal_type: Optional[DealTypeEnum] = None
    stage: Optional[DealStageEnum] = None
    priority: Optional[DealPriorityEnum] = None

    target_company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    target_company_website: Optional[str] = Field(None, max_length=500)
    target_company_description: Optional[str] = None
    target_industry: Optional[str] = Field(None, max_length=100)
    target_country: Optional[str] = Field(None, max_length=2, pattern="^[A-Z]{2}$")
    target_employees: Optional[int] = Field(None, gt=0)

    deal_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deal_currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    enterprise_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    equity_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    probability_of_close: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")

    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None

    deal_lead_id: Optional[UUID] = None
    sponsor_id: Optional[UUID] = None

    executive_summary: Optional[str] = None
    investment_thesis: Optional[str] = None
    strategic_rationale: Optional[str] = None

    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DealStageUpdate(BaseModel):
    """Schema specifically for updating deal stage"""

    stage: DealStageEnum
    reason: Optional[str] = Field(None, description="Reason for stage change")
    probability_of_close: Optional[int] = Field(None, ge=0, le=100)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DealInDB(DealBase):
    """Schema for Deal as stored in database"""

    id: UUID
    organization_id: UUID
    deal_number: str

    # Team
    deal_lead_id: Optional[UUID] = None
    sponsor_id: Optional[UUID] = None

    # Status fields
    is_active: bool = True
    is_confidential: bool = True

    # Computed fields
    days_in_pipeline: int
    days_to_expected_close: Optional[int] = None
    is_overdue: bool

    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DealResponse(DealInDB):
    """Schema for API response with additional computed fields"""

    # Additional response fields
    team_members_count: Optional[int] = 0
    activities_count: Optional[int] = 0
    documents_count: Optional[int] = 0

    # Related data (optional, based on include parameters)
    team_members: Optional[List[Dict[str, Any]]] = None
    recent_activities: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class DealListResponse(BaseModel):
    """Schema for paginated deal list response"""

    data: List[DealResponse]
    pagination: Dict[str, Any] = Field(
        ...,
        example={
            "page": 1,
            "per_page": 20,
            "total": 100,
            "pages": 5
        }
    )
    filters: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class DealBulkOperation(BaseModel):
    """Schema for bulk deal operations"""

    operation: str = Field(..., pattern="^(update|delete|archive|stage_change)$")
    deal_ids: List[UUID] = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None

    @model_validator(mode='after')
    def validate_operation_data(self) -> 'DealBulkOperation':
        """Validate that update operations include data"""
        if self.operation in ['update', 'stage_change'] and not self.data:
            raise ValueError(f"Operation '{self.operation}' requires data")
        return self


class DealFilters(BaseModel):
    """Schema for deal filtering parameters"""

    stage: Optional[List[DealStageEnum]] = None
    priority: Optional[List[DealPriorityEnum]] = None
    deal_type: Optional[List[DealTypeEnum]] = None

    min_value: Optional[Decimal] = Field(None, ge=0)
    max_value: Optional[Decimal] = Field(None, ge=0)

    deal_lead_id: Optional[UUID] = None
    sponsor_id: Optional[UUID] = None

    is_active: Optional[bool] = None
    is_overdue: Optional[bool] = None

    expected_close_date_from: Optional[date] = None
    expected_close_date_to: Optional[date] = None

    probability_min: Optional[int] = Field(None, ge=0, le=100)
    probability_max: Optional[int] = Field(None, ge=0, le=100)

    search: Optional[str] = Field(None, min_length=1, max_length=100)
    tags: Optional[List[str]] = None

    sort_by: Optional[str] = Field(
        "created_at",
        pattern="^(created_at|updated_at|expected_close_date|deal_value|probability_of_close|priority|stage)$"
    )
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$")

    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

    @model_validator(mode='after')
    def validate_value_range(self) -> 'DealFilters':
        """Validate min/max value relationship"""
        if self.min_value and self.max_value:
            if self.min_value > self.max_value:
                raise ValueError("min_value cannot be greater than max_value")

        if self.probability_min and self.probability_max:
            if self.probability_min > self.probability_max:
                raise ValueError("probability_min cannot be greater than probability_max")

        return self


class DealStatistics(BaseModel):
    """Schema for deal statistics and analytics"""

    total_deals: int
    active_deals: int

    by_stage: Dict[str, int]
    by_priority: Dict[str, int]
    by_type: Dict[str, int]

    total_value: Decimal
    average_value: Decimal
    median_value: Decimal

    average_probability: float
    average_days_in_pipeline: float

    overdue_deals: int
    closing_this_month: int

    conversion_rates: Dict[str, float]

    model_config = ConfigDict(from_attributes=True)