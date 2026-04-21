"""
Self-service user tools for CDP Permissions API.

Implements 6 MCP tools: list, get, create, update, delete, update-status self-service users.
Source: acquia/cdp-permissions-api SelfServiceUserController.java
Endpoints: /v2/{tenantId}/selfservice-users
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_self_service_user_tools(server: FastMCP) -> None:
    """Register self-service user tools on the MCP server."""

    @server.tool(
        name="cdp_list_selfservice_users",
        description="List all self-service users for a tenant",
    )
    async def cdp_list_selfservice_users(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List all self-service users for a tenant."""
        result = await http_client.get(
            "selfservice-users",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_selfservice_user",
        description="Get a specific self-service user by ID",
    )
    async def cdp_get_selfservice_user(
        user_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific self-service user by ID."""
        result = await http_client.get(
            f"selfservice-users/{user_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_selfservice_user",
        description="Create a new self-service user. Pass user details as a JSON string.",
    )
    async def cdp_create_selfservice_user(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new self-service user."""
        result = await http_client.post(
            "selfservice-users",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_selfservice_user",
        description="Update a self-service user. Pass updated fields as a JSON string.",
    )
    async def cdp_update_selfservice_user(
        user_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a self-service user."""
        result = await http_client.put(
            f"selfservice-users/{user_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_selfservice_user",
        description="Delete a self-service user by ID",
    )
    async def cdp_delete_selfservice_user(
        user_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a self-service user by ID."""
        result = await http_client.delete(
            f"selfservice-users/{user_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Self-service user deleted successfully."

    @server.tool(
        name="cdp_update_selfservice_user_status",
        description=(
            "Update a self-service user's status (e.g., activate/deactivate). "
            "Pass action and body as JSON string."
        ),
    )
    async def cdp_update_selfservice_user_status(
        user_id: int,
        action: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a self-service user's status."""
        result = await http_client.put(
            f"selfservice-users/{user_id}",
            tenant_id=tenant_id,
            params={"action": action},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
