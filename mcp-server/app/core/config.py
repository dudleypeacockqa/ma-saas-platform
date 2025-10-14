"""
BMAD v6 MCP Server Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "BMAD v6 MCP Server"
    APP_VERSION: str = "1.0.0"
    BMAD_VERSION: str = "6.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mcp_db")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "bmad-v6-mcp-secret")
    MCP_ENCRYPTION_KEY: str = os.getenv("MCP_ENCRYPTION_KEY", "a_very_secret_key_that_is_32_bytes") # Must be 32 url-safe base64-encoded bytes

    # API Keys
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

