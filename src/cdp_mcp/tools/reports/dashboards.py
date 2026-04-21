"""
Dashboard tools for CDP Report API.

Implements 6 MCP tools: list, create, get, update, delete, copy dashboards.
Source: acquia/cdp-campaignapi DashboardDefController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/dashboards
Note: Collection POST accepts arrays — single objects are wrapped in an array.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_dashboard_tools(server: FastMCP) -> None:
    """Register all dashboard tools on the MCP server."""

    @server.tool(
        name="cdp_list_dashboards",
        description="List all accessible dashboards for a tenant",
    )
    async def cdp_list_dashboards(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all accessible dashboards for a tenant."""
        result = await http_client.get(
            "report/dashboards",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_dashboard",
        description=(
            "Create a new dashboard. Pass dashboard definition as a JSON string. "
            "Should include name and optionally description, widgets array, and layout."
        ),
    )
    async def cdp_create_dashboard(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new dashboard. API expects an array — wraps single object."""
        dashboard = json.loads(body)
        payload = dashboard if isinstance(dashboard, list) else [dashboard]

        result = await http_client.post(
            "report/dashboards",
            tenant_id=tenant_id,
            body=payload,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dashboard",
        description="Get a dashboard by ID. Returns full definition including widgets and layout structure.",
    )
    async def cdp_get_dashboard(
        dashboard_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a dashboard by ID."""
        result = await http_client.get(
            f"report/dashboards/{dashboard_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_dashboard",
        description="Update an existing dashboard by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_dashboard(
        dashboard_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing dashboard by ID."""
        result = await http_client.put(
            f"report/dashboards/{dashboard_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_dashboard",
        description="Delete a dashboard by ID",
    )
    async def cdp_delete_dashboard(
        dashboard_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a dashboard by ID."""
        result = await http_client.delete(
            f"report/dashboards/{dashboard_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Dashboard {dashboard_id} deleted successfully."

    @server.tool(
        name="cdp_copy_dashboard",
        description="Copy a dashboard by ID. Creates a duplicate of the dashboard.",
    )
    async def cdp_copy_dashboard(
        dashboard_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy a dashboard by ID."""
        result = await http_client.post(
            f"report/dashboards/{dashboard_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
