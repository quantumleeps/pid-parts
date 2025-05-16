"""
Configuration settings for the PID Parts application.

This module defines the configuration settings for the application,
including API endpoints, model selection, and secret management.
Settings are loaded from environment variables or .env files.
"""

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Non-sensitive configuration settings for the PID Parts application.

    This class manages configuration settings that can be safely exposed,
    such as API endpoints and model selection parameters. Settings are
    loaded from environment variables or the .env file.
    """

    openrouter_base_url: str = Field(
        "https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API",
    )
    ingestion_model: str = Field(
        "google/gemini-2.0-flash-lite-001",
        description="Model name for the ingestion process",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra fields in the environment
    }


class SecretSettings(BaseSettings):
    """Sensitive configuration settings for the PID Parts application.

    This class manages sensitive configuration settings like API keys
    that should be handled securely. Values are loaded from environment
    variables or the .env file and stored as SecretStr to prevent
    accidental exposure in logs or error messages.
    """

    openrouter_api_key: SecretStr = Field(
        "",
        description="API key for OpenRouter",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Ignore extra fields in the environment
    }


# Create singleton instances of the settings classes
# These will be imported by other modules to access configuration
app_settings = AppSettings()
secret_settings = SecretSettings()
