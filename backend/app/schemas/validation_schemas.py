"""
Reusable Pydantic validation schemas for M&A SaaS Platform
Provides common validators and constraints for API inputs
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============================================================================
# COMMON FIELD CONSTRAINTS
# ============================================================================

# String constraints
ShortString = str  # Field(..., min_length=1, max_length=100)
MediumString = str  # Field(..., min_length=1, max_length=500)
LongString = str  # Field(..., min_length=1, max_length=10000)

# Numeric constraints
PositiveInt = int  # Field(..., gt=0)
NonNegativeInt = int  # Field(..., ge=0)
PositiveFloat = float  # Field(..., gt=0)
NonNegativeFloat = float  # Field(..., ge=0)

# Percentage (0-100)
Percentage = float  # Field(..., ge=0, le=100)

# Probability (0-1)
Probability = float  # Field(..., ge=0, le=1)


# ============================================================================
# COMMON ENUMS
# ============================================================================

class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(str, Enum):
    """Generic status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class CurrencyCode(str, Enum):
    """Common ISO 4217 currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"


class CountryCode(str, Enum):
    """Common ISO 3166-1 alpha-2 country codes"""
    US = "US"
    GB = "GB"
    CA = "CA"
    AU = "AU"
    DE = "DE"
    FR = "FR"
    JP = "JP"
    CN = "CN"
    IN = "IN"


# ============================================================================
# BASE VALIDATION SCHEMAS
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class IDMixin(BaseModel):
    """Mixin for ID fields"""
    id: Optional[str] = None
    organization_id: Optional[str] = None


class PaginationParams(BaseModel):
    """Reusable pagination parameters"""
    page: int = Field(1, ge=1, le=1000, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

    @validator("per_page")
    def validate_per_page(cls, v):
        """Ensure reasonable page size"""
        if v > 100:
            raise ValueError("Maximum page size is 100")
        return v


class SortParams(BaseModel):
    """Reusable sort parameters"""
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="Sort order")


class SearchParams(BaseModel):
    """Reusable search parameters"""
    search: Optional[str] = Field(None, min_length=1, max_length=200, description="Search query")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


class DateRangeParams(BaseModel):
    """Reusable date range parameters"""
    date_from: Optional[date] = Field(None, description="Start date")
    date_to: Optional[date] = Field(None, description="End date")

    @root_validator
    def validate_date_range(cls, values):
        """Validate date range is logical"""
        date_from = values.get("date_from")
        date_to = values.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise ValueError("date_from must be before date_to")

        return values


# ============================================================================
# FINANCIAL VALIDATION SCHEMAS
# ============================================================================

class MoneyField(BaseModel):
    """Money amount with currency"""
    amount: float = Field(..., description="Amount")
    currency: CurrencyCode = Field(CurrencyCode.USD, description="Currency code")

    @validator("amount")
    def validate_amount(cls, v):
        """Validate amount has at most 2 decimal places"""
        if round(v, 2) != v:
            raise ValueError("Amount must have at most 2 decimal places")
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class FinancialMetrics(BaseModel):
    """Common financial metrics"""
    revenue: Optional[float] = Field(None, ge=0, description="Revenue")
    ebitda: Optional[float] = Field(None, description="EBITDA")
    net_income: Optional[float] = Field(None, description="Net income")
    total_assets: Optional[float] = Field(None, ge=0, description="Total assets")
    total_debt: Optional[float] = Field(None, ge=0, description="Total debt")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")

    currency: CurrencyCode = Field(CurrencyCode.USD, description="Currency")
    fiscal_year: Optional[int] = Field(None, ge=2000, le=2100, description="Fiscal year")


# ============================================================================
# COMPANY VALIDATION SCHEMAS
# ============================================================================

class CompanyInfo(BaseModel):
    """Basic company information"""
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    website: Optional[str] = Field(None, max_length=500, description="Company website")
    description: Optional[str] = Field(None, max_length=2000, description="Company description")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    country: Optional[CountryCode] = Field(None, description="Country code")
    headquarters_location: Optional[str] = Field(None, max_length=200, description="HQ location")
    founded_year: Optional[int] = Field(None, ge=1800, le=2100, description="Year founded")
    employees: Optional[int] = Field(None, ge=0, description="Number of employees")

    @validator("website")
    def validate_website(cls, v):
        """Validate website URL format"""
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    @validator("name")
    def validate_name(cls, v):
        """Validate company name"""
        if not v or not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip()


# ============================================================================
# CONTACT VALIDATION SCHEMAS
# ============================================================================

class ContactInfo(BaseModel):
    """Contact information"""
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    address: Optional[str] = Field(None, max_length=500, description="Physical address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State/Province")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal/ZIP code")
    country: Optional[CountryCode] = Field(None, description="Country code")

    @validator("email")
    def validate_email(cls, v):
        """Validate email format"""
        if v:
            import re
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(pattern, v):
                raise ValueError("Invalid email format")
            return v.lower()
        return v

    @validator("phone")
    def validate_phone(cls, v):
        """Basic phone validation"""
        if v:
            # Remove common formatting
            clean = re.sub(r"[\s\-\(\)\+]", "", v)
            if not clean.isdigit():
                raise ValueError("Phone must contain only digits and formatting characters")
        return v


# ============================================================================
# FILE VALIDATION SCHEMAS
# ============================================================================

class FileInfo(BaseModel):
    """File information"""
    filename: str = Field(..., min_length=1, max_length=255, description="Filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., min_length=1, max_length=100, description="MIME type")
    file_extension: Optional[str] = Field(None, max_length=10, description="File extension")

    @validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size (max 100MB)"""
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f"File size cannot exceed {max_size} bytes")
        return v

    @validator("filename")
    def sanitize_filename(cls, v):
        """Sanitize filename"""
        import re
        # Remove directory traversal attempts
        v = v.replace("..", "")
        v = v.replace("/", "_")
        v = v.replace("\\", "_")
        # Remove null bytes
        v = v.replace("\x00", "")
        return v


