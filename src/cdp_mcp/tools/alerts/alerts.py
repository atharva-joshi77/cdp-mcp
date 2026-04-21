"""
Alert management tools for CDP Alert API — CURRENTLY DISABLED.

P0 audit finding (2026-04-20):
    The alert endpoints this module was written against
    (`/{tenantId}/alertdefs`, `/{tenantId}/alerts`, etc.) do not exist on any
    service reachable via the configured `agilone.com` base URL. In the
    current CDP architecture, Alerts are served by a separate MuleSoft / Go
    stack:

      - acquia/eee-eapi-cdp-alerts   (Experience API)
      - acquia/eee-papi-cdp-alerts   (Process API)
      - acquia/ent-go-eapi-cdp-alerts
      - acquia/ent-go-papi-cdp-alerts

    Those services live on different hostnames and may use different auth
    schemes, so they must be wired up with a dedicated HTTP client / base URL
    before these tools can be exposed again.

    Until that plumbing exists, `register_alert_tools()` is a no-op. The
    original tool implementations are preserved below under
    `_register_legacy_alert_tools` so they can be revived once a correct
    target is configured.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client

# Historical value — preserved here only for reference. Not safe to use.
PATH_STYLE = "none"


def register_alert_tools(server: FastMCP) -> None:
    """No-op. See module docstring for why alert tools are disabled."""
    return


# --------------------------------------------------------------------------- #
# Preserved legacy implementation. DO NOT call until a correct Alerts API
# base URL + auth scheme is configured.
# --------------------------------------------------------------------------- #


def _register_legacy_alert_tools(server: FastMCP) -> None:  # pragma: no cover
    """Register all alert tools on the MCP server."""

    # ---- Alert Definitions ----

    @server.tool(
        name="cdp_list_alert_defs",
        description="List alert definitions for a tenant",
    )
    async def cdp_list_alert_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List alert definitions for a tenant."""
        result = await http_client.get(
            "alertdefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_alert_def",
        description="Get a specific alert definition by ID",
    )
    async def cdp_get_alert_def(
        alert_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific alert definition by ID."""
        result = await http_client.get(
            f"alertdef/{alert_def_id}",
            tenant_id=tenant_id,
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_alert_def",
        description=(
            "Create a new alert definition. Provide name and expression for simple creation, "
            "or pass a full JSON body string for advanced configuration."
        ),
    )
    async def cdp_create_alert_def(
        name: str,
        expression: str,
        body: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new alert definition."""
        request_body = json.loads(body) if body else {"name": name, "expression": expression}

        result = await http_client.post(
            "alertdef",
            tenant_id=tenant_id,
            body=request_body,
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_alert_def",
        description="Delete an alert definition",
    )
    async def cdp_delete_alert_def(
        alert_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an alert definition."""
        result = await http_client.delete(
            f"alertdef/{alert_def_id}",
            tenant_id=tenant_id,
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Alert definition deleted successfully."

    # ---- Triggered Alerts ----

    @server.tool(
        name="cdp_list_alerts",
        description="List triggered alerts (alert instances that have fired)",
    )
    async def cdp_list_alerts(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List triggered alerts."""
        result = await http_client.get(
            "alerts",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_alert",
        description="Get a specific triggered alert by ID",
    )
    async def cdp_get_alert(
        alert_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific triggered alert by ID."""
        result = await http_client.get(
            f"alert/{alert_id}",
            tenant_id=tenant_id,
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_alert",
        description="Delete/dismiss a triggered alert",
    )
    async def cdp_delete_alert(
        alert_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete/dismiss a triggered alert."""
        result = await http_client.delete(
            f"alert/{alert_id}",
            tenant_id=tenant_id,
            path_style=PATH_STYLE,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Alert deleted successfully."
