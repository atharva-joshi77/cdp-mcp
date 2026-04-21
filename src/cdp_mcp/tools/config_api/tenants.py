"""
Tenant tools for CDP Config API.

Implements 2 MCP tools: list tenants, get tenant.
Source: acquia/cdp-configapi TenantController.java
Endpoints: /v2/config/tenants (no tenant scoping — uses bare path style)
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_tenant_tools(server: FastMCP) -> None:
    """Register tenant tools on the MCP server."""

    @server.tool(
        name="cdp_list_tenants",
        description="List all tenants accessible to the current user",
    )
    async def cdp_list_tenants(
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all tenants accessible to the current user."""
        result = await http_client.get(
            "v2/config/tenants",
            params={"offset": offset, "limit": limit},
            path_style="bare",
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_tenant",
        description=(
            "Get details of a specific tenant by ID. "
            "Tenant IDs are strings — may be numeric, a GUID, or a slug."
        ),
    )
    async def cdp_get_tenant(
        target_tenant_id: str,
    ) -> str:
        """Get details of a specific tenant by ID."""
        result = await http_client.get(
            f"v2/config/tenants/{target_tenant_id}",
            path_style="bare",
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
