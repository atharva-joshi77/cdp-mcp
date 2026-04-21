"""
Summary customization tools for CDP Config API.

Implements 2 MCP tools: list summary customizations, get summary customization.
Source: acquia/cdp-configapi SummaryCustomizationController
Endpoints: /v2/{tenantId}/config/summaryCustomizations
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_summary_customization_tools(server: FastMCP) -> None:
    """Register all summary customization tools on the MCP server."""

    @server.tool(
        name="cdp_list_summary_customizations",
        description="List summary customizations for a tenant",
    )
    async def cdp_list_summary_customizations(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List summary customizations for a tenant."""
        result = await http_client.get(
            "config/summaryCustomizations",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_summary_customization",
        description="Get a specific summary customization by ID",
    )
    async def cdp_get_summary_customization(
        customization_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific summary customization by ID."""
        result = await http_client.get(
            f"config/summaryCustomizations/{customization_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
