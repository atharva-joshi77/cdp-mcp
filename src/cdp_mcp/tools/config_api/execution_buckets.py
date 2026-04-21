"""
Execution bucket tools for CDP Config API.

Implements 4 MCP tools: list, create, update, delete execution buckets.
Source: acquia/cdp-configapi ExecutionBucketController.java
Endpoints: /v2/{tenantId}/config/executionBuckets
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_execution_bucket_tools(server: FastMCP) -> None:
    """Register all execution bucket tools on the MCP server."""

    @server.tool(
        name="cdp_list_execution_buckets",
        description="List execution buckets for a tenant",
    )
    async def cdp_list_execution_buckets(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List execution buckets for a tenant."""
        result = await http_client.get(
            "config/executionBuckets",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_execution_bucket",
        description="Create a new execution bucket. Pass configuration as a JSON string.",
    )
    async def cdp_create_execution_bucket(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new execution bucket."""
        result = await http_client.post(
            "config/executionBuckets",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_execution_bucket",
        description="Update an execution bucket. Pass updated fields as a JSON string.",
    )
    async def cdp_update_execution_bucket(
        bucket_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an execution bucket."""
        result = await http_client.put(
            f"config/executionBuckets/{bucket_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_execution_bucket",
        description="Delete an execution bucket",
    )
    async def cdp_delete_execution_bucket(
        bucket_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an execution bucket."""
        result = await http_client.delete(
            f"config/executionBuckets/{bucket_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Execution bucket deleted successfully."
