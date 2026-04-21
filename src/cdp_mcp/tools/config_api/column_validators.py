"""
Column validator tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete column validators.
Source: acquia/cdp-configapi ValidatorController.java
Endpoints: /v2/{tenantId}/config/columnValidators
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_column_validator_tools(server: FastMCP) -> None:
    """Register all column validator tools on the MCP server."""

    @server.tool(
        name="cdp_list_column_validators",
        description="List column validators for a tenant",
    )
    async def cdp_list_column_validators(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List column validators for a tenant."""
        result = await http_client.get(
            "config/columnValidators",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_column_validator",
        description="Get a specific column validator by ID",
    )
    async def cdp_get_column_validator(
        validator_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific column validator by ID."""
        result = await http_client.get(
            f"config/columnValidators/{validator_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_column_validator",
        description="Create a new column validator. Pass validator as a JSON string.",
    )
    async def cdp_create_column_validator(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new column validator."""
        result = await http_client.post(
            "config/columnValidators",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_column_validator",
        description="Update a column validator. Pass updated fields as a JSON string.",
    )
    async def cdp_update_column_validator(
        validator_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update a column validator."""
        result = await http_client.put(
            f"config/columnValidators/{validator_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_column_validator",
        description="Delete a column validator",
    )
    async def cdp_delete_column_validator(
        validator_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a column validator."""
        result = await http_client.delete(
            f"config/columnValidators/{validator_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Column validator deleted successfully."
