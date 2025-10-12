"""
Request validation middleware for M&A SaaS Platform
Provides centralized input validation, sanitization, and security checks
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any, List
import re
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request validation and sanitization
    """

    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_string_length = 10000
        self.max_array_length = 1000

    async def dispatch(self, request: Request, call_next):
        """Process request with validation"""
        try:
            # Skip validation for certain paths
            if self._should_skip_validation(request.url.path):
                return await call_next(request)

            # Validate request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                logger.warning(
                    "Request too large",
                    path=request.url.path,
                    size=content_length,
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": f"Request body too large. Maximum size is {self.max_request_size} bytes"
                    },
                )

            # Validate content type for POST/PUT/PATCH
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if not self._is_valid_content_type(content_type):
                    logger.warning(
                        "Invalid content type",
                        path=request.url.path,
                        content_type=content_type,
                    )
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content={"detail": "Unsupported content type"},
                    )

            # Process request
            response = await call_next(request)

            return response

        except Exception as e:
            logger.error(
                "Validation middleware error",
                error=str(e),
                path=request.url.path,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )

    def _should_skip_validation(self, path: str) -> bool:
        """Check if validation should be skipped for this path"""
        skip_paths = [
            "/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/static/",
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _is_valid_content_type(self, content_type: str) -> bool:
        """Validate content type"""
        valid_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]
        return any(valid_type in content_type for valid_type in valid_types)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


def validate_string_length(
    value: str, field_name: str, max_length: int = 10000, min_length: int = 0
) -> str:
    """Validate string length"""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    if len(value) < min_length:
        raise ValueError(
            f"{field_name} must be at least {min_length} characters long"
        )

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} must be no more than {max_length} characters long"
        )

    return value


def validate_email(email: str) -> str:
    """Validate email format"""
    email_pattern = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    if not email_pattern.match(email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_url(url: str) -> str:
    """Validate URL format"""
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or IP
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not url_pattern.match(url):
        raise ValueError("Invalid URL format")
    return url


def validate_phone(phone: str) -> str:
    """Validate phone number (basic validation)"""
    # Remove common formatting characters
    clean_phone = re.sub(r"[\s\-\(\)\+]", "", phone)

    if not clean_phone.isdigit():
        raise ValueError("Phone number must contain only digits")

    if len(clean_phone) < 10 or len(clean_phone) > 15:
        raise ValueError("Phone number must be between 10 and 15 digits")

    return phone


def validate_date_range(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> tuple:
    """Validate date range"""
    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
    return start_date, end_date


def validate_numeric_range(
    value: float, field_name: str, min_value: Optional[float] = None, max_value: Optional[float] = None
) -> float:
    """Validate numeric value is within range"""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number")

    if min_value is not None and value < min_value:
        raise ValueError(f"{field_name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name} must be no more than {max_value}")

    return value


def validate_array_length(
    array: List, field_name: str, max_length: int = 1000, min_length: int = 0
) -> List:
    """Validate array length"""
    if not isinstance(array, list):
        raise ValueError(f"{field_name} must be an array")

    if len(array) < min_length:
        raise ValueError(
            f"{field_name} must contain at least {min_length} items"
        )

    if len(array) > max_length:
        raise ValueError(
            f"{field_name} must contain no more than {max_length} items"
        )

    return array


def sanitize_string(value: str) -> str:
    """Sanitize string by removing potentially dangerous characters"""
    if not isinstance(value, str):
        return value

    # Remove null bytes
    value = value.replace("\x00", "")

    # Remove control characters except newlines and tabs
    value = "".join(char for char in value if char in ["\n", "\t"] or ord(char) >= 32)

    return value.strip()


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> str:
    """Validate file extension"""
    if not filename:
        raise ValueError("Filename cannot be empty")

    file_ext = filename.lower().split(".")[-1] if "." in filename else ""

    if file_ext not in [ext.lower().lstrip(".") for ext in allowed_extensions]:
        raise ValueError(
            f"File extension .{file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )

    return filename


def validate_enum_value(value: str, allowed_values: List[str], field_name: str) -> str:
    """Validate value is in allowed enum values"""
    if value not in allowed_values:
        raise ValueError(
            f"Invalid {field_name}. Must be one of: {', '.join(allowed_values)}"
        )
    return value


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate JSON structure has required fields"""
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return data


def validate_currency_code(code: str) -> str:
    """Validate ISO 4217 currency code"""
    valid_codes = [
        "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "SEK", "NZD",
        "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "RUB", "INR", "BRL", "ZAR",
    ]

    code = code.upper()
    if code not in valid_codes:
        raise ValueError(f"Invalid currency code: {code}")

    return code


def validate_country_code(code: str) -> str:
    """Validate ISO 3166-1 alpha-2 country code"""
    # Common country codes (subset)
    valid_codes = [
        "US", "GB", "CA", "AU", "DE", "FR", "JP", "CN", "IN", "BR",
        "MX", "ES", "IT", "NL", "SE", "NO", "DK", "FI", "PL", "RU",
        "ZA", "SG", "HK", "NZ", "IE", "CH", "AT", "BE", "PT", "GR",
    ]

    code = code.upper()
    if code not in valid_codes:
        raise ValueError(f"Invalid country code: {code}")

    return code


def validate_percentage(value: float, field_name: str) -> float:
    """Validate percentage value (0-100)"""
    return validate_numeric_range(value, field_name, min_value=0, max_value=100)


def validate_probability(value: float, field_name: str) -> float:
    """Validate probability value (0-1)"""
    return validate_numeric_range(value, field_name, min_value=0, max_value=1)


# ============================================================================
# SQL INJECTION PREVENTION
# ============================================================================


def detect_sql_injection(value: str) -> bool:
    """Detect potential SQL injection patterns"""
    if not isinstance(value, str):
        return False

    sql_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)",
        r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(--|\#|\/\*)",  # SQL comments
        r"(\bOR\b.*=.*)",  # OR 1=1 pattern
        r"(';|\"'|`)",  # Quote injection
    ]

    for pattern in sql_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(
                "Potential SQL injection detected",
                pattern=pattern,
                value=value[:100],
            )
            return True

    return False


def validate_safe_input(value: str, field_name: str) -> str:
    """Validate input doesn't contain SQL injection attempts"""
    if detect_sql_injection(value):
        raise ValueError(f"{field_name} contains potentially dangerous content")

    return sanitize_string(value)


# ============================================================================
# XSS PREVENTION
# ============================================================================


def detect_xss(value: str) -> bool:
    """Detect potential XSS patterns"""
    if not isinstance(value, str):
        return False

    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers like onclick=
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            logger.warning(
                "Potential XSS detected",
                pattern=pattern,
                value=value[:100],
            )
            return True

    return False


def sanitize_html(value: str) -> str:
    """Remove potentially dangerous HTML"""
    if not isinstance(value, str):
        return value

    if detect_xss(value):
        # Remove all HTML tags
        value = re.sub(r"<[^>]+>", "", value)

    return value
