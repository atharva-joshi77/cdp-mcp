"""
Widget tools for CDP Report API.

Implements 6 MCP tools: list, create, get, update, delete, copy widgets.
Source: acquia/cdp-campaignapi WidgetDefController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/widgets
Note: Collection POST accepts arrays — single objects are wrapped in an array.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_widget_tools(server: FastMCP) -> None:
    """Register all widget tools on the MCP server."""

    @server.tool(
        name="cdp_list_widgets",
        description=(
            "List all accessible widgets for a tenant. "
            "Returns id, name, editedby, editeddate by default."
        ),
    )
    async def cdp_list_widgets(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all accessible widgets for a tenant."""
        result = await http_client.get(
            "report/widgets",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_widget",
        description=(
            "Create a new widget. Pass widget definition as a JSON string. "
            "Requires name and visualizationType at minimum."
        ),
    )
    async def cdp_create_widget(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new widget. API expects an array — wraps single object."""
        widget = json.loads(body)
        payload = widget if isinstance(widget, list) else [widget]

        result = await http_client.post(
            "report/widgets",
            tenant_id=tenant_id,
            body=payload,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_widget",
        description="Get a widget by ID. Returns full definition including reportDef and visualization settings.",
    )
    async def cdp_get_widget(
        widget_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a widget by ID."""
        result = await http_client.get(
            f"report/widgets/{widget_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_widget",
        description="Update an existing widget by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_widget(
        widget_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing widget by ID."""
        result = await http_client.put(
            f"report/widgets/{widget_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_widget",
        description="Delete a widget by ID",
    )
    async def cdp_delete_widget(
        widget_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a widget by ID."""
        result = await http_client.delete(
            f"report/widgets/{widget_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"Widget {widget_id} deleted successfully."

    @server.tool(
        name="cdp_copy_widget",
        description="Copy a widget by ID. Creates a duplicate of the widget.",
    )
    async def cdp_copy_widget(
        widget_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy a widget by ID."""
        result = await http_client.post(
            f"report/widgets/{widget_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
