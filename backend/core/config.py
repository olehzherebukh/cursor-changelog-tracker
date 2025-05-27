from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    CHANGELOG_URL: str = "https://www.cursor.com/en/changelog"
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT: int = 30

    LOG_LEVEL: str = "INFO"

    STORAGE_TYPE: str = "memory"  # Options: memory, file, s3, dynamodb
    STORAGE_FILE_PATH: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
