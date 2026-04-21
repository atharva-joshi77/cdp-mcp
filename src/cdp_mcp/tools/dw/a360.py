"""
Customer 360 tools for CDP Data Warehouse API.

Implements 4 MCP tools: customer 360 list, detail, realtime, identities.
Source: apiSpecification/specs/dwAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/dw/a360/{resourceName}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_a360_tools(server: FastMCP) -> None:
    """Register all Customer 360 tools on the MCP server."""

    @server.tool(
        name="cdp_get_customer_360",
        description=(
            "Get Customer 360 summary view for a resource type "
            "(e.g., list of customer profiles)"
        ),
    )
    async def cdp_get_customer_360(
        resource_name: str,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        fq: Optional[str] = None,
    ) -> str:
        """Get Customer 360 summary view for a resource type."""
        params: dict = {"offset": offset, "limit": limit}
        if fq is not None:
            params["fq"] = fq

        result = await http_client.get(
            f"dw/a360/{resource_name}",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_customer_360_detail",
        description="Get detailed Customer 360 profile for a specific customer",
    )
    async def cdp_get_customer_360_detail(
        resource_name: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get detailed Customer 360 profile for a specific customer."""
        result = await http_client.get(
            f"dw/a360/{resource_name}/{resource_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_customer_360_realtime",
        description="Get real-time Customer 360 data (includes latest streaming events)",
    )
    async def cdp_get_customer_360_realtime(
        resource_name: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get real-time Customer 360 data (includes latest streaming events)."""
        result = await http_client.get(
            f"dw/a360/{resource_name}/{resource_id}/rt",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_customer_identities",
        description=(
            "Get all identities associated with given customer IDs. "
            "Pass customer IDs as a JSON string body."
        ),
    )
    async def cdp_get_customer_identities(
        resource_name: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get all identities associated with given customer IDs."""
        result = await http_client.post(
            f"dw/a360/{resource_name}",
            tenant_id=tenant_id,
            params={"action": "getidentities"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
