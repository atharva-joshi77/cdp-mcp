"""
Audience definition tools for CDP Campaign API.

Implements 7 MCP tools: list, get, create, update, delete audience defs + lookup + calculate count.
Source: acquia/cdp-campaignapi AudienceDefController.java
Controller path: /v2/{tenantId}/campaign/audienceDefs
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_audience_def_tools(server: FastMCP) -> None:
    """Register all audience definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_audience_defs",
        description="List audience definitions for a tenant. Returns paged results.",
    )
    async def cdp_list_audience_defs(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List audience definitions for a tenant."""
        result = await http_client.get(
            "campaign/audienceDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_audience_def",
        description="Get a specific audience definition by ID",
    )
    async def cdp_get_audience_def(
        audience_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific audience definition by ID."""
        result = await http_client.get(
            f"campaign/audienceDefs/{audience_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_audience_def",
        description=(
            "Create a new audience definition. WARNING: the underlying endpoint "
            "POST /campaign/audienceDefs is NOT supported on current CDP builds and "
            "will return E400 'Request method POST is not supported'. Instead, define "
            "the audience INLINE on a campaign via cdp_create_campaign + cdp_update_campaign. "
            "See resource cdp://docs/campaign-playbook."
        ),
    )
    async def cdp_create_audience_def(
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Create a new audience definition."""
        result = await http_client.post(
            "campaign/audienceDefs",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_audience_def",
        description="Update an existing audience definition. Pass updated fields as a JSON string.",
    )
    async def cdp_update_audience_def(
        audience_def_id: int,
        body: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Update an existing audience definition."""
        result = await http_client.put(
            f"campaign/audienceDefs/{audience_def_id}",
            tenant_id=tenant_id,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_audience_def",
        description="Delete an audience definition",
    )
    async def cdp_delete_audience_def(
        audience_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete an audience definition."""
        result = await http_client.delete(
            f"campaign/audienceDefs/{audience_def_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Audience definition deleted successfully."

    @server.tool(
        name="cdp_execute_audience_def",
        description=(
            "Execute/calculate an audience definition. "
            "Triggers the audience calculation workflow."
        ),
    )
    async def cdp_execute_audience_def(
        audience_def_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Execute an audience definition to calculate the audience."""
        result = await http_client.post(
            f"campaign/audienceDefs/{audience_def_id}",
            tenant_id=tenant_id,
            params={"action": "execute"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_lookup_audience_defs",
        description=(
            "Lookup audiences by name. "
            "Returns matching audience definitions with optional offset/limit."
        ),
    )
    async def cdp_lookup_audience_defs(
        lookup: str,
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """Lookup audiences by name."""
        params: dict = {"lookup": lookup}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        result = await http_client.get(
            "campaign/audienceDefs",
            tenant_id=tenant_id,
            params=params,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
