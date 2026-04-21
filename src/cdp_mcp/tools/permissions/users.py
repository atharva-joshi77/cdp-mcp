"""
User management tools for CDP Permissions API.

Implements 5 MCP tools: list, get, create, update, delete users.
Source: acquia/cdp-permissions-api UserController.java
Endpoints: /v2/{tenantId}/users, /v2/{tenantId}/users/{userId}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_user_tools(server: FastMCP) -> None:
    """Register all user management tools on the MCP server."""

    @server.tool(
        name="cdp_list_users",
        description="List all CDP users for a tenant with pagination; optional search filter",
    )
    async def cdp_list_users(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> str:
        """List all CDP users for a tenant with pagination and optional search string."""
        result = await http_client.get(
            "users",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit, "search": search},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_user",
        description="Get a specific CDP user by ID",
    )
    async def cdp_get_user(
        user_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific CDP user by ID."""
        result = await http_client.get(
            f"users/{user_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_user",
        description="Create a new CDP user. Requires userName and password.",
    )
    async def cdp_create_user(
        user_name: str,
        password: str,
        tenant_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> str:
        """Create a new CDP user. Requires username and password."""
        body: dict = {"username": user_name, "password": password}
        if first_name is not None:
            body["firstName"] = first_name
        if last_name is not None:
            body["lastName"] = last_name

        result = await http_client.post(
            "users",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_user",
        description="Update an existing CDP user's details",
    )
    async def cdp_update_user(
        user_id: int,
        tenant_id: Optional[str] = None,
        user_name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> str:
        """Update an existing CDP user's details."""
        body: dict = {}
        if user_name is not None:
            body["username"] = user_name
        if first_name is not None:
            body["firstName"] = first_name
        if last_name is not None:
            body["lastName"] = last_name
        if password is not None:
            body["password"] = password

        result = await http_client.put(
            f"users/{user_id}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_user",
        description="Delete a CDP user by ID",
    )
    async def cdp_delete_user(
        user_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a CDP user by ID."""
        result = await http_client.delete(
            f"users/{user_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "User deleted successfully."
