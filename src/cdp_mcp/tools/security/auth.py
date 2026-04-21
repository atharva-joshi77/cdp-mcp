"""
Security & Authorization tools for CDP Security/Auth APIs.

Implements 7 MCP tools covering TokenController and AuthenticationController.
Source: acquia/cdp-security-service

Endpoints use bare paths (no tenant prefix, no /v2):
  - TokenController: /token
  - AuthenticationController: /authentication

Authentication uses standard HTTP Authorization header:
  - Basic auth: Authorization: Basic <base64(username:password)>
  - Bearer auth: Authorization: Bearer <token>

These tools use raw httpx because the standard http_client injects
a bearer token and uses tenant-scoped paths. These endpoints are the
ones that CREATE tokens in the first place.
"""

from __future__ import annotations

import base64
import json

import httpx

from mcp.server.fastmcp import FastMCP

from cdp_mcp.config import get_base_url


def _basic_auth_header(username: str, password: str) -> str:
    """Build a standard HTTP Basic Authorization header value."""
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return f"Basic {credentials}"


def _bearer_auth_header(token: str) -> str:
    """Build a standard HTTP Bearer Authorization header value."""
    return f"Bearer {token}"


def register_security_tools(server: FastMCP) -> None:
    """Register token and authentication tools on the MCP server."""

    # ── TokenController: /token ──────────────────────────────────────

    @server.tool(
        name="cdp_create_token",
        description=(
            "Create an access token using Basic authentication. "
            "Credentials are sent via the standard Authorization header. "
            "Returns access_token, token_type, expires_in."
        ),
    )
    async def cdp_create_token(
        username: str,
        password: str,
        scheme: str = "A1USER",
    ) -> str:
        """POST /token?action=create&scheme={scheme}"""
        base_url = get_base_url()
        url = f"{base_url}/token?action=create&scheme={scheme}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": _basic_auth_header(username, password),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/hal+json",
                },
            )

        if not response.is_success:
            return f"Token creation failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)

    @server.tool(
        name="cdp_extend_token",
        description=(
            "Extend the expiry of an existing bearer token. "
            "The token is sent via the Authorization header."
        ),
    )
    async def cdp_extend_token(
        token: str,
        scheme: str = "A1USER",
    ) -> str:
        """POST /token?action=extend&scheme={scheme}"""
        base_url = get_base_url()
        url = f"{base_url}/token?action=extend&scheme={scheme}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": _bearer_auth_header(token),
                },
            )

        if not response.is_success:
            return f"Token extension failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)

    @server.tool(
        name="cdp_revoke_token",
        description=(
            "Revoke an access token. Pass either a bearer token to revoke "
            "that specific token, or username/password (Basic auth) to "
            "revoke all tokens for that user."
        ),
    )
    async def cdp_revoke_token(
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        scheme: str = "A1USER",
    ) -> str:
        """DELETE /token?scheme={scheme}"""
        base_url = get_base_url()
        url = f"{base_url}/token?scheme={scheme}"

        if token:
            auth_header = _bearer_auth_header(token)
        elif username and password:
            auth_header = _basic_auth_header(username, password)
        else:
            return "Error: provide either 'token' or both 'username' and 'password'."

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                url,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/hal+json",
                },
            )

        if not response.is_success:
            return f"Token revocation failed ({response.status_code}): {response.text}"
        return "Token revoked successfully."

    @server.tool(
        name="cdp_get_token",
        description=(
            "Get token information. Pass a bearer token to fetch info "
            "about that specific token, or username/password (Basic auth) "
            "to fetch the user's token."
        ),
    )
    async def cdp_get_token(
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        scheme: str = "A1USER",
    ) -> str:
        """GET /token?scheme={scheme}"""
        base_url = get_base_url()
        url = f"{base_url}/token?scheme={scheme}"

        if token:
            auth_header = _bearer_auth_header(token)
        elif username and password:
            auth_header = _basic_auth_header(username, password)
        else:
            return "Error: provide either 'token' or both 'username' and 'password'."

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": auth_header},
            )

        if not response.is_success:
            return f"Get token failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)

    # ── AuthenticationController: /authentication ────────────────────

    @server.tool(
        name="cdp_login",
        description=(
            "Authenticate a user via Basic auth and generate a bearer token. "
            "Optionally specify a tenant_name to scope the login. "
            "Returns access_token, token_type, expires_in."
        ),
    )
    async def cdp_login(
        username: str,
        password: str,
        tenant_name: str | None = None,
    ) -> str:
        """POST /authentication?action=login"""
        base_url = get_base_url()
        url = f"{base_url}/authentication?action=login"

        headers = {
            "Authorization": _basic_auth_header(username, password),
            "Content-Type": "application/json",
            "Accept": "application/hal+json",
        }

        body = None
        if tenant_name:
            body = json.dumps({"tenantName": tenant_name})

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=body)

        if not response.is_success:
            return f"Login failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)

    @server.tool(
        name="cdp_logout",
        description=(
            "Logout and revoke the current bearer token. "
            "Pass a bearer token to revoke it, or username/password "
            "to revoke all tokens for that user."
        ),
    )
    async def cdp_logout(
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> str:
        """POST /authentication?action=logout"""
        base_url = get_base_url()
        url = f"{base_url}/authentication?action=logout"

        if token:
            auth_header = _bearer_auth_header(token)
        elif username and password:
            auth_header = _basic_auth_header(username, password)
        else:
            return "Error: provide either 'token' or both 'username' and 'password'."

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                    "Accept": "application/hal+json",
                },
            )

        if not response.is_success:
            return f"Logout failed ({response.status_code}): {response.text}"
        return "Logout successful. Token revoked."

    @server.tool(
        name="cdp_get_session_info",
        description=(
            "Get session and permissions info for the current bearer token. "
            "Optionally specify a tenant_name to scope the response."
        ),
    )
    async def cdp_get_session_info(
        token: str,
        tenant_name: str | None = None,
    ) -> str:
        """POST /authentication/session"""
        base_url = get_base_url()
        url = f"{base_url}/authentication/session"

        headers = {
            "Authorization": _bearer_auth_header(token),
            "Content-Type": "application/json",
            "Accept": "application/hal+json",
        }

        body = None
        if tenant_name:
            body = json.dumps({"tenantName": tenant_name})

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=body)

        if not response.is_success:
            return f"Get session info failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)
