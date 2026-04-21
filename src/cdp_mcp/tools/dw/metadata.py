"""
Resource metadata tools for CDP Data Warehouse API.

Implements 2 MCP tools: list resources, describe entity schema.
Source: apiSpecification/specs/dwAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/dw/resources, /v2/{tenantId}/dw/entities/{resourceName}?action=describe
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_metadata_tools(server: FastMCP) -> None:
    """Register all resource metadata tools on the MCP server."""

    @server.tool(
        name="cdp_describe_resources",
        description="List all available DW resources (tables/entities) for a tenant",
    )
    async def cdp_describe_resources(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List all available DW resources (tables/entities) for a tenant."""
        result = await http_client.get(
            "dw/resources",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_describe_entity",
        description="Get the schema/attribute definitions for a DW entity resource",
    )
    async def cdp_describe_entity(
        resource_name: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get the schema/attribute definitions for a DW entity resource."""
        result = await http_client.post(
            f"dw/entities/{resource_name}",
            tenant_id=tenant_id,
            params={"action": "describe"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
