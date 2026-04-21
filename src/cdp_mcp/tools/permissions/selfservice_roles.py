"""
Self-service role tools for CDP Permissions API.

Implements 1 MCP tool: list self-service roles.
Source: acquia/cdp-permissions-api SelfServiceRoleController.java
Endpoints: /v2/{tenantId}/selfservice-roles
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_self_service_role_tools(server: FastMCP) -> None:
    """Register self-service role tools on the MCP server."""

    @server.tool(
        name="cdp_list_selfservice_roles",
        description="List available self-service roles for a tenant",
    )
    async def cdp_list_selfservice_roles(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List available self-service roles for a tenant."""
        result = await http_client.get(
            "selfservice-roles",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
