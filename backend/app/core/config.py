from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./esg.db"
    REDIS_URL: str = ""

    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-5-mini"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-ada-002"
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    PINECONE_API_KEY: str = ""
    PINECONE_INDEX: str = "esg-rag"
    PINECONE_ENVIRONMENT: str = "us-east-1"

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
