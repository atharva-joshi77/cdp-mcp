"""
Audience count tools for CDP Data Warehouse API.

Implements 3 MCP tools: sync count, async calculate, poll result.
Source: apiSpecification/specs/dwAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/dw/audienceCount
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_audience_tools(server: FastMCP) -> None:
    """Register all audience count tools on the MCP server."""

    @server.tool(
        name="cdp_get_audience_count",
        description=(
            "Get audience count based on a segment definition (synchronous). "
            "Pass segment definition as a JSON string."
        ),
    )
    async def cdp_get_audience_count(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get audience count based on a segment definition (synchronous)."""
        result = await http_client.post(
            "dw/audienceCount",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_calculate_audience",
        description=(
            "Start an asynchronous audience count calculation. "
            "Returns a jobId to poll with cdp_get_calculated_count. "
            "Pass segment definition as a JSON string."
        ),
    )
    async def cdp_calculate_audience(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Start an asynchronous audience count calculation."""
        result = await http_client.post(
            "dw/audienceCount",
            tenant_id=tenant_id,
            params={"action": "calculate"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_calculated_count",
        description=(
            "Get the result of an async audience calculation "
            "(poll after cdp_calculate_audience)"
        ),
    )
    async def cdp_get_calculated_count(
        tenant_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """Get the result of an async audience calculation."""
        params: dict = {"action": "getcount"}
        if job_id is not None:
            params["jobId"] = job_id

        result = await http_client.get(
            "dw/audienceCount",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
