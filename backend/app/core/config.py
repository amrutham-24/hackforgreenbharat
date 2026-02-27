from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://esg_user:esg_pass@localhost:5432/esg_db"
    DATABASE_URL_SYNC: str = "postgresql://esg_user:esg_pass@localhost:5432/esg_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "esg-rag"
    PINECONE_ENVIRONMENT: str = "us-east-1"

    AZURE_SUBSCRIPTION_ID: str = ""
    AZURE_RESOURCE_GROUP: str = "green-bharath-rg"
    AZURE_LOCATION: str = "centralindia"

    SLACK_WEBHOOK_URL: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    ALERT_EMAIL_FROM: str = "alerts@greenbharat.ai"

    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"
    INTERNAL_API_KEY: str = "change-me-internal-key"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
