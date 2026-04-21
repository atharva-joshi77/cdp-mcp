"""
Schema checkpoint tools for CDP Config API.

Implements 1 MCP tool: get schema checkpoints.
Source: acquia/cdp-configapi SchemaCheckpointController.java
Endpoints: /v2/{tenantId}/config/schemaCheckpoints
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_schema_checkpoint_tools(server: FastMCP) -> None:
    """Register schema checkpoint tools on the MCP server."""

    @server.tool(
        name="cdp_get_schema_checkpoints",
        description="Get schema checkpoints for a tenant",
    )
    async def cdp_get_schema_checkpoints(
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get schema checkpoints for a tenant."""
        result = await http_client.get(
            "config/schemaCheckpoints",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
