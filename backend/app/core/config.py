import os
from typing import Optional, List

class Settings:
    """Simple settings class without Pydantic to avoid parsing issues"""
    
    def __init__(self):
        # Database
        self.DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost/ma_saas_db")
        self.database_url = self.DATABASE_URL  # Legacy compatibility
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Redis Cache
        self.REDIS_URL = os.getenv("REDIS_URL")

        # Claude MCP
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        # Stripe Payment Processing
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
        self.STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

        # Clerk Authentication
        self.CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
        self.CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")
        self.CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")

        # Application
        self.app_name = "M&A SaaS Platform"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # CORS - Handle comma-separated string from environment
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Create settings instance
settings = Settings()
