"""
Tracking and profile tools for CDP Data Warehouse API.

Endpoints:
- POST /{apiVersion}/{tenantId}/dw/tracker   (DwTrackerController — apiVersion is a path variable)
- POST /v2/{tenantId}/dw/profile             (DwProfileController)
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_tracker_tools(server: FastMCP) -> None:
    """Register all tracking and profile tools on the MCP server."""

    @server.tool(
        name="cdp_post_tracking_event",
        description=(
            "Post a real-time tracking event to the CDP "
            "(POST /{apiVersion}/{tenantId}/dw/tracker). "
            "api_version is a routable path segment — defaults to 'v2' but the "
            "controller accepts any version clients want to pin. "
            "Pass event data as a JSON string with eventType, identityHash, properties."
        ),
    )
    async def cdp_post_tracking_event(
        body: str,
        tenant_id: Optional[str] = None,
        api_version: str = "v2",
    ) -> str:
        """Post a real-time tracking event to the CDP."""
        # DwTrackerController's mapping uses {apiVersion} as a path variable, so we
        # build the prefix manually via path_style="bare" rather than the default
        # "v2" style that would hard-code the version.
        tid = http_client._resolve_tenant_id(tenant_id)  # noqa: SLF001
        result = await http_client.post(
            f"{api_version}/{tid}/dw/tracker",
            path_style="bare",
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_customer_profile",
        description=(
            "Update customer profile attributes in real-time "
            "(POST /v2/{tenantId}/dw/profile). "
            "Pass profile update data as a JSON string."
        ),
    )
    async def cdp_update_customer_profile(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update customer profile attributes in real-time."""
        result = await http_client.post(
            "dw/profile",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
