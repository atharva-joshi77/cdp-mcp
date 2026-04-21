"""
Message definition CRUD tools for CDP Campaign API.

Implements 5 MCP tools: list, get, create, update, delete message definitions.
Source: acquia/cdp-campaignapi MessageDefController.java
Controller path: /v2/{tenantId}/campaign/messageDefs
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_message_def_tools(server: FastMCP) -> None:
    """Register all message definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_message_defs",
        description="List message definitions for a tenant. Returns paged results.",
    )
    async def cdp_list_message_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List message definitions for a tenant."""
        result = await http_client.get(
            "campaign/messageDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_message_def",
        description="Get a specific message definition by ID",
    )
    async def cdp_get_message_def(
        message_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific message definition by ID."""
        result = await http_client.get(
            f"campaign/messageDefs/{message_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_message_def",
        description=(
            "Create standalone message definitions. Pass as a JSON string list. "
            "WARNING: standalone messageDefs created here CANNOT be referenced from a "
            "campaign by resourceId — the server rejects shared references with E0420. "
            "For campaign-bound emails, instead put the messageDef object INLINE in the "
            "campaign's 'messageDefs' array via cdp_update_campaign. Only use this tool "
            "for message templates that are independently managed."
        ),
    )
    async def cdp_create_message_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create message definitions."""
        parsed = json.loads(body)
        # Source controller expects List<MessageDef>
        if not isinstance(parsed, list):
            parsed = [parsed]

        result = await http_client.post(
            "campaign/messageDefs",
            tenant_id=tenant_id,
            body=parsed,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_message_def",
        description="Update a message definition by ID. Pass updated fields as a JSON string.",
    )
    async def cdp_update_message_def(
        message_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a message definition."""
        result = await http_client.put(
            f"campaign/messageDefs/{message_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_message_def",
        description="Delete a message definition by ID",
    )
    async def cdp_delete_message_def(
        message_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a message definition."""
        result = await http_client.delete(
            f"campaign/messageDefs/{message_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Message definition deleted successfully."
