"""
Real-time metadata tools for CDP Data Warehouse API.

Implements 1 MCP tool: refresh real-time metadata switch.
Source: acquia/cdp-dwapi RTMetaController.java
Endpoints: /v2/{tenantId}/dw/rtmeta/refresh
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_rtmeta_tools(server: FastMCP) -> None:
    """Register real-time metadata tools on the MCP server."""

    @server.tool(
        name="cdp_refresh_rtmeta",
        description=(
            "Refresh the real-time metadata switch values. "
            "Must be called with tenantId=0."
        ),
    )
    async def cdp_refresh_rtmeta(
        tenant_id: Optional[str] = None,
    ) -> str:
        """Refresh the real-time metadata switch values."""
        result = await http_client.post(
            "dw/rtmeta/refresh",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Real-time metadata refreshed successfully."
