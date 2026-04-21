"""
Connector definition (template) tools for CDP Config API.

Implements 4 MCP tools: list, get, create, delete connector definitions.
Source: acquia/cdp-configapi ConnectorDefController.java
Endpoints: /v2/{tenantId}/config/connectorDefs
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_connector_template_tools(server: FastMCP) -> None:
    """Register all connector definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_connector_templates",
        description="List available connector definitions (templates)",
    )
    async def cdp_list_connector_templates(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List available connector definitions."""
        result = await http_client.get(
            "config/connectorDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_connector_template",
        description="Get a specific connector definition by ID",
    )
    async def cdp_get_connector_template(
        connector_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific connector definition by ID."""
        result = await http_client.get(
            f"config/connectorDefs/{connector_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_connector_template",
        description="Create a new connector definition. Pass definition as a JSON string.",
    )
    async def cdp_create_connector_template(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new connector definition."""
        result = await http_client.post(
            "config/connectorDefs",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_connector_template",
        description="Delete a connector definition",
    )
    async def cdp_delete_connector_template(
        connector_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a connector definition."""
        result = await http_client.delete(
            f"config/connectorDefs/{connector_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Connector definition deleted successfully."
