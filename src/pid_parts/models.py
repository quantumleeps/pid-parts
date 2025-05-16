"""Model registry for obtaining multimodal LangChain chat models.

This module provides a unified interface for creating chat models that can
process both text and images, abstracting away provider-specific details.

Supported providers:
-------------------
* **OpenRouter** – via ChatOpenRouter (sub-class of ChatOpenAI)
* **Google Gemini** (optional) – if `model_name` starts with "gemini"
"""

from __future__ import annotations

import os
from functools import cache
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import Field, SecretStr
from langchain_core.utils.utils import secret_from_env

from pid_parts.configure import app_settings, secret_settings

# Gemini is optional
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None


class ChatOpenRouter(ChatOpenAI):
    """ChatOpenAI-compatible class that connects to OpenRouter.ai.

    This class provides a drop-in replacement for ChatOpenAI that routes
    requests to OpenRouter.ai instead of OpenAI directly. It handles
    authentication and API configuration while maintaining the same interface.

    The class securely manages API keys by reading from environment variables
    and properly exposing them to LangChain's tracing system for redaction.
    """

    # expose the secret as a Pydantic field so LCEL can mask it
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        """Define secrets that should be redacted in LangChain's tracing.

        Returns:
            Dictionary mapping field names to environment variable names
        """
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    # constructor – inject OpenRouter URL and key
    def __init__(
        self,
        model_name: str,
        openai_api_key: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the ChatOpenRouter with API key and base URL.

        Sets up the connection to OpenRouter with appropriate authentication
        and configuration. Will attempt to get the API key from environment
        variables or settings if not explicitly provided.

        Args:
            model_name: The name of the model to use on OpenRouter
            openai_api_key: The OpenRouter API key (optional if set in environment)
            **kwargs: Additional keyword arguments to pass to the parent class

        Raises:
            ValueError: If no API key is provided and none can be found in settings
        """
        # Use the API key from secret_settings if not provided
        if not openai_api_key:
            if (
                secret_settings.openrouter_api_key
                and secret_settings.openrouter_api_key.get_secret_value()
            ):
                openai_api_key = secret_settings.openrouter_api_key.get_secret_value()
            else:
                raise ValueError(
                    "Set an OPENROUTER_API_KEY env var (get yours at openrouter.ai)"
                )

        super().__init__(
            base_url=app_settings.openrouter_base_url,
            openai_api_key=openai_api_key,
            model_name=model_name,
            **kwargs,
        )


__all__ = ["ChatOpenRouter", "vision_llm"]


@cache
def ingestor_llm(model_name: str) -> BaseChatModel:
    """Return a chat model able to receive image inputs.

    Creates and configures a multimodal LLM based on the provided model name.
    The function handles routing to the appropriate provider and setting
    optimal parameters for PID drawing analysis.

    Args:
        model_name: Name of the model to use, determines which provider is used

    Returns:
        Configured chat model instance ready to process text and images

    Raises:
        NotImplementedError: If a Gemini model is requested (not yet implemented)
        ValueError: If OpenRouter API key is missing when using OpenRouter models

    Usage example:
        >>> llm = ingestor_llm("openai/gpt-4o")
        >>> llm.invoke([...])

    Provider selection:
    * Model names starting with "gemini" route to Google Generative AI
    * All other model names route to OpenRouter
    """
    # -- Google Gemini branch (optional) ------------------------------------
    if model_name.lower().startswith("gemini"):
        raise NotImplementedError(
            "Google Gemini is not yet implemented. " "Please use OpenRouter for now."
        )

    # -- Default: OpenRouter -------------------------------------------------
    return ChatOpenRouter(
        model_name=model_name,
        temperature=0.1,
        max_tokens=3400,
    )
