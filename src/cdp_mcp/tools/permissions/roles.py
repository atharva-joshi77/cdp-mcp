"""
Role management tools for CDP Permissions API.

Implements 6 MCP tools: list, get, create, update, delete roles + list actions.
Source: acquia/cdp-permissions-api RoleController.java
Endpoints: /v2/{tenantId}/roles, /v2/{tenantId}/roles/{roleId}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_role_tools(server: FastMCP) -> None:
    """Register all role management tools on the MCP server."""

    @server.tool(
        name="cdp_list_roles",
        description=(
            "List all roles for a CDP tenant. Supports optional search and "
            "tenantIds (comma-separated string, e.g. '0,425,802') for multi-tenant queries."
        ),
    )
    async def cdp_list_roles(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        tenant_ids: Optional[str] = None,
    ) -> str:
        """List all roles for a CDP tenant."""
        result = await http_client.get(
            "roles",
            tenant_id=tenant_id,
            params={
                "offset": offset,
                "limit": limit,
                "search": search,
                "tenantIds": tenant_ids,
            },
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_role",
        description="Get a specific role by ID",
    )
    async def cdp_get_role(
        role_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific role by ID."""
        result = await http_client.get(
            f"roles/{role_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_role",
        description="Create a new role with whitelist/blacklist permissions. Pass whitelist/blacklist as JSON arrays of Permission objects.",
    )
    async def cdp_create_role(
        name: str,
        tenant_id: Optional[str] = None,
        whitelist: Optional[str] = None,
        blacklist: Optional[str] = None,
        included: Optional[str] = None,
    ) -> str:
        """Create a new role with whitelist/blacklist permissions."""
        body: dict = {"name": name}
        if whitelist is not None:
            body["whitelist"] = json.loads(whitelist)
        if blacklist is not None:
            body["blacklist"] = json.loads(blacklist)
        if included is not None:
            body["included"] = json.loads(included)

        result = await http_client.post(
            "roles",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_role",
        description="Update an existing role. Pass whitelist/blacklist/included as JSON strings.",
    )
    async def cdp_update_role(
        role_id: int,
        tenant_id: Optional[str] = None,
        name: Optional[str] = None,
        whitelist: Optional[str] = None,
        blacklist: Optional[str] = None,
        included: Optional[str] = None,
    ) -> str:
        """Update an existing role."""
        body: dict = {}
        if name is not None:
            body["name"] = name
        if whitelist is not None:
            body["whitelist"] = json.loads(whitelist)
        if blacklist is not None:
            body["blacklist"] = json.loads(blacklist)
        if included is not None:
            body["included"] = json.loads(included)

        result = await http_client.put(
            f"roles/{role_id}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_role",
        description="Delete a role by ID",
    )
    async def cdp_delete_role(
        role_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a role by ID."""
        result = await http_client.delete(
            f"roles/{role_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Role deleted successfully."

    @server.tool(
        name="cdp_list_role_actions",
        description="List all available permission actions that can be assigned to roles",
    )
    async def cdp_list_role_actions(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List all available permission actions that can be assigned to roles."""
        result = await http_client.get(
            "roles/actions",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
