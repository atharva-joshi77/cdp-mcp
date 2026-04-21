"""
Execution summary group tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete execution summary groups.
Source: acquia/cdp-configapi ExecutionSummaryGroupController.java
Endpoints: /v2/{tenantId}/config/executionSummaryGroups
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_execution_summary_group_tools(server: FastMCP) -> None:
    """Register all execution summary group tools on the MCP server."""

    @server.tool(
        name="cdp_list_execution_summary_groups",
        description="List execution summary groups for a tenant",
    )
    async def cdp_list_execution_summary_groups(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List execution summary groups for a tenant."""
        result = await http_client.get(
            "config/executionSummaryGroups",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_execution_summary_group",
        description="Get a specific execution summary group by ID",
    )
    async def cdp_get_execution_summary_group(
        group_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific execution summary group by ID."""
        result = await http_client.get(
            f"config/executionSummaryGroups/{group_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_execution_summary_group",
        description="Create a new execution summary group. Pass configuration as a JSON string.",
    )
    async def cdp_create_execution_summary_group(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new execution summary group."""
        result = await http_client.post(
            "config/executionSummaryGroups",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_execution_summary_group",
        description="Update an execution summary group. Pass updated fields as a JSON string.",
    )
    async def cdp_update_execution_summary_group(
        group_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an execution summary group."""
        result = await http_client.put(
            f"config/executionSummaryGroups/{group_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_execution_summary_group",
        description="Delete an execution summary group",
    )
    async def cdp_delete_execution_summary_group(
        group_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an execution summary group."""
        result = await http_client.delete(
            f"config/executionSummaryGroups/{group_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Execution summary group deleted successfully."
