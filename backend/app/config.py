import json
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./argus.db"

    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS Origins (JSON list of strings or list directly if loaded correctly)
    CORS_ORIGINS: List[str] = ["*"]

    # AI Configs
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v) -> List[str]:
        if isinstance(v, str):
            try:
                # In case it is a JSON array string
                return json.loads(v)
            except json.JSONDecodeError:
                # Split by comma
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

settings = Settings()
