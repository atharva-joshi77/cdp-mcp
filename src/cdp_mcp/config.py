"""
Environment-based configuration for CDP MCP Server.

Uses pydantic-settings to load configuration from environment variables
and .env files. Supports multi-environment URL routing (dev, qa, prod).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class CDPConfig(BaseSettings):
    """CDP MCP Server configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Environment selector
    CDP_ENVIRONMENT: Literal["dev", "qa", "prod"] = "dev"

    # Base URLs per environment
    CDP_BASE_URL_DEV: str = "https://dev-api6.agilone.com"
    CDP_BASE_URL_QA: str = "https://qa-api6.agilone.com"
    CDP_BASE_URL_PROD: str = "https://api.agilone.com"

    # Default tenant ID (can be overridden per-tool-call)
    CDP_TENANT_ID: Optional[str] = None

    # OAuth2 credentials
    CDP_CLIENT_ID: Optional[str] = None
    CDP_CLIENT_SECRET: Optional[str] = None
    CDP_USERNAME: Optional[str] = None
    CDP_PASSWORD: Optional[str] = None

    # Pre-existing bearer token (alternative to OAuth2 flow)
    CDP_AUTH_TOKEN: Optional[str] = None

    @property
    def base_url(self) -> str:
        """Return the base URL for the current environment."""
        urls = {
            "dev": self.CDP_BASE_URL_DEV,
            "qa": self.CDP_BASE_URL_QA,
            "prod": self.CDP_BASE_URL_PROD,
        }
        return urls[self.CDP_ENVIRONMENT]


@lru_cache(maxsize=1)
def get_config() -> CDPConfig:
    """Get the singleton CDP configuration instance."""
    return CDPConfig()


def get_base_url() -> str:
    """Get the base URL for the current environment."""
    return get_config().base_url


def get_default_tenant_id() -> Optional[str]:
    """Get the default tenant ID from configuration."""
    return get_config().CDP_TENANT_ID
