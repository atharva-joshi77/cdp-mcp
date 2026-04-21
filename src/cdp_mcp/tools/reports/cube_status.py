"""
Cube status tools for CDP Report API.

Implements 2 MCP tools: get cube status for specific cubes, get all cube statuses.
Source: acquia/cdp-campaignapi CubeStatusController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/cubeStatus
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_cube_status_tools(server: FastMCP) -> None:
    """Register cube status tools on the MCP server."""

    @server.tool(
        name="cdp_get_cube_status",
        description=(
            "Get the processing status of all OLAP cubes for a tenant. "
            "Returns the status of each cube including whether it is ready."
        ),
    )
    async def cdp_get_cube_status(
        tenant_id: Optional[str] = None,
    ) -> str:
        """GET /v2/{tenantId}/report/cubeStatus"""
        result = await http_client.get(
            "report/cubeStatus",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_cube_status_by_names",
        description=(
            "Get the processing status of specific OLAP cubes by name. "
            "Pass a JSON array of cube unique names as a string."
        ),
    )
    async def cdp_get_cube_status_by_names(
        cube_names: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """GET /v2/{tenantId}/report/cubeStatus?cubes={cubeNames}"""
        result = await http_client.get(
            "report/cubeStatus",
            tenant_id=tenant_id,
            params={"cubes": cube_names},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
