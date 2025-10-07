import os
from typing import Optional, List

class Settings:
    """Simple settings class without Pydantic to avoid parsing issues"""
    
    def __init__(self):
        # Database
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ma_saas_db")
        
        # Security
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Claude MCP
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Application
        self.app_name = "M&A SaaS Platform"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # CORS - Handle comma-separated string from environment
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
        self.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Create settings instance
settings = Settings()
