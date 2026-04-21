"""
Compaction request tools for CDP Config API.

Implements 3 MCP tools: list, create, unschedule compaction requests.
Source: acquia/cdp-configapi CompactionRequestController.java
Endpoints: /v2/{tenantId}/config/compactionRequests
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_compaction_request_tools(server: FastMCP) -> None:
    """Register all compaction request tools on the MCP server."""

    @server.tool(
        name="cdp_list_compaction_requests",
        description="List compaction requests for a tenant",
    )
    async def cdp_list_compaction_requests(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List compaction requests for a tenant."""
        result = await http_client.get(
            "config/compactionRequests",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_compaction_request",
        description="Create a new compaction request. Pass request details as a JSON string.",
    )
    async def cdp_create_compaction_request(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new compaction request."""
        result = await http_client.post(
            "config/compactionRequests",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_unschedule_compaction_request",
        description="Unschedule a compaction request by ID",
    )
    async def cdp_unschedule_compaction_request(
        request_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Unschedule a compaction request."""
        result = await http_client.delete(
            f"config/compactionRequests/{request_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Compaction request unscheduled successfully."
