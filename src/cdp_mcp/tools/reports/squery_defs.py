"""
SQueryDef tools for CDP Report API.

Implements 8 MCP tools: list, create, get, update, delete, copy, generate, validate
SQueryDefs (SQL query definitions).
Source: acquia/cdp-campaignapi SQueryDefController
Endpoints use pathStyle "v2" (default): /v2/{tenantId}/report/sQueryDefs

SQueryDefs are SQL-based query definitions that can contain parameterized
expressions with input arguments and output attributes.
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_squery_def_tools(server: FastMCP) -> None:
    """Register all SQueryDef tools on the MCP server."""

    @server.tool(
        name="cdp_list_squery_defs",
        description="List all SQueryDefs (SQL query definitions) for a tenant.",
    )
    async def cdp_list_squery_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all SQueryDefs for a tenant."""
        result = await http_client.get(
            "report/sQueryDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_squery_def",
        description=(
            "Create a new SQueryDef. Pass definition as a JSON string. "
            "Requires name and expression (SQL query)."
        ),
    )
    async def cdp_create_squery_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new SQueryDef. API expects an array — wraps single object."""
        squery_def = json.loads(body)
        payload = squery_def if isinstance(squery_def, list) else [squery_def]

        result = await http_client.post(
            "report/sQueryDefs",
            tenant_id=tenant_id,
            body=payload,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_squery_def",
        description="Get a SQueryDef by ID. Returns the full definition including expression and arguments.",
    )
    async def cdp_get_squery_def(
        squery_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a SQueryDef by ID."""
        result = await http_client.get(
            f"report/sQueryDefs/{squery_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_squery_def",
        description="Update an existing SQueryDef by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_squery_def(
        squery_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing SQueryDef by ID."""
        result = await http_client.put(
            f"report/sQueryDefs/{squery_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_squery_def",
        description="Delete a SQueryDef by ID.",
    )
    async def cdp_delete_squery_def(
        squery_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a SQueryDef by ID."""
        result = await http_client.delete(
            f"report/sQueryDefs/{squery_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return f"SQueryDef {squery_def_id} deleted successfully."

    @server.tool(
        name="cdp_copy_squery_def",
        description="Copy a SQueryDef by ID. Creates a duplicate of the query definition.",
    )
    async def cdp_copy_squery_def(
        squery_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Copy a SQueryDef by ID."""
        result = await http_client.post(
            f"report/sQueryDefs/{squery_def_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_generate_squery_def",
        description=(
            "Generate input/output arguments for a SQueryDef from its expression. "
            "Pass a SQueryDef JSON with an expression field. Returns the def "
            "with arguments and outputAttributes filled in."
        ),
    )
    async def cdp_generate_squery_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Generate arguments from a SQueryDef expression."""
        result = await http_client.post(
            "report/sQueryDefs",
            tenant_id=tenant_id,
            params={"action": "generate"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_validate_squery_def",
        description=(
            "Validate a SQueryDef's expression, arguments, and output attributes. "
            "Checks that parameter names, data types, and counts match the expression."
        ),
    )
    async def cdp_validate_squery_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Validate a SQueryDef expression."""
        result = await http_client.post(
            "report/sQueryDefs",
            tenant_id=tenant_id,
            params={"action": "validate"},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
