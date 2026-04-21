"""
CubicSetDef tools for CDP Report API.

Implements 6 MCP tools: list, create, get, update, delete, copy cubic set definitions.
Source: acquia/cdp-campaignapi CubicSetDefController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/cubicSetDefs
CubicSetDefs are Saiku-based OLAP query definitions referenced by CUBE-type reports.
Note: Collection POST accepts arrays — single objects are wrapped in an array.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_cubic_set_def_tools(server: FastMCP) -> None:
    """Register all cubic set definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_cubic_set_defs",
        description=(
            "List all CubicSetDefs (OLAP query definitions) for a tenant. "
            "These define Saiku-based cube queries used by CUBE-type reports."
        ),
    )
    async def cdp_list_cubic_set_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all CubicSetDefs for a tenant."""
        result = await http_client.get(
            "report/cubicSetDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_cubic_set_def",
        description=(
            "Create a new CubicSetDef. Pass definition as a JSON string. "
            "Requires name. The model field should be a serialized Saiku JSON string."
        ),
    )
    async def cdp_create_cubic_set_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new CubicSetDef. API expects an array — wraps single object."""
        cubic_set_def = json.loads(body)
        payload = cubic_set_def if isinstance(cubic_set_def, list) else [cubic_set_def]

        result = await http_client.post(
            "report/cubicSetDefs",
            tenant_id=tenant_id,
            body=payload,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_cubic_set_def",
        description="Get a CubicSetDef by ID. Returns the full definition including the model (Saiku query JSON).",
    )
    async def cdp_get_cubic_set_def(
        cubic_set_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a CubicSetDef by ID."""
        result = await http_client.get(
            f"report/cubicSetDefs/{cubic_set_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_cubic_set_def",
        description="Update an existing CubicSetDef by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_cubic_set_def(
        cubic_set_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing CubicSetDef by ID."""
        result = await http_client.put(
            f"report/cubicSetDefs/{cubic_set_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_cubic_set_def",
        description="Delete a CubicSetDef by ID",
    )
    async def cdp_delete_cubic_set_def(
        cubic_set_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a CubicSetDef by ID."""
        result = await http_client.delete(
            f"report/cubicSetDefs/{cubic_set_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"CubicSetDef {cubic_set_def_id} deleted successfully."

    @server.tool(
        name="cdp_copy_cubic_set_def",
        description="Copy a CubicSetDef by ID. Creates a duplicate of the OLAP query definition.",
    )
    async def cdp_copy_cubic_set_def(
        cubic_set_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy a CubicSetDef by ID."""
        result = await http_client.post(
            f"report/cubicSetDefs/{cubic_set_def_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
