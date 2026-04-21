"""
UDMP (Unified Data Model Platform) tools for CDP Config API.

Implements 3 MCP tools: list UDMP tables, get UDMP table, list UDMP resources.
Source: acquia/cdp-configapi UDMPTableController, UDMPResourceController
Endpoints: /v2/{tenantId}/config/UDMPTables, /v2/{tenantId}/config/UDMPResources
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_udmp_tools(server: FastMCP) -> None:
    """Register all UDMP tools on the MCP server."""

    @server.tool(
        name="cdp_list_udmp_tables",
        description="List UDMP (Unified Data Model Platform) tables",
    )
    async def cdp_list_udmp_tables(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List UDMP tables."""
        result = await http_client.get(
            "config/UDMPTables",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_udmp_table",
        description="Get a specific UDMP table by ID",
    )
    async def cdp_get_udmp_table(
        table_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific UDMP table by ID."""
        result = await http_client.get(
            f"config/UDMPTables/{table_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_list_udmp_resources",
        description="List UDMP resources (available data resources in the platform)",
    )
    async def cdp_list_udmp_resources(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List UDMP resources."""
        result = await http_client.get(
            "config/UDMPResources",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
