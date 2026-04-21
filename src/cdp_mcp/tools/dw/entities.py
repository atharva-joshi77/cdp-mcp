"""
Entity CRUD tools for CDP Data Warehouse API.

Implements 5 MCP tools: list, get, create, update, lookup entities.
Source: apiSpecification/specs/dwAPI.yaml
Endpoints use pathStyle "v2": /v2/{tenantId}/dw/entities/{resourceName}
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_entity_tools(server: FastMCP) -> None:
    """Register all entity CRUD tools on the MCP server."""

    @server.tool(
        name="cdp_list_entities",
        description=(
            "Query entities from a CDP data warehouse resource "
            "(e.g., customer, organization, transaction). "
            "Supports filtering via fq parameter."
        ),
    )
    async def cdp_list_entities(
        resource_name: str,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        fq: Optional[str] = None,
        sort: Optional[str] = None,
        include: Optional[str] = None,
    ) -> str:
        """Query entities from a CDP data warehouse resource."""
        params: dict = {"offset": offset, "limit": limit}
        if fq is not None:
            params["fq"] = fq
        if sort is not None:
            params["sort"] = sort
        if include is not None:
            params["include"] = include

        result = await http_client.get(
            f"dw/entities/{resource_name}",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_entity",
        description="Get a single entity by its resource name and ID",
    )
    async def cdp_get_entity(
        resource_name: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
        include: Optional[str] = None,
    ) -> str:
        """Get a single entity by its resource name and ID."""
        params: dict = {}
        if include is not None:
            params["include"] = include

        result = await http_client.get(
            f"dw/entities/{resource_name}/{resource_id}",
            tenant_id=tenant_id,
            params=params if params else None,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_entity",
        description="Create a new entity in a DW resource. Pass entity data as a JSON string.",
    )
    async def cdp_create_entity(
        resource_name: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new entity in a DW resource."""
        result = await http_client.post(
            f"dw/entities/{resource_name}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_entity",
        description="Update an existing entity in a DW resource. Pass updated fields as a JSON string.",
    )
    async def cdp_update_entity(
        resource_name: str,
        resource_id: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing entity in a DW resource."""
        result = await http_client.put(
            f"dw/entities/{resource_name}/{resource_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_lookup_values",
        description=(
            "Lookup distinct values for a field in a DW entity resource. "
            "Requires the field name to look up. Pass lookup request as JSON string."
        ),
    )
    async def cdp_lookup_values(
        resource_name: str,
        field: str,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Lookup distinct values for a field in a DW entity resource."""
        result = await http_client.post(
            f"dw/entities/{resource_name}",
            tenant_id=tenant_id,
            params={"action": "lookup", "field": field},
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
