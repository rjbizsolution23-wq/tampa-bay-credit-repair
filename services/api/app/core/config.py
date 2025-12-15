from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, EmailStr, validator

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Tampa Bay Credit Repair API"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    NODE_ENV: str = "development"
    
    # Database
    DATABASE_URL: str
    DIRECT_URL: str | None = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Integrations
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    
    MFSN_API_BASE: str | None = None
    MFSN_EMAIL: str | None = None
    MFSN_PASSWORD: str | None = None
    MFSN_AID: str | None = None
    
    DISPUTEFOX_API_KEY: str | None = None
    DISPUTEFOX_EMAIL: str | None = None
    
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_PHONE_NUMBER: str | None = None
    
    RESEND_API_KEY: str | None = None
    FROM_EMAIL: str | None = None
    
    # Monitoring
    SENTRY_DSN: str | None = None
    
    # Storage
    R2_ACCOUNT_ID: str | None = None
    R2_ACCESS_KEY_ID: str | None = None
    R2_SECRET_ACCESS_KEY: str | None = None
    R2_BUCKET_NAME: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
