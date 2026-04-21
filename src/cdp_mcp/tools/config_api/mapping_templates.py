"""
Mapping template tools for CDP Config API.

Implements 5 MCP tools: list, get, create, update, delete mapping templates.
Source: acquia/cdp-configapi MappingTemplateController.java
Endpoints: /v2/{tenantId}/config/mappingTemplates
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_mapping_template_tools(server: FastMCP) -> None:
    """Register all mapping template tools on the MCP server."""

    @server.tool(
        name="cdp_list_mapping_templates",
        description="List mapping templates for a tenant",
    )
    async def cdp_list_mapping_templates(
        tenant_id: Optional[str] = None,
    ) -> str:
        """List mapping templates for a tenant."""
        result = await http_client.get(
            "config/mappingTemplates",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_mapping_template",
        description="Get a specific mapping template by ID",
    )
    async def cdp_get_mapping_template(
        template_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific mapping template by ID."""
        result = await http_client.get(
            f"config/mappingTemplates/{template_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_mapping_template",
        description="Create a new mapping template. Pass template as a JSON string.",
    )
    async def cdp_create_mapping_template(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new mapping template."""
        result = await http_client.post(
            "config/mappingTemplates",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_mapping_template",
        description="Update an existing mapping template. Pass updated fields as a JSON string.",
    )
    async def cdp_update_mapping_template(
        template_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing mapping template."""
        result = await http_client.put(
            f"config/mappingTemplates/{template_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_mapping_template",
        description="Delete a mapping template",
    )
    async def cdp_delete_mapping_template(
        template_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a mapping template."""
        result = await http_client.delete(
            f"config/mappingTemplates/{template_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Mapping template deleted successfully."
