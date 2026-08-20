import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # AI Model Configuration
    GEMINI_API_KEY: str = Field(default="")
    OPENAI_API_KEY: str = Field(default="")
    DEFAULT_AI_PROVIDER: str = Field(default="gemini")
    AI_MODEL_NAME: str = Field(default="gemini-2.5-flash")

    # Notion Integration
    NOTION_API_KEY: str = Field(default="")
    NOTION_REQUESTS_DB_ID: str = Field(default="")
    NOTION_RUN_LOG_DB_ID: str = Field(default="")
    NOTION_RULEBOOK_DB_ID: str = Field(default="")
    MOCK_NOTION: bool = Field(default=True)

    # Email Dispatch
    RESEND_API_KEY: str = Field(default="")
    SENDER_EMAIL: str = Field(default="campusdesk@university.edu.in")
    MOCK_EMAIL: bool = Field(default=True)

    # Business Logic Thresholds
    AUTO_APPROVE_BUDGET_MAX_INR: float = 1000.0
    AUTO_APPROVE_LEAVE_MAX_DAYS: int = 1


settings = Settings()
