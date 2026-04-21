"""
OAuth2 token management for CDP API authentication.

The CDP platform uses OAuth2 password grant. The token endpoint
accepts credentials via headers (not body).

Source: apiSpecification/specs/securityAPI.yaml — POST /token?action=create

Auth flow:
1. POST to {baseUrl}/token?action=create with headers:
   client_id, client_secret, username, password, grant_type=password
2. Response: {"access_token": "...", "token_type": "bearer", "expires_in": 3600}
3. Use Authorization: Bearer {access_token} on all subsequent requests
"""

from __future__ import annotations

import asyncio
import time

import httpx

from cdp_mcp.config import get_base_url, get_config


class AuthProvider:
    """Manages OAuth2 tokens with caching and automatic refresh."""

    def __init__(self) -> None:
        self._access_token: str | None = None
        self._token_expiry: float = 0
        # Serialize concurrent refreshes so we don't issue N parallel
        # POST /token?action=create calls when many tools fire at once.
        self._refresh_lock = asyncio.Lock()

    async def get_token(self, *, force_refresh: bool = False) -> str:
        """
        Get a valid access token.

        Returns a static token if CDP_AUTH_TOKEN is configured,
        otherwise manages OAuth2 token lifecycle with caching.

        Args:
            force_refresh: If True, ignore the cached token and fetch a new
                one. Used by `HttpClient` when a 401 is received.
        """
        config = get_config()

        # If a static token is configured, use it directly (no refresh needed).
        if config.CDP_AUTH_TOKEN:
            return config.CDP_AUTH_TOKEN

        # Fast-path: valid cached token (with 60s safety buffer).
        if (
            not force_refresh
            and self._access_token
            and time.time() < self._token_expiry - 60
        ):
            return self._access_token

        # Serialize concurrent refreshes. First caller refreshes; others
        # re-check the cache under the lock and reuse the newly minted token.
        async with self._refresh_lock:
            if (
                not force_refresh
                and self._access_token
                and time.time() < self._token_expiry - 60
            ):
                return self._access_token
            return await self._refresh_token()

    async def _refresh_token(self) -> str:
        """Fetch a new OAuth2 access token using password grant."""
        config = get_config()
        base_url = get_base_url().rstrip("/")

        if not all([
            config.CDP_CLIENT_ID,
            config.CDP_CLIENT_SECRET,
            config.CDP_USERNAME,
            config.CDP_PASSWORD,
        ]):
            raise RuntimeError(
                "OAuth2 credentials not configured. Set CDP_CLIENT_ID, CDP_CLIENT_SECRET, "
                "CDP_USERNAME, CDP_PASSWORD in environment, or provide CDP_AUTH_TOKEN."
            )

        url = f"{base_url}/token?action=create"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "client_id": config.CDP_CLIENT_ID,  # type: ignore[arg-type]
                    "client_secret": config.CDP_CLIENT_SECRET,  # type: ignore[arg-type]
                    "username": config.CDP_USERNAME,  # type: ignore[arg-type]
                    "password": config.CDP_PASSWORD,  # type: ignore[arg-type]
                    "grant_type": "password",
                },
            )

        if response.status_code != 200:
            body = response.text
            raise RuntimeError(
                f"OAuth2 token request failed ({response.status_code}): {body}"
            )

        data = response.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data["expires_in"]

        return self._access_token  # type: ignore[return-value]

    def invalidate(self) -> None:
        """
        Drop the cached token so the next `get_token()` call refreshes.

        Used by `HttpClient` when the server returns 401 Unauthorized on an
        otherwise-valid request — typically because the token was revoked
        or rotated server-side before its advertised expiry.
        """
        self._access_token = None
        self._token_expiry = 0

    async def revoke_token(self) -> None:
        """Revoke the current access token."""
        if not self._access_token:
            return

        base_url = get_base_url().rstrip("/")
        url = f"{base_url}/token?action=revoke"

        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._access_token}",
                },
            )

        self.invalidate()


# Singleton instance
auth_provider = AuthProvider()
