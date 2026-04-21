"""
Data purge tools for CDP Data Warehouse API.

Implements 1 MCP tool: purge customer data.
Source: acquia/cdp-dwapi DwPurgeController.java
Endpoints: /v2/{tenantId}/dw/purge
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_purge_tools(server: FastMCP) -> None:
    """Register data purge tools on the MCP server."""

    @server.tool(
        name="cdp_purge_data",
        description=(
            "Purge customer data from the data warehouse. "
            "Pass purge request as a JSON string with customerIds, "
            "purgeReason, and optional purgeTypes."
        ),
    )
    async def cdp_purge_data(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Purge customer data from the data warehouse."""
        result = await http_client.post(
            "dw/purge",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
