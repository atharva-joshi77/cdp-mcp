"""
SSO tools for CDP Security API.

Implements 1 MCP tool for SsoController.
Source: acquia/cdp-security-service
       SsoController at /sso

Note: The SSO login and SAML ACS endpoints are browser redirect
flows and not suitable as MCP tools. Only the state-check endpoint
returns JSON and is exposed here.
"""

from __future__ import annotations

import json

import httpx

from mcp.server.fastmcp import FastMCP

from cdp_mcp.config import get_base_url


def register_sso_tools(server: FastMCP) -> None:
    """Register SSO tools on the MCP server."""

    @server.tool(
        name="cdp_check_sso_state",
        description=(
            "Check the SSO state for a given user. "
            "Returns whether SSO is required for the user, "
            "optionally scoped to a specific tenant."
        ),
    )
    async def cdp_check_sso_state(
        username: str,
        tenant: str | None = None,
    ) -> str:
        """GET /sso/state?user={username}&tenant={tenant}"""
        base_url = get_base_url()
        params = {"user": username}
        if tenant:
            params["tenant"] = tenant
        url = f"{base_url}/sso/state"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)

        if not response.is_success:
            return f"SSO state check failed ({response.status_code}): {response.text}"
        return json.dumps(response.json(), indent=2)