# ============================================================================
# CUSTOM FIELD VALIDATION
# ============================================================================

class CustomFieldValue(BaseModel):
    """Custom field with flexible value"""
    key: str = Field(..., min_length=1, max_length=100, description="Field key")
    value: Any = Field(..., description="Field value")
    type: Optional[str] = Field(None, regex="^(string|number|boolean|date|array|object)$", description="Value type")

    @validator("key")
    def validate_key(cls, v):
        """Validate key format (alphanumeric and underscore only)"""
        import re
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Custom field key must contain only letters, numbers, and underscores")
        return v


# ============================================================================
# METADATA VALIDATION
# ============================================================================

class AuditInfo(BaseModel):
    """Audit trail information"""
    created_by: Optional[str] = Field(None, description="User who created")
    updated_by: Optional[str] = Field(None, description="User who last updated")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TagsMixin(BaseModel):
    """Mixin for tags field"""
    tags: List[str] = Field(default_factory=list, max_items=50, description="Tags")

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags"""
        if not v:
            return []

        # Deduplicate
        v = list(set(v))

        # Validate each tag
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError("Tags must be strings")
            if len(tag) > 50:
                raise ValueError("Each tag must be 50 characters or less")
            if not tag.strip():
                raise ValueError("Tags cannot be empty")

        return v


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    pagination: Dict[str, int] = Field(..., description="Pagination info")
    total: int = Field(..., ge=0, description="Total items")

    @validator("pagination")
    def validate_pagination(cls, v):
        """Ensure pagination has required fields"""
        required_fields = ["page", "per_page", "pages"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Pagination must include '{field}'")
        return v


# ============================================================================
# BULK OPERATION SCHEMAS
# ============================================================================

class BulkOperationRequest(BaseModel):
    """Bulk operation request"""
    operation: str = Field(..., min_length=1, max_length=50, description="Operation type")
    ids: List[str] = Field(..., min_items=1, max_items=1000, description="Record IDs")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")

    @validator("ids")
    def validate_ids(cls, v):
        """Validate IDs list"""
        if len(v) > 1000:
            raise ValueError("Cannot perform bulk operation on more than 1000 items")
        # Deduplicate
        return list(set(v))


class BulkOperationResponse(BaseModel):
    """Bulk operation response"""
    success: bool
    processed: int = Field(..., ge=0, description="Number processed")
    failed: int = Field(0, ge=0, description="Number failed")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Error details")
