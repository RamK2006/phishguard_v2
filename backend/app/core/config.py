from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://phishguard:phishguard_password@localhost:5432/phishguard"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    
    # Extension API Key
    EXTENSION_API_KEY: str
    
    # Threat Intelligence APIs
    VIRUSTOTAL_API_KEY: str
    URLHAUS_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: str
    
    # Groq API
    GROQ_API_KEY: str
    
    # ML Model Path
    MODEL_PATH: str = "./backend/app/ml/models/lgbm_v1.pkl"
    
    # Application
    APP_NAME: str = "PhishGuard"
    DEBUG: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
