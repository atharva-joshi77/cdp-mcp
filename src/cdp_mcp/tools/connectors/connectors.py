"""
Connector CRUD tools for CDP Config API.

Implements 6 MCP tools: list, get, create, update, delete connectors + versions.
Source: acquia/cdp-configapi ConnectorController.java
Endpoints: /v2/{tenantId}/config/connectors
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_connector_tools(server: FastMCP) -> None:
    """Register all connector CRUD tools on the MCP server."""

    @server.tool(
        name="cdp_list_connectors",
        description="List all configured connectors for a tenant",
    )
    async def cdp_list_connectors(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all configured connectors for a tenant."""
        result = await http_client.get(
            "config/connectors",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_connector",
        description="Get a specific connector by ID",
    )
    async def cdp_get_connector(
        connector_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific connector by ID."""
        result = await http_client.get(
            f"config/connectors/{connector_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_connector",
        description=(
            "Create a new connector. Provide name and connector_type for simple creation, "
            "or pass a full JSON body string for advanced configuration. "
            "Channel options: email, export, sms, ads, facebook, any."
        ),
    )
    async def cdp_create_connector(
        name: str,
        connector_type: str,
        channel: Optional[str] = None,
        body: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new connector."""
        if body:
            request_body = json.loads(body)
        else:
            request_body: dict = {"name": name, "connectorType": connector_type}
            if channel is not None:
                request_body["channel"] = channel

        result = await http_client.post(
            "config/connectors",
            tenant_id=tenant_id,
            body=request_body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_connector",
        description="Update an existing connector. Pass updated fields as a JSON string.",
    )
    async def cdp_update_connector(
        connector_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing connector."""
        result = await http_client.put(
            f"config/connectors/{connector_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_connector",
        description="Delete a connector",
    )
    async def cdp_delete_connector(
        connector_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a connector."""
        result = await http_client.delete(
            f"config/connectors/{connector_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Connector deleted successfully."

    @server.tool(
        name="cdp_get_connector_versions",
        description="Get connector history / past batch runs for a connector",
    )
    async def cdp_get_connector_versions(
        connector_id: int,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Get connector history for a connector."""
        result = await http_client.get(
            f"config/connectors/{connector_id}/history",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
