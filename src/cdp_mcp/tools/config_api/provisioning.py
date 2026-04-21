"""
Provisioning tools for CDP Config API.

Implements 1 MCP tool: list provisioning packages.
Source: acquia/cdp-configapi ProvisionerController.java
Endpoints: /v2/{tenantId}/config/provisioning/packages
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_provisioning_tools(server: FastMCP) -> None:
    """Register provisioning tools on the MCP server."""

    @server.tool(
        name="cdp_list_provisioning_packages",
        description="List available provisioning packages for a tenant",
    )
    async def cdp_list_provisioning_packages(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List available provisioning packages."""
        result = await http_client.get(
            "config/provisioning/packages",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
