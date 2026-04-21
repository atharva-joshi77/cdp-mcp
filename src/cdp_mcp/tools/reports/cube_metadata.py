"""
OLAP cube metadata tools for CDP Report API.

Implements 2 MCP tools: list cubes, get dimension values.
Source: acquia/cdp-campaignapi CubeMetadataController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/cubemetadata

Note: The dimension values endpoint has a deeply nested path:
  /report/cubemetadata/{cubeId}/dimensions/{dimensionId}/hierarchies/{hierarchyId}/levels/{levelName}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_cube_metadata_tools(server: FastMCP) -> None:
    """Register all OLAP cube metadata tools on the MCP server."""

    @server.tool(
        name="cdp_list_cube_metadata",
        description="List all available OLAP cubes for a tenant. Returns cube unique names and captions.",
    )
    async def cdp_list_cube_metadata(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all available OLAP cubes for a tenant."""
        result = await http_client.get(
            "report/cubemetadata",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_dimension_values",
        description=(
            "Get the values for a specific dimension level within an OLAP cube hierarchy. "
            "Requires cube_id, dimension_id, hierarchy_id, and level_name. "
            "Use cdp_get_cube_metadata first to discover these identifiers."
        ),
    )
    async def cdp_get_dimension_values(
        cube_id: str,
        dimension_id: str,
        hierarchy_id: str,
        level_name: str,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Get values for a specific dimension level within an OLAP cube hierarchy."""
        path = (
            f"report/cubemetadata/{cube_id}"
            f"/dimensions/{dimension_id}"
            f"/hierarchies/{hierarchy_id}"
            f"/levels/{level_name}"
        )
        result = await http_client.get(
            path,
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
