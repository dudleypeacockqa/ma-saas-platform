from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ma_saas_db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Claude MCP
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Application
    app_name: str = "M&A SaaS Platform"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS - Handle comma-separated string from environment
    allowed_origins_str: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    @property
    def allowed_origins(self) -> list:
        """Convert comma-separated origins string to list"""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"

settings = Settings()
