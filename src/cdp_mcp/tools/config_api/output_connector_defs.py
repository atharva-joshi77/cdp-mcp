"""
Output connector definition tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete output connector defs.
Source: acquia/cdp-configapi OutputConnectorDefController.java
Endpoints: /v2/{tenantId}/config/outputConnectorDefs
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_output_connector_def_tools(server: FastMCP) -> None:
    """Register all output connector definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_output_connector_defs",
        description="List available output connector definitions",
    )
    async def cdp_list_output_connector_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List available output connector definitions."""
        result = await http_client.get(
            "config/outputConnectorDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_output_connector_def",
        description="Get a specific output connector definition by ID",
    )
    async def cdp_get_output_connector_def(
        connector_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific output connector definition by ID."""
        result = await http_client.get(
            f"config/outputConnectorDefs/{connector_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_output_connector_def",
        description="Create a new output connector definition. Pass definition as a JSON string.",
    )
    async def cdp_create_output_connector_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new output connector definition."""
        result = await http_client.post(
            "config/outputConnectorDefs",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_output_connector_def",
        description="Update an output connector definition. Pass updated fields as a JSON string.",
    )
    async def cdp_update_output_connector_def(
        connector_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an output connector definition."""
        result = await http_client.put(
            f"config/outputConnectorDefs/{connector_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_output_connector_def",
        description="Delete an output connector definition",
    )
    async def cdp_delete_output_connector_def(
        connector_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an output connector definition."""
        result = await http_client.delete(
            f"config/outputConnectorDefs/{connector_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Output connector definition deleted successfully."
