"""Application configuration settings"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, HttpUrl


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    TESTING: bool = False

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "M&A SaaS Platform"
    VERSION: str = "1.0.0"
    SHOW_DOCS: bool = True

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour default

    # Claude AI Integration
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.7
    CLAUDE_SYSTEM_PROMPT: str = """You are an expert M&A advisor and ecosystem intelligence analyst.
    Your role is to provide strategic insights, deal analysis, partnership recommendations,
    and wealth-building optimization strategies for the M&A ecosystem platform."""

    # OpenAI (for embeddings)
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # Stripe Payment Processing
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PUBLISHABLE_KEY: str

    # Subscription Tiers
    SUBSCRIPTION_TIERS = {
        "solo": {
            "price_id": "",  # To be filled with Stripe price ID
            "monthly_price": 279,
            "annual_price": 3010,  # 10% discount
            "features": [
                "Core M&A intelligence tools",
                "Deal flow tracking",
                "Basic analytics",
                "Email support"
            ]
        },
        "growth": {
            "price_id": "",  # To be filled with Stripe price ID
            "monthly_price": 798,
            "annual_price": 8618,  # 10% discount
            "features": [
                "Everything in Solo",
                "AI-powered deal analysis",
                "Partnership recommendations",
                "Advanced analytics",
                "Priority support"
            ]
        },
        "enterprise": {
            "price_id": "",  # To be filled with Stripe price ID
            "monthly_price": 1598,
            "annual_price": 17258,  # 10% discount
            "features": [
                "Everything in Growth",
                "Custom AI training",
                "White-label options",
                "API access",
                "Dedicated success manager",
                "24/7 phone support"
            ]
        }
    }

    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: Optional[str] = None

    # Email Configuration
    EMAIL_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Monitoring
    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # File Storage
    UPLOAD_MAX_SIZE_MB: int = 100
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".csv", ".txt"
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # AI Rate Limits
    AI_RATE_LIMIT_PER_MINUTE: int = 20
    AI_RATE_LIMIT_PER_DAY: int = 1000

    # Performance
    QUERY_TIMEOUT_SECONDS: int = 30
    REQUEST_TIMEOUT_SECONDS: int = 60

    # Feature Flags
    FEATURE_AI_ANALYSIS: bool = True
    FEATURE_PARTNERSHIP_MATCHING: bool = True
    FEATURE_DEAL_SCORING: bool = True
    FEATURE_ECOSYSTEM_MAPPING: bool = True


settings = Settings()