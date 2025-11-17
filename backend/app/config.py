"""Application configuration module."""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Interface Wizard"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # OpenEMR
    OPENEMR_USERNAME: str
    OPENEMR_PASSWORD: str
    OPENEMR_BASE_URL: str

    # Mirth Connect
    MIRTH_HOST: str
    MIRTH_PORT: int = 8443
    MIRTH_USERNAME: str
    MIRTH_PASSWORD: str
    MIRTH_USE_HTTPS: bool = True

    # HL7 MLLP
    MLLP_HOST: str
    MLLP_PORT: int
    MLLP_TIMEOUT: int = 30

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7

    # FHIR
    FHIR_BASE_URL: str
    FHIR_VERSION: str = "R4"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/interface-wizard.log"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3001", "http://localhost:4200", "http://localhost:4201"]'

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        import json
        return json.loads(self.CORS_ORIGINS)

    @property
    def mirth_base_url(self) -> str:
        """Get Mirth Connect base URL."""
        protocol = "https" if self.MIRTH_USE_HTTPS else "http"
        return f"{protocol}://{self.MIRTH_HOST}:{self.MIRTH_PORT}"

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
