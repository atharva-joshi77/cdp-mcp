"""
Output connector tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete output connectors.
Source: acquia/cdp-configapi OutputConnectorController.java
Endpoints: /v2/{tenantId}/config/outputConnectors
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_output_connector_tools(server: FastMCP) -> None:
    """Register all output connector tools on the MCP server."""

    @server.tool(
        name="cdp_list_output_connectors",
        description="List all configured output connectors for a tenant",
    )
    async def cdp_list_output_connectors(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all configured output connectors for a tenant."""
        result = await http_client.get(
            "config/outputConnectors",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_output_connector",
        description="Get a specific output connector by ID",
    )
    async def cdp_get_output_connector(
        connector_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific output connector by ID."""
        result = await http_client.get(
            f"config/outputConnectors/{connector_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_output_connector",
        description="Create a new output connector. Pass configuration as a JSON string.",
    )
    async def cdp_create_output_connector(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new output connector."""
        result = await http_client.post(
            "config/outputConnectors",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_output_connector",
        description="Update an existing output connector. Pass updated fields as a JSON string.",
    )
    async def cdp_update_output_connector(
        connector_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing output connector."""
        result = await http_client.put(
            f"config/outputConnectors/{connector_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_output_connector",
        description="Delete an output connector",
    )
    async def cdp_delete_output_connector(
        connector_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an output connector."""
        result = await http_client.delete(
            f"config/outputConnectors/{connector_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Output connector deleted successfully."
