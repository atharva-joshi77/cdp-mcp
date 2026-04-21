"""
Dispatch definition tools for CDP Campaign API.

Implements 5 MCP tools: list, get, create, update, delete dispatches.
Source: apiSpecification/specs/campaignAPI.json
Note: Dispatch endpoints are not present in the cdp-campaignapi source controllers.
      These may be served through an API gateway or a separate microservice.
Endpoints: /v2/{tenantId}/campaign/campaignDefs/{id}/dispatchDefs, etc.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_dispatch_tools(server: FastMCP) -> None:
    """Register all dispatch definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_dispatches",
        description="List dispatch definitions for a campaign",
    )
    async def cdp_list_dispatches(
        campaign_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """List dispatch definitions for a campaign."""
        result = await http_client.get(
            f"campaign/campaignDefs/{campaign_id}/dispatchDefs",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dispatch",
        description="Get a specific dispatch definition by ID",
    )
    async def cdp_get_dispatch(
        dispatch_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific dispatch definition by ID."""
        result = await http_client.get(
            f"campaign/campaignDefs/dispatchDef/{dispatch_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_dispatch",
        description="Create a dispatch definition for a campaign. Pass dispatch definition as a JSON string.",
    )
    async def cdp_create_dispatch(
        campaign_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a dispatch definition for a campaign."""
        result = await http_client.post(
            f"campaign/campaignDefs/{campaign_id}/dispatchDef",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_dispatch",
        description="Update a dispatch definition. Pass updated fields as a JSON string.",
    )
    async def cdp_update_dispatch(
        dispatch_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a dispatch definition."""
        result = await http_client.put(
            f"campaign/campaignDefs/dispatchDef/{dispatch_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_dispatch",
        description="Delete a dispatch definition",
    )
    async def cdp_delete_dispatch(
        dispatch_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a dispatch definition."""
        result = await http_client.delete(
            f"campaign/campaignDefs/dispatchDef/{dispatch_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Dispatch definition deleted successfully."
