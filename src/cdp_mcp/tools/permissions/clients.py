"""
OAuth client management tools for CDP Permissions API.

Implements 5 MCP tools: list, get, create, update, delete clients.
Source: apiSpecification/specs/permissionsAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/clients, /v2/{tenantId}/clients/{clientId}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_client_tools(server: FastMCP) -> None:
    """Register all OAuth client management tools on the MCP server."""

    @server.tool(
        name="cdp_list_clients",
        description="List all OAuth clients for a tenant",
    )
    async def cdp_list_clients(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all OAuth clients for a tenant."""
        result = await http_client.get(
            "clients",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_client",
        description="Get a specific OAuth client by numeric ID",
    )
    async def cdp_get_client(
        client_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific OAuth client by numeric ID."""
        result = await http_client.get(
            f"clients/{client_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_client",
        description="Create a new OAuth client. Requires client_id_str, client_secret, grants, and token_validity.",
    )
    async def cdp_create_client(
        client_id_str: str,
        client_secret: str,
        grants: str,
        token_validity: int,
        tenant_id: Optional[str] = None,
        authorities: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> str:
        """Create a new OAuth client."""
        body: dict = {
            "clientId": client_id_str,
            "clientSecret": client_secret,
            "grants": grants,
            "tokenValidity": token_validity,
        }
        if authorities is not None:
            body["authorities"] = authorities
        if scope is not None:
            body["scope"] = scope

        result = await http_client.post(
            "clients",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_client",
        description="Update an existing OAuth client",
    )
    async def cdp_update_client(
        client_numeric_id: int,
        tenant_id: Optional[str] = None,
        client_id_str: Optional[str] = None,
        client_secret: Optional[str] = None,
        grants: Optional[str] = None,
        token_validity: Optional[int] = None,
        authorities: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> str:
        """Update an existing OAuth client."""
        body: dict = {}
        if client_id_str is not None:
            body["clientId"] = client_id_str
        if client_secret is not None:
            body["clientSecret"] = client_secret
        if grants is not None:
            body["grants"] = grants
        if token_validity is not None:
            body["tokenValidity"] = token_validity
        if authorities is not None:
            body["authorities"] = authorities
        if scope is not None:
            body["scope"] = scope

        result = await http_client.put(
            f"clients/{client_numeric_id}",
            tenant_id=tenant_id,
            body=body,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_client",
        description="Delete an OAuth client by numeric ID",
    )
    async def cdp_delete_client(
        client_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an OAuth client by numeric ID."""
        result = await http_client.delete(
            f"clients/{client_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Client deleted successfully."
