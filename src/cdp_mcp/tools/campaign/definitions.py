"""
Campaign definition CRUD tools for CDP Campaign API.

Implements 6 MCP tools: list, get, create, update, delete, clone campaigns.
Source: acquia/cdp-campaignapi CampaignDefController.java
Controller path: /v2/{tenantId}/campaign/campaignDefs
"""

from __future__ import annotations

import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from cdp_mcp.utils.error_handler import format_error
from cdp_mcp.utils.http_client import http_client


def register_campaign_def_tools(server: FastMCP) -> None:
    """Register all campaign definition tools on the MCP server."""

    @server.tool(
        name="cdp_list_campaigns",
        description="List all campaign definitions for a tenant. Returns paged results.",
    )
    async def cdp_list_campaigns(
        tenant_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """List all campaign definitions for a tenant."""
        result = await http_client.get(
            "campaign/campaignDefs",
            tenant_id=tenant_id,
            params={"offset": offset, "limit": limit},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_get_campaign",
        description="Get a specific campaign definition by ID",
    )
    async def cdp_get_campaign(
        campaign_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Get a specific campaign definition by ID."""
        result = await http_client.get(
            f"campaign/campaignDefs/{campaign_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_create_campaign",
        description=(
            "Create a new campaign definition. Recommended workflow: call with "
            "name+description ONLY to get a resourceId, then call cdp_update_campaign "
            "with the full body containing INLINE 'audience' and INLINE 'messageDefs' "
            "objects. Do NOT reference an existing messageDef by resourceId — shared "
            "messageDefs are rejected with E0420. See resource cdp://docs/campaign-playbook "
            "for the full body template, operator enum, and time-window math.\n\n"
            "Pass folder_id to place the campaign under a specific Campaign folder (the "
            "UI always does this). Omit it to let the backend default to the tenant's "
            "root folder."
        ),
    )
    async def cdp_create_campaign(
        name: str,
        tenant_id: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
        folder_id: Optional[int] = None,
    ) -> str:
        """Create a new campaign definition."""
        if body is not None:
            campaign = json.loads(body)
        else:
            campaign: dict = {"name": name}
            if description is not None:
                campaign["description"] = description

        params: dict = {}
        if folder_id is not None:
            params["folderId"] = folder_id

        # Source controller expects a List<CampaignDef>
        result = await http_client.post(
            "campaign/campaignDefs",
            tenant_id=tenant_id,
            params=params or None,
            body=[campaign],
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_update_campaign",
        description=(
            "Update an existing campaign definition. Pass updated fields as a JSON string. "
            "Pass folder_id to move the campaign into a specific folder (matches UI save "
            "behaviour, which always sends ?folderId=...)."
        ),
    )
    async def cdp_update_campaign(
        campaign_id: int,
        body: str,
        tenant_id: Optional[str] = None,
        folder_id: Optional[int] = None,
    ) -> str:
        """Update an existing campaign definition."""
        params: dict = {}
        if folder_id is not None:
            params["folderId"] = folder_id

        result = await http_client.put(
            f"campaign/campaignDefs/{campaign_id}",
            tenant_id=tenant_id,
            params=params or None,
            body=json.loads(body),
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)

    @server.tool(
        name="cdp_delete_campaign",
        description="Delete a campaign definition by ID",
    )
    async def cdp_delete_campaign(
        campaign_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Delete a campaign definition."""
        result = await http_client.delete(
            f"campaign/campaignDefs/{campaign_id}",
            tenant_id=tenant_id,
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return "Campaign deleted successfully."

    @server.tool(
        name="cdp_clone_campaign",
        description="Clone/copy a campaign definition by ID. Creates a duplicate.",
    )
    async def cdp_clone_campaign(
        campaign_id: int,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Clone a campaign definition."""
        result = await http_client.post(
            f"campaign/campaignDefs/{campaign_id}",
            tenant_id=tenant_id,
            params={"action": "copy"},
        )
        if not result.success:
            return f"Error: {format_error(result.error)}"
        return json.dumps(result.data, indent=2)
