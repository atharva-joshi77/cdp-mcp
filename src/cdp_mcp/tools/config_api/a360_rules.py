"""
A360 rule tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete A360 rules.
Source: acquia/cdp-configapi A360RuleController.java
Endpoints: /v2/{tenantId}/config/a360Rules
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_a360_rule_tools(server: FastMCP) -> None:
    """Register all A360 rule tools on the MCP server."""

    @server.tool(
        name="cdp_list_a360_rules",
        description="List A360 identity resolution rules",
    )
    async def cdp_list_a360_rules(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List A360 identity resolution rules."""
        result = await http_client.get(
            "config/a360Rules",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_a360_rule",
        description="Get a specific A360 rule by ID",
    )
    async def cdp_get_a360_rule(
        rule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific A360 rule by ID."""
        result = await http_client.get(
            f"config/a360Rules/{rule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_a360_rule",
        description="Create a new A360 identity resolution rule. Pass rule as a JSON string.",
    )
    async def cdp_create_a360_rule(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new A360 rule."""
        result = await http_client.post(
            "config/a360Rules",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_a360_rule",
        description="Update an existing A360 rule. Pass updated fields as a JSON string.",
    )
    async def cdp_update_a360_rule(
        rule_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing A360 rule."""
        result = await http_client.put(
            f"config/a360Rules/{rule_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_a360_rule",
        description="Delete an A360 rule",
    )
    async def cdp_delete_a360_rule(
        rule_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an A360 rule."""
        result = await http_client.delete(
            f"config/a360Rules/{rule_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "A360 rule deleted successfully."
