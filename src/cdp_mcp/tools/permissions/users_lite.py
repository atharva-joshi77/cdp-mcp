"""
User-lite tools for CDP Permissions API.

Implements 2 MCP tools: list, get lightweight user representations.
Source: acquia/cdp-permissions-api UserLiteController.java
Endpoints: /v2/{tenantId}/users-lite
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_user_lite_tools(server: FastMCP) -> None:
    """Register user-lite tools on the MCP server."""

    @server.tool(
        name="cdp_list_users_lite",
        description="List all users in lightweight format (fewer fields, faster response)",
    )
    async def cdp_list_users_lite(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all users in lightweight format."""
        result = await http_client.get(
            "users-lite",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_user_lite",
        description="Get a specific user in lightweight format by ID",
    )
    async def cdp_get_user_lite(
        user_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific user in lightweight format by ID."""
        result = await http_client.get(
            f"users-lite/{user_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
