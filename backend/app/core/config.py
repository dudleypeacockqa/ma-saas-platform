from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/ma_saas_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Claude MCP
    anthropic_api_key: Optional[str] = None
    
    # Application
    app_name: str = "M&A SaaS Platform"
    debug: bool = False
    
    class Config:
        env_file = ".env"

# Create settings instance and handle environment variables manually
settings = Settings()

# Override with environment variables
settings.database_url = os.getenv("DATABASE_URL", settings.database_url)
settings.secret_key = os.getenv("SECRET_KEY", settings.secret_key)
settings.debug = os.getenv("DEBUG", "false").lower() == "true"
settings.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
settings.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Handle CORS origins manually to avoid parsing issues
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
settings.allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
