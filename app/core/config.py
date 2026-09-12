import os
from typing import Literal
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuração do Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Aplicação
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    PORT: int = 8000
    PROJECT_NAME: str = "AI SDR Engine"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database
    POSTGRES_USER: str = "sdr_user"
    POSTGRES_PASSWORD: str = "sdr_password"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sdr_db"
    DATABASE_URL: str | None = None

    @computed_field
    @property
    def ASYNC_DATABASE_URI(self) -> str:
        """
        Gera dinamicamente a URI assíncrona (postgresql+asyncpg://) para o SQLAlchemy AsyncEngine,
        respeitando a variável DATABASE_URL se ela já estiver configurada explicitamente.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # AWS Bedrock Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Evolution API Configuration (WhatsApp Gateway)
    EVOLUTION_API_URL: str = "http://evolution-api:8080"
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE: str = "sdr_atlas"


# Instância global singleton das configurações
settings = Settings()

